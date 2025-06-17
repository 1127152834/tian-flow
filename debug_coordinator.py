#!/usr/bin/env python3

"""
调试 Coordinator 的详细行为
"""

import asyncio
import logging
from src.graph.nodes import coordinator_node
from src.config.configuration import Configuration
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def debug_coordinator():
    """调试 Coordinator 的详细行为"""
    
    # 创建测试状态
    test_state = {
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
    
    logger.info("=== 调试 Coordinator ===")
    logger.info(f"输入消息: {test_state['messages'][0].content}")
    
    try:
        # 调用 coordinator_node
        result = coordinator_node(test_state, config)
        
        logger.info(f"Coordinator 返回类型: {type(result)}")
        logger.info(f"Coordinator 返回值: {result}")
        
        if hasattr(result, 'goto'):
            logger.info(f"goto 字段: {result.goto}")
        
        if hasattr(result, 'update'):
            logger.info(f"update 字段: {result.update}")
            
        # 检查返回值的所有属性
        logger.info(f"返回值的所有属性: {dir(result)}")
        
        if result.goto == "data_analyst":
            logger.info("✅ Coordinator 正确返回了 data_analyst")
        else:
            logger.error(f"❌ Coordinator 返回了: {result.goto}")
            
    except Exception as e:
        logger.error(f"❌ Coordinator 调用失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """运行调试"""
    logger.info("开始调试 Coordinator...")
    await debug_coordinator()
    logger.info("调试完成！")

if __name__ == "__main__":
    asyncio.run(main())
