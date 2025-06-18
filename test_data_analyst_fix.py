#!/usr/bin/env python3
"""
测试数据分析师修复效果
验证智能体是否按照新的严格协议执行
"""

import asyncio
import logging
from langchain_core.messages import HumanMessage
from langgraph.types import RunnableConfig

from src.graph.nodes import data_analyst_node
from src.graph.types import State

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_data_analyst_execution():
    """测试数据分析师的执行逻辑"""
    
    # 测试用例
    test_cases = [
        {
            "name": "仓库收发信息查询",
            "message": "查询今天的仓库收发信息",
            "expected_tools": ["discover_resources", "smart_text2sql_query"],
            "expected_behavior": "应该自动生成柱状图"
        },
        {
            "name": "生产数据趋势查询", 
            "message": "显示本周的生产数据趋势",
            "expected_tools": ["discover_resources", "smart_text2sql_query"],
            "expected_behavior": "应该自动生成折线图"
        },
        {
            "name": "质量数据分布查询",
            "message": "分析产品质量数据的分布情况",
            "expected_tools": ["discover_resources", "smart_text2sql_query"],
            "expected_behavior": "应该自动生成饼图"
        }
    ]
    
    # 创建配置
    config = RunnableConfig(
        configurable={
            "max_search_results": 5,
            "max_plan_iterations": 1,
            "max_step_num": 10,
            "enable_background_investigation": False,
            "resources": []
        }
    )
    
    logger.info("=== 开始测试数据分析师修复效果 ===")
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n--- 测试 {i}: {test_case['name']} ---")
        logger.info(f"查询: {test_case['message']}")
        logger.info(f"期望工具: {test_case['expected_tools']}")
        logger.info(f"期望行为: {test_case['expected_behavior']}")
        
        # 创建测试状态
        test_state: State = {
            "messages": [HumanMessage(content=test_case["message"])],
            "locale": "zh-CN",
            "research_topic": test_case["message"],
            "enable_background_investigation": False,
            "resources": [],
            "observations": [],
            "current_plan": None,
            "final_report": None,
            "data_query": test_case["message"]
        }
        
        try:
            logger.info("🚀 执行数据分析师节点...")
            
            # 执行数据分析师节点
            result = await data_analyst_node(test_state, config)
            
            # 检查结果
            if hasattr(result, 'update') and 'final_report' in result.update:
                final_report = result.update['final_report']
                logger.info(f"✅ 分析完成")
                logger.info(f"📊 最终报告长度: {len(final_report)} 字符")
                
                # 检查是否提到了图表生成
                chart_keywords = ["图表", "chart", "生成", "推送", "显示", "可视化"]
                chart_mentioned = any(keyword in final_report.lower() for keyword in chart_keywords)
                
                if chart_mentioned:
                    logger.info("✅ 报告中提到了图表生成")
                else:
                    logger.warning("⚠️  报告中未明确提到图表生成")
                
                # 检查是否有"思考"过程（应该避免）
                thinking_keywords = ["让我", "我需要", "首先", "然后", "接下来", "分析一下"]
                thinking_detected = any(keyword in final_report for keyword in thinking_keywords)
                
                if thinking_detected:
                    logger.warning("⚠️  检测到可能的思考过程，应该直接执行工具")
                else:
                    logger.info("✅ 没有检测到多余的思考过程")
                
                # 显示报告摘要
                logger.info(f"📝 报告摘要: {final_report[:200]}...")
                
            else:
                logger.error("❌ 未获得有效的分析结果")
                
        except Exception as e:
            logger.error(f"❌ 测试失败: {e}")
            import traceback
            logger.error(f"错误详情: {traceback.format_exc()}")
    
    logger.info("\n=== 测试完成 ===")

async def test_smart_text2sql_tool():
    """单独测试 smart_text2sql_query 工具"""
    logger.info("\n=== 测试 smart_text2sql_query 工具 ===")
    
    try:
        from src.tools.text2sql_tools import smart_text2sql_query
        
        # 测试工具调用
        test_query = "查询今天的仓库收发信息"
        logger.info(f"测试查询: {test_query}")
        
        result = smart_text2sql_query.invoke({
            "question": test_query,
            "database_id": 1,
            "auto_chart": True,
            "chart_title": "仓库收发统计"
        })
        
        logger.info(f"✅ 工具调用成功")
        logger.info(f"📊 结果长度: {len(result)} 字符")
        logger.info(f"📝 结果摘要: {result[:300]}...")
        
        # 检查是否提到图表生成
        if "图表" in result or "chart" in result.lower():
            logger.info("✅ 结果中提到了图表生成")
        else:
            logger.warning("⚠️  结果中未提到图表生成")
            
    except Exception as e:
        logger.error(f"❌ 工具测试失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_data_analyst_execution())
    asyncio.run(test_smart_text2sql_tool())
