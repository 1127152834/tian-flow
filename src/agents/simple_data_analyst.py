#!/usr/bin/env python3
"""
简单数据分析师 - 绕过LangGraph工具调用问题
直接使用工具，避免LLM工具调用格式问题
"""

import logging
import json
from typing import Optional

from src.llms.llm import get_llm_by_type
from src.tools.resource_discovery_tool import discover_resources
from src.tools.text2sql_tools import smart_text2sql_query

logger = logging.getLogger(__name__)

class SimpleDataAnalyst:
    """简单数据分析师 - 直接调用工具"""
    
    def __init__(self):
        """初始化简单数据分析师"""
        self.llm = get_llm_by_type('basic')
        logger.info("✅ 简单数据分析师初始化完成")
    
    def analyze(self, question: str, **kwargs) -> str:
        """
        分析数据查询请求
        
        Args:
            question: 用户问题
            **kwargs: 其他参数
            
        Returns:
            分析结果
        """
        try:
            logger.info(f"🔍 简单数据分析师开始分析: {question[:100]}...")
            
            # 第一步：资源发现
            logger.info("📋 第一步：资源发现")
            resource_result = discover_resources.invoke({"query": question})
            
            logger.info(f"资源发现结果: {resource_result[:200]}...")
            
            # 解析资源发现结果，提取数据库ID
            database_id = self._extract_database_id(resource_result)
            
            if not database_id:
                return f"""🔍 资源发现结果：
{resource_result}

❌ 未能找到合适的数据库资源，无法执行查询。
建议：
- 尝试使用更通用的关键词
- 检查数据库配置是否正确
- 联系管理员确认数据源状态"""
            
            # 第二步：执行SQL查询
            logger.info(f"📊 第二步：执行SQL查询，数据库ID: {database_id}")
            sql_result = smart_text2sql_query.invoke({
                "question": question,
                "database_id": database_id,
                "auto_chart": True,
                "chart_title": f"查询结果: {question[:30]}..."
            })
            
            logger.info(f"SQL查询结果: {sql_result[:200]}...")
            
            # 第三步：生成最终报告
            final_report = f"""📊 **数据分析结果**

🎯 **资源发现**：
{resource_result}

📈 **查询执行**：
{sql_result}

✅ **分析完成**，如需进一步分析请告知具体需求。"""
            
            logger.info(f"✅ 简单数据分析完成，报告长度: {len(final_report)} 字符")
            return final_report
                
        except Exception as e:
            logger.error(f"❌ 简单数据分析异常: {e}")
            import traceback
            logger.error(f"错误详情: {traceback.format_exc()}")
            return f"分析过程中发生异常: {str(e)}"
    
    def _extract_database_id(self, resource_text: str) -> Optional[int]:
        """从资源发现结果中提取数据库ID"""
        try:
            # 查找 database_X 模式
            import re
            
            # 查找 "数据库ID: X" 模式
            id_match = re.search(r'数据库ID:\s*(\d+)', resource_text)
            if id_match:
                return int(id_match.group(1))
            
            # 查找 "傲雷仓储中心库" 等关键词，映射到已知的数据库ID
            if "仓储中心库" in resource_text or "仓库" in resource_text:
                return 8  # 傲雷仓储中心库
            elif "制造中心库" in resource_text:
                return 6  # 傲雷制造中心库
            elif "采购中心库" in resource_text:
                return 7  # 傲雷采购中心库
            
            # 默认使用仓储中心库
            logger.info("未能精确匹配数据库，使用默认仓储中心库 (ID: 8)")
            return 8
            
        except Exception as e:
            logger.error(f"提取数据库ID失败: {e}")
            return 8  # 默认使用仓储中心库

# 创建全局实例
simple_data_analyst = SimpleDataAnalyst()

def analyze_with_simple_agent(question: str, **kwargs) -> str:
    """
    使用简单数据分析师分析问题
    
    Args:
        question: 用户问题
        **kwargs: 其他参数
        
    Returns:
        分析结果
    """
    return simple_data_analyst.analyze(question, **kwargs)

if __name__ == "__main__":
    # 测试
    test_questions = [
        "查看今天仓库收料（入库）信息",
        "统计本月的生产订单完成情况",
        "分析供应商交货及时率"
    ]
    
    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"测试问题: {question}")
        print(f"{'='*60}")
        
        result = analyze_with_simple_agent(question)
        print(f"分析结果:\n{result}")
