#!/usr/bin/env python3
"""
测试前端响应格式
模拟完整的前端请求流程
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

async def test_frontend_response():
    """测试前端响应格式"""
    
    logger.info("=== 测试前端响应格式 ===")
    
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
            
            # 检查是否包含技术细节
            technical_terms = [
                'smart_text2sql_query', 'discover_resources', 'tool_call',
                'function_name', 'parameters', 'arguments', 'database_id'
            ]
            
            contains_technical = any(term in final_report.lower() for term in technical_terms)
            
            if contains_technical:
                logger.warning("⚠️  响应包含技术细节，需要清理")
                for term in technical_terms:
                    if term in final_report.lower():
                        logger.warning(f"   - 发现技术术语: {term}")
            else:
                logger.info("✅ 响应格式良好，无技术细节")
            
            # 检查是否包含有用信息
            useful_terms = ['SQL', '查询', '数据', '结果', '图表', '分析']
            contains_useful = any(term in final_report for term in useful_terms)
            
            if contains_useful:
                logger.info("✅ 响应包含有用信息")
            else:
                logger.warning("⚠️  响应缺少有用信息")
            
            logger.info("📝 最终报告内容:")
            logger.info("=" * 50)
            logger.info(final_report)
            logger.info("=" * 50)
                
        else:
            logger.error("❌ 未获得有效的分析结果")
            logger.error(f"结果类型: {type(result)}")
            if hasattr(result, 'update'):
                logger.error(f"更新内容: {result.update}")
            
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_frontend_response())
