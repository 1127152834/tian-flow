# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
资源发现工具

为智能体提供资源发现功能，根据用户查询找到最相关的系统资源和推荐工具
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Annotated

from langchain_core.tools import tool
from src.tools.decorators import log_io
from src.services.resource_discovery.resource_matcher import ResourceMatcher
from src.config.resource_discovery import get_resource_discovery_config
from src.database import get_db_session

logger = logging.getLogger(__name__)


class ToolResult:
    """统一的工具返回值结构"""
    
    def __init__(
        self, 
        success: bool, 
        message: str, 
        data: Any = None, 
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.message = message
        self.data = data
        self.error = error
        self.metadata = metadata or {}
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps({
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata
        }, ensure_ascii=False, indent=2)


@tool
@log_io
def discover_resources(
    query: Annotated[str, "用户查询或问题描述"],
    resource_types: Annotated[Optional[List[str]], "资源类型过滤，如 ['API', 'DATABASE', 'TEXT2SQL']"] = None,
    top_k: Annotated[int, "返回的最大资源数量"] = 5,
    min_confidence: Annotated[float, "最小置信度阈值 (0.0-1.0)"] = 0.3
) -> str:
    """
    智能体资源发现工具
    
    根据用户查询找到最相关的系统资源，返回资源信息和推荐的工具名称。
    这是智能体的核心工具，用于动态发现可用的系统资源。
    
    返回格式包含：
    - 匹配的资源列表
    - 每个资源的推荐工具
    - 置信度评分
    - 使用建议
    """
    try:
        logger.info(f"🔍 智能体资源发现: '{query}'")
        
        # 获取配置和服务
        config = get_resource_discovery_config()
        matcher = ResourceMatcher()
        session = next(get_db_session())
        
        try:
            # 执行资源匹配 (处理事件循环)
            try:
                # 尝试获取当前事件循环
                asyncio.get_running_loop()
                # 如果已有事件循环，使用线程池执行
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        matcher.match_resources(
                            session=session,
                            user_query=query,
                            top_k=top_k,
                            resource_types=resource_types,
                            min_confidence=min_confidence
                        )
                    )
                    matches = future.result(timeout=30)
            except RuntimeError:
                # 没有运行的事件循环，直接使用 asyncio.run
                matches = asyncio.run(matcher.match_resources(
                    session=session,
                    user_query=query,
                    top_k=top_k,
                    resource_types=resource_types,
                    min_confidence=min_confidence
                ))
            
            if not matches:
                return ToolResult(
                    success=True,
                    message="未找到匹配的资源",
                    data={
                        "query": query,
                        "matches": [],
                        "total_matches": 0,
                        "suggestions": [
                            "尝试使用更通用的关键词",
                            "检查拼写是否正确",
                            "降低置信度阈值"
                        ]
                    },
                    metadata={
                        "search_params": {
                            "resource_types": resource_types,
                            "top_k": top_k,
                            "min_confidence": min_confidence
                        }
                    }
                ).to_json()
            
            # 转换匹配结果为智能体友好的格式
            agent_resources = []
            for match in matches:
                resource = match.resource
                
                # 从元数据中提取工具信息
                tool_name = None
                if hasattr(resource, 'metadata') and resource.metadata:
                    tool_methods = resource.metadata.get('tool_methods', [])
                    if tool_methods:
                        tool_name = tool_methods[0]  # 使用第一个工具作为主要工具
                
                # 如果没有从元数据获取到工具，尝试从配置获取
                if not tool_name:
                    resource_config = config.get_resource_by_table(resource.source_table)
                    if resource_config:
                        tool_name = resource_config.tool
                
                agent_resource = {
                    "resource_id": resource.resource_id,
                    "resource_name": resource.resource_name,
                    "resource_type": resource.resource_type,
                    "description": resource.description,
                    "confidence": match.confidence_score,
                    "recommended_tool": tool_name,
                    "capabilities": resource.capabilities or [],
                    "tags": resource.tags or [],
                    "usage_suggestion": _generate_usage_suggestion(resource, tool_name),
                    "metadata": {
                        "source_table": resource.source_table,
                        "source_id": resource.source_id,
                        "match_reasoning": match.match_reasoning
                    }
                }
                agent_resources.append(agent_resource)
            
            # 生成整体建议
            overall_suggestions = _generate_overall_suggestions(agent_resources, query)
            
            return ToolResult(
                success=True,
                message=f"找到 {len(agent_resources)} 个相关资源",
                data={
                    "query": query,
                    "matches": agent_resources,
                    "total_matches": len(agent_resources),
                    "best_match": agent_resources[0] if agent_resources else None,
                    "suggestions": overall_suggestions
                },
                metadata={
                    "search_params": {
                        "resource_types": resource_types,
                        "top_k": top_k,
                        "min_confidence": min_confidence
                    },
                    "config_info": {
                        "total_configured_resources": len(config.get_enabled_resources()),
                        "available_tools": config.get_all_tools()
                    }
                }
            ).to_json()
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"❌ 智能体资源发现失败: {e}")
        return ToolResult(
            success=False,
            message="资源发现过程中发生错误",
            error=str(e),
            metadata={"query": query}
        ).to_json()


def _generate_usage_suggestion(resource, tool_name: Optional[str]) -> str:
    """生成使用建议"""
    if not tool_name:
        return "请联系管理员配置相应的工具"
    
    resource_type = resource.resource_type
    
    if resource_type == "API":
        return f"使用 {tool_name} 工具调用此API，传入相应的参数"
    elif resource_type == "DATABASE":
        return f"使用 {tool_name} 工具查询数据库信息、表结构或测试连接"
    elif resource_type == "TEXT2SQL":
        return f"使用 {tool_name} 工具将自然语言转换为SQL查询"
    else:
        return f"使用 {tool_name} 工具操作此资源"


def _generate_overall_suggestions(resources: List[Dict[str, Any]], query: str) -> List[str]:
    """生成整体建议"""
    suggestions = []
    
    if not resources:
        return ["未找到相关资源，请尝试其他关键词"]
    
    # 按资源类型分组
    type_groups = {}
    for resource in resources:
        res_type = resource["resource_type"]
        if res_type not in type_groups:
            type_groups[res_type] = []
        type_groups[res_type].append(resource)
    
    # 生成针对性建议
    if "API" in type_groups:
        api_count = len(type_groups["API"])
        suggestions.append(f"找到 {api_count} 个API资源，可以用于外部数据获取和服务调用")
    
    if "DATABASE" in type_groups:
        db_count = len(type_groups["DATABASE"])
        suggestions.append(f"找到 {db_count} 个数据库资源，可以用于数据查询和分析")
    
    if "TEXT2SQL" in type_groups:
        sql_count = len(type_groups["TEXT2SQL"])
        suggestions.append(f"找到 {sql_count} 个Text2SQL资源，可以用于自然语言查询转换")
    
    # 添加最佳匹配建议
    best_match = resources[0]
    suggestions.append(f"推荐优先使用 '{best_match['resource_name']}' (置信度: {best_match['confidence']:.2f})")
    
    return suggestions


@tool
@log_io
def get_available_tools() -> str:
    """
    获取所有可用的工具列表
    
    返回系统中配置的所有工具及其对应的资源类型。
    """
    try:
        logger.info("📋 获取可用工具列表")
        
        config = get_resource_discovery_config()
        
        tool_info = {}
        for resource in config.get_enabled_resources():
            tool_name = resource.tool
            if tool_name not in tool_info:
                tool_info[tool_name] = {
                    "tool_name": tool_name,
                    "resource_types": [],
                    "tables": [],
                    "descriptions": []
                }
            
            # 推断资源类型
            if "api" in resource.table.lower():
                resource_type = "API"
            elif "text2sql" in resource.table.lower() or "vanna" in resource.table.lower():
                resource_type = "TEXT2SQL"
            elif "database" in resource.table.lower():
                resource_type = "DATABASE"
            else:
                resource_type = "TOOL"
            
            if resource_type not in tool_info[tool_name]["resource_types"]:
                tool_info[tool_name]["resource_types"].append(resource_type)
            
            tool_info[tool_name]["tables"].append(resource.table)
            if resource.description and resource.description not in tool_info[tool_name]["descriptions"]:
                tool_info[tool_name]["descriptions"].append(resource.description)
        
        return ToolResult(
            success=True,
            message=f"找到 {len(tool_info)} 个可用工具",
            data={
                "tools": list(tool_info.values()),
                "total_tools": len(tool_info),
                "tool_names": list(tool_info.keys())
            },
            metadata={
                "config_resources": len(config.get_enabled_resources())
            }
        ).to_json()
        
    except Exception as e:
        logger.error(f"❌ 获取工具列表失败: {e}")
        return ToolResult(
            success=False,
            message="获取工具列表过程中发生错误",
            error=str(e)
        ).to_json()


@tool
@log_io
def get_resource_details(
    resource_id: Annotated[str, "资源ID"]
) -> str:
    """
    获取特定资源的详细信息
    
    返回指定资源的完整信息，包括元数据、能力和使用方法。
    """
    try:
        logger.info(f"🔍 获取资源详情: {resource_id}")
        
        session = next(get_db_session())
        
        try:
            from sqlalchemy import text
            
            query = text("""
                SELECT resource_id, resource_name, resource_type, description,
                       capabilities, tags, metadata, source_table, source_id,
                       vectorization_status, usage_count, success_rate,
                       created_at, updated_at
                FROM resource_discovery.resource_registry
                WHERE resource_id = :resource_id AND is_active = true
            """)
            
            result = session.execute(query, {"resource_id": resource_id})
            row = result.fetchone()
            
            if not row:
                return ToolResult(
                    success=False,
                    message=f"资源不存在: {resource_id}",
                    error="RESOURCE_NOT_FOUND"
                ).to_json()
            
            # 获取对应的工具信息
            config = get_resource_discovery_config()
            resource_config = config.get_resource_by_table(row.source_table)
            recommended_tool = resource_config.tool if resource_config else None
            
            resource_details = {
                "resource_id": row.resource_id,
                "resource_name": row.resource_name,
                "resource_type": row.resource_type,
                "description": row.description,
                "capabilities": row.capabilities or [],
                "tags": row.tags or [],
                "metadata": row.metadata or {},
                "source_table": row.source_table,
                "source_id": row.source_id,
                "recommended_tool": recommended_tool,
                "usage_suggestion": _generate_usage_suggestion(row, recommended_tool),
                "statistics": {
                    "usage_count": row.usage_count or 0,
                    "success_rate": row.success_rate or 0.0,
                    "vectorization_status": row.vectorization_status
                },
                "timestamps": {
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None
                }
            }
            
            return ToolResult(
                success=True,
                message="资源详情获取成功",
                data=resource_details
            ).to_json()
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"❌ 获取资源详情失败: {e}")
        return ToolResult(
            success=False,
            message="获取资源详情过程中发生错误",
            error=str(e),
            metadata={"resource_id": resource_id}
        ).to_json()
