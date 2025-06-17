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

from src.agents import create_agent, create_agent_async
from src.tools.search import LoggedTavilySearch
from src.tools import (
    crawl_tool,
    get_web_search_tool,
    get_retriever_tool,
    python_repl_tool,
    # 新增的查询工具
    execute_api,
    list_available_apis,
    get_api_details,
    text2sql_query,
    generate_sql_only,
    get_training_examples,
    validate_sql,
    database_query,
    list_databases,
    test_database_connection,
    # 图表生成工具
    generate_chart,
)

from src.config.agents import AGENT_LLM_MAP
from src.config.configuration import Configuration
from src.llms.llm import get_llm_by_type
from src.prompts.planner_model import Plan
from src.prompts.template import apply_prompt_template
from src.utils.json_utils import repair_json_output

from .types import State
from ..config import SELECTED_SEARCH_ENGINE, SearchEngine

logger = logging.getLogger(__name__)


def create_fallback_plan(state: State, response_content: str) -> dict:
    """
    Create a fallback plan when LLM response is invalid or unparseable.
    """
    research_topic = state.get("research_topic", "Research Task")
    locale = state.get("locale", "en-US")

    # Extract any meaningful content from the response
    title = research_topic
    thought = f"Based on the request: {research_topic}"

    # Try to extract steps from the response if it contains step-like content
    steps = []
    if "research" in response_content.lower() or "search" in response_content.lower():
        steps.append({
            "need_search": True,
            "title": f"Research on {research_topic}",
            "description": f"Conduct research to gather information about {research_topic}",
            "step_type": "research"
        })

    if not steps:
        # Default step if nothing can be extracted
        steps.append({
            "need_search": True,
            "title": "General Research",
            "description": "Gather relevant information for the research task",
            "step_type": "research"
        })

    return {
        "locale": locale,
        "has_enough_context": False,
        "thought": thought,
        "title": title,
        "steps": steps
    }


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
    data_analysis_task: Annotated[str, "The data analysis task to be handed off."],
    locale: Annotated[str, "The user's detected language locale (e.g., en-US, zh-CN)."],
):
    """Handoff to data analyst agent for data analysis and chart generation tasks."""
    # This tool is not returning anything: we're just using it
    # as a way for LLM to signal that it needs to hand off to data analyst agent
    return


def background_investigation_node(state: State, config: RunnableConfig):
    logger.info("background investigation node is running.")
    configurable = Configuration.from_runnable_config(config)
    query = state.get("research_topic")
    background_investigation_results = None
    if SELECTED_SEARCH_ENGINE == SearchEngine.TAVILY.value:
        searched_content = LoggedTavilySearch(
            max_results=configurable.max_search_results
        ).invoke(query)
        if isinstance(searched_content, list):
            background_investigation_results = [
                f"## {elem['title']}\n\n{elem['content']}" for elem in searched_content
            ]
            return {
                "background_investigation_results": "\n\n".join(
                    background_investigation_results
                )
            }
        else:
            logger.error(
                f"Tavily search returned malformed response: {searched_content}"
            )
    else:
        background_investigation_results = get_web_search_tool(
            configurable.max_search_results
        ).invoke(query)
    return {
        "background_investigation_results": json.dumps(
            background_investigation_results, ensure_ascii=False
        )
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
    curr_plan = None

    try:
        if AGENT_LLM_MAP["planner"] == "basic" and not configurable.enable_deep_thinking:
            response = llm.invoke(messages)
            # Check if response is a Plan object or something else
            if hasattr(response, 'model_dump'):
                # It's a Pydantic model
                full_response = response.model_dump_json(indent=4, exclude_none=True)
                curr_plan = response.model_dump()
            else:
                # It's not a Plan object, treat as raw response
                logger.warning(f"Unexpected response type from structured output: {type(response)}")
                full_response = str(response)
                # Try to create a fallback plan
                curr_plan = create_fallback_plan(state, full_response)
        else:
            response = llm.stream(messages)
            for chunk in response:
                full_response += chunk.content
            try:
                curr_plan = json.loads(repair_json_output(full_response))
            except json.JSONDecodeError:
                logger.warning("Planner response is not a valid JSON")
                curr_plan = create_fallback_plan(state, full_response)
    except Exception as e:
        logger.error(f"Error processing planner response: {e}")
        curr_plan = create_fallback_plan(state, full_response or "Error occurred")

    logger.debug(f"Current state messages: {state['messages']}")
    logger.info(f"Planner response: {full_response}")

    # Validate curr_plan
    if not curr_plan or not isinstance(curr_plan, dict):
        logger.warning("Invalid plan format, using fallback")
        curr_plan = create_fallback_plan(state, full_response)

    if curr_plan.get("has_enough_context"):
        logger.info("Planner response has enough context.")
        try:
            new_plan = Plan.model_validate(curr_plan)
            return Command(
                update={
                    "messages": [AIMessage(content=full_response, name="planner")],
                    "current_plan": new_plan,
                },
                goto="reporter",
            )
        except Exception as e:
            logger.error(f"Failed to validate plan with enough context: {e}")
            # Fall through to human feedback
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
        if new_plan["has_enough_context"]:
            goto = "reporter"
    except json.JSONDecodeError:
        logger.warning("Planner response is not a valid JSON")
        if plan_iterations > 0:
            return Command(goto="reporter")
        else:
            return Command(goto="__end__")

    # Validate and create Plan object
    try:
        if isinstance(new_plan, dict):
            validated_plan = Plan.model_validate(new_plan)
        else:
            validated_plan = new_plan  # Already a Plan object
    except Exception as e:
        logger.error(f"Failed to validate plan: {e}")
        return Command(goto="__end__")

    return Command(
        update={
            "current_plan": validated_plan,
            "plan_iterations": plan_iterations,
            "locale": new_plan.get("locale", "en-US") if isinstance(new_plan, dict) else validated_plan.locale,
        },
        goto=goto,
    )


def coordinator_node(
    state: State, config: RunnableConfig
) -> Command[Literal["planner", "background_investigator", "data_analyst", "__end__"]]:
    """Coordinator node that communicate with customers."""
    logger.info("Coordinator talking.")
    configurable = Configuration.from_runnable_config(config)

    # 获取用户设置
    user_settings = configurable.user_settings or {}
    enable_background_investigation = user_settings.get("enableBackgroundInvestigation", False)

    # 获取最新的用户消息
    messages = state.get("messages", [])
    user_messages = [msg for msg in messages if hasattr(msg, 'type') and msg.type == "human"]
    latest_user_message = user_messages[-1].content if user_messages else ""

    logger.info(f"研究模式状态: {enable_background_investigation}")
    logger.info(f"用户消息: {latest_user_message}")

    # 快速路由逻辑 - 减少 LLM 调用
    goto = "__end__"
    locale = state.get("locale", "en-US")
    research_topic = state.get("research_topic", "")
    data_analysis_task = ""

    # 检查是否是简单的问候或闲聊
    greeting_keywords = ["hello", "hi", "你好", "嗨", "how are you", "你好吗", "good morning", "早上好", "good afternoon", "下午好", "good evening", "晚上好"]
    is_greeting = any(keyword.lower() in latest_user_message.lower() for keyword in greeting_keywords)

    # 检查是否是数据分析/图表请求
    chart_keywords = ["图表", "chart", "graph", "visualization", "可视化", "数据分析", "data analysis", "柱状图", "折线图", "饼图", "bar chart", "line chart", "pie chart"]
    is_chart_request = any(keyword.lower() in latest_user_message.lower() for keyword in chart_keywords)

    if is_greeting:
        # 简单问候，直接回复
        logger.info("检测到问候消息，直接回复")
        messages = apply_prompt_template("coordinator", state)
        response = get_llm_by_type(AGENT_LLM_MAP["coordinator"]).invoke(messages)
    elif is_chart_request:
        # 数据分析请求，直接路由到数据分析师
        logger.info("检测到图表/数据分析请求，直接路由到数据分析师")
        goto = "data_analyst"
        data_analysis_task = latest_user_message
        research_topic = data_analysis_task
        response = type('Response', (), {
            'content': f"我将为您处理这个数据分析请求：{latest_user_message}",
            'tool_calls': []
        })()
    elif enable_background_investigation:
        # 研究模式开启，直接路由到规划师
        logger.info("研究模式开启，直接路由到规划师")
        goto = "planner"
        research_topic = latest_user_message
        response = type('Response', (), {
            'content': f"我将为您研究这个问题：{latest_user_message}",
            'tool_calls': []
        })()
    else:
        # 非研究模式，使用 LLM 判断
        logger.info("使用 LLM 进行智能路由判断")
        messages = apply_prompt_template("coordinator", state)
        response = (
            get_llm_by_type(AGENT_LLM_MAP["coordinator"])
            .bind_tools([handoff_to_planner, handoff_to_data_analyst])
            .invoke(messages)
        )

    # 处理工具调用（仅在使用 LLM 判断时需要）
    if hasattr(response, 'tool_calls') and len(response.tool_calls) > 0:
        try:
            for tool_call in response.tool_calls:
                tool_name = tool_call.get("name", "")

                if tool_name == "handoff_to_planner":
                    goto = "planner"
                    # 根据研究模式设置决定是否使用背景调查
                    if enable_background_investigation:
                        goto = "background_investigator"

                    if tool_call.get("args", {}).get("locale") and tool_call.get("args", {}).get("research_topic"):
                        locale = tool_call.get("args", {}).get("locale")
                        research_topic = tool_call.get("args", {}).get("research_topic")
                    break

                elif tool_name == "handoff_to_data_analyst":
                    goto = "data_analyst"

                    if tool_call.get("args", {}).get("locale") and tool_call.get("args", {}).get("data_analysis_task"):
                        locale = tool_call.get("args", {}).get("locale")
                        data_analysis_task = tool_call.get("args", {}).get("data_analysis_task")
                        research_topic = data_analysis_task  # Use data_analysis_task as research_topic for consistency
                    break

        except Exception as e:
            logger.error(f"Error processing tool calls: {e}")
    elif goto == "__end__" and not is_greeting:
        # 只有在没有明确路由且不是问候时才警告
        logger.warning(
            "Coordinator response contains no tool calls. Terminating workflow execution."
        )
        logger.debug(f"Coordinator response: {response}")

    logger.info(f"Coordinator 路由决定: {goto}")
    if goto != "__end__":
        logger.info(f"研究主题: {research_topic}")
        if data_analysis_task:
            logger.info(f"数据分析任务: {data_analysis_task}")

    return Command(
        update={
            "locale": locale,
            "research_topic": research_topic,
            "resources": configurable.resources,
        },
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
            loaded_tools = default_tools[:]
            for tool in client.get_tools():
                if tool.name in enabled_tools:
                    tool.description = (
                        f"Powered by '{enabled_tools[tool.name]}'.\n{tool.description}"
                    )
                    loaded_tools.append(tool)
            agent = create_agent(agent_type, agent_type, loaded_tools, agent_type)
            return await _execute_agent_step(state, agent, agent_type)
    else:
        # Use default tools if no MCP servers are configured
        agent = create_agent(agent_type, agent_type, default_tools, agent_type)
        return await _execute_agent_step(state, agent, agent_type)


async def researcher_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Researcher node that do research"""
    logger.info("Researcher node is researching.")
    configurable = Configuration.from_runnable_config(config)

    # 基础搜索和爬虫工具
    tools = [get_web_search_tool(configurable.max_search_results), crawl_tool]

    # 检索工具（条件性添加）
    retriever_tool = get_retriever_tool(state.get("resources", []))
    if retriever_tool:
        tools.insert(0, retriever_tool)

    # 新增的查询工具 - 为Researcher提供更强的数据查询能力
    query_tools = [
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
        test_database_connection,
        # 图表生成工具
        generate_chart,
    ]
    tools.extend(query_tools)

    logger.info(f"Researcher tools: {[tool.name if hasattr(tool, 'name') else str(tool) for tool in tools]}")
    return await _setup_and_execute_agent_step(
        state,
        config,
        "researcher",
        tools,
    )


async def coder_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Coder node that do code analysis."""
    logger.info("Coder node is coding.")
    return await _setup_and_execute_agent_step(
        state,
        config,
        "coder",
        [python_repl_tool],
    )


async def data_analyst_node(state: State, config: RunnableConfig):
    """Data analyst node that performs data analysis and chart generation."""
    logger.info("Data analyst node is analyzing data.")
    configurable = Configuration.from_runnable_config(config)

    # 获取用户消息
    user_message = state.get("messages", [])[-1].content if state.get("messages") else ""

    # 基础搜索和爬虫工具
    tools = [get_web_search_tool(configurable.max_search_results), crawl_tool]

    # 检索工具（条件性添加）
    retriever_tool = get_retriever_tool(state.get("resources", []))
    if retriever_tool:
        tools.insert(0, retriever_tool)

    # 数据查询和分析工具
    query_tools = [
        # API工具
        execute_api,
        list_available_apis,
        get_api_details,
        # Text2SQL工具
        text2sql_query,
        generate_sql_only,
        validate_sql,
        # 数据库工具
        database_query,
        list_databases,
        test_database_connection,
        # 图表生成工具
        generate_chart,
    ]
    tools.extend(query_tools)

    # 创建数据分析师智能体
    agent = create_agent_async("data_analyst", "data_analyst", tools, "data_analyst")

    # 准备输入
    agent_input = {
        "messages": [
            HumanMessage(
                content=f"# Data Analysis Task\n\n{user_message}\n\nLocale: {state.get('locale', 'en-US')}"
            )
        ]
    }

    # 执行数据分析
    default_recursion_limit = 25
    try:
        env_value_str = os.getenv("AGENT_RECURSION_LIMIT", str(default_recursion_limit))
        parsed_limit = int(env_value_str)
        if parsed_limit > 0:
            recursion_limit = parsed_limit
        else:
            recursion_limit = default_recursion_limit
    except ValueError:
        recursion_limit = default_recursion_limit

    logger.info(f"Data analyst input: {agent_input}")
    result = await agent.ainvoke(
        input=agent_input, config={"recursion_limit": recursion_limit}
    )

    # 处理结果
    response_content = result["messages"][-1].content
    logger.info(f"Data analyst response: {response_content}")

    return {
        "final_report": response_content,
        "messages": [AIMessage(content=response_content, name="data_analyst")]
    }
