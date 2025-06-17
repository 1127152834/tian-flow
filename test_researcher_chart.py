#!/usr/bin/env python3

"""
测试 Researcher 是否能正确识别图表生成请求并调用 generate_chart 工具
"""

import asyncio
import logging
from src.graph.nodes import researcher_node
from src.graph.types import State
from src.config.configuration import Configuration
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_researcher_chart_generation():
    """测试 Researcher 对图表生成请求的处理"""
    
    # 创建测试状态
    test_state: State = {
        "messages": [
            HumanMessage(content="请帮我生成一个图表，显示以下销售数据：1月1000，2月1200，3月1100。请用柱状图显示。")
        ],
        "locale": "zh-CN",
        "research_topic": "create_data_visualization",
        "enable_background_investigation": False,
        "resources": [],
        "observations": [],
        "current_plan": {
            "title": "销售数据柱状图生成",
            "steps": [
                {
                    "title": "生成销售数据柱状图",
                    "description": "根据提供的销售数据（1月1000，2月1200，3月1100）生成柱状图",
                    "step_type": "research",
                    "need_search": False
                }
            ]
        },
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
    
    logger.info("测试 Researcher 对图表生成请求的处理...")
    logger.info(f"输入消息: {test_state['messages'][0].content}")
    
    try:
        # 调用 researcher_node
        result = researcher_node(test_state, config)
        
        logger.info(f"Researcher 结果:")
        logger.info(f"  - 更新的状态: {result}")
        
        # 检查是否生成了图表相关的内容
        if "observations" in result and result["observations"]:
            observations = result["observations"]
            logger.info(f"  - 观察结果数量: {len(observations)}")
            
            # 检查是否包含图表相关内容
            chart_found = False
            for obs in observations:
                if any(keyword in str(obs).lower() for keyword in ["chart", "图表", "recharts", "visualization"]):
                    chart_found = True
                    logger.info(f"  - 找到图表相关内容: {obs}")
                    break
            
            if chart_found:
                logger.info("✅ 成功！Researcher 生成了图表相关内容")
            else:
                logger.error("❌ 失败！Researcher 没有生成图表相关内容")
                logger.info("观察结果:")
                for i, obs in enumerate(observations):
                    logger.info(f"  {i+1}. {obs}")
        else:
            logger.error("❌ 失败！Researcher 没有生成任何观察结果")
            
    except Exception as e:
        logger.error(f"❌ 测试失败，出现异常: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """运行测试"""
    logger.info("开始测试 Researcher 图表生成...")
    
    await test_researcher_chart_generation()
    
    logger.info("测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
