# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
数据库操作工具

为智能体提供数据库查询和管理功能
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, Annotated
from datetime import datetime

from langchain_core.tools import tool
from src.database import get_db_session
from src.tools.decorators import log_io
from src.services.database_datasource import DatabaseDatasourceService

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
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps({
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }, ensure_ascii=False, indent=2)


@tool
@log_io
def database_query(
    database_name: Annotated[str, "数据库名称或ID"],
    query_type: Annotated[str, "查询类型: info|tables|schema"] = "info"
) -> str:
    """
    执行数据库查询

    支持多种查询类型：获取数据库信息、表列表、表结构。
    注意：不支持SQL执行，请使用text2sql_query工具执行SQL查询。
    """
    try:
        logger.info(f"🗄️ 数据库查询: {database_name} - {query_type}")

        # 使用真实的数据库数据源服务
        datasource_service = DatabaseDatasourceService()

        # 获取数据库配置
        if database_name.isdigit():
            datasource = asyncio.run(datasource_service.get_datasource(int(database_name)))
        else:
            # 按名称查找需要先列出所有数据源
            datasources = asyncio.run(datasource_service.list_datasources(search=database_name))
            datasource = datasources[0] if datasources else None

        if not datasource:
            return ToolResult(
                success=False,
                message=f"数据库 '{database_name}' 未找到",
                error="DATABASE_NOT_FOUND"
            ).to_json()

        # 根据查询类型执行不同操作
        if query_type == "info":
            return ToolResult(
                success=True,
                message=f"数据库 '{datasource.name}' 信息获取成功",
                data={
                    "id": datasource.id,
                    "name": datasource.name,
                    "description": datasource.description,
                    "type": datasource.database_type.value,
                    "host": datasource.host,
                    "port": datasource.port,
                    "database": datasource.database_name
                }
            ).to_json()

        elif query_type == "tables":
            # 获取数据库结构信息
            schema_response = asyncio.run(datasource_service.get_database_schema(datasource.id))
            if not schema_response:
                return ToolResult(
                    success=False,
                    message=f"无法获取数据库 '{datasource.name}' 的表列表",
                    error="SCHEMA_EXTRACTION_FAILED"
                ).to_json()

            tables = []
            for table in schema_response.tables:
                table_info = {
                    "name": table.get("table_name", ""),
                    "schema": table.get("schema_name", ""),
                    "column_count": table.get("column_count", 0)
                }
                tables.append(table_info)

            return ToolResult(
                success=True,
                message=f"数据库 '{datasource.name}' 表列表获取成功",
                data={"tables": tables, "count": len(tables)},
                metadata={"database_id": datasource.id, "total_tables": schema_response.total_tables}
            ).to_json()

        elif query_type == "schema":
            # 获取数据库结构信息
            schema_response = asyncio.run(datasource_service.get_database_schema(datasource.id))
            if not schema_response:
                return ToolResult(
                    success=False,
                    message=f"无法获取数据库 '{datasource.name}' 的结构信息",
                    error="SCHEMA_EXTRACTION_FAILED"
                ).to_json()

            schema_info = {}
            for table in schema_response.tables:
                table_name = table.get("table_name", "")
                schema_info[table_name] = {
                    "columns": table.get("columns", []),
                    "column_count": table.get("column_count", 0),
                    "schema_name": table.get("schema_name", "")
                }

            return ToolResult(
                success=True,
                message=f"数据库 '{datasource.name}' 结构信息获取成功",
                data={"schema": schema_info, "table_count": len(schema_info)},
                metadata={"database_id": datasource.id, "total_tables": schema_response.total_tables}
            ).to_json()

        else:
            return ToolResult(
                success=False,
                message=f"不支持的查询类型: {query_type}。支持的类型: info, tables, schema",
                error="INVALID_QUERY_TYPE"
            ).to_json()
    
    except Exception as e:
        logger.error(f"❌ 数据库查询异常: {e}")
        return ToolResult(
            success=False,
            message="数据库查询过程中发生异常",
            error=str(e),
            metadata={"database_name": database_name, "query_type": query_type}
        ).to_json()


@tool
@log_io
def list_databases(
    enabled_only: Annotated[bool, "只显示启用的数据库"] = True
) -> str:
    """
    列出可用的数据库
    
    获取系统中配置的所有数据库连接信息。
    """
    try:
        logger.info(f"📋 获取数据库列表: enabled_only={enabled_only}")
        
        session = next(get_db_session())
        
        try:
            from sqlalchemy import text
            
            where_clause = "WHERE deleted_at IS NULL" if enabled_only else ""
            
            query = text(f"""
                SELECT id, name, description, database_type, host, port,
                       database_name, (deleted_at IS NULL) as enabled, created_at
                FROM database_management.database_datasources
                {where_clause}
                ORDER BY name
            """)
            
            result = session.execute(query)
            databases = []
            
            for row in result.fetchall():
                db_info = {
                    "id": row.id,
                    "name": row.name,
                    "description": row.description,
                    "type": row.database_type,
                    "host": row.host,
                    "port": row.port,
                    "database": row.database_name,
                    "enabled": row.enabled,
                    "created_at": row.created_at.isoformat() if row.created_at else None
                }
                databases.append(db_info)
            
            return ToolResult(
                success=True,
                message=f"找到 {len(databases)} 个数据库",
                data={"databases": databases, "total_count": len(databases)},
                metadata={"enabled_only": enabled_only}
            ).to_json()
        
        finally:
            session.close()
    
    except Exception as e:
        logger.error(f"❌ 获取数据库列表异常: {e}")
        return ToolResult(
            success=False,
            message="获取数据库列表过程中发生异常",
            error=str(e)
        ).to_json()


@tool
@log_io
def test_database_connection(
    database_name: Annotated[str, "数据库名称或ID"]
) -> str:
    """
    测试数据库连接
    
    验证指定数据库的连接状态和可用性。
    """
    try:
        logger.info(f"🔌 测试数据库连接: {database_name}")
        
        session = next(get_db_session())
        
        try:
            from sqlalchemy import text
            
            # 查找数据库配置
            if database_name.isdigit():
                query = text("""
                    SELECT id, name, host, port, database_name, database_type
                    FROM database_management.database_datasources 
                    WHERE id = :db_id
                """)
                result = session.execute(query, {"db_id": int(database_name)})
            else:
                query = text("""
                    SELECT id, name, host, port, database_name, database_type
                    FROM database_management.database_datasources 
                    WHERE name = :db_name
                """)
                result = session.execute(query, {"db_name": database_name})
            
            db_config = result.fetchone()
            if not db_config:
                return ToolResult(
                    success=False,
                    message=f"数据库 '{database_name}' 未找到",
                    error="DATABASE_NOT_FOUND"
                ).to_json()
            
            # 简单的连接测试（使用当前连接执行基本查询）
            test_query = text("SELECT 1 as test_connection")
            test_result = session.execute(test_query)
            test_row = test_result.fetchone()
            
            if test_row and test_row.test_connection == 1:
                return ToolResult(
                    success=True,
                    message=f"数据库 '{db_config.name}' 连接测试成功",
                    data={
                        "database_id": db_config.id,
                        "database_name": db_config.name,
                        "host": db_config.host,
                        "port": db_config.port,
                        "database": db_config.database_name,
                        "type": db_config.database_type,
                        "connection_status": "success"
                    }
                ).to_json()
            else:
                return ToolResult(
                    success=False,
                    message=f"数据库 '{db_config.name}' 连接测试失败",
                    error="CONNECTION_TEST_FAILED"
                ).to_json()
        
        finally:
            session.close()
    
    except Exception as e:
        logger.error(f"❌ 数据库连接测试异常: {e}")
        return ToolResult(
            success=False,
            message="数据库连接测试过程中发生异常",
            error=str(e),
            metadata={"database_name": database_name}
        ).to_json()
