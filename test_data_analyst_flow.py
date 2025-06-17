#!/usr/bin/env python3

"""
测试完整的数据分析师流程：Coordinator → Data Analyst
"""

import asyncio
import logging
from src.graph.nodes import coordinator_node, data_analyst_node
from src.graph.types import State
from src.config.configuration import Configuration
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_coordinator_to_data_analyst_flow():
    """测试从 Coordinator 到 Data Analyst 的完整流程"""
    
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
    
    logger.info("=== 第一步：测试 Coordinator 路由 ===")
    logger.info(f"输入消息: {test_state['messages'][0].content}")
    
    try:
        # 第一步：调用 coordinator_node
        coordinator_result = coordinator_node(test_state, config)
        
        logger.info(f"Coordinator 结果:")
        logger.info(f"  - goto: {coordinator_result.goto}")
        logger.info(f"  - update: {coordinator_result.update}")
        
        if coordinator_result.goto == "data_analyst":
            logger.info("✅ 成功！Coordinator 正确识别了数据分析请求并路由到 Data Analyst")
            
            # 更新状态
            if coordinator_result.update:
                test_state.update(coordinator_result.update)
            
            logger.info("\n=== 第二步：测试 Data Analyst 执行 ===")
            
            # 第二步：调用 data_analyst_node
            analyst_result = await data_analyst_node(test_state, config)
            
            logger.info(f"Data Analyst 结果:")
            logger.info(f"  - final_report 长度: {len(analyst_result.get('final_report', ''))}")
            
            # 检查是否包含图表相关内容
            final_report = analyst_result.get('final_report', '')
            if any(keyword in final_report.lower() for keyword in ['chart', '图表', 'recharts', 'visualization', 'barchart']):
                logger.info("✅ 成功！Data Analyst 生成了包含图表的报告")
                logger.info(f"报告预览: {final_report[:200]}...")
            else:
                logger.error("❌ 失败！Data Analyst 没有生成图表相关内容")
                logger.info(f"实际报告: {final_report}")
                
        elif coordinator_result.goto == "planner":
            logger.warning("⚠️  Coordinator 将请求路由到了 Planner 而不是 Data Analyst")
        elif coordinator_result.goto == "__end__":
            logger.error("❌ 失败！Coordinator 直接结束了，没有路由到任何智能体")
        else:
            logger.warning(f"⚠️  未知路由: {coordinator_result.goto}")
            
    except Exception as e:
        logger.error(f"❌ 测试失败，出现异常: {e}")
        import traceback
        traceback.print_exc()

async def test_different_data_requests():
    """测试不同类型的数据分析请求"""
    
    test_cases = [
        "请生成一个饼图显示市场份额：苹果40%，三星30%，华为20%，其他10%",
        "帮我做一个折线图，显示过去6个月的用户增长：1月100，2月150，3月200，4月180，5月220，6月250",
        "我需要一个数据分析报告，包含以下数据的可视化：产品A销量500，产品B销量300，产品C销量200"
    ]
    
    config = RunnableConfig(
        configurable={
            "max_search_results": 5,
            "max_plan_iterations": 1,
            "max_step_num": 3,
            "enable_background_investigation": False,
            "resources": []
        }
    )
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n=== 测试用例 {i} ===")
        logger.info(f"输入: {test_case}")
        
        test_state: State = {
            "messages": [HumanMessage(content=test_case)],
            "locale": "zh-CN",
            "research_topic": "",
            "enable_background_investigation": False,
            "resources": [],
            "observations": [],
            "current_plan": None,
            "final_report": None
        }
        
        try:
            coordinator_result = coordinator_node(test_state, config)
            
            if coordinator_result.goto == "data_analyst":
                logger.info(f"✅ 测试用例 {i}: Coordinator 正确路由到 Data Analyst")
            else:
                logger.error(f"❌ 测试用例 {i}: Coordinator 路由到了 {coordinator_result.goto}")
                
        except Exception as e:
            logger.error(f"❌ 测试用例 {i} 失败: {e}")

async def main():
    """运行所有测试"""
    logger.info("开始测试数据分析师完整流程...")
    
    await test_coordinator_to_data_analyst_flow()
    
    logger.info("\n" + "="*60 + "\n")
    
    await test_different_data_requests()
    
    logger.info("\n测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
