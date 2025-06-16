# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Text2SQL service for DeerFlow.

Provides SQL generation, training data management, and query execution services.
Integrates with Vanna AI and pgvector for intelligent SQL generation.
"""

import logging
import asyncio
import time
import json
import os
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
import uuid

from src.models.text2sql import (
    SQLQuery,
    QueryHistory,
    TrainingData,
    QueryStatus,
    TrainingDataType,
    SQLGenerationRequest,
    SQLGenerationResponse,
    SQLExecutionRequest,
    SQLExecutionResponse,
    TrainingDataRequest,
    TrainingDataResponse,
    Text2SQLStatistics,
)
from src.services.vector_store import get_vector_store
from src.services.database_datasource import DatabaseDatasourceService
from src.config.loader import load_yaml_config

logger = logging.getLogger(__name__)


class Text2SQLService:
    """Text2SQL service - configuration-based storage with vector search"""
    
    def __init__(self, config_file: str = "conf.yaml"):
        self.config_file = config_file
        self.vector_store = get_vector_store()
        self.datasource_service = DatabaseDatasourceService(config_file)
        
        # In-memory storage for queries and training data (could be moved to database later)
        self._queries_cache: Dict[int, SQLQuery] = {}
        self._training_data_cache: Dict[int, TrainingData] = {}
        self._query_history_cache: List[QueryHistory] = []
        
        self._next_query_id = 1
        self._next_training_id = 1
        
        self._load_data()
    
    def _load_data(self):
        """Load existing data from configuration"""
        try:
            if os.path.exists(self.config_file):
                config = load_yaml_config(self.config_file)
                
                # Load queries
                queries_data = config.get("TEXT2SQL_QUERIES", [])
                for query_data in queries_data:
                    query = SQLQuery(**query_data)
                    self._queries_cache[query.id] = query
                    if query.id >= self._next_query_id:
                        self._next_query_id = query.id + 1
                
                # Load training data
                training_data = config.get("TEXT2SQL_TRAINING_DATA", [])
                for data in training_data:
                    training_item = TrainingData(**data)
                    self._training_data_cache[training_item.id] = training_item
                    if training_item.id >= self._next_training_id:
                        self._next_training_id = training_item.id + 1
                
                # Load query history
                history_data = config.get("TEXT2SQL_QUERY_HISTORY", [])
                for history_item in history_data:
                    self._query_history_cache.append(QueryHistory(**history_item))
                
                logger.info(f"Loaded {len(self._queries_cache)} queries and {len(self._training_data_cache)} training items")
                
        except Exception as e:
            logger.warning(f"Failed to load Text2SQL data from config: {e}")
    
    def _save_data(self):
        """Save data to configuration file"""
        try:
            config = load_yaml_config(self.config_file) if os.path.exists(self.config_file) else {}
            
            # Save queries
            config["TEXT2SQL_QUERIES"] = [
                query.model_dump() for query in self._queries_cache.values()
            ]
            
            # Save training data
            config["TEXT2SQL_TRAINING_DATA"] = [
                data.model_dump() for data in self._training_data_cache.values()
            ]
            
            # Save query history (keep only recent 1000 entries)
            config["TEXT2SQL_QUERY_HISTORY"] = [
                history.model_dump() for history in self._query_history_cache[-1000:]
            ]
            
            # Write back to file
            import yaml
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config, f, default_flow_style=False, allow_unicode=True)
                
        except Exception as e:
            logger.error(f"Failed to save Text2SQL data to config: {e}")
    
    async def generate_sql(self, request: SQLGenerationRequest) -> SQLGenerationResponse:
        """Generate SQL from natural language question"""
        start_time = time.time()
        
        try:
            # Validate datasource exists
            datasource = await self.datasource_service.get_datasource(request.datasource_id)
            if not datasource:
                raise ValueError(f"Datasource {request.datasource_id} not found")
            
            # For now, implement a simple rule-based SQL generation
            # In a real implementation, this would use Vanna AI or similar
            generated_sql = await self._generate_sql_simple(request.question, datasource)
            
            # Create query record
            now = datetime.now(timezone.utc)
            query = SQLQuery(
                id=self._next_query_id,
                question=request.question,
                generated_sql=generated_sql,
                datasource_id=request.datasource_id,
                status=QueryStatus.PENDING,
                explanation=f"Generated SQL for: {request.question}" if request.include_explanation else None,
                confidence_score=0.8,  # Mock confidence score
                created_at=now
            )
            
            self._queries_cache[self._next_query_id] = query
            self._next_query_id += 1
            self._save_data()
            
            generation_time = int((time.time() - start_time) * 1000)
            
            return SQLGenerationResponse(
                query_id=query.id,
                question=query.question,
                generated_sql=query.generated_sql,
                explanation=query.explanation,
                confidence_score=query.confidence_score,
                similar_examples=[],  # Would be populated by vector search
                generation_time_ms=generation_time
            )
            
        except Exception as e:
            logger.error(f"Failed to generate SQL: {e}")
            raise
    
    async def _generate_sql_simple(self, question: str, datasource) -> str:
        """Simple rule-based SQL generation (placeholder for Vanna AI)"""
        question_lower = question.lower()
        
        # Get database schema for context
        schema = await self.datasource_service.get_database_schema(datasource.id)
        
        if not schema or not schema.tables:
            return "-- No tables found in database"
        
        # Simple pattern matching for common queries
        if "count" in question_lower or "how many" in question_lower:
            first_table = schema.tables[0]['table_name']
            return f"SELECT COUNT(*) FROM {first_table};"
        
        elif "all" in question_lower or "list" in question_lower:
            first_table = schema.tables[0]['table_name']
            return f"SELECT * FROM {first_table} LIMIT 10;"
        
        elif "user" in question_lower and any("user" in table['table_name'].lower() for table in schema.tables):
            user_table = next((table for table in schema.tables if "user" in table['table_name'].lower()), None)
            if user_table:
                return f"SELECT * FROM {user_table['table_name']} LIMIT 10;"
        
        # Default query
        first_table = schema.tables[0]['table_name']
        return f"SELECT * FROM {first_table} LIMIT 10;"
    
    async def execute_sql(self, request: SQLExecutionRequest) -> SQLExecutionResponse:
        """Execute generated SQL query"""
        try:
            query = self._queries_cache.get(request.query_id)
            if not query:
                raise ValueError(f"Query {request.query_id} not found")
            
            # Update query status
            query.status = QueryStatus.RUNNING
            self._save_data()
            
            start_time = time.time()
            
            # Execute SQL using datasource service
            datasource = await self.datasource_service.get_datasource(query.datasource_id)
            if not datasource:
                raise ValueError(f"Datasource {query.datasource_id} not found")
            
            # For safety, only allow SELECT queries in readonly mode
            if datasource.readonly_mode and not query.generated_sql.strip().upper().startswith('SELECT'):
                raise ValueError("Only SELECT queries are allowed in readonly mode")
            
            # Execute the query (simplified implementation)
            result_data, result_rows = await self._execute_sql_query(
                datasource, query.generated_sql, request.limit
            )
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Update query with results
            query.status = QueryStatus.SUCCESS
            query.execution_time_ms = execution_time
            query.result_rows = result_rows
            query.executed_at = datetime.now(timezone.utc)
            
            # Add to history
            history = QueryHistory(
                id=len(self._query_history_cache) + 1,
                query_id=query.id,
                question=query.question,
                generated_sql=query.generated_sql,
                datasource_id=query.datasource_id,
                datasource_name=datasource.name,
                status=query.status,
                execution_time_ms=execution_time,
                result_rows=result_rows,
                confidence_score=query.confidence_score,
                created_at=query.created_at
            )
            self._query_history_cache.append(history)
            self._save_data()
            
            return SQLExecutionResponse(
                query_id=query.id,
                status=query.status,
                result_data=result_data,
                result_rows=result_rows,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            # Update query with error
            if request.query_id in self._queries_cache:
                query = self._queries_cache[request.query_id]
                query.status = QueryStatus.ERROR
                query.error_message = str(e)
                query.executed_at = datetime.now(timezone.utc)
                self._save_data()
            
            logger.error(f"Failed to execute SQL: {e}")
            return SQLExecutionResponse(
                query_id=request.query_id,
                status=QueryStatus.ERROR,
                error_message=str(e)
            )
    
    async def _execute_sql_query(
        self, datasource, sql: str, limit: int
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Execute SQL query against datasource"""
        # This is a simplified implementation
        # In a real scenario, you'd use the actual database connection
        
        # Mock result for demonstration
        mock_result = [
            {"id": 1, "name": "Sample Data", "created_at": "2025-06-16T10:00:00Z"},
            {"id": 2, "name": "Another Record", "created_at": "2025-06-16T10:01:00Z"},
        ]
        
        return mock_result[:limit], len(mock_result)
    
    async def add_training_data(self, request: TrainingDataRequest) -> TrainingDataResponse:
        """Add training data"""
        try:
            # Validate datasource exists
            datasource = await self.datasource_service.get_datasource(request.datasource_id)
            if not datasource:
                raise ValueError(f"Datasource {request.datasource_id} not found")
            
            now = datetime.now(timezone.utc)
            training_data = TrainingData(
                id=self._next_training_id,
                datasource_id=request.datasource_id,
                content_type=request.content_type,
                content=request.content,
                metadata=request.metadata,
                created_at=now,
                updated_at=now
            )
            
            self._training_data_cache[self._next_training_id] = training_data
            self._next_training_id += 1
            self._save_data()
            
            # TODO: Generate and store embedding in vector store
            
            return TrainingDataResponse(
                id=training_data.id,
                datasource_id=training_data.datasource_id,
                content_type=training_data.content_type,
                content=training_data.content,
                metadata=training_data.metadata,
                is_active=training_data.is_active,
                created_at=training_data.created_at,
                updated_at=training_data.updated_at
            )
            
        except Exception as e:
            logger.error(f"Failed to add training data: {e}")
            raise

    async def get_training_data(
        self,
        datasource_id: int,
        content_type: Optional[TrainingDataType] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[TrainingDataResponse]:
        """Get training data for a datasource"""
        try:
            # Filter training data
            filtered_data = [
                data for data in self._training_data_cache.values()
                if data.datasource_id == datasource_id and data.is_active
                and (content_type is None or data.content_type == content_type)
            ]

            # Sort by creation time (newest first)
            filtered_data.sort(key=lambda x: x.created_at, reverse=True)

            # Apply pagination
            paginated_data = filtered_data[offset:offset + limit]

            return [
                TrainingDataResponse(
                    id=data.id,
                    datasource_id=data.datasource_id,
                    content_type=data.content_type,
                    content=data.content,
                    metadata=data.metadata,
                    is_active=data.is_active,
                    created_at=data.created_at,
                    updated_at=data.updated_at
                )
                for data in paginated_data
            ]

        except Exception as e:
            logger.error(f"Failed to get training data: {e}")
            raise

    async def delete_training_data(self, training_id: int) -> bool:
        """Delete training data"""
        try:
            if training_id not in self._training_data_cache:
                return False

            # Mark as inactive instead of deleting
            training_data = self._training_data_cache[training_id]
            training_data.is_active = False
            training_data.updated_at = datetime.now(timezone.utc)

            self._save_data()

            # TODO: Remove from vector store

            logger.info(f"Deleted training data {training_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete training data: {e}")
            raise

    async def get_query_history(
        self,
        datasource_id: Optional[int] = None,
        status: Optional[QueryStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[QueryHistory]:
        """Get query history"""
        try:
            # Filter history
            filtered_history = [
                history for history in self._query_history_cache
                if (datasource_id is None or history.datasource_id == datasource_id)
                and (status is None or history.status == status)
            ]

            # Sort by creation time (newest first)
            filtered_history.sort(key=lambda x: x.created_at, reverse=True)

            # Apply pagination
            return filtered_history[offset:offset + limit]

        except Exception as e:
            logger.error(f"Failed to get query history: {e}")
            raise

    async def get_statistics(self, datasource_id: Optional[int] = None) -> Text2SQLStatistics:
        """Get Text2SQL statistics"""
        try:
            # Filter data by datasource if specified
            queries = [
                query for query in self._queries_cache.values()
                if datasource_id is None or query.datasource_id == datasource_id
            ]

            training_data = [
                data for data in self._training_data_cache.values()
                if (datasource_id is None or data.datasource_id == datasource_id)
                and data.is_active
            ]

            # Calculate statistics
            total_queries = len(queries)
            successful_queries = len([q for q in queries if q.status == QueryStatus.SUCCESS])
            failed_queries = len([q for q in queries if q.status == QueryStatus.ERROR])

            # Calculate average confidence
            confidence_scores = [q.confidence_score for q in queries if q.confidence_score is not None]
            average_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else None

            # Training data by type
            training_data_by_type = {}
            for data_type in TrainingDataType:
                count = len([d for d in training_data if d.content_type == data_type])
                training_data_by_type[data_type.value] = count

            # Last query and training times
            last_query_time = max([q.created_at for q in queries]) if queries else None
            last_training_time = max([d.created_at for d in training_data]) if training_data else None

            return Text2SQLStatistics(
                total_queries=total_queries,
                successful_queries=successful_queries,
                failed_queries=failed_queries,
                average_confidence=average_confidence,
                total_training_data=len(training_data),
                training_data_by_type=training_data_by_type,
                last_query_time=last_query_time,
                last_training_time=last_training_time
            )

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            raise

    async def retrain_model(self, datasource_id: int, force_rebuild: bool = False) -> str:
        """Retrain model for a datasource"""
        try:
            # Validate datasource exists
            datasource = await self.datasource_service.get_datasource(datasource_id)
            if not datasource:
                raise ValueError(f"Datasource {datasource_id} not found")

            # Generate a task ID for tracking
            task_id = str(uuid.uuid4())

            # TODO: Implement actual retraining logic
            # This would involve:
            # 1. Extracting database schema
            # 2. Generating embeddings for training data
            # 3. Storing embeddings in vector store
            # 4. Training/updating the model

            logger.info(f"Started retraining task {task_id} for datasource {datasource_id}")

            return task_id

        except Exception as e:
            logger.error(f"Failed to start retraining: {e}")
            raise
