# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
API调用工具

为智能体提供API调用功能
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional, Annotated
from datetime import datetime

from langchain_core.tools import tool
from src.database import get_db_session
from src.tools.decorators import log_io
from src.services.api_tools.api_executor import APIExecutor
from src.models.api_tools import APIDefinition

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
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def __str__(self) -> str:
        """返回格式化的字符串表示"""
        if self.success:
            result = f"✅ {self.message}"
            if self.data is not None:
                if isinstance(self.data, (dict, list)):
                    result += f"\n📊 数据: {json.dumps(self.data, ensure_ascii=False, indent=2)}"
                else:
                    result += f"\n📊 数据: {self.data}"
            if self.metadata:
                result += f"\n🔍 元数据: {json.dumps(self.metadata, ensure_ascii=False)}"
        else:
            result = f"❌ {self.message}"
            if self.error:
                result += f"\n🚨 错误: {self.error}"
        
        result += f"\n⏰ 时间: {self.timestamp}"
        return result


@tool
@log_io
def execute_api(
    api_name: Annotated[str, "API名称或ID"],
    parameters: Annotated[Optional[Dict[str, Any]], "API参数字典"] = None
) -> str:
    """
    执行API调用
    
    根据API名称或ID执行对应的API调用，支持动态参数传递。
    返回统一格式的JSON结果，包含执行状态、数据和元信息。
    """
    try:
        logger.info(f"🔗 执行API调用: {api_name}")
        
        # 获取数据库会话
        session = next(get_db_session())
        
        try:
            # 查找API定义
            from sqlalchemy import text
            
            # 根据名称或ID查找API
            if api_name.isdigit():
                # 按ID查找
                query = text("""
                    SELECT id, name, description, url, method, parameters
                    FROM api_tools.api_definitions
                    WHERE id = :api_id AND enabled = true
                """)
                result = session.execute(query, {"api_id": int(api_name)})
            else:
                # 按名称查找
                query = text("""
                    SELECT id, name, description, url, method, parameters
                    FROM api_tools.api_definitions
                    WHERE name = :api_name AND enabled = true
                """)
                result = session.execute(query, {"api_name": api_name})
            
            api_def = result.fetchone()
            if not api_def:
                return ToolResult(
                    success=False,
                    message=f"API '{api_name}' 未找到或已禁用",
                    error="API_NOT_FOUND"
                ).to_json()
            
            # 使用真实的API执行器
            executor = APIExecutor()

            # 构建API定义对象
            api_definition = APIDefinition(
                id=api_def.id,
                name=api_def.name,
                description=api_def.description,
                url=api_def.url,
                method=api_def.method,
                parameters=api_def.parameters or [],
                headers={},
                timeout_seconds=30,
                rate_limit={"requests_per_minute": 60},
                auth_config={"type": "none"}
            )

            # 执行API调用 (同步调用异步方法)
            execution_result = asyncio.run(executor.execute_api(
                api_def=api_definition,
                parameters=parameters or {}
            ))

            if execution_result.success:
                return ToolResult(
                    success=True,
                    message=f"API '{api_def.name}' 调用成功",
                    data={
                        "result": execution_result.result.extracted_data or execution_result.result.parsed_data,
                        "status_code": execution_result.result.status_code,
                        "execution_time_ms": execution_result.execution_time_ms,
                        "raw_content": execution_result.result.raw_content[:500] if execution_result.result.raw_content else None
                    },
                    metadata={
                        "api_id": api_def.id,
                        "api_name": api_def.name,
                        "url": api_def.url,
                        "method": api_def.method,
                        "parameters_provided": list(parameters.keys()) if parameters else []
                    }
                ).to_json()
            else:
                return ToolResult(
                    success=False,
                    message=f"API '{api_def.name}' 调用失败",
                    error=execution_result.result.error_message,
                    metadata={
                        "api_id": api_def.id,
                        "api_name": api_def.name,
                        "execution_time_ms": execution_result.execution_time_ms
                    }
                ).to_json()
        
        finally:
            session.close()
    
    except Exception as e:
        logger.error(f"❌ API调用异常: {e}")
        return ToolResult(
            success=False,
            message="API调用过程中发生异常",
            error=str(e),
            metadata={"api_name": api_name}
        ).to_json()


@tool
@log_io
def list_available_apis(
    category: Annotated[Optional[str], "API分类过滤"] = None,
    enabled_only: Annotated[bool, "只显示启用的API"] = True
) -> str:
    """
    列出可用的API
    
    获取系统中所有可用的API列表，支持按分类过滤。
    """
    try:
        logger.info(f"📋 获取API列表: category={category}, enabled_only={enabled_only}")
        
        session = next(get_db_session())
        
        try:
            from sqlalchemy import text
            
            # 构建查询
            where_conditions = []
            params = {}
            
            if enabled_only:
                where_conditions.append("enabled = true")
            
            if category:
                where_conditions.append("category = :category")
                params["category"] = category
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            query = text(f"""
                SELECT id, name, description, category, url, method, enabled
                FROM api_tools.api_definitions 
                WHERE {where_clause}
                ORDER BY category, name
            """)
            
            result = session.execute(query, params)
            apis = []
            
            for row in result.fetchall():
                api_info = {
                    "id": row.id,
                    "name": row.name,
                    "description": row.description,
                    "category": row.category,
                    "url": row.url,
                    "method": row.method,
                    "enabled": row.enabled
                }
                apis.append(api_info)
            
            return ToolResult(
                success=True,
                message=f"找到 {len(apis)} 个API",
                data={"apis": apis, "total_count": len(apis)},
                metadata={
                    "category_filter": category,
                    "enabled_only": enabled_only
                }
            ).to_json()
        
        finally:
            session.close()
    
    except Exception as e:
        logger.error(f"❌ 获取API列表异常: {e}")
        return ToolResult(
            success=False,
            message="获取API列表过程中发生异常",
            error=str(e)
        ).to_json()


@tool
@log_io
def get_api_details(
    api_name: Annotated[str, "API名称或ID"]
) -> str:
    """
    获取API详细信息
    
    获取指定API的详细配置信息，包括参数定义、响应格式等。
    """
    try:
        logger.info(f"🔍 获取API详情: {api_name}")
        
        session = next(get_db_session())
        
        try:
            from sqlalchemy import text
            
            # 根据名称或ID查找API
            if api_name.isdigit():
                query = text("""
                    SELECT id, name, description, category, url, method, parameters, 
                           headers, timeout, enabled, created_at, updated_at
                    FROM api_tools.api_definitions 
                    WHERE id = :api_id
                """)
                result = session.execute(query, {"api_id": int(api_name)})
            else:
                query = text("""
                    SELECT id, name, description, category, url, method, parameters, 
                           headers, timeout, enabled, created_at, updated_at
                    FROM api_tools.api_definitions 
                    WHERE name = :api_name
                """)
                result = session.execute(query, {"api_name": api_name})
            
            api_def = result.fetchone()
            if not api_def:
                return ToolResult(
                    success=False,
                    message=f"API '{api_name}' 未找到",
                    error="API_NOT_FOUND"
                ).to_json()
            
            api_details = {
                "id": api_def.id,
                "name": api_def.name,
                "description": api_def.description,
                "category": api_def.category,
                "url": api_def.url,
                "method": api_def.method,
                "parameters": api_def.parameters,
                "headers": api_def.headers,
                "timeout": api_def.timeout,
                "enabled": api_def.enabled,
                "created_at": api_def.created_at.isoformat() if api_def.created_at else None,
                "updated_at": api_def.updated_at.isoformat() if api_def.updated_at else None
            }
            
            return ToolResult(
                success=True,
                message=f"API '{api_def.name}' 详情获取成功",
                data=api_details
            ).to_json()
        
        finally:
            session.close()
    
    except Exception as e:
        logger.error(f"❌ 获取API详情异常: {e}")
        return ToolResult(
            success=False,
            message="获取API详情过程中发生异常",
            error=str(e),
            metadata={"api_name": api_name}
        ).to_json()
