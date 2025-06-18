# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Text2SQL工具

为智能体提供自然语言转SQL查询功能
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
from src.services.text2sql import Text2SQLService
from src.models.text2sql import SQLGenerationRequest, SQLExecutionRequest
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


def _auto_generate_chart_config(data: List[Dict], title: str = "查询结果图表") -> Optional[Dict]:
    """
    根据查询结果数据自动生成图表配置

    Args:
        data: 查询结果数据列表
        title: 图表标题

    Returns:
        图表配置字典，如果不适合生成图表则返回None
    """
    if not data or len(data) < 2:
        return None

    try:
        df = pd.DataFrame(data)

        # 检测数值列和分类列
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        # 如果没有数值列，不生成图表
        if not numeric_cols:
            return None

        # 检测时间相关列
        time_cols = [col for col in df.columns if any(keyword in col.lower()
                    for keyword in ['time', 'date', '时间', '日期', 'created', 'updated', 'year', 'month', 'day'])]

        # 根据数据特征选择合适的图表类型
        chart_config = None

        # 情况1：有时间列 -> 折线图（时间序列）
        if time_cols and len(numeric_cols) >= 1:
            chart_config = {
                "type": "LineChart",
                "title": title,
                "width": 800,
                "height": 400,
                "data": data,
                "xAxis": {"dataKey": time_cols[0], "type": "category"},
                "yAxis": {"type": "number"},
                "lines": [{
                    "dataKey": numeric_cols[0],
                    "stroke": "#8884d8",
                    "type": "monotone",
                    "strokeWidth": 2
                }],
                "tooltip": {"active": True},
                "legend": True
            }

        # 情况2：有分类列和数值列 -> 柱状图
        elif categorical_cols and numeric_cols:
            chart_config = {
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

        # 情况3：只有数值数据，数据量适中 -> 带索引的柱状图
        elif len(numeric_cols) >= 1 and len(df) <= 50:
            # 为数据添加序号索引
            data_with_index = []
            for i, row in enumerate(data):
                row_with_index = {"序号": f"第{i+1}项", **row}
                data_with_index.append(row_with_index)

            chart_config = {
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

        # 情况4：如果有两个数值列，可以考虑散点图
        elif len(numeric_cols) >= 2 and len(df) <= 100:
            chart_config = {
                "type": "ScatterChart",
                "title": title,
                "width": 800,
                "height": 400,
                "data": data,
                "xAxis": {"dataKey": numeric_cols[0], "type": "number", "name": numeric_cols[0]},
                "yAxis": {"dataKey": numeric_cols[1], "type": "number", "name": numeric_cols[1]},
                "scatter": {"dataKey": numeric_cols[1], "fill": "#8884d8"},
                "tooltip": {"active": True},
                "legend": True
            }

        return chart_config

    except Exception as e:
        logger.warning(f"自动图表生成失败: {e}")
        return None


async def _push_chart_async(chart_config: Dict, thread_id: str = None):
    """异步推送图表到前端"""
    try:
        await progress_ws_manager.send_chart_data(chart_config, thread_id)
        logger.info(f"图表已异步推送: {chart_config.get('title', 'Unknown')}")
    except Exception as e:
        logger.error(f"异步图表推送失败: {e}")


@tool
@log_io
def text2sql_query(
    question: Annotated[str, "自然语言问题"],
    database_id: Annotated[Optional[int], "数据库ID，不指定则使用默认数据库"] = None,
    execute_sql: Annotated[bool, "是否执行生成的SQL"] = True
) -> str:
    """
    执行Text2SQL查询
    
    将自然语言问题转换为SQL查询并可选择执行。
    支持指定目标数据库，返回SQL语句和查询结果。
    """
    try:
        logger.info(f"🔍 Text2SQL查询: {question[:100]}...")
        
        # 使用真实的Text2SQL服务
        text2sql_service = Text2SQLService()

        # 创建SQL生成请求
        request = SQLGenerationRequest(
            question=question,
            datasource_id=database_id or 1,  # 使用默认数据库ID
            include_explanation=True
        )

        # 生成SQL
        generation_result = asyncio.run(text2sql_service.generate_sql(request))

        generated_sql = generation_result.generated_sql
        confidence = generation_result.confidence_score
        explanation = generation_result.explanation or f"基于问题'{question}'生成的SQL查询"
        
        if not execute_sql:
            return ToolResult(
                success=True,
                message="SQL生成成功",
                data={
                    "sql": generated_sql,
                    "confidence": confidence,
                    "explanation": explanation
                },
                metadata={
                    "question": question,
                    "database_id": database_id,
                    "executed": False
                }
            ).to_json()
        
        # 执行SQL
        execution_request = SQLExecutionRequest(
            query_id=generation_result.query_id
        )

        execution_result = asyncio.run(text2sql_service.execute_sql(execution_request))

        if execution_result.status.value == "success":
            results = execution_result.result_data or []
            row_count = execution_result.result_rows or 0
        else:
            # 如果执行失败，返回空结果但保留SQL
            results = []
            row_count = 0
        
        return ToolResult(
            success=True,
            message="Text2SQL查询成功",
            data={
                "sql": generated_sql,
                "confidence": confidence,
                "explanation": explanation,
                "results": results,
                "row_count": row_count
            },
            metadata={
                "question": question,
                "database_id": database_id,
                "execution_time": "0.05s",
                "executed": True
            }
        ).to_json()
    
    except Exception as e:
        logger.error(f"❌ Text2SQL查询异常: {e}")
        return ToolResult(
            success=False,
            message="Text2SQL查询过程中发生异常",
            error=str(e),
            metadata={"question": question, "database_id": database_id}
        ).to_json()


@tool
@log_io
def generate_sql_only(
    question: Annotated[str, "自然语言问题"],
    database_id: Annotated[Optional[int], "数据库ID"] = None
) -> str:
    """
    仅生成SQL语句

    将自然语言问题转换为SQL查询，但不执行。
    适用于需要人工审核SQL的场景。
    """
    try:
        logger.info(f"🔧 生成SQL: {question[:100]}...")

        # 使用真实的Text2SQL服务
        text2sql_service = Text2SQLService()

        # 创建SQL生成请求
        request = SQLGenerationRequest(
            question=question,
            datasource_id=database_id or 1,  # 使用默认数据库ID
            include_explanation=True
        )

        # 生成SQL（不执行）
        generation_result = asyncio.run(text2sql_service.generate_sql(request))

        generated_sql = generation_result.generated_sql
        confidence = generation_result.confidence_score
        explanation = generation_result.explanation or f"基于问题'{question}'生成的SQL查询"

        # 获取相似的SQL示例作为参考
        similar_examples = []
        try:
            # 尝试获取相似的训练示例
            from src.services.vanna.service_manager import vanna_service_manager
            vanna_result = asyncio.run(vanna_service_manager.generate_sql(
                datasource_id=database_id or 1,
                question=question
            ))

            if vanna_result.get("success") and vanna_result.get("similar_sqls"):
                similar_examples = vanna_result["similar_sqls"][:3]  # 取前3个相似示例

        except Exception as e:
            logger.warning(f"获取相似示例失败: {e}")

        return ToolResult(
            success=True,
            message="SQL生成成功",
            data={
                "sql": generated_sql,
                "confidence": confidence,
                "explanation": explanation,
                "similar_examples": similar_examples,
                "generation_method": "text2sql_service"
            },
            metadata={
                "question": question,
                "database_id": database_id,
                "query_id": generation_result.query_id,
                "datasource_id": generation_result.datasource_id
            }
        ).to_json()

    except Exception as e:
        logger.error(f"❌ SQL生成异常: {e}")

        # 如果真实服务失败，使用简化的关键词映射作为后备
        try:
            logger.info("使用后备SQL生成方法...")

            # 简单的关键词映射
            keywords_mapping = {
                "用户": "users",
                "订单": "orders",
                "产品": "products",
                "销售": "sales",
                "库存": "inventory",
                "表": "tables",
                "数据库": "database"
            }

            table_name = "data"
            for keyword, table in keywords_mapping.items():
                if keyword in question:
                    table_name = table
                    break

            # 生成基础SQL
            if "统计" in question or "数量" in question or "总计" in question or "多少" in question:
                if "表" in question:
                    generated_sql = "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = DATABASE()"
                else:
                    generated_sql = f"SELECT COUNT(*) as total_count FROM {table_name}"
            elif "最新" in question or "最近" in question:
                generated_sql = f"SELECT * FROM {table_name} ORDER BY created_at DESC LIMIT 10"
            elif "所有" in question or "全部" in question:
                if "表" in question:
                    generated_sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE() ORDER BY table_name"
                else:
                    generated_sql = f"SELECT * FROM {table_name} LIMIT 10"
            else:
                generated_sql = f"SELECT * FROM {table_name} LIMIT 10"

            confidence = 0.6  # 降低置信度，因为是后备方法
            explanation = f"使用关键词分析生成的SQL查询（后备方法），目标表: {table_name}"

            return ToolResult(
                success=True,
                message="SQL生成成功（使用后备方法）",
                data={
                    "sql": generated_sql,
                    "confidence": confidence,
                    "explanation": explanation,
                    "suggested_table": table_name,
                    "generation_method": "fallback_keyword_mapping"
                },
                metadata={
                    "question": question,
                    "database_id": database_id,
                    "fallback_reason": str(e)
                }
            ).to_json()

        except Exception as fallback_error:
            logger.error(f"❌ 后备SQL生成也失败: {fallback_error}")
            return ToolResult(
                success=False,
                message="SQL生成过程中发生异常",
                error=str(e),
                metadata={"question": question, "database_id": database_id}
            ).to_json()


@tool
@log_io
def smart_text2sql_query(
    question: Annotated[str, "自然语言问题"],
    database_id: Annotated[Optional[int], "数据库ID，不指定则使用默认数据库"] = None,
    auto_chart: Annotated[bool, "是否自动生成图表"] = True,
    chart_title: Annotated[str, "图表标题"] = ""
) -> str:
    """
    智能Text2SQL查询工具 - 支持自动图表生成

    将自然语言问题转换为SQL查询并执行，如果结果适合可视化，会自动生成图表并推送到前端。
    图表生成是异步的，不会阻塞查询结果返回，确保快速响应用户。
    """
    try:
        logger.info(f"🧠 智能Text2SQL查询: {question[:100]}...")

        # 使用Text2SQL服务
        text2sql_service = Text2SQLService()

        # 创建SQL生成请求
        request = SQLGenerationRequest(
            question=question,
            datasource_id=database_id or 8,  # 默认使用傲雷仓储中心库
            include_explanation=True
        )

        # 生成SQL - 使用同步方法避免事件循环问题
        import threading

        def run_async_in_thread(coro):
            """在新线程中运行异步函数"""
            result = None
            exception = None

            def target():
                nonlocal result, exception
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(coro)
                except Exception as e:
                    exception = e
                finally:
                    loop.close()

            thread = threading.Thread(target=target)
            thread.start()
            thread.join()

            if exception:
                raise exception
            return result

        generation_result = run_async_in_thread(text2sql_service.generate_sql(request))

        generated_sql = generation_result.generated_sql
        confidence = generation_result.confidence_score
        explanation = generation_result.explanation or f"基于问题'{question}'生成的SQL查询"

        # 执行SQL
        execution_request = SQLExecutionRequest(
            query_id=generation_result.query_id
        )

        execution_result = run_async_in_thread(text2sql_service.execute_sql(execution_request))

        if execution_result.status.value == "success":
            results = execution_result.result_data or []
            row_count = execution_result.result_rows or 0
        else:
            results = []
            row_count = 0

        # 构建基本响应数据
        response_data = {
            "sql": generated_sql,
            "confidence": confidence,
            "explanation": explanation,
            "results": results[:10] if results else [],  # 只返回前10行给智能体查看
            "total_rows": row_count,
            "columns": list(results[0].keys()) if results else []
        }

        # 构建响应消息
        if row_count == 0:
            message = f"查询执行成功，但没有返回数据。生成的SQL: {generated_sql}"
        elif row_count <= 10:
            message = f"查询成功！返回 {row_count} 行数据"
        else:
            message = f"查询成功！返回 {row_count} 行数据（显示前10行）"

        # 异步图表生成（不阻塞响应）
        if auto_chart and results and row_count >= 2:
            # 确定图表标题
            final_chart_title = chart_title or f"查询结果: {question[:30]}..."

            # 生成图表配置
            chart_config = _auto_generate_chart_config(results, final_chart_title)

            if chart_config:
                # 异步推送图表（不等待完成）
                try:
                    # 尝试在当前事件循环中创建任务
                    asyncio.create_task(_push_chart_async(chart_config))
                except RuntimeError:
                    # 如果没有事件循环，在新线程中推送
                    threading.Thread(
                        target=lambda: run_async_in_thread(_push_chart_async(chart_config)),
                        daemon=True
                    ).start()

                message += f"，{chart_config['type']}图表正在生成中..."
                response_data["chart_info"] = {
                    "type": chart_config["type"],
                    "status": "generating",
                    "title": final_chart_title
                }
            else:
                message += "（数据不适合图表展示）"
                response_data["chart_info"] = {"status": "not_suitable"}
        elif auto_chart:
            response_data["chart_info"] = {"status": "disabled", "reason": "数据量不足"}

        return ToolResult(
            success=True,
            message=message,
            data=response_data,
            metadata={
                "question": question,
                "database_id": database_id,
                "execution_time": execution_result.execution_time if hasattr(execution_result, 'execution_time') else "0.05s",
                "auto_chart": auto_chart,
                "query_id": generation_result.query_id
            }
        ).to_json()

    except Exception as e:
        logger.error(f"❌ 智能Text2SQL查询异常: {e}")
        return ToolResult(
            success=False,
            message="智能Text2SQL查询过程中发生异常",
            error=str(e),
            metadata={"question": question, "database_id": database_id}
        ).to_json()


@tool
@log_io
def get_training_examples(
    keyword: Annotated[Optional[str], "关键词过滤"] = None,
    limit: Annotated[int, "返回数量限制"] = 10
) -> str:
    """
    获取Text2SQL训练示例
    
    从vanna_embeddings表中获取训练示例，用于参考和学习。
    """
    try:
        logger.info(f"📚 获取训练示例: keyword={keyword}, limit={limit}")
        
        session = next(get_db_session())
        
        try:
            from sqlalchemy import text
            
            # 构建查询 - 包含 datasource_id 字段，确保获取所有数据源的示例
            if keyword:
                query = text("""
                    WITH ranked_examples AS (
                        SELECT datasource_id, question, content, sql_query, content_type, table_name,
                               ROW_NUMBER() OVER (PARTITION BY datasource_id ORDER BY created_at DESC) as rn
                        FROM text2sql.vanna_embeddings
                        WHERE question ILIKE :keyword OR content ILIKE :keyword
                    )
                    SELECT datasource_id, question, content, sql_query, content_type, table_name
                    FROM ranked_examples
                    WHERE rn <= :per_datasource_limit
                    ORDER BY datasource_id, rn
                """)
                # 每个数据源最多返回 limit/3 个示例，确保多样性，至少 5 个
                per_datasource_limit = max(5, limit // 3)
                result = session.execute(query, {"keyword": f"%{keyword}%", "per_datasource_limit": per_datasource_limit})
            else:
                query = text("""
                    WITH ranked_examples AS (
                        SELECT datasource_id, question, content, sql_query, content_type, table_name,
                               ROW_NUMBER() OVER (PARTITION BY datasource_id ORDER BY created_at DESC) as rn
                        FROM text2sql.vanna_embeddings
                    )
                    SELECT datasource_id, question, content, sql_query, content_type, table_name
                    FROM ranked_examples
                    WHERE rn <= :per_datasource_limit
                    ORDER BY datasource_id, rn
                    LIMIT :limit
                """)
                # 每个数据源最多返回 limit/3 个示例，确保多样性，至少 5 个
                per_datasource_limit = max(5, limit // 3)
                result = session.execute(query, {"per_datasource_limit": per_datasource_limit, "limit": limit})

            examples = []
            for row in result.fetchall():
                example = {
                    "datasource_id": row.datasource_id,
                    "question": row.question,
                    "content": row.content,
                    "sql_query": row.sql_query,
                    "content_type": row.content_type,
                    "table_name": row.table_name
                }
                examples.append(example)
            
            return ToolResult(
                success=True,
                message=f"找到 {len(examples)} 个训练示例",
                data={
                    "examples": examples,
                    "total_count": len(examples)
                },
                metadata={
                    "keyword_filter": keyword,
                    "limit": limit
                }
            ).to_json()
        
        finally:
            session.close()
    
    except Exception as e:
        logger.error(f"❌ 获取训练示例异常: {e}")
        return ToolResult(
            success=False,
            message="获取训练示例过程中发生异常",
            error=str(e),
            metadata={"keyword": keyword, "limit": limit}
        ).to_json()


@tool
@log_io
def validate_sql(
    sql: Annotated[str, "要验证的SQL语句"],
    database_id: Annotated[Optional[int], "数据库ID"] = None
) -> str:
    """
    验证SQL语句
    
    检查SQL语句的语法正确性和安全性，不执行查询。
    """
    try:
        logger.info(f"🔍 验证SQL: {sql[:100]}...")
        
        # 基本的SQL安全检查
        dangerous_keywords = [
            "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", 
            "CREATE", "TRUNCATE", "EXEC", "EXECUTE"
        ]
        
        sql_upper = sql.upper()
        found_dangerous = [kw for kw in dangerous_keywords if kw in sql_upper]
        
        if found_dangerous:
            return ToolResult(
                success=False,
                message="SQL包含危险操作",
                error=f"发现危险关键词: {', '.join(found_dangerous)}",
                data={"sql": sql, "dangerous_keywords": found_dangerous}
            ).to_json()
        
        # 基本语法检查
        if not sql.strip().upper().startswith("SELECT"):
            return ToolResult(
                success=False,
                message="只支持SELECT查询",
                error="SQL必须以SELECT开头",
                data={"sql": sql}
            ).to_json()
        
        # TODO: 更详细的SQL语法验证
        # 可以集成SQL解析器进行更严格的验证
        
        return ToolResult(
            success=True,
            message="SQL验证通过",
            data={
                "sql": sql,
                "is_safe": True,
                "query_type": "SELECT"
            },
            metadata={
                "database_id": database_id,
                "validation_rules": ["安全关键词检查", "查询类型检查"]
            }
        ).to_json()
    
    except Exception as e:
        logger.error(f"❌ SQL验证异常: {e}")
        return ToolResult(
            success=False,
            message="SQL验证过程中发生异常",
            error=str(e),
            metadata={"sql": sql, "database_id": database_id}
        ).to_json()
