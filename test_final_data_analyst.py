#!/usr/bin/env python3

"""
最终测试：验证数据分析师的完整功能，包括数据真实性限制
"""

import asyncio
import logging
from src.graph.nodes import data_analyst_node
from src.config.configuration import Configuration
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_data_analyst_with_user_data():
    """测试数据分析师处理用户提供的数据"""
    
    test_state = {
        "messages": [
            HumanMessage(content="请帮我生成一个图表，显示以下销售数据：1月1000，2月1200，3月1100。请用柱状图显示。")
        ],
        "locale": "zh-CN",
        "research_topic": "生成一个柱状图来展示销售数据,1月1000，2月1200，3月1100",
        "enable_background_investigation": False,
        "resources": [],
        "observations": [],
        "current_plan": None,
        "final_report": None
    }
    
    config = RunnableConfig(
        configurable={
            "max_search_results": 5,
            "max_plan_iterations": 1,
            "max_step_num": 3,
            "enable_background_investigation": False,
            "resources": []
        }
    )
    
    logger.info("=== 测试用户提供数据的图表生成 ===")
    
    try:
        result = await data_analyst_node(test_state, config)
        
        final_report = result.get('final_report', '')
        logger.info(f"报告长度: {len(final_report)}")
        
        # 检查是否包含图表配置
        if any(keyword in final_report.lower() for keyword in ['chart', '图表', 'recharts', 'barchart', 'json']):
            logger.info("✅ 成功生成了图表相关内容")
            
            # 检查是否包含用户数据
            if all(data in final_report for data in ['1000', '1200', '1100']):
                logger.info("✅ 正确使用了用户提供的数据")
            else:
                logger.warning("⚠️  可能没有使用用户提供的数据")
                
            # 检查是否说明了数据来源
            if any(source in final_report.lower() for source in ['用户提供', '用户数据', 'user', 'provided']):
                logger.info("✅ 正确标注了数据来源")
            else:
                logger.warning("⚠️  没有明确标注数据来源")
                
        else:
            logger.error("❌ 没有生成图表相关内容")
            
        logger.info(f"报告预览: {final_report[:300]}...")
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_data_analyst_without_data():
    """测试数据分析师在没有数据时的行为"""
    
    test_state = {
        "messages": [
            HumanMessage(content="请帮我生成一个图表，显示最近三年的全球GDP增长率。")
        ],
        "locale": "zh-CN",
        "research_topic": "生成全球GDP增长率图表",
        "enable_background_investigation": False,
        "resources": [],
        "observations": [],
        "current_plan": None,
        "final_report": None
    }
    
    config = RunnableConfig(
        configurable={
            "max_search_results": 5,
            "max_plan_iterations": 1,
            "max_step_num": 3,
            "enable_background_investigation": False,
            "resources": []
        }
    )
    
    logger.info("\n=== 测试没有数据时的处理 ===")
    
    try:
        result = await data_analyst_node(test_state, config)
        
        final_report = result.get('final_report', '')
        logger.info(f"报告长度: {len(final_report)}")
        
        # 检查是否正确处理了数据缺失
        if any(keyword in final_report.lower() for keyword in ['数据不足', '无法获取', '需要数据', 'insufficient', 'not available']):
            logger.info("✅ 正确处理了数据缺失情况")
        else:
            logger.warning("⚠️  可能没有正确处理数据缺失")
            
        # 检查是否建议了数据获取方法
        if any(method in final_report.lower() for method in ['数据库查询', 'api', '数据源', 'database']):
            logger.info("✅ 建议了数据获取方法")
        else:
            logger.warning("⚠️  没有建议数据获取方法")
            
        logger.info(f"报告预览: {final_report[:300]}...")
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_data_analyst_chart_types():
    """测试数据分析师生成不同类型的图表"""
    
    test_cases = [
        {
            "name": "饼图测试",
            "message": "请生成一个饼图显示市场份额：苹果40%，三星30%，华为20%，其他10%",
            "expected_chart": "piechart"
        },
        {
            "name": "折线图测试", 
            "message": "请生成一个折线图显示用户增长：1月100，2月150，3月200，4月180，5月220",
            "expected_chart": "linechart"
        }
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
    
    for test_case in test_cases:
        logger.info(f"\n=== {test_case['name']} ===")
        
        test_state = {
            "messages": [HumanMessage(content=test_case["message"])],
            "locale": "zh-CN",
            "research_topic": test_case["message"],
            "enable_background_investigation": False,
            "resources": [],
            "observations": [],
            "current_plan": None,
            "final_report": None
        }
        
        try:
            result = await data_analyst_node(test_state, config)
            final_report = result.get('final_report', '')
            
            if test_case["expected_chart"].lower() in final_report.lower():
                logger.info(f"✅ {test_case['name']} 成功")
            else:
                logger.warning(f"⚠️  {test_case['name']} 可能没有生成正确的图表类型")
                
        except Exception as e:
            logger.error(f"❌ {test_case['name']} 失败: {e}")

async def main():
    """运行所有测试"""
    logger.info("开始数据分析师最终测试...")
    
    await test_data_analyst_with_user_data()
    await test_data_analyst_without_data()
    await test_data_analyst_chart_types()
    
    logger.info("\n测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
