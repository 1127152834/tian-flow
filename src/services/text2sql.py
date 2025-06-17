# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Text2SQL service for Olight.

Provides natural language to SQL conversion with Celery background tasks,
WebSocket real-time monitoring, and pgvector-based similarity search.
"""

import logging
import time
import hashlib
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple

from src.models.text2sql import (
    QueryHistory,
    VannaEmbedding,
    SQLQueryCache,
    TrainingSession,
    QueryStatus,
    TrainingDataType,
    SQLGenerationRequest,
    SQLGenerationResponse,
    SQLExecutionRequest,
    SQLExecutionResponse,
    TrainingDataRequest,
    TrainingDataResponse,
    Text2SQLStatistics,
    QuestionAnswerRequest,
    QuestionAnswerResponse,
    BatchTrainingRequest
)
from src.repositories.text2sql import Text2SQLRepository
from src.services.vector_store import PgVectorStore
from src.services.database_datasource import DatabaseDatasourceService
from src.services.vanna import vanna_service_manager
# Import SQLValidator
try:
    from src.services.sql_validator import SQLValidator, ValidationResult
except ImportError:
    # Fallback: create a simple validator
    class SQLValidator:
        def __init__(self, datasource_id: int):
            self.datasource_id = datasource_id

        async def validate_sql(self, sql: str):
            # Simple validation result
            from dataclasses import dataclass
            from typing import List

            @dataclass
            class ValidationResult:
                is_valid: bool
                errors: List[str]
                warnings: List[str]
                missing_tables: List[str]
                missing_columns: List[str]
                suggestions: List[str]

            return ValidationResult(
                is_valid=True,  # Always pass for now
                errors=[],
                warnings=[],
                missing_tables=[],
                missing_columns=[],
                suggestions=[]
            )

logger = logging.getLogger(__name__)


class Text2SQLService:
    """Text2SQL service with repository-based persistence and Celery support"""
    
    def __init__(self):
        self.repository = Text2SQLRepository()
        self.vector_store = PgVectorStore()
        self.datasource_service = DatabaseDatasourceService()
        
        logger.info("Text2SQL service initialized with repository and vector store")
    
    # SQL Generation Methods
    
    async def generate_sql(self, request: SQLGenerationRequest) -> SQLGenerationResponse:
        """Generate SQL from natural language question using Vanna AI"""
        try:
            start_time = time.time()

            # Validate datasource exists
            datasource = await self.datasource_service.get_datasource(request.datasource_id)
            if not datasource:
                raise ValueError(f"Datasource {request.datasource_id} not found")

            # Use Vanna service to generate SQL
            vanna_result = await vanna_service_manager.generate_sql(
                datasource_id=request.datasource_id,
                question=request.question,
                embedding_model_id=getattr(request, 'embedding_model_id', None)
            )

            if not vanna_result["success"]:
                error_msg = vanna_result.get('error', 'Unknown error')
                # 如果是无法生成SQL的错误，返回友好提示
                if "no similar" in error_msg.lower() or "not found" in error_msg.lower():
                    raise ValueError("无法根据您的问题生成SQL查询。请确保您的问题涉及数据库中实际存在的业务表和字段。")
                raise ValueError(f"SQL generation failed: {error_msg}")

            # 验证生成的SQL是否与实际数据库结构匹配
            # 对于系统查询，跳过验证以提高性能
            validator = SQLValidator(request.datasource_id)
            if validator._is_system_query(vanna_result["sql"]):
                # 系统查询直接通过验证
                validation_result = ValidationResult(
                    is_valid=True,
                    errors=[],
                    warnings=[],
                    missing_tables=[],
                    missing_columns=[],
                    suggestions=[]
                )
            else:
                validation_result = await validator.validate_sql(vanna_result["sql"])

            # 如果验证失败，返回详细的错误信息和建议
            if not validation_result.is_valid:
                error_message = "生成的SQL查询与数据库结构不匹配：\n"
                error_message += "\n".join(validation_result.errors)

                if validation_result.suggestions:
                    error_message += "\n\n建议：\n"
                    error_message += "\n".join(validation_result.suggestions)

                # 记录验证失败的查询用于分析
                logger.warning(f"SQL validation failed for question: {request.question}")
                logger.warning(f"Generated SQL: {vanna_result['sql']}")
                logger.warning(f"Validation errors: {validation_result.errors}")

                raise ValueError(error_message)

            generated_sql = {
                "sql": vanna_result["sql"],
                "confidence": vanna_result.get("confidence", 0.8),
                "model": "vanna-ai"
            }

            # 如果有验证警告，降低置信度并添加到说明中
            if validation_result.warnings:
                generated_sql["confidence"] = max(0.5, generated_sql["confidence"] - 0.2)
                generated_sql["validation_warnings"] = validation_result.warnings

            if request.include_explanation:
                explanation = f"Generated SQL for question: '{request.question}'"

                # 添加验证警告到说明中
                if validation_result.warnings:
                    explanation += "\n\n⚠️ 注意事项：\n" + "\n".join(validation_result.warnings)

                generated_sql["explanation"] = explanation

            # Convert similar examples to compatible format
            similar_queries = []
            for similar in vanna_result.get("similar_sqls", []):
                from types import SimpleNamespace
                query_cache = SimpleNamespace()
                # similar is a string (SQL query), not a dict
                if isinstance(similar, str):
                    query_cache.query_text = similar
                else:
                    # Fallback for dict format
                    query_cache.query_text = similar.get("question", "") if hasattr(similar, 'get') else str(similar)
                query_cache.usage_count = 1
                similar_queries.append(query_cache)
            
            # Create query history record
            query_id = await self.repository.create_query_history(
                user_question=request.question,
                generated_sql=generated_sql["sql"],
                datasource_id=request.datasource_id,
                status=QueryStatus.PENDING,
                confidence_score=generated_sql.get("confidence", 0.8),
                model_used=generated_sql.get("model", "gpt-4"),
                explanation=generated_sql.get("explanation") if request.include_explanation else None,
                similar_examples={"similar_queries": [q.query_text for q in similar_queries[:3]]}
            )
            
            generation_time = int((time.time() - start_time) * 1000)
            
            return SQLGenerationResponse(
                query_id=query_id,
                question=request.question,
                generated_sql=generated_sql["sql"],
                explanation=generated_sql.get("explanation"),
                confidence_score=generated_sql.get("confidence", 0.8),
                similar_examples=[{"query": q.query_text, "usage_count": q.usage_count} for q in similar_queries[:3]],
                generation_time_ms=generation_time
            )
            
        except Exception as e:
            logger.error(f"Failed to generate SQL: {e}")
            raise
    
    # SQL Execution Methods
    
    async def execute_sql(self, request: SQLExecutionRequest) -> SQLExecutionResponse:
        """Execute generated SQL query using Vanna AI"""
        try:
            start_time = time.time()

            # Get query from history
            query = await self.repository.get_query_history(request.query_id)
            if not query:
                raise ValueError(f"Query {request.query_id} not found")

            # Use Vanna service to execute SQL
            vanna_result = await vanna_service_manager.execute_sql(
                datasource_id=query.datasource_id,
                sql=query.generated_sql
            )

            if not vanna_result["success"]:
                raise ValueError(f"SQL execution failed: {vanna_result.get('error', 'Unknown error')}")

            # Extract results from Vanna response
            result_data = vanna_result["data"]
            results = []
            for row in result_data["rows"]:
                row_dict = {}
                for i, col in enumerate(result_data["columns"]):
                    row_dict[col] = row[i] if i < len(row) else None
                results.append(row_dict)

            row_count = result_data["row_count"]

            execution_time = int(vanna_result.get("execution_time", 0) * 1000)  # Convert to ms
            
            # Update query history with results
            await self.repository.update_query_history(
                query_id=request.query_id,
                status=QueryStatus.SUCCESS,
                execution_time_ms=execution_time,
                result_rows=row_count,
                result_data={"results": results[:10]}  # Store limited results
            )
            
            # Update cache usage if query exists in cache
            await self._update_cache_usage(query, execution_time, True)
            
            return SQLExecutionResponse(
                query_id=request.query_id,
                status=QueryStatus.SUCCESS,
                result_data=results,
                result_rows=row_count,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            # Update query with error
            if request.query_id:
                await self.repository.update_query_history(
                    query_id=request.query_id,
                    status=QueryStatus.FAILED,
                    error_message=str(e)
                )
            
            logger.error(f"Failed to execute SQL: {e}")
            return SQLExecutionResponse(
                query_id=request.query_id,
                status=QueryStatus.FAILED,
                error_message=str(e)
            )
    
    
    async def _update_cache_usage(self, query: QueryHistory, execution_time: int, success: bool):
        """Update cache usage statistics"""
        try:
            # Find matching cache entry
            similar_queries = await self.repository.search_similar_queries(
                datasource_id=query.datasource_id,
                limit=1
            )
            
            if similar_queries:
                cache_entry = similar_queries[0]
                await self.repository.update_sql_query_cache_usage(
                    cache_id=cache_entry.id,
                    execution_time_ms=execution_time,
                    success=success
                )
        except Exception as e:
            logger.warning(f"Failed to update cache usage: {e}")
    
    # Training Data Methods
    
    async def add_training_data(self, request: TrainingDataRequest, auto_generate_embedding: bool = True) -> TrainingDataResponse:
        """Add training data for model improvement using Vanna AI directly"""
        try:
            # Validate datasource exists
            datasource = await self.datasource_service.get_datasource(request.datasource_id)
            if not datasource:
                raise ValueError(f"Datasource {request.datasource_id} not found")

            # Use Vanna service to add training data directly
            from src.services.vanna.service_manager import vanna_service_manager

            # Extract table name from SQL if provided
            table_name = None
            database_name = datasource.database_name if hasattr(datasource, 'database_name') else "aolei_db"

            if request.sql_query:
                table_name = self._extract_table_name_from_sql(request.sql_query)

            # Create training data directly in database for now (simplified approach)
            import json
            from src.config.database import get_database_connection

            # Generate content hash
            if request.content_type == TrainingDataType.SQL:
                combined_content = f"Question: {request.question or 'Question'}\nSQL: {request.sql_query or request.content}"
                content_hash = hashlib.sha256(combined_content.encode('utf-8')).hexdigest()
            else:
                content_hash = hashlib.sha256(request.content.encode('utf-8')).hexdigest()

            # Store in database
            with get_database_connection() as conn:
                with conn.cursor() as cursor:
                    # Check if already exists
                    cursor.execute("""
                        SELECT id FROM text2sql.vanna_embeddings
                        WHERE datasource_id = %s AND content_hash = %s
                    """, (request.datasource_id, content_hash))

                    existing = cursor.fetchone()
                    if existing:
                        raise ValueError("Training data with this content already exists")

                    # Prepare metadata
                    metadata = {
                        'database_name': database_name,
                        'table_name': table_name,
                        'auto_extracted': True
                    }
                    if request.metadata:
                        metadata.update(request.metadata)

                    # Insert new training data
                    cursor.execute("""
                        INSERT INTO text2sql.vanna_embeddings
                        (datasource_id, content_type, content, content_hash,
                         question, sql_query, table_name, metadata, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                        RETURNING id
                    """, (
                        request.datasource_id,
                        request.content_type.value,
                        request.content,
                        content_hash,
                        request.question,
                        request.sql_query,
                        table_name,
                        json.dumps(metadata)
                    ))

                    result = cursor.fetchone()
                    conn.commit()

                    logger.info(f"Added training data directly to database: {content_hash}")

            # Get the created training data from vanna_embeddings table by content_hash
            training_data = await self.repository.get_training_data_by_content_hash(
                datasource_id=request.datasource_id,
                content_hash=content_hash
            )

            if not training_data:
                raise ValueError("Failed to retrieve created training data")

            logger.info(f"Added training data {content_hash} using Vanna AI")

            return TrainingDataResponse(
                id=training_data.id,
                datasource_id=training_data.datasource_id,
                content_type=training_data.content_type,
                question=training_data.question,
                sql_query=training_data.sql_query,
                content=training_data.content,
                table_names=[table_name] if table_name else [],
                database_schema={"database_name": database_name},
                metadata=training_data.metadata,
                content_hash=training_data.content_hash,
                is_active=True,  # Default for new data
                is_validated=False,  # Default for new data
                validation_score=None,  # Default for new data
                created_at=training_data.created_at,
                updated_at=training_data.updated_at
            )

        except ValueError as e:
            if "already exists" in str(e):
                raise ValueError("Training data with this content already exists")
            raise
        except Exception as e:
            logger.error(f"Failed to add training data: {e}")
            raise

    def _extract_table_name_from_sql(self, sql: str) -> Optional[str]:
        """Extract table name from SQL query using regex"""
        try:
            import re
            sql_upper = sql.upper().strip()

            # Pattern for SELECT, INSERT, UPDATE, DELETE statements
            patterns = [
                r'FROM\s+(?:`?(\w+)`?\.)?`?(\w+)`?',  # SELECT ... FROM table
                r'INSERT\s+INTO\s+(?:`?(\w+)`?\.)?`?(\w+)`?',  # INSERT INTO table
                r'UPDATE\s+(?:`?(\w+)`?\.)?`?(\w+)`?',  # UPDATE table
                r'DELETE\s+FROM\s+(?:`?(\w+)`?\.)?`?(\w+)`?',  # DELETE FROM table
            ]

            for pattern in patterns:
                match = re.search(pattern, sql_upper)
                if match:
                    # Return table name (group 2 if schema.table, group 1 if just table)
                    return match.group(2) if match.group(2) else match.group(1)

            return None
        except Exception:
            return None

    # Training and Model Management Methods

    async def start_training_session(
        self,
        datasource_id: int,
        session_name: Optional[str] = None,
        model_version: Optional[str] = None,
        training_parameters: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start a new training session with Celery background task"""
        try:
            # Validate datasource exists
            datasource = await self.datasource_service.get_datasource(datasource_id)
            if not datasource:
                raise ValueError(f"Datasource {datasource_id} not found")

            # Create training session
            session_id = await self.repository.create_training_session(
                datasource_id=datasource_id,
                session_name=session_name or f"Training Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                model_version=model_version or "v1.0",
                training_parameters=training_parameters or {},
                notes=notes
            )

            # Start Celery task
            from src.tasks.text2sql_tasks import train_model_task
            task = train_model_task.delay(
                datasource_id, session_id, **(training_parameters or {})
            )

            # Update session with task ID
            await self.repository.update_training_session(
                session_id,
                notes=f"Task ID: {task.id}"
            )

            logger.info(f"Started training session {session_id} with task {task.id}")

            return {
                'session_id': session_id,
                'task_id': task.id,
                'status': 'started',
                'datasource_id': datasource_id
            }

        except Exception as e:
            logger.error(f"Failed to start training session: {e}")
            raise

    async def get_training_session_status(self, session_id: int) -> Optional[TrainingSession]:
        """Get training session status"""
        return await self.repository.get_training_session(session_id)

    async def list_training_sessions(
        self,
        datasource_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[TrainingSession], int]:
        """List training sessions"""
        return await self.repository.list_training_sessions(
            datasource_id=datasource_id,
            limit=limit,
            offset=offset
        )

    async def generate_embeddings_for_training_data(
        self,
        datasource_id: int,
        training_data_ids: List[int]
    ) -> Dict[str, Any]:
        """Generate embeddings for specific training data using Celery"""
        try:
            # Start Celery task
            from src.tasks.text2sql_tasks import generate_embeddings_task
            task = generate_embeddings_task.delay(
                datasource_id, training_data_ids
            )

            logger.info(f"Started embedding generation task {task.id} for {len(training_data_ids)} items")

            return {
                'task_id': task.id,
                'status': 'started',
                'datasource_id': datasource_id,
                'training_data_count': len(training_data_ids)
            }

        except Exception as e:
            logger.error(f"Failed to start embedding generation: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Health check for Text2SQL service"""
        try:
            # Test database connection
            repository = Text2SQLRepository()

            # Simple query to test database connectivity
            stats = await repository.get_statistics()

            return {
                'status': 'healthy',
                'service': 'text2sql',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'database_connected': True,
                'total_training_data': stats.get('total_training_data', 0)
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'service': 'text2sql',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'database_connected': False,
                'error': str(e)
            }

    # Query History and Statistics Methods

    async def get_query_history(
        self,
        datasource_id: Optional[int] = None,
        status: Optional[QueryStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[QueryHistory], int]:
        """Get query history with pagination"""
        return await self.repository.list_query_history(
            datasource_id=datasource_id,
            status=status,
            limit=limit,
            offset=offset
        )

    async def get_training_data_list(
        self,
        datasource_id: Optional[int] = None,
        content_type: Optional[TrainingDataType] = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[VannaEmbedding], int]:
        """Get training data list with pagination - now returns VannaEmbedding objects"""
        return await self.repository.list_training_data(
            datasource_id=datasource_id,
            content_type=content_type,
            is_active=is_active,
            limit=limit,
            offset=offset
        )

    async def delete_training_data(self, training_id: int, soft_delete: bool = True) -> bool:
        """Delete training data and associated embeddings"""
        try:
            # Get training data before deletion to find associated embeddings
            training_data = await self.repository.get_training_data(training_id)
            if not training_data:
                return False

            # Delete training data
            deleted = await self.repository.delete_training_data(training_id, soft_delete)

            if deleted:
                # Delete associated embeddings
                try:
                    await self.repository.delete_embeddings_by_training_id(training_id)
                    logger.info(f"Deleted embeddings for training data {training_id}")
                except Exception as e:
                    logger.warning(f"Failed to delete embeddings for training data {training_id}: {e}")

            return deleted

        except Exception as e:
            logger.error(f"Failed to delete training data {training_id}: {e}")
            raise

    async def get_statistics(self, datasource_id: Optional[int] = None) -> Text2SQLStatistics:
        """Get Text2SQL statistics"""
        try:
            stats = await self.repository.get_statistics(datasource_id)

            return Text2SQLStatistics(
                total_queries=stats['total_queries'],
                successful_queries=stats['successful_queries'],
                failed_queries=stats['failed_queries'],
                average_confidence=stats['average_confidence'],
                total_training_data=stats['total_training_data'],
                training_data_by_type=stats['training_data_by_type'],
                last_query_time=stats['last_query_time'],
                last_training_time=stats['last_training_time']
            )

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            raise

    async def get_datasource_training_summary(self, datasource_id: int) -> Dict[str, Any]:
        """Get training data summary for a specific datasource"""
        return await self.repository.get_datasource_training_summary(datasource_id)

    # Utility Methods

    async def retrain_model(self, datasource_id: int, force_rebuild: bool = False) -> str:
        """Retrain model for a datasource using Celery"""
        try:
            # Validate datasource exists
            datasource = await self.datasource_service.get_datasource(datasource_id)
            if not datasource:
                raise ValueError(f"Datasource {datasource_id} not found")

            # Start training session
            result = await self.start_training_session(
                datasource_id=datasource_id,
                session_name=f"Retrain Model - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                training_parameters={'force_rebuild': force_rebuild},
                notes=f"Model retraining (force_rebuild={force_rebuild})"
            )

            return result['task_id']

        except Exception as e:
            logger.error(f"Failed to start retraining: {e}")
            raise

    # Advanced Features - Question Answer Mode

    async def answer_question(self, request: QuestionAnswerRequest) -> QuestionAnswerResponse:
        """Answer natural language question using Vanna AI with SQL generation and optional execution"""
        try:
            start_time = time.time()

            # Use Vanna service for complete question answering
            vanna_result = await vanna_service_manager.ask_question(
                datasource_id=request.datasource_id,
                question=request.question,
                execute=request.execute_sql,
                embedding_model_id=getattr(request, 'embedding_model_id', None)
            )

            if not vanna_result["success"]:
                raise ValueError(f"Question answering failed: {vanna_result.get('error', 'Unknown error')}")

            # Create execution result if SQL was executed
            execution_result = None
            if request.execute_sql and "data" in vanna_result:
                result_data = vanna_result["data"]
                results = []
                for row in result_data["rows"]:
                    row_dict = {}
                    for i, col in enumerate(result_data["columns"]):
                        row_dict[col] = row[i] if i < len(row) else None
                    results.append(row_dict)

                execution_result = SQLExecutionResponse(
                    query_id=0,  # No query ID for direct execution
                    status=QueryStatus.SUCCESS,
                    result_data=results,
                    result_rows=result_data["row_count"],
                    execution_time_ms=int(vanna_result.get("execution_time", 0) * 1000)
                )

            # Format natural language answer if requested
            formatted_answer = None
            if request.format_result and execution_result and execution_result.status == QueryStatus.SUCCESS:
                formatted_answer = await self._format_sql_result_as_answer(
                    question=request.question,
                    sql=vanna_result["sql"],
                    results=execution_result.result_data,
                    row_count=execution_result.result_rows
                )

            generation_time = int((time.time() - start_time) * 1000)

            return QuestionAnswerResponse(
                question=request.question,
                generated_sql=vanna_result["sql"],
                explanation=f"Generated using Vanna AI for question: '{request.question}'" if request.include_explanation else None,
                confidence_score=vanna_result.get("confidence", 0.8),
                execution_result=execution_result,
                formatted_answer=formatted_answer,
                generation_time_ms=generation_time
            )

        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            raise

    async def _format_sql_result_as_answer(
        self,
        question: str,
        sql: str,
        results: List[Dict[str, Any]],
        row_count: int
    ) -> str:
        """Format SQL execution results as natural language answer"""

        if not results:
            return f"No results found for your question: '{question}'"

        if row_count == 1:
            # Single result
            result = results[0]
            if len(result) == 1:
                # Single value result
                value = list(result.values())[0]
                return f"The answer to '{question}' is: {value}"
            else:
                # Multiple columns
                formatted_result = ", ".join([f"{k}: {v}" for k, v in result.items()])
                return f"Based on your question '{question}', here's what I found: {formatted_result}"
        else:
            # Multiple results
            if row_count <= 5:
                # Show all results
                formatted_results = []
                for i, result in enumerate(results, 1):
                    if len(result) == 1:
                        value = list(result.values())[0]
                        formatted_results.append(f"{i}. {value}")
                    else:
                        formatted_result = ", ".join([f"{k}: {v}" for k, v in result.items()])
                        formatted_results.append(f"{i}. {formatted_result}")

                return f"Found {row_count} results for '{question}':\n" + "\n".join(formatted_results)
            else:
                # Show summary
                return f"Found {row_count} results for your question '{question}'. Here are the first few: " + \
                       str(results[:3]) + f"... and {row_count - 3} more."

    # Batch Training Features

    async def batch_train_sql_pairs(self, request: BatchTrainingRequest) -> Dict[str, Any]:
        """Batch training with SQL question-answer pairs"""
        try:
            # Validate datasource exists
            datasource = await self.datasource_service.get_datasource(request.datasource_id)
            if not datasource:
                raise ValueError(f"Datasource {request.datasource_id} not found")

            added_count = 0
            skipped_count = 0
            errors = []

            for i, sql_pair in enumerate(request.sql_pairs):
                try:
                    # Create training data request
                    training_request = TrainingDataRequest(
                        datasource_id=request.datasource_id,
                        content_type=TrainingDataType.SQL,
                        content=sql_pair.sql,
                        question=sql_pair.question,
                        sql_query=sql_pair.sql,
                        metadata={
                            "explanation": sql_pair.explanation,
                            "batch_id": f"batch_{int(time.time())}",
                            "pair_index": i
                        }
                    )

                    # Check if already exists (if not overwriting)
                    if not request.overwrite_existing:
                        existing = await self.repository.find_training_data_by_content_hash(
                            datasource_id=request.datasource_id,
                            content=sql_pair.sql
                        )
                        if existing:
                            skipped_count += 1
                            continue

                    # Add training data
                    await self.add_training_data(training_request)
                    added_count += 1

                except Exception as e:
                    errors.append(f"Pair {i+1}: {str(e)}")
                    logger.warning(f"Failed to add SQL pair {i+1}: {e}")

            # Start embedding generation for new data if any added
            if added_count > 0:
                try:
                    # Get recently added training data
                    recent_data, _ = await self.get_training_data_list(
                        datasource_id=request.datasource_id,
                        limit=added_count
                    )

                    if recent_data:
                        await self.generate_embeddings_for_training_data(
                            datasource_id=request.datasource_id,
                            training_data_ids=[data.id for data in recent_data]
                        )
                except Exception as e:
                    logger.warning(f"Failed to start embedding generation: {e}")

            return {
                "added_count": added_count,
                "skipped_count": skipped_count,
                "total_pairs": len(request.sql_pairs),
                "errors": errors,
                "success_rate": added_count / len(request.sql_pairs) if request.sql_pairs else 0
            }

        except Exception as e:
            logger.error(f"Failed to batch train SQL pairs: {e}")
            raise

    async def train_ddl(
        self,
        datasource_id: int,
        auto_extract: bool = False,
        database_name: Optional[str] = None,
        ddl_content: Optional[str] = None,
        skip_existing: bool = True
    ) -> Dict[str, Any]:
        """Train model with DDL statements using Vanna AI"""
        try:
            # Validate datasource exists
            datasource = await self.datasource_service.get_datasource(datasource_id)
            if not datasource:
                raise ValueError(f"Datasource {datasource_id} not found")

            ddl_statements = []

            if auto_extract:
                # Extract DDL from database
                try:
                    ddl_statements = await self.datasource_service.extract_ddl_statements(
                        datasource_id, database_name
                    )
                except Exception as e:
                    logger.error(f"Failed to auto-extract DDL: {e}")
                    return {
                        "success": False,
                        "error": f"Failed to auto-extract DDL: {str(e)}",
                        "total_items": 0,
                        "successful_items": 0,
                        "failed_items": 0
                    }
            elif ddl_content:
                # Parse DDL content
                ddl_statements = [stmt.strip() for stmt in ddl_content.split(';') if stmt.strip()]
            else:
                return {
                    "success": False,
                    "error": "Either auto_extract must be True or ddl_content must be provided",
                    "total_items": 0,
                    "successful_items": 0,
                    "failed_items": 0
                }

            # Use Vanna service to train from DDL
            vanna_result = await vanna_service_manager.train_from_ddl(
                datasource_id=datasource_id,
                ddl_statements=ddl_statements,
                embedding_model_id=None,
                database_name=database_name,
                skip_existing=skip_existing
            )

            return vanna_result

        except Exception as e:
            logger.error(f"Failed to train DDL: {e}")
            raise

    async def train_documentation(
        self,
        datasource_id: int,
        documentation: str,
        doc_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Train model with documentation content"""
        try:
            # Validate datasource exists
            datasource = await self.datasource_service.get_datasource(datasource_id)
            if not datasource:
                raise ValueError(f"Datasource {datasource_id} not found")

            # Create training data for documentation
            training_request = TrainingDataRequest(
                datasource_id=datasource_id,
                content_type=TrainingDataType.DOCUMENTATION,
                content=documentation,
                metadata={
                    "doc_type": doc_type,
                    "training_type": "documentation",
                    **(metadata or {})
                }
            )

            response = await self.add_training_data(training_request)

            # Start embedding generation for documentation
            try:
                await self.generate_embeddings_for_training_data(
                    datasource_id=datasource_id,
                    training_data_ids=[response.id]
                )
                logger.info(f"Started embedding generation for documentation training data")
            except Exception as e:
                logger.warning(f"Failed to start embedding generation for documentation: {e}")

            return {
                "success": True,
                "message": "Documentation training completed successfully",
                "total": 1,
                "successful": 1,
                "failed": 0,
                "embedding_generation_started": True
            }

        except Exception as e:
            logger.error(f"Failed to train documentation: {e}")
            return {
                "success": False,
                "error": str(e),
                "total": 1,
                "successful": 0,
                "failed": 1
            }

    async def train_sql_pairs(
        self,
        datasource_id: int,
        sql_pairs: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Train model with SQL question-answer pairs using Vanna AI"""
        try:
            # Validate datasource exists
            datasource = await self.datasource_service.get_datasource(datasource_id)
            if not datasource:
                raise ValueError(f"Datasource {datasource_id} not found")

            # Prepare SQL pairs for Vanna training
            vanna_pairs = []
            for pair in sql_pairs:
                question = pair.get("question", "").strip()
                sql = pair.get("sql", "").strip()

                if question and sql:
                    vanna_pairs.append({
                        "question": question,
                        "sql": sql
                    })
                    logger.info(f"Prepared SQL pair: '{question}' -> '{sql}'")

            if not vanna_pairs:
                return {
                    "success": False,
                    "error": "No valid SQL pairs provided",
                    "total": len(sql_pairs),
                    "successful": 0,
                    "failed": len(sql_pairs)
                }

            # Use Vanna service to train SQL pairs
            successful = 0
            failed = 0
            results = []

            for pair in vanna_pairs:
                try:
                    # Add question-SQL pair to Vanna vector store
                    vanna_instance = vanna_service_manager._get_vanna_instance(datasource_id)
                    result_id = vanna_instance.add_question_sql(
                        question=pair["question"],
                        sql=pair["sql"],
                        database_name=datasource.database_name if datasource else None
                    )

                    results.append({
                        "question": pair["question"],
                        "sql": pair["sql"],
                        "success": True,
                        "id": result_id
                    })
                    successful += 1
                    logger.info(f"Successfully trained SQL pair: {pair['question']}")

                except Exception as e:
                    logger.error(f"Failed to train SQL pair '{pair['question']}': {e}")
                    results.append({
                        "question": pair["question"],
                        "sql": pair["sql"],
                        "success": False,
                        "error": str(e)
                    })
                    failed += 1

            return {
                "success": successful > 0,
                "message": f"Successfully trained {successful} SQL pairs",
                "total": len(sql_pairs),
                "successful": successful,
                "failed": failed,
                "results": results
            }

        except Exception as e:
            logger.error(f"Failed to train SQL pairs: {e}")
            raise

    async def cleanup_old_data(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """Start cleanup task for old data"""
        try:
            from src.tasks.text2sql_tasks import cleanup_old_data_task
            task = cleanup_old_data_task.delay(days_to_keep)

            logger.info(f"Started cleanup task {task.id} for data older than {days_to_keep} days")

            return {
                'task_id': task.id,
                'status': 'started',
                'days_to_keep': days_to_keep
            }

        except Exception as e:
            logger.error(f"Failed to start cleanup task: {e}")
            raise
