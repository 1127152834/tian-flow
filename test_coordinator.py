#!/usr/bin/env python3

"""
测试 Coordinator 是否能正确识别图表生成请求
"""

import asyncio
import logging
from src.graph.nodes import coordinator_node, handoff_to_planner
from src.graph.types import State
from src.config.configuration import Configuration
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_coordinator_chart_request():
    """测试 Coordinator 对图表请求的处理"""
    
    # 创建测试状态
    test_state: State = {
        "messages": [
            HumanMessage(content="请帮我生成一个图表，显示以下销售数据：1月1000，2月1200，3月1100。请用柱状图显示。")
        ],
        "locale": "zh-CN",
        "research_topic": "",
        "enable_background_investigation": False,
        "resources": [],
        "observations": [],
        "current_plan": None,
        "final_report": None
    }
    
    # 创建配置
    config = RunnableConfig(
        configurable={
            "max_search_results": 5,
            "max_plan_iterations": 1,
            "max_step_num": 3,
            "enable_background_investigation": False,
            "resources": []
        }
    )
    
    logger.info("测试 Coordinator 对图表请求的处理...")
    logger.info(f"输入消息: {test_state['messages'][0].content}")
    
    try:
        # 调用 coordinator_node
        result = coordinator_node(test_state, config)
        
        logger.info(f"Coordinator 结果:")
        logger.info(f"  - goto: {result.goto}")
        logger.info(f"  - update: {result.update}")
        
        if result.goto == "planner" or result.goto == "background_investigator":
            logger.info("✅ 成功！Coordinator 正确识别了图表请求并转发给 Planner")
        elif result.goto == "__end__":
            logger.error("❌ 失败！Coordinator 没有转发请求，直接结束了")
        else:
            logger.warning(f"⚠️  未知状态: goto = {result.goto}")
            
    except Exception as e:
        logger.error(f"❌ 测试失败，出现异常: {e}")
        import traceback
        traceback.print_exc()

async def test_coordinator_simple_greeting():
    """测试 Coordinator 对简单问候的处理"""
    
    # 创建测试状态
    test_state: State = {
        "messages": [
            HumanMessage(content="你好")
        ],
        "locale": "zh-CN",
        "research_topic": "",
        "enable_background_investigation": False,
        "resources": [],
        "observations": [],
        "current_plan": None,
        "final_report": None
    }
    
    # 创建配置
    config = RunnableConfig(
        configurable={
            "max_search_results": 5,
            "max_plan_iterations": 1,
            "max_step_num": 3,
            "enable_background_investigation": False,
            "resources": []
        }
    )
    
    logger.info("测试 Coordinator 对简单问候的处理...")
    logger.info(f"输入消息: {test_state['messages'][0].content}")
    
    try:
        # 调用 coordinator_node
        result = coordinator_node(test_state, config)
        
        logger.info(f"Coordinator 结果:")
        logger.info(f"  - goto: {result.goto}")
        logger.info(f"  - update: {result.update}")
        
        if result.goto == "__end__":
            logger.info("✅ 成功！Coordinator 正确处理了简单问候，直接结束")
        else:
            logger.warning(f"⚠️  Coordinator 将问候转发了: goto = {result.goto}")
            
    except Exception as e:
        logger.error(f"❌ 测试失败，出现异常: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """运行所有测试"""
    logger.info("开始测试 Coordinator...")
    
    await test_coordinator_simple_greeting()
    print("\n" + "="*50 + "\n")
    await test_coordinator_chart_request()
    
    logger.info("测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
