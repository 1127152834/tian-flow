# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Text2SQL repository for Olight.

Provides data access layer for Text2SQL functionality including query history,
training data, SQL query cache, and training sessions.
"""

import logging
import hashlib
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor, Json

from src.config.database import get_database_config
from src.models.text2sql import (
    QueryHistory,
    VannaEmbedding,
    SQLQueryCache,
    TrainingSession,
    QueryStatus,
    TrainingDataType,
    QueryComplexity,
    TrainingSessionStatus,
)

logger = logging.getLogger(__name__)


class TimestampJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Timestamp, datetime, and other objects (following ti-flow pattern)"""
    def default(self, obj):
        # Handle datetime, date, time objects
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        # Handle Decimal objects (like ti-flow's DecimalJSONEncoder)
        elif hasattr(obj, '__float__'):
            return float(obj)
        # Handle Pydantic models (like ti-flow's PydanticJSONEncoder)
        elif hasattr(obj, 'model_dump'):
            return obj.model_dump()
        elif hasattr(obj, 'dict'):
            return obj.dict()
        # Handle objects with __dict__ (like Timestamp)
        elif hasattr(obj, '__dict__'):
            return str(obj)
        # Fallback to string representation
        return str(obj)


def safe_json_serialize(data):
    """Safely serialize data to JSON, handling Timestamp objects"""
    if data is None:
        return None
    try:
        return json.dumps(data, cls=TimestampJSONEncoder, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Failed to serialize data to JSON: {e}, falling back to string representation")
        return str(data)


class Text2SQLRepository:
    """Repository for Text2SQL data operations"""
    
    def __init__(self):
        self.db_config = get_database_config()
        self._ensure_schema_if_needed()
    
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(
            host=self.db_config["host"],
            port=self.db_config["port"],
            database=self.db_config["database"],
            user=self.db_config["user"],
            password=self.db_config["password"],
            cursor_factory=RealDictCursor
        )
    
    def _ensure_schema_if_needed(self):
        """Ensure Text2SQL schema exists (should already be created by migration)"""
        try:
            conn = self._get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM information_schema.schemata WHERE schema_name = 'text2sql'")
                    if not cursor.fetchone():
                        logger.warning("Text2SQL schema not found - please run migrations")
                    else:
                        logger.info("✅ Text2SQL schema verified")

                    # Also check if tables exist
                    cursor.execute("""
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = 'text2sql' AND table_name = 'query_history'
                    """)
                    if not cursor.fetchone():
                        logger.warning("Text2SQL tables not found - please run migrations")
                    else:
                        logger.info("✅ Text2SQL tables verified")
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Failed to verify Text2SQL schema: {e}")
    
    # Query History Operations
    
    async def create_query_history(
        self,
        user_question: str,
        generated_sql: str,
        datasource_id: int,
        status: QueryStatus = QueryStatus.PENDING,
        **kwargs
    ) -> int:
        """Create a new query history record"""
        conn = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO text2sql.query_history (
                        user_question, generated_sql, datasource_id, status,
                        execution_time_ms, result_rows, result_data, error_message,
                        confidence_score, model_used, explanation, similar_examples,
                        user_rating, user_feedback, created_at
                    ) VALUES (
                        %(user_question)s, %(generated_sql)s, %(datasource_id)s, %(status)s,
                        %(execution_time_ms)s, %(result_rows)s, %(result_data)s, %(error_message)s,
                        %(confidence_score)s, %(model_used)s, %(explanation)s, %(similar_examples)s,
                        %(user_rating)s, %(user_feedback)s, %(created_at)s
                    ) RETURNING id
                """, {
                    'user_question': user_question,
                    'generated_sql': generated_sql,
                    'datasource_id': datasource_id,
                    'status': status.value,
                    'execution_time_ms': kwargs.get('execution_time_ms'),
                    'result_rows': kwargs.get('result_rows'),
                    'result_data': Json(kwargs.get('result_data')) if kwargs.get('result_data') else None,
                    'error_message': kwargs.get('error_message'),
                    'confidence_score': kwargs.get('confidence_score'),
                    'model_used': kwargs.get('model_used'),
                    'explanation': kwargs.get('explanation'),
                    'similar_examples': Json(kwargs.get('similar_examples')) if kwargs.get('similar_examples') else None,
                    'user_rating': kwargs.get('user_rating'),
                    'user_feedback': kwargs.get('user_feedback'),
                    'created_at': datetime.now(timezone.utc)
                })

                query_id = cursor.fetchone()['id']
                conn.commit()

                logger.info(f"Created query history record: {query_id}")
                return query_id

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Failed to create query history: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    async def update_query_history(
        self,
        query_id: int,
        **updates
    ) -> bool:
        """Update query history record"""
        try:
            if not updates:
                return True
            
            # Build dynamic update query
            set_clauses = []
            params = {'query_id': query_id}
            
            for key, value in updates.items():
                if key in ['result_data', 'similar_examples'] and value is not None:
                    set_clauses.append(f"{key} = %({key})s")
                    # Use safe JSON serialization for complex data
                    try:
                        params[key] = Json(value)
                    except Exception as e:
                        logger.warning(f"Failed to serialize {key} as JSON: {e}, using safe serialization")
                        # Convert to JSON string first to handle Timestamp objects
                        json_str = safe_json_serialize(value)
                        params[key] = Json(json.loads(json_str) if json_str else {})
                else:
                    set_clauses.append(f"{key} = %({key})s")
                    params[key] = value
            
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                        UPDATE text2sql.query_history 
                        SET {', '.join(set_clauses)}
                        WHERE id = %(query_id)s
                    """, params)
                    
                    updated = cursor.rowcount > 0
                    conn.commit()
                    
                    if updated:
                        logger.info(f"Updated query history: {query_id}")
                    
                    return updated
                    
        except Exception as e:
            logger.error(f"Failed to update query history {query_id}: {e}")
            raise
    
    async def get_query_history(
        self,
        query_id: int
    ) -> Optional[QueryHistory]:
        """Get query history by ID"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM text2sql.query_history 
                        WHERE id = %s
                    """, (query_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        return QueryHistory(**dict(row))
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to get query history {query_id}: {e}")
            raise
    
    async def list_query_history(
        self,
        datasource_id: Optional[int] = None,
        status: Optional[QueryStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[QueryHistory], int]:
        """List query history with pagination"""
        try:
            conditions = []
            params = {'limit': limit, 'offset': offset}
            
            if datasource_id is not None:
                conditions.append("datasource_id = %(datasource_id)s")
                params['datasource_id'] = datasource_id
            
            if status is not None:
                conditions.append("status = %(status)s")
                params['status'] = status.value
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get total count
                    cursor.execute(f"""
                        SELECT COUNT(*) as total 
                        FROM text2sql.query_history 
                        {where_clause}
                    """, params)
                    total = cursor.fetchone()['total']
                    
                    # Get paginated results
                    cursor.execute(f"""
                        SELECT * FROM text2sql.query_history 
                        {where_clause}
                        ORDER BY created_at DESC
                        LIMIT %(limit)s OFFSET %(offset)s
                    """, params)
                    
                    rows = cursor.fetchall()
                    queries = [QueryHistory(**dict(row)) for row in rows]
                    
                    return queries, total
                    
        except Exception as e:
            logger.error(f"Failed to list query history: {e}")
            raise

    # Training Data Operations

    def _generate_content_hash(self, content: str, datasource_id: int) -> str:
        """Generate hash for content deduplication"""
        content_str = f"{datasource_id}:{content}"
        return hashlib.sha256(content_str.encode()).hexdigest()

    # Training data operations removed - using VannaEmbedding directly

    # get_training_data removed - using VannaEmbedding directly

    async def list_training_data(
        self,
        datasource_id: Optional[int] = None,
        content_type: Optional[TrainingDataType] = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[VannaEmbedding], int]:
        """List training data with pagination - now reads from vanna_embeddings table"""
        try:
            conditions = []
            params = {'limit': limit, 'offset': offset}

            if datasource_id is not None:
                conditions.append("datasource_id = %(datasource_id)s")
                params['datasource_id'] = datasource_id

            if content_type is not None:
                conditions.append("content_type = %(content_type)s")
                params['content_type'] = content_type.value

            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get total count from vanna_embeddings
                    cursor.execute(f"""
                        SELECT COUNT(*) as total
                        FROM text2sql.vanna_embeddings
                        {where_clause}
                    """, params)
                    total = cursor.fetchone()['total']

                    # Get paginated results from vanna_embeddings
                    cursor.execute(f"""
                        SELECT
                            id,
                            datasource_id,
                            content,
                            content_type,
                            content_hash,
                            question,
                            sql_query,
                            table_name,
                            column_name,
                            embedding_vector,
                            created_at,
                            updated_at,
                            metadata
                        FROM text2sql.vanna_embeddings
                        {where_clause}
                        ORDER BY created_at DESC
                        LIMIT %(limit)s OFFSET %(offset)s
                    """, params)

                    rows = cursor.fetchall()
                    training_data = []

                    for row in rows:
                        # Convert vanna_embeddings row to VannaEmbedding format
                        # Get embedding vector if available
                        embedding_vector = []
                        raw_vector = row.get('embedding_vector')

                        # Debug: log all vector-related info
                        logger.info(f"Row ID: {row.get('id')}, embedding_vector exists: {raw_vector is not None}, type: {type(raw_vector)}")

                        if raw_vector is not None:
                            try:
                                logger.info(f"Raw embedding_vector type: {type(raw_vector)}, length: {len(str(raw_vector))}")

                                # PostgreSQL vector type returns as string like "[1.0,2.0,3.0]"
                                if isinstance(raw_vector, list):
                                    # Already a list
                                    embedding_vector = [float(x) for x in raw_vector]
                                elif isinstance(raw_vector, str):
                                    # PostgreSQL vector type string format: "[1.0,2.0,3.0]"
                                    vector_str = raw_vector.strip()
                                    if vector_str:
                                        # Handle both "[...]" and "{...}" formats
                                        if (vector_str.startswith('[') and vector_str.endswith(']')) or \
                                           (vector_str.startswith('{') and vector_str.endswith('}')):
                                            # Remove brackets/braces and split by comma
                                            vector_str = vector_str[1:-1]  # Remove [ ] or { }
                                            if vector_str.strip():  # Check if not empty
                                                # Split by comma and convert to float
                                                embedding_vector = [float(x.strip()) for x in vector_str.split(',') if x.strip()]

                                logger.info(f"Parsed embedding_vector length: {len(embedding_vector)}")
                            except (TypeError, ValueError, AttributeError) as e:
                                logger.warning(f"Failed to parse embedding vector: {e}")
                                logger.warning(f"Raw vector sample: {str(raw_vector)[:100]}...")
                                embedding_vector = []

                        training_data.append(VannaEmbedding(
                            id=row['id'],
                            datasource_id=row['datasource_id'],
                            content_type=TrainingDataType(row['content_type']),
                            content=row['content'],
                            content_hash=row['content_hash'],
                            question=row['question'],
                            sql_query=row['sql_query'],
                            table_name=row['table_name'],
                            column_name=row['column_name'],
                            embedding_vector=embedding_vector,
                            metadata=row['metadata'],
                            created_at=row['created_at'],
                            updated_at=row['updated_at']
                        ))

                    return training_data, total

        except Exception as e:
            logger.error(f"Failed to list training data: {e}")
            raise

    # VannaEmbedding operations (replacing training_data table methods)

    async def get_training_data(self, training_id: int) -> Optional[VannaEmbedding]:
        """Get training data by ID from vanna_embeddings table"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT
                            id, datasource_id, content, content_type, content_hash,
                            question, sql_query, table_name, column_name,
                            embedding_vector, created_at, updated_at, metadata
                        FROM text2sql.vanna_embeddings
                        WHERE id = %s
                    """, (training_id,))

                    row = cursor.fetchone()
                    if row:
                        # Get embedding vector if available
                        embedding_vector = []
                        if row.get('embedding_vector'):
                            try:
                                raw_vector = row['embedding_vector']
                                # PostgreSQL vector type returns as string like "[1.0,2.0,3.0]"
                                if isinstance(raw_vector, list):
                                    # Already a list
                                    embedding_vector = [float(x) for x in raw_vector]
                                elif isinstance(raw_vector, str):
                                    # PostgreSQL vector type string format: "[1.0,2.0,3.0]"
                                    vector_str = raw_vector.strip()
                                    if vector_str:
                                        # Handle both "[...]" and "{...}" formats
                                        if (vector_str.startswith('[') and vector_str.endswith(']')) or \
                                           (vector_str.startswith('{') and vector_str.endswith('}')):
                                            # Remove brackets/braces and split by comma
                                            vector_str = vector_str[1:-1]  # Remove [ ] or { }
                                            if vector_str.strip():  # Check if not empty
                                                # Split by comma and convert to float
                                                embedding_vector = [float(x.strip()) for x in vector_str.split(',') if x.strip()]
                            except (TypeError, ValueError, AttributeError) as e:
                                logger.warning(f"Failed to parse embedding vector: {e}")
                                embedding_vector = []

                        return VannaEmbedding(
                            id=row['id'],
                            datasource_id=row['datasource_id'],
                            content=row['content'],
                            content_type=TrainingDataType(row['content_type']),
                            content_hash=row['content_hash'],
                            question=row['question'],
                            sql_query=row['sql_query'],
                            table_name=row['table_name'],
                            column_name=row['column_name'],
                            embedding_vector=embedding_vector,
                            metadata=row['metadata'],
                            created_at=row['created_at'],
                            updated_at=row['updated_at']
                        )
                    return None

        except Exception as e:
            logger.error(f"Failed to get training data {training_id}: {e}")
            raise

    async def get_training_data_by_content_hash(self, datasource_id: int, content_hash: str) -> Optional[VannaEmbedding]:
        """Get training data by content hash from vanna_embeddings table"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT
                            id, datasource_id, content, content_type, content_hash,
                            question, sql_query, table_name, column_name,
                            created_at, updated_at, metadata
                        FROM text2sql.vanna_embeddings
                        WHERE datasource_id = %s AND content_hash = %s
                        ORDER BY created_at DESC
                        LIMIT 1
                    """, (datasource_id, content_hash))

                    row = cursor.fetchone()
                    if row:
                        return VannaEmbedding(
                            id=row['id'],
                            datasource_id=row['datasource_id'],
                            content=row['content'],
                            content_type=TrainingDataType(row['content_type']),
                            content_hash=row['content_hash'],
                            question=row['question'],
                            sql_query=row['sql_query'],
                            table_name=row['table_name'],
                            column_name=row['column_name'],
                            embedding_vector=[],  # Vector not needed for basic operations
                            metadata=row['metadata'],
                            created_at=row['created_at'],
                            updated_at=row['updated_at']
                        )
                    return None

        except Exception as e:
            logger.error(f"Failed to get training data by content hash {content_hash}: {e}")
            raise

    async def update_training_data(self, training_id: int, **updates) -> bool:
        """Update training data in vanna_embeddings table"""
        try:
            if not updates:
                return True

            # Add updated_at automatically
            updates['updated_at'] = datetime.now(timezone.utc)

            # Build dynamic update query
            set_clauses = []
            params = {'training_id': training_id}

            for key, value in updates.items():
                if key == 'metadata' and value is not None:
                    set_clauses.append(f"{key} = %({key})s")
                    params[key] = Json(value)
                elif key == 'content_type' and value is not None:
                    set_clauses.append(f"{key} = %({key})s")
                    params[key] = value.value if hasattr(value, 'value') else value
                else:
                    set_clauses.append(f"{key} = %({key})s")
                    params[key] = value

            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                        UPDATE text2sql.vanna_embeddings
                        SET {', '.join(set_clauses)}
                        WHERE id = %(training_id)s
                    """, params)

                    updated = cursor.rowcount > 0
                    conn.commit()

                    if updated:
                        logger.info(f"Updated training data: {training_id}")

                    return updated

        except Exception as e:
            logger.error(f"Failed to update training data {training_id}: {e}")
            raise

    async def delete_training_data(self, training_id: int, soft_delete: bool = True) -> bool:
        """Delete training data from vanna_embeddings table"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # For vanna_embeddings, we do hard delete since there's no is_active field
                    cursor.execute("""
                        DELETE FROM text2sql.vanna_embeddings
                        WHERE id = %s
                    """, (training_id,))

                    deleted = cursor.rowcount > 0
                    conn.commit()

                    if deleted:
                        logger.info(f"Deleted training data: {training_id}")

                    return deleted

        except Exception as e:
            logger.error(f"Failed to delete training data {training_id}: {e}")
            raise

    # SQL Query Cache Operations

    async def create_sql_query_cache(
        self,
        query_text: str,
        sql_text: str,
        datasource_id: int,
        table_names: Optional[List[str]] = None,
        query_complexity: QueryComplexity = QueryComplexity.SIMPLE,
        embedding_model: Optional[str] = None
    ) -> int:
        """Create SQL query cache entry"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO text2sql.sql_queries (
                            query_text, sql_text, datasource_id, table_names,
                            query_complexity, embedding_model, usage_count,
                            success_rate, created_at, updated_at
                        ) VALUES (
                            %(query_text)s, %(sql_text)s, %(datasource_id)s, %(table_names)s,
                            %(query_complexity)s, %(embedding_model)s, %(usage_count)s,
                            %(success_rate)s, %(created_at)s, %(updated_at)s
                        ) RETURNING id
                    """, {
                        'query_text': query_text,
                        'sql_text': sql_text,
                        'datasource_id': datasource_id,
                        'table_names': table_names,
                        'query_complexity': query_complexity.value,
                        'embedding_model': embedding_model,
                        'usage_count': 0,
                        'success_rate': 1.0,
                        'created_at': datetime.now(timezone.utc),
                        'updated_at': datetime.now(timezone.utc)
                    })

                    cache_id = cursor.fetchone()['id']
                    conn.commit()

                    logger.info(f"Created SQL query cache: {cache_id}")
                    return cache_id

        except Exception as e:
            logger.error(f"Failed to create SQL query cache: {e}")
            raise

    async def update_sql_query_cache_usage(
        self,
        cache_id: int,
        execution_time_ms: Optional[int] = None,
        success: bool = True
    ) -> bool:
        """Update SQL query cache usage statistics"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get current stats
                    cursor.execute("""
                        SELECT usage_count, average_execution_time_ms, success_rate
                        FROM text2sql.sql_queries
                        WHERE id = %s
                    """, (cache_id,))

                    row = cursor.fetchone()
                    if not row:
                        return False

                    current_usage = row['usage_count']
                    current_avg_time = row['average_execution_time_ms'] or 0
                    current_success_rate = row['success_rate']

                    # Calculate new stats
                    new_usage = current_usage + 1

                    # Update average execution time
                    if execution_time_ms is not None:
                        if current_avg_time == 0:
                            new_avg_time = execution_time_ms
                        else:
                            new_avg_time = int((current_avg_time * current_usage + execution_time_ms) / new_usage)
                    else:
                        new_avg_time = current_avg_time

                    # Update success rate
                    total_attempts = new_usage
                    successful_attempts = int(current_success_rate * current_usage) + (1 if success else 0)
                    new_success_rate = successful_attempts / total_attempts

                    # Update record
                    cursor.execute("""
                        UPDATE text2sql.sql_queries
                        SET usage_count = %s,
                            average_execution_time_ms = %s,
                            success_rate = %s,
                            last_used_at = %s,
                            updated_at = %s
                        WHERE id = %s
                    """, (
                        new_usage, new_avg_time, new_success_rate,
                        datetime.now(timezone.utc), datetime.now(timezone.utc), cache_id
                    ))

                    updated = cursor.rowcount > 0
                    conn.commit()

                    if updated:
                        logger.info(f"Updated SQL query cache usage: {cache_id}")

                    return updated

        except Exception as e:
            logger.error(f"Failed to update SQL query cache usage {cache_id}: {e}")
            raise

    async def search_similar_queries(
        self,
        datasource_id: int,
        limit: int = 5
    ) -> List[SQLQueryCache]:
        """Search for similar cached queries (placeholder for vector search)"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM text2sql.sql_queries
                        WHERE datasource_id = %s
                        ORDER BY usage_count DESC, last_used_at DESC
                        LIMIT %s
                    """, (datasource_id, limit))

                    rows = cursor.fetchall()
                    return [SQLQueryCache(**dict(row)) for row in rows]

        except Exception as e:
            logger.error(f"Failed to search similar queries: {e}")
            raise

    # Training Session Operations

    async def create_training_session(
        self,
        datasource_id: int,
        session_name: Optional[str] = None,
        model_version: Optional[str] = None,
        training_parameters: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None
    ) -> int:
        """Create training session"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO text2sql.training_sessions (
                            datasource_id, session_name, model_version,
                            training_parameters, notes, status, started_at
                        ) VALUES (
                            %(datasource_id)s, %(session_name)s, %(model_version)s,
                            %(training_parameters)s, %(notes)s, %(status)s, %(started_at)s
                        ) RETURNING id
                    """, {
                        'datasource_id': datasource_id,
                        'session_name': session_name,
                        'model_version': model_version,
                        'training_parameters': Json(training_parameters) if training_parameters else None,
                        'notes': notes,
                        'status': TrainingSessionStatus.PENDING.value,
                        'started_at': datetime.now(timezone.utc)
                    })

                    session_id = cursor.fetchone()['id']
                    conn.commit()

                    logger.info(f"Created training session: {session_id}")
                    return session_id

        except Exception as e:
            logger.error(f"Failed to create training session: {e}")
            raise

    async def update_training_session(
        self,
        session_id: int,
        **updates
    ) -> bool:
        """Update training session"""
        try:
            if not updates:
                return True

            # Build dynamic update query
            set_clauses = []
            params = {'session_id': session_id}

            for key, value in updates.items():
                if key == 'training_parameters' and value is not None:
                    set_clauses.append(f"{key} = %({key})s")
                    params[key] = Json(value)
                else:
                    set_clauses.append(f"{key} = %({key})s")
                    params[key] = value

            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                        UPDATE text2sql.training_sessions
                        SET {', '.join(set_clauses)}
                        WHERE id = %(session_id)s
                    """, params)

                    updated = cursor.rowcount > 0
                    conn.commit()

                    if updated:
                        logger.info(f"Updated training session: {session_id}")

                    return updated

        except Exception as e:
            logger.error(f"Failed to update training session {session_id}: {e}")
            raise

    async def get_training_session(
        self,
        session_id: int
    ) -> Optional[TrainingSession]:
        """Get training session by ID"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM text2sql.training_sessions
                        WHERE id = %s
                    """, (session_id,))

                    row = cursor.fetchone()
                    if row:
                        return TrainingSession(**dict(row))
                    return None

        except Exception as e:
            logger.error(f"Failed to get training session {session_id}: {e}")
            raise

    async def list_training_sessions(
        self,
        datasource_id: Optional[int] = None,
        status: Optional[TrainingSessionStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[TrainingSession], int]:
        """List training sessions with pagination"""
        try:
            conditions = []
            params = {'limit': limit, 'offset': offset}

            if datasource_id is not None:
                conditions.append("datasource_id = %(datasource_id)s")
                params['datasource_id'] = datasource_id

            if status is not None:
                conditions.append("status = %(status)s")
                params['status'] = status.value

            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get total count
                    cursor.execute(f"""
                        SELECT COUNT(*) as total
                        FROM text2sql.training_sessions
                        {where_clause}
                    """, params)
                    total = cursor.fetchone()['total']

                    # Get paginated results
                    cursor.execute(f"""
                        SELECT * FROM text2sql.training_sessions
                        {where_clause}
                        ORDER BY started_at DESC
                        LIMIT %(limit)s OFFSET %(offset)s
                    """, params)

                    rows = cursor.fetchall()
                    sessions = [TrainingSession(**dict(row)) for row in rows]

                    return sessions, total

        except Exception as e:
            logger.error(f"Failed to list training sessions: {e}")
            raise

    # Statistics and Utility Methods

    async def get_statistics(
        self,
        datasource_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get Text2SQL statistics"""
        try:
            conditions = []
            params = {}

            if datasource_id is not None:
                conditions.append("datasource_id = %(datasource_id)s")
                params['datasource_id'] = datasource_id

            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Query history stats
                    cursor.execute(f"""
                        SELECT
                            COUNT(*) as total_queries,
                            COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as successful_queries,
                            COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed_queries,
                            AVG(confidence_score) as average_confidence,
                            MAX(created_at) as last_query_time
                        FROM text2sql.query_history
                        {where_clause}
                    """, params)

                    query_stats = cursor.fetchone()

                    # Training data stats from vanna_embeddings table
                    cursor.execute(f"""
                        SELECT
                            COUNT(*) as total_training_data,
                            COUNT(CASE WHEN content_type = 'DDL' THEN 1 END) as ddl_count,
                            COUNT(CASE WHEN content_type = 'DOCUMENTATION' THEN 1 END) as doc_count,
                            COUNT(CASE WHEN content_type = 'SQL' THEN 1 END) as sql_count,
                            COUNT(CASE WHEN content_type = 'SCHEMA' THEN 1 END) as schema_count,
                            MAX(created_at) as last_training_time
                        FROM text2sql.vanna_embeddings
                        {where_clause}
                    """, params)

                    training_stats = cursor.fetchone()

                    return {
                        'total_queries': query_stats['total_queries'],
                        'successful_queries': query_stats['successful_queries'],
                        'failed_queries': query_stats['failed_queries'],
                        'average_confidence': float(query_stats['average_confidence']) if query_stats['average_confidence'] else None,
                        'total_training_data': training_stats['total_training_data'],
                        'training_data_by_type': {
                            'DDL': training_stats['ddl_count'],
                            'DOCUMENTATION': training_stats['doc_count'],
                            'SQL': training_stats['sql_count'],
                            'SCHEMA': training_stats['schema_count']
                        },
                        'last_query_time': query_stats['last_query_time'],
                        'last_training_time': training_stats['last_training_time']
                    }

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            raise

    async def cleanup_old_data(
        self,
        days_to_keep: int = 30
    ) -> Dict[str, int]:
        """Clean up old data (query history older than specified days)"""
        try:
            cutoff_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_to_keep)

            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Clean up old query history
                    cursor.execute("""
                        DELETE FROM text2sql.query_history
                        WHERE created_at < %s
                    """, (cutoff_date,))

                    deleted_queries = cursor.rowcount

                    # Clean up unused SQL query cache entries
                    cursor.execute("""
                        DELETE FROM text2sql.sql_queries
                        WHERE last_used_at < %s OR (last_used_at IS NULL AND created_at < %s)
                    """, (cutoff_date, cutoff_date))

                    deleted_cache = cursor.rowcount

                    conn.commit()

                    logger.info(f"Cleaned up {deleted_queries} query history records and {deleted_cache} cache entries")

                    return {
                        'deleted_queries': deleted_queries,
                        'deleted_cache': deleted_cache
                    }

        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            raise

    async def get_datasource_training_summary(
        self,
        datasource_id: int
    ) -> Dict[str, Any]:
        """Get training data summary for a specific datasource"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get data from vanna_embeddings table instead of training_data
                    cursor.execute("""
                        SELECT
                            content_type,
                            COUNT(*) as count
                        FROM text2sql.vanna_embeddings
                        WHERE datasource_id = %s
                        GROUP BY content_type
                    """, (datasource_id,))

                    rows = cursor.fetchall()

                    summary = {
                        'total_items': 0,
                        'total_validated': 0,
                        'by_type': {}
                    }

                    for row in rows:
                        content_type = row['content_type']
                        count = row['count']

                        summary['total_items'] += count
                        summary['total_validated'] += count  # All embeddings in the table are validated
                        summary['by_type'][content_type] = {
                            'count': count,
                            'validated_count': count,
                            'avg_validation_score': 1.0  # All embeddings are considered validated
                        }

                    return summary

        except Exception as e:
            logger.error(f"Failed to get datasource training summary: {e}")
            raise

    # Vector Embedding Operations

    async def delete_embeddings_by_training_id(self, training_id: int) -> bool:
        """Delete vector embeddings associated with a training data ID"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM text2sql.vanna_embeddings
                        WHERE training_data_id = %s
                    """, (training_id,))

                    deleted_count = cursor.rowcount
                    conn.commit()

                    if deleted_count > 0:
                        logger.info(f"Deleted {deleted_count} embeddings for training data {training_id}")

                    return deleted_count > 0

        except Exception as e:
            logger.error(f"Failed to delete embeddings for training data {training_id}: {e}")
            raise

    async def get_embeddings_by_training_id(self, training_id: int) -> List[Dict[str, Any]]:
        """Get vector embeddings associated with a training data ID"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, content, content_type, content_hash, created_at, updated_at
                        FROM text2sql.vanna_embeddings
                        WHERE training_data_id = %s
                        ORDER BY created_at DESC
                    """, (training_id,))

                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get embeddings for training data {training_id}: {e}")
            raise
