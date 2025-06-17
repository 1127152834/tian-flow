# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import os
from typing import Annotated, Literal

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.types import Command, interrupt
from langchain_mcp_adapters.client import MultiServerMCPClient

from src.agents import create_agent
from src.tools import (
    python_repl_tool,
    # API工具
    execute_api,
    list_available_apis,
    get_api_details,
    # Text2SQL工具
    text2sql_query,
    smart_text2sql_query,
    generate_sql_only,
    get_training_examples,
    validate_sql,
    # 数据库工具
    database_query,
    list_databases,
    search_databases,
    find_database_by_name,
    get_database_info,
    test_database_connection,
    # 图表生成工具
    generate_chart,
)
from src.tools.resource_discovery_tool import discover_resources
from src.agents import create_agent

from src.config.agents import AGENT_LLM_MAP
from src.config.configuration import Configuration
from src.llms.llm import get_llm_by_type
from src.prompts.planner_model import Plan
from src.prompts.template import apply_prompt_template
from src.utils.json_utils import repair_json_output

from .types import State

logger = logging.getLogger(__name__)


@tool
def handoff_to_planner(
    research_topic: Annotated[str, "The topic of the research task to be handed off."],
    locale: Annotated[str, "The user's detected language locale (e.g., en-US, zh-CN)."],
):
    """Handoff to planner agent to do plan."""
    # This tool is not returning anything: we're just using it
    # as a way for LLM to signal that it needs to hand off to planner agent
    return


@tool
def handoff_to_data_analyst(
    data_query: Annotated[str, "The data analysis request to be handed off."],
    locale: Annotated[str, "The user's detected language locale (e.g., en-US, zh-CN)."],
):
    """Handoff to data analyst for direct data analysis, visualization, and Q&A."""
    # This tool is not returning anything: we're just using it
    # as a way for LLM to signal that it needs to hand off to data analyst
    return


def background_investigation_node(state: State, config: RunnableConfig):
    logger.info("background investigation node is running.")
    query = state.get("research_topic")

    # 使用数据库查询替代网络搜索进行背景调研
    logger.info(f"使用数据库查询进行背景调研: {query}")
    background_investigation_results = f"基于查询 '{query}' 的数据库调研结果将由专门的数据分析师处理。"

    return {
        "background_investigation_results": background_investigation_results
    }


def planner_node(
    state: State, config: RunnableConfig
) -> Command[Literal["human_feedback", "reporter"]]:
    """Planner node that generate the full plan."""
    logger.info("Planner generating full plan")
    configurable = Configuration.from_runnable_config(config)
    plan_iterations = state["plan_iterations"] if state.get("plan_iterations", 0) else 0
    messages = apply_prompt_template("planner", state, configurable)

    if state.get("enable_background_investigation") and state.get(
        "background_investigation_results"
    ):
        messages += [
            {
                "role": "user",
                "content": (
                    "background investigation results of user query:\n"
                    + state["background_investigation_results"]
                    + "\n"
                ),
            }
        ]

    if configurable.enable_deep_thinking:
        llm = get_llm_by_type("reasoning")
    elif AGENT_LLM_MAP["planner"] == "basic":
        llm = get_llm_by_type("basic").with_structured_output(
            Plan,
            method="json_mode",
        )
    else:
        llm = get_llm_by_type(AGENT_LLM_MAP["planner"])

    # if the plan iterations is greater than the max plan iterations, return the reporter node
    if plan_iterations >= configurable.max_plan_iterations:
        return Command(goto="reporter")

    full_response = ""
    if AGENT_LLM_MAP["planner"] == "basic" and not configurable.enable_deep_thinking:
        response = llm.invoke(messages)
        full_response = response.model_dump_json(indent=4, exclude_none=True)
    else:
        response = llm.stream(messages)
        for chunk in response:
            full_response += chunk.content
    logger.debug(f"Current state messages: {state['messages']}")
    logger.info(f"Planner response: {full_response}")

    try:
        curr_plan = json.loads(repair_json_output(full_response))
    except json.JSONDecodeError:
        logger.warning("Planner response is not a valid JSON")
        if plan_iterations > 0:
            return Command(goto="reporter")
        else:
            return Command(goto="__end__")
    if curr_plan.get("has_enough_context"):
        logger.info("Planner response has enough context.")
        new_plan = Plan.model_validate(curr_plan)
        return Command(
            update={
                "messages": [AIMessage(content=full_response, name="planner")],
                "current_plan": new_plan,
            },
            goto="reporter",
        )
    return Command(
        update={
            "messages": [AIMessage(content=full_response, name="planner")],
            "current_plan": full_response,
        },
        goto="human_feedback",
    )


def human_feedback_node(
    state,
) -> Command[Literal["planner", "research_team", "reporter", "__end__"]]:
    current_plan = state.get("current_plan", "")
    # check if the plan is auto accepted
    auto_accepted_plan = state.get("auto_accepted_plan", False)
    if not auto_accepted_plan:
        feedback = interrupt("Please Review the Plan.")

        # if the feedback is not accepted, return the planner node
        if feedback and str(feedback).upper().startswith("[EDIT_PLAN]"):
            return Command(
                update={
                    "messages": [
                        HumanMessage(content=feedback, name="feedback"),
                    ],
                },
                goto="planner",
            )
        elif feedback and str(feedback).upper().startswith("[ACCEPTED]"):
            logger.info("Plan is accepted by user.")
        else:
            raise TypeError(f"Interrupt value of {feedback} is not supported.")

    # if the plan is accepted, run the following node
    plan_iterations = state["plan_iterations"] if state.get("plan_iterations", 0) else 0
    goto = "research_team"
    try:
        current_plan = repair_json_output(current_plan)
        # increment the plan iterations
        plan_iterations += 1
        # parse the plan
        new_plan = json.loads(current_plan)

        # HACK: Add default step_type to each step if it's missing
        for step in new_plan.get("steps", []):
            if "step_type" not in step:
                step["step_type"] = "research"

        if new_plan["has_enough_context"]:
            goto = "reporter"
    except json.JSONDecodeError:
        logger.warning("Planner response is not a valid JSON")
        if plan_iterations > 0:
            return Command(goto="reporter")
        else:
            return Command(goto="__end__")

    return Command(
        update={
            "current_plan": Plan.model_validate(new_plan),
            "plan_iterations": plan_iterations,
            "locale": new_plan["locale"],
        },
        goto=goto,
    )


def coordinator_node(
    state: State, config: RunnableConfig
) -> Command[Literal["planner", "data_analyst", "background_investigator", "__end__"]]:
    """Coordinator node that communicate with customers."""
    logger.info("Coordinator talking.")
    configurable = Configuration.from_runnable_config(config)
    messages = apply_prompt_template("coordinator", state)
    response = (
        get_llm_by_type(AGENT_LLM_MAP["coordinator"])
        .bind_tools([handoff_to_planner, handoff_to_data_analyst])
        .invoke(messages)
    )
    logger.debug(f"Current state messages: {state['messages']}")

    goto = "__end__"
    locale = state.get("locale", "en-US")  # Default locale if not specified
    research_topic = state.get("research_topic", "")

    if len(response.tool_calls) > 0:
        goto = "planner"  # default
        data_query = ""

        try:
            for tool_call in response.tool_calls:
                tool_name = tool_call.get("name", "")

                if tool_name == "handoff_to_planner":
                    goto = "planner"
                    if state.get("enable_background_investigation"):
                        goto = "background_investigator"
                    if tool_call.get("args", {}).get("locale") and tool_call.get("args", {}).get("research_topic"):
                        locale = tool_call.get("args", {}).get("locale")
                        research_topic = tool_call.get("args", {}).get("research_topic")
                    break

                elif tool_name == "handoff_to_data_analyst":
                    goto = "data_analyst"
                    if tool_call.get("args", {}).get("locale") and tool_call.get("args", {}).get("data_query"):
                        locale = tool_call.get("args", {}).get("locale")
                        data_query = tool_call.get("args", {}).get("data_query")
                    break

        except Exception as e:
            logger.error(f"Error processing tool calls: {e}")
    else:
        logger.warning(
            "Coordinator response contains no tool calls. Terminating workflow execution."
        )
        logger.debug(f"Coordinator response: {response}")

    update_dict = {
        "locale": locale,
        "resources": configurable.resources,
    }

    # 根据goto目标添加相应的参数
    if goto == "data_analyst":
        update_dict["data_query"] = data_query
    else:
        update_dict["research_topic"] = research_topic

    return Command(
        update=update_dict,
        goto=goto,
    )


def reporter_node(state: State, config: RunnableConfig):
    """Reporter node that write a final report."""
    logger.info("Reporter write final report")
    configurable = Configuration.from_runnable_config(config)
    current_plan = state.get("current_plan")
    input_ = {
        "messages": [
            HumanMessage(
                f"# Research Requirements\n\n## Task\n\n{current_plan.title}\n\n## Description\n\n{current_plan.thought}"
            )
        ],
        "locale": state.get("locale", "en-US"),
    }
    invoke_messages = apply_prompt_template("reporter", input_, configurable)
    observations = state.get("observations", [])

    # Add a reminder about the new report format, citation style, and table usage
    invoke_messages.append(
        HumanMessage(
            content="IMPORTANT: Structure your report according to the format in the prompt. Remember to include:\n\n1. Key Points - A bulleted list of the most important findings\n2. Overview - A brief introduction to the topic\n3. Detailed Analysis - Organized into logical sections\n4. Survey Note (optional) - For more comprehensive reports\n5. Key Citations - List all references at the end\n\nFor citations, DO NOT include inline citations in the text. Instead, place all citations in the 'Key Citations' section at the end using the format: `- [Source Title](URL)`. Include an empty line between each citation for better readability.\n\nPRIORITIZE USING MARKDOWN TABLES for data presentation and comparison. Use tables whenever presenting comparative data, statistics, features, or options. Structure tables with clear headers and aligned columns. Example table format:\n\n| Feature | Description | Pros | Cons |\n|---------|-------------|------|------|\n| Feature 1 | Description 1 | Pros 1 | Cons 1 |\n| Feature 2 | Description 2 | Pros 2 | Cons 2 |",
            name="system",
        )
    )

    for observation in observations:
        invoke_messages.append(
            HumanMessage(
                content=f"Below are some observations for the research task:\n\n{observation}",
                name="observation",
            )
        )
    logger.debug(f"Current invoke messages: {invoke_messages}")
    response = get_llm_by_type(AGENT_LLM_MAP["reporter"]).invoke(invoke_messages)
    response_content = response.content
    logger.info(f"reporter response: {response_content}")

    return {"final_report": response_content}


def research_team_node(state: State):
    """Research team node that collaborates on tasks."""
    logger.info("Research team is collaborating on tasks.")
    pass


async def _execute_agent_step(
    state: State, agent, agent_name: str
) -> Command[Literal["research_team"]]:
    """Helper function to execute a step using the specified agent."""
    current_plan = state.get("current_plan")
    observations = state.get("observations", [])

    # Find the first unexecuted step
    current_step = None
    completed_steps = []
    for step in current_plan.steps:
        if not step.execution_res:
            current_step = step
            break
        else:
            completed_steps.append(step)

    if not current_step:
        logger.warning("No unexecuted step found")
        return Command(goto="research_team")

    logger.info(f"Executing step: {current_step.title}, agent: {agent_name}")

    # Format completed steps information
    completed_steps_info = ""
    if completed_steps:
        completed_steps_info = "# Existing Research Findings\n\n"
        for i, step in enumerate(completed_steps):
            completed_steps_info += f"## Existing Finding {i + 1}: {step.title}\n\n"
            completed_steps_info += f"<finding>\n{step.execution_res}\n</finding>\n\n"

    # Prepare the input for the agent with completed steps info
    agent_input = {
        "messages": [
            HumanMessage(
                content=f"{completed_steps_info}# Current Task\n\n## Title\n\n{current_step.title}\n\n## Description\n\n{current_step.description}\n\n## Locale\n\n{state.get('locale', 'en-US')}"
            )
        ]
    }

    # Add citation reminder for researcher agent
    if agent_name == "researcher":
        if state.get("resources"):
            resources_info = "**The user mentioned the following resource files:**\n\n"
            for resource in state.get("resources"):
                resources_info += f"- {resource.title} ({resource.description})\n"

            agent_input["messages"].append(
                HumanMessage(
                    content=resources_info
                    + "\n\n"
                    + "You MUST use the **local_search_tool** to retrieve the information from the resource files.",
                )
            )

        agent_input["messages"].append(
            HumanMessage(
                content="IMPORTANT: DO NOT include inline citations in the text. Instead, track all sources and include a References section at the end using link reference format. Include an empty line between each citation for better readability. Use this format for each reference:\n- [Source Title](URL)\n\n- [Another Source](URL)",
                name="system",
            )
        )

    # Invoke the agent
    default_recursion_limit = 25
    try:
        env_value_str = os.getenv("AGENT_RECURSION_LIMIT", str(default_recursion_limit))
        parsed_limit = int(env_value_str)

        if parsed_limit > 0:
            recursion_limit = parsed_limit
            logger.info(f"Recursion limit set to: {recursion_limit}")
        else:
            logger.warning(
                f"AGENT_RECURSION_LIMIT value '{env_value_str}' (parsed as {parsed_limit}) is not positive. "
                f"Using default value {default_recursion_limit}."
            )
            recursion_limit = default_recursion_limit
    except ValueError:
        raw_env_value = os.getenv("AGENT_RECURSION_LIMIT")
        logger.warning(
            f"Invalid AGENT_RECURSION_LIMIT value: '{raw_env_value}'. "
            f"Using default value {default_recursion_limit}."
        )
        recursion_limit = default_recursion_limit

    logger.info(f"Agent input: {agent_input}")
    result = await agent.ainvoke(
        input=agent_input, config={"recursion_limit": recursion_limit}
    )

    # Process the result
    response_content = result["messages"][-1].content
    logger.debug(f"{agent_name.capitalize()} full response: {response_content}")

    # Update the step with the execution result
    current_step.execution_res = response_content
    logger.info(f"Step '{current_step.title}' execution completed by {agent_name}")

    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name=agent_name,
                )
            ],
            "observations": observations + [response_content],
        },
        goto="research_team",
    )


async def _setup_and_execute_agent_step(
    state: State,
    config: RunnableConfig,
    agent_type: str,
    default_tools: list,
) -> Command[Literal["research_team"]]:
    """Helper function to set up an agent with appropriate tools and execute a step.

    This function handles the common logic for both researcher_node and coder_node:
    1. Configures MCP servers and tools based on agent type
    2. Creates an agent with the appropriate tools or uses the default agent
    3. Executes the agent on the current step

    Args:
        state: The current state
        config: The runnable config
        agent_type: The type of agent ("researcher" or "coder")
        default_tools: The default tools to add to the agent

    Returns:
        Command to update state and go to research_team
    """
    configurable = Configuration.from_runnable_config(config)
    mcp_servers = {}
    enabled_tools = {}

    # Extract MCP server configuration for this agent type
    if configurable.mcp_settings:
        for server_name, server_config in configurable.mcp_settings["servers"].items():
            if (
                server_config["enabled_tools"]
                and agent_type in server_config["add_to_agents"]
            ):
                mcp_servers[server_name] = {
                    k: v
                    for k, v in server_config.items()
                    if k in ("transport", "command", "args", "url", "env")
                }
                for tool_name in server_config["enabled_tools"]:
                    enabled_tools[tool_name] = server_name

    # Create and execute agent with MCP tools if available
    if mcp_servers:
        async with MultiServerMCPClient(mcp_servers) as client:
            # 获取MCP工具
            mcp_tools = []
            for tool in client.get_tools():
                if tool.name in enabled_tools:
                    tool.description = (
                        f"Powered by '{enabled_tools[tool.name]}'.\n{tool.description}"
                    )
                    mcp_tools.append(tool)

            # 使用MCP工具和默认工具创建智能体
            all_additional_tools = default_tools + mcp_tools
            agent = create_agent(
                agent_name=agent_type,
                agent_type=agent_type,
                tools=all_additional_tools,
                prompt_template=agent_type
            )
            return await _execute_agent_step(state, agent, agent_type)
    else:
        # 使用默认工具创建智能体
        agent = create_agent(
            agent_name=agent_type,
            agent_type=agent_type,
            tools=default_tools,
            prompt_template=agent_type
        )
        return await _execute_agent_step(state, agent, agent_type)


async def researcher_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Researcher node that do research"""
    logger.info("Researcher node is researching.")

    # 使用数据库查询和API调用工具替代网络搜索
    additional_tools = [
        # API工具
        execute_api,
        list_available_apis,
        get_api_details,
        # Text2SQL工具
        text2sql_query,
        generate_sql_only,
        get_training_examples,
        validate_sql,
        # 数据库工具
        database_query,
        list_databases,
        search_databases,
        find_database_by_name,
        get_database_info,
        test_database_connection,
        # 图表生成工具
        generate_chart,
    ]
    logger.info(f"Researcher additional tools: {[tool.name if hasattr(tool, 'name') else str(tool) for tool in additional_tools]}")

    return await _setup_and_execute_agent_step(
        state,
        config,
        "researcher",
        additional_tools,  # 这些将作为额外工具添加到默认工具中
    )


async def coder_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Coder node that do code analysis."""
    logger.info("Coder node is coding.")

    # 使用自动工具配置，但保留传统的Python REPL工具作为额外工具
    additional_tools = [python_repl_tool]
    logger.info(f"Coder additional tools: {additional_tools}")

    return await _setup_and_execute_agent_step(
        state,
        config,
        "coder",
        additional_tools,  # 这些将作为额外工具添加到默认工具中
    )


async def data_analyst_node(state: State, config: RunnableConfig) -> Command[Literal["__end__"]]:
    """Data analyst node that provides comprehensive data analysis and Q&A."""
    logger.info("Data analyst is analyzing.")

    # 获取用户查询 - 从data_query或messages中获取
    data_query = state.get("data_query")
    if not data_query:
        messages = state.get("messages", [])
        if messages:
            data_query = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
        else:
            return Command(goto="__end__")

    # LangSmith追踪支持
    from src.config.langsmith import create_langsmith_run_name, add_langsmith_metadata, is_langsmith_enabled

    if is_langsmith_enabled():
        logger.info(f"🔍 LangSmith追踪已启用，正在记录数据分析师执行过程")
        run_name = create_langsmith_run_name("data_analyst", data_query)
        logger.debug(f"LangSmith运行名称: {run_name}")

    # 使用所有数据分析工具
    data_tools = [
        # 资源发现工具
        discover_resources,
        # API工具
        execute_api,
        list_available_apis,
        get_api_details,
        # Text2SQL工具
        text2sql_query,
        smart_text2sql_query,  # 新增：支持自动图表生成的智能查询工具
        generate_sql_only,
        get_training_examples,
        validate_sql,
        # 数据库工具
        database_query,
        list_databases,
        search_databases,
        find_database_by_name,
        get_database_info,
        test_database_connection,
        # 图表生成工具
        generate_chart,
    ]

    # 创建数据分析师智能体 - 这是一个完整的ReAct智能体，使用异步版本
    from src.agents import create_agent_async
    agent = create_agent_async(
        agent_name="data_analyst",
        agent_type="data_analyst",
        tools=data_tools,
        prompt_template="data_analyst"
    )

    # 准备智能体输入，包含用户查询和当前状态信息
    agent_input = {
        "messages": [
            HumanMessage(content=f"用户请求: {data_query}")
        ],
        "locale": state.get("locale", "zh-CN")
    }

    logger.info(f"Data analyst processing query: {data_query}")

    # 执行分析 - 智能体会自动进行工具调用和推理循环
    result = await agent.ainvoke(
        input=agent_input,
        config={"recursion_limit": 50}  # 增加递归限制以支持多轮工具调用
    )

    # 获取最终响应 - 这是智能体经过工具调用和推理后的最终答案
    final_message = result["messages"][-1]
    response_content = final_message.content

    logger.info(f"Data analyst completed analysis")
    logger.debug(f"Data analyst final response: {response_content}")

    return Command(
        update={
            "messages": [
                AIMessage(content=response_content, name="data_analyst")
            ],
            "final_report": response_content,
        },
        goto="__end__",
    )
