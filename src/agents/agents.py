# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from langgraph.prebuilt import create_react_agent

from src.prompts import apply_prompt_template
from src.prompts.template import apply_prompt_template_async
from src.llms.llm import get_llm_by_type
from src.config.agents import AGENT_LLM_MAP


# Create agents using configured LLM types
def create_agent(agent_name: str, agent_type: str, tools: list, prompt_template: str):
    """Factory function to create agents with consistent configuration."""
    return create_react_agent(
        name=agent_name,
        model=get_llm_by_type(AGENT_LLM_MAP[agent_type]),
        tools=tools,
        prompt=lambda state: apply_prompt_template(prompt_template, state),
    )


def create_agent_async(agent_name: str, agent_type: str, tools: list, prompt_template: str):
    """Factory function to create agents with async prompt template loading."""
    import logging

    logger = logging.getLogger(__name__)

    try:
        logger.info(f"创建智能体: {agent_name}, 类型: {agent_type}")

        # 检查智能体类型是否在映射中
        if agent_type not in AGENT_LLM_MAP:
            raise ValueError(f"未知的智能体类型: {agent_type}, 可用类型: {list(AGENT_LLM_MAP.keys())}")

        llm_type = AGENT_LLM_MAP[agent_type]
        logger.info(f"智能体 {agent_type} 对应的 LLM 类型: {llm_type}")

        # 获取 LLM 实例
        logger.info(f"获取 LLM 实例: {llm_type}")
        llm = get_llm_by_type(llm_type)
        logger.info(f"LLM 实例获取成功: {type(llm)}")

        async def async_prompt(state):
            return await apply_prompt_template_async(prompt_template, state)

        logger.info(f"创建 React 智能体: {agent_name}")
        agent = create_react_agent(
            name=agent_name,
            model=llm,
            tools=tools,
            prompt=async_prompt,
        )
        logger.info(f"React 智能体创建成功: {agent_name}")
        return agent

    except Exception as e:
        logger.error(f"智能体创建失败: {agent_name}, 错误: {e}")
        import traceback
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        raise
