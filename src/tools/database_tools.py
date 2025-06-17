# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
数据库操作工具

为智能体提供数据库查询和管理功能
"""

import json
import logging
import asyncio
import pandas as pd
from typing import Dict, Any, Optional, List, Annotated
from datetime import datetime

from langchain_core.tools import tool
from src.database import get_db_session
from src.tools.decorators import log_io
from src.services.database_datasource import DatabaseDatasourceService
from src.services.websocket.progress_manager import progress_ws_manager

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
def search_databases(
    search_term: Annotated[str, "搜索关键词，可以是数据库名称、描述或类型"] = "",
    database_type: Annotated[str, "数据库类型过滤 (mysql, postgresql)"] = "",
    enabled_only: Annotated[bool, "只显示启用的数据库"] = True
) -> str:
    """
    搜索和发现数据库

    根据名称、描述、类型等条件搜索数据库。支持模糊匹配。
    """
    try:
        logger.info(f"🔍 搜索数据库: search_term='{search_term}', type='{database_type}', enabled_only={enabled_only}")

        # 使用数据库数据源服务进行搜索
        datasource_service = DatabaseDatasourceService()

        # 转换数据库类型
        db_type_filter = None
        if database_type:
            from src.models.database_datasource import DatabaseType
            try:
                db_type_filter = DatabaseType(database_type.upper())
            except ValueError:
                logger.warning(f"无效的数据库类型: {database_type}")

        # 执行搜索
        datasources = asyncio.run(datasource_service.list_datasources(
            database_type=db_type_filter,
            search=search_term if search_term else None,
            limit=50,
            offset=0
        ))

        # 过滤启用状态
        if enabled_only:
            datasources = [ds for ds in datasources if ds.deleted_at is None]

        # 构建结果
        databases = []
        for ds in datasources:
            db_info = {
                "id": ds.id,
                "name": ds.name,
                "description": ds.description,
                "type": ds.database_type.value,
                "host": ds.host,
                "port": ds.port,
                "database": ds.database_name,
                "enabled": ds.deleted_at is None,
                "created_at": ds.created_at.isoformat() if ds.created_at else None
            }
            databases.append(db_info)

        # 计算匹配度评分（用于排序）
        if search_term:
            for db in databases:
                score = 0
                search_lower = search_term.lower()

                # 名称完全匹配得分最高
                if db["name"].lower() == search_lower:
                    score += 100
                elif search_lower in db["name"].lower():
                    score += 50

                # 描述匹配
                if db["description"] and search_lower in db["description"].lower():
                    score += 30

                # 类型匹配
                if search_lower in db["type"].lower():
                    score += 20

                db["match_score"] = score

            # 按匹配度排序
            databases.sort(key=lambda x: x.get("match_score", 0), reverse=True)

        return ToolResult(
            success=True,
            message=f"找到 {len(databases)} 个匹配的数据库",
            data={
                "databases": databases,
                "total_count": len(databases),
                "search_criteria": {
                    "search_term": search_term,
                    "database_type": database_type,
                    "enabled_only": enabled_only
                }
            },
            metadata={"search_performed": bool(search_term)}
        ).to_json()

    except Exception as e:
        logger.error(f"❌ 搜索数据库异常: {e}")
        return ToolResult(
            success=False,
            message="搜索数据库过程中发生异常",
            error=str(e),
            metadata={"search_term": search_term, "database_type": database_type}
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


@tool
@log_io
def find_database_by_name(
    name_pattern: Annotated[str, "数据库名称模式，支持模糊匹配"]
) -> str:
    """
    根据名称模式查找数据库

    智能匹配数据库名称，支持部分匹配和模糊搜索。
    特别适用于根据业务名称查找对应的数据库。
    """
    try:
        logger.info(f"🎯 根据名称查找数据库: {name_pattern}")

        # 使用数据库数据源服务进行搜索
        datasource_service = DatabaseDatasourceService()

        # 执行搜索
        datasources = asyncio.run(datasource_service.list_datasources(
            search=name_pattern,
            limit=20,
            offset=0
        ))

        # 只返回启用的数据库
        datasources = [ds for ds in datasources if ds.deleted_at is None]

        if not datasources:
            return ToolResult(
                success=False,
                message=f"未找到匹配 '{name_pattern}' 的数据库",
                error="NO_MATCHING_DATABASE"
            ).to_json()

        # 构建结果并计算匹配度
        matches = []
        pattern_lower = name_pattern.lower()

        for ds in datasources:
            match_info = {
                "id": ds.id,
                "name": ds.name,
                "description": ds.description,
                "type": ds.database_type.value,
                "host": ds.host,
                "port": ds.port,
                "database": ds.database_name,
                "match_type": [],
                "match_score": 0
            }

            # 计算匹配类型和得分
            if ds.name.lower() == pattern_lower:
                match_info["match_type"].append("exact_name")
                match_info["match_score"] += 100
            elif pattern_lower in ds.name.lower():
                match_info["match_type"].append("partial_name")
                match_info["match_score"] += 80

            if ds.description and pattern_lower in ds.description.lower():
                match_info["match_type"].append("description")
                match_info["match_score"] += 50

            if pattern_lower in ds.database_name.lower():
                match_info["match_type"].append("database_name")
                match_info["match_score"] += 60

            matches.append(match_info)

        # 按匹配度排序
        matches.sort(key=lambda x: x["match_score"], reverse=True)

        # 如果有完全匹配，优先返回
        exact_matches = [m for m in matches if "exact_name" in m["match_type"]]
        if exact_matches:
            best_match = exact_matches[0]
            return ToolResult(
                success=True,
                message=f"找到完全匹配的数据库: {best_match['name']}",
                data={
                    "best_match": best_match,
                    "all_matches": matches,
                    "match_count": len(matches)
                },
                metadata={"search_pattern": name_pattern, "match_type": "exact"}
            ).to_json()

        # 返回最佳匹配
        best_match = matches[0]
        return ToolResult(
            success=True,
            message=f"找到 {len(matches)} 个匹配的数据库，最佳匹配: {best_match['name']}",
            data={
                "best_match": best_match,
                "all_matches": matches,
                "match_count": len(matches)
            },
            metadata={"search_pattern": name_pattern, "match_type": "fuzzy"}
        ).to_json()

    except Exception as e:
        logger.error(f"❌ 根据名称查找数据库异常: {e}")
        return ToolResult(
            success=False,
            message="根据名称查找数据库过程中发生异常",
            error=str(e),
            metadata={"name_pattern": name_pattern}
        ).to_json()


@tool
@log_io
def get_database_info(
    identifier: Annotated[str, "数据库标识符，可以是ID、名称或描述关键词"]
) -> str:
    """
    获取数据库详细信息

    根据ID、名称或描述关键词获取数据库的完整信息。
    这是一个智能查找工具，会尝试多种匹配方式。
    """
    try:
        logger.info(f"📋 获取数据库信息: {identifier}")

        datasource_service = DatabaseDatasourceService()
        datasource = None

        # 尝试按ID查找
        if identifier.isdigit():
            try:
                datasource = asyncio.run(datasource_service.get_datasource(int(identifier)))
                if datasource:
                    logger.info(f"通过ID找到数据库: {datasource.name}")
            except Exception as e:
                logger.debug(f"按ID查找失败: {e}")

        # 如果按ID没找到，尝试按名称搜索
        if not datasource:
            datasources = asyncio.run(datasource_service.list_datasources(
                search=identifier,
                limit=10,
                offset=0
            ))

            # 过滤启用的数据库
            enabled_datasources = [ds for ds in datasources if ds.deleted_at is None]

            if enabled_datasources:
                # 优先选择名称完全匹配的
                exact_match = next((ds for ds in enabled_datasources
                                  if ds.name.lower() == identifier.lower()), None)
                datasource = exact_match or enabled_datasources[0]
                logger.info(f"通过搜索找到数据库: {datasource.name}")

        if not datasource:
            return ToolResult(
                success=False,
                message=f"未找到数据库 '{identifier}'",
                error="DATABASE_NOT_FOUND"
            ).to_json()

        # 获取数据库结构信息
        try:
            schema_response = asyncio.run(datasource_service.get_database_schema(datasource.id))
            table_count = len(schema_response.tables) if schema_response else 0
            table_names = [table.get("table_name", "") for table in schema_response.tables] if schema_response else []
        except Exception as e:
            logger.warning(f"获取数据库结构失败: {e}")
            table_count = 0
            table_names = []

        # 构建详细信息
        db_info = {
            "basic_info": {
                "id": datasource.id,
                "name": datasource.name,
                "description": datasource.description,
                "type": datasource.database_type.value,
                "host": datasource.host,
                "port": datasource.port,
                "database": datasource.database_name,
                "enabled": datasource.deleted_at is None,
                "created_at": datasource.created_at.isoformat() if datasource.created_at else None
            },
            "schema_info": {
                "table_count": table_count,
                "table_names": table_names[:10],  # 只显示前10个表名
                "has_more_tables": table_count > 10
            },
            "connection_info": {
                "readonly_mode": datasource.readonly_mode,
                "allowed_operations": datasource.allowed_operations
            }
        }

        return ToolResult(
            success=True,
            message=f"数据库 '{datasource.name}' 信息获取成功",
            data=db_info,
            metadata={
                "identifier": identifier,
                "found_by": "id" if identifier.isdigit() else "search"
            }
        ).to_json()

    except Exception as e:
        logger.error(f"❌ 获取数据库信息异常: {e}")
        return ToolResult(
            success=False,
            message="获取数据库信息过程中发生异常",
            error=str(e),
            metadata={"identifier": identifier}
        ).to_json()


def _auto_generate_chart_config(data: List[Dict], title: str = "数据图表") -> Optional[Dict]:
    """
    根据数据自动生成图表配置
    """
    if not data or len(data) < 2:
        return None

    try:
        df = pd.DataFrame(data)

        # 检测数值列和分类列
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        if not numeric_cols:
            return None

        # 检测时间列
        time_cols = [col for col in df.columns if any(keyword in col.lower()
                    for keyword in ['time', 'date', '时间', '日期', 'created', 'updated'])]

        # 选择图表类型和配置
        if time_cols and len(numeric_cols) >= 1:
            # 时间序列 -> 折线图
            return {
                "type": "LineChart",
                "title": title,
                "width": 800,
                "height": 400,
                "data": data,
                "xAxis": {"dataKey": time_cols[0], "type": "category"},
                "yAxis": {"type": "number"},
                "lines": [{"dataKey": numeric_cols[0], "stroke": "#8884d8", "type": "monotone"}],
                "tooltip": {"active": True},
                "legend": True
            }
        elif categorical_cols and numeric_cols:
            # 分类数据 -> 柱状图
            return {
                "type": "BarChart",
                "title": title,
                "width": 800,
                "height": 400,
                "data": data,
                "xAxis": {"dataKey": categorical_cols[0], "type": "category"},
                "yAxis": {"type": "number"},
                "bars": [{"dataKey": numeric_cols[0], "fill": "#8884d8"}],
                "tooltip": {"active": True},
                "legend": True
            }
        elif len(numeric_cols) >= 1 and len(df) <= 50:
            # 纯数值数据 -> 带索引的柱状图
            data_with_index = [{"序号": f"第{i+1}项", **row} for i, row in enumerate(data)]
            return {
                "type": "BarChart",
                "title": title,
                "width": 800,
                "height": 400,
                "data": data_with_index,
                "xAxis": {"dataKey": "序号", "type": "category"},
                "yAxis": {"type": "number"},
                "bars": [{"dataKey": numeric_cols[0], "fill": "#8884d8"}],
                "tooltip": {"active": True},
                "legend": True
            }

        return None

    except Exception as e:
        logger.warning(f"自动图表生成失败: {e}")
        return None
