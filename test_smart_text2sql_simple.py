#!/usr/bin/env python3
"""
简化测试 smart_text2sql_query 工具
"""

import asyncio
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_smart_text2sql_sync():
    """同步测试 smart_text2sql_query 工具"""
    logger.info("=== 测试 smart_text2sql_query 工具 (同步) ===")
    
    try:
        from src.tools.text2sql_tools import smart_text2sql_query
        
        # 测试工具调用
        test_query = "查询今天的仓库收发信息"
        logger.info(f"测试查询: {test_query}")
        
        result = smart_text2sql_query.invoke({
            "question": test_query,
            "database_id": 8,  # 使用傲雷仓储中心库
            "auto_chart": True,
            "chart_title": "仓库收发统计"
        })
        
        logger.info(f"✅ 工具调用成功")
        logger.info(f"📊 结果长度: {len(result)} 字符")
        logger.info(f"📝 结果摘要: {result[:500]}...")
        
        # 检查是否提到图表生成
        if "图表" in result or "chart" in result.lower():
            logger.info("✅ 结果中提到了图表生成")
        else:
            logger.warning("⚠️  结果中未提到图表生成")
            
        # 检查是否成功
        if '"success": true' in result:
            logger.info("✅ 查询执行成功")
        else:
            logger.warning("⚠️  查询可能失败")
            
    except Exception as e:
        logger.error(f"❌ 工具测试失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")

def test_discover_resources():
    """测试资源发现工具"""
    logger.info("\n=== 测试资源发现工具 ===")
    
    try:
        from src.tools.resource_discovery_tool import discover_resources
        
        test_query = "查询今天的仓库收发信息"
        logger.info(f"测试查询: {test_query}")
        
        result = discover_resources.invoke({
            "query": test_query
        })
        
        logger.info(f"✅ 资源发现成功")
        logger.info(f"📊 结果长度: {len(result)} 字符")
        
        # 检查是否找到TEXT2SQL资源
        if "TEXT2SQL" in result:
            logger.info("✅ 找到了TEXT2SQL资源")
        else:
            logger.warning("⚠️  未找到TEXT2SQL资源")
            
        # 检查是否找到数据库资源
        if "DATABASE" in result:
            logger.info("✅ 找到了数据库资源")
        else:
            logger.warning("⚠️  未找到数据库资源")
            
    except Exception as e:
        logger.error(f"❌ 资源发现测试失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")

if __name__ == "__main__":
    # 运行测试
    test_discover_resources()
    test_smart_text2sql_sync()
