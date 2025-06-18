#!/usr/bin/env python3
"""
LangGraph数据分析师 - 使用预构建智能体
基于LangGraph最佳实践重新实现
"""

import logging
from typing import List, Optional, Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState

from src.llms.llm import get_llm_by_type
from src.tools.text2sql_tools import smart_text2sql_query
from src.tools.resource_discovery_tool import discover_resources

logger = logging.getLogger(__name__)

class LangGraphDataAnalyst:
    """基于LangGraph预构建智能体的数据分析师"""
    
    def __init__(self):
        """初始化LangGraph数据分析师"""
        self.llm = get_llm_by_type('basic')
        
        # 定义工具列表
        self.tools = [
            discover_resources,
            smart_text2sql_query
        ]
        
        # 创建预构建的ReAct智能体
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools
        )
        
        logger.info("✅ LangGraph数据分析师初始化完成")
    
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
            logger.info(f"🔍 LangGraph数据分析师开始分析: {question[:100]}...")
            
            # 构建系统提示
            system_prompt = """你是傲雷数据分析师，专门处理制造业数据分析任务。

## 核心职责
1. 理解用户的数据查询需求
2. 使用资源发现工具找到相关数据源
3. 使用智能SQL查询工具获取数据
4. 提供清晰的数据分析结果

## 严格工作流程
1. **第一步 - 资源发现**: 调用 discover_resources 工具找到相关资源
2. **第二步 - 数据查询**: 如果找到资源，立即调用 smart_text2sql_query 工具执行查询
   - 对于数据库资源，从资源ID中提取数据库ID（如 database_8 → 8）
   - 使用提取的数据库ID作为 database_id 参数
   - 设置 auto_chart=True 自动生成图表
3. **第三步 - 结果分析**: 分析查询结果，提供有价值的洞察

## 关键规则
- 找到资源后，必须立即执行数据查询，不要询问用户
- 从资源ID提取数据库ID：database_8 → database_id=8
- 即使置信度不高，也要尝试查询最佳匹配的资源
- 专注于数据驱动的分析，不要编造信息
- 如果查询结果为空，说明可能的原因并建议改进
"""
            
            # 构建消息
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=question)
            ]
            
            # 调用智能体
            result = self.agent.invoke({"messages": messages})
            
            # 提取最后的AI消息
            if result and "messages" in result:
                last_message = result["messages"][-1]
                if hasattr(last_message, 'content'):
                    response = last_message.content
                    logger.info(f"✅ LangGraph分析完成，响应长度: {len(response)} 字符")
                    return response
                else:
                    logger.warning("⚠️ 智能体响应格式异常")
                    return "分析完成，但响应格式异常"
            else:
                logger.warning("⚠️ 智能体未返回有效结果")
                return "分析过程中出现问题，请重试"
                
        except Exception as e:
            logger.error(f"❌ LangGraph数据分析异常: {e}")
            import traceback
            logger.error(f"错误详情: {traceback.format_exc()}")
            return f"分析过程中发生异常: {str(e)}"

# 创建全局实例
langgraph_data_analyst = LangGraphDataAnalyst()

def analyze_with_langgraph(question: str, **kwargs) -> str:
    """
    使用LangGraph数据分析师分析问题
    
    Args:
        question: 用户问题
        **kwargs: 其他参数
        
    Returns:
        分析结果
    """
    return langgraph_data_analyst.analyze(question, **kwargs)

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
        
        result = analyze_with_langgraph(question)
        print(f"分析结果:\n{result}")
