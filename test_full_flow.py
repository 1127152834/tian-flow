#!/usr/bin/env python3
"""
测试完整的数据分析师流程
模拟前端请求
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

async def test_full_data_analyst_flow():
    """测试完整的数据分析师流程"""
    
    logger.info("=== 开始测试完整数据分析师流程 ===")
    
    # 创建测试状态 - 模拟前端发送的请求
    test_state: State = {
        "messages": [HumanMessage(content="查看今天仓库收料（入库）信息")],
        "locale": "zh-CN",
        "research_topic": "查看今天仓库收料（入库）信息",
        "enable_background_investigation": False,
        "resources": [],
        "observations": [],
        "current_plan": None,
        "final_report": None,
        "data_query": "查看今天仓库收料（入库）信息"
    }
    
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
    
    try:
        logger.info("🚀 开始执行数据分析师节点...")
        logger.info(f"📝 用户查询: {test_state['messages'][0].content}")
        
        # 执行数据分析师节点
        result = await data_analyst_node(test_state, config)
        
        logger.info("✅ 数据分析师执行完成")
        
        # 检查结果
        if hasattr(result, 'update') and 'final_report' in result.update:
            final_report = result.update['final_report']
            logger.info(f"📊 最终报告长度: {len(final_report)} 字符")
            logger.info(f"📝 最终报告内容:")
            logger.info("=" * 50)
            logger.info(final_report)
            logger.info("=" * 50)
            
            # 检查是否包含关键信息
            if "SQL" in final_report:
                logger.info("✅ 报告包含SQL查询")
            if "图表" in final_report or "chart" in final_report.lower():
                logger.info("✅ 报告提到了图表生成")
            if "数据" in final_report:
                logger.info("✅ 报告包含数据信息")
                
        else:
            logger.error("❌ 未获得有效的分析结果")
            logger.error(f"结果类型: {type(result)}")
            if hasattr(result, 'update'):
                logger.error(f"更新内容: {result.update}")
            
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")

async def test_step_by_step():
    """逐步测试每个工具"""
    logger.info("\n=== 逐步测试工具 ===")
    
    # 1. 测试资源发现
    logger.info("1. 测试资源发现...")
    try:
        from src.tools.resource_discovery_tool import discover_resources
        result1 = discover_resources.invoke({"query": "查看今天仓库收料（入库）信息"})
        logger.info("✅ 资源发现成功")
        
        # 检查是否找到TEXT2SQL资源
        if "TEXT2SQL" in result1:
            logger.info("✅ 找到TEXT2SQL资源")
        else:
            logger.warning("⚠️  未找到TEXT2SQL资源")
            
    except Exception as e:
        logger.error(f"❌ 资源发现失败: {e}")
        return
    
    # 2. 测试smart_text2sql_query
    logger.info("2. 测试smart_text2sql_query...")
    try:
        from src.tools.text2sql_tools import smart_text2sql_query
        result2 = smart_text2sql_query.invoke({
            "question": "查看今天仓库收料（入库）信息",
            "database_id": 8,
            "auto_chart": True,
            "chart_title": "今天仓库收料统计"
        })
        logger.info("✅ smart_text2sql_query成功")
        logger.info(f"📊 结果: {result2[:200]}...")
        
    except Exception as e:
        logger.error(f"❌ smart_text2sql_query失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_step_by_step())
    asyncio.run(test_full_data_analyst_flow())
