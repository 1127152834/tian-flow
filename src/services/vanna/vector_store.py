# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
PgVector store implementation for Vanna AI
"""

import logging
import hashlib
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.config.settings import get_settings
from src.llms.embedding import embed_query
from src.models.text2sql import VannaEmbedding, TrainingDataType

logger = logging.getLogger(__name__)


class PgVectorStore:
    """
    PgVector vector store for Vanna AI
    
    Provides vector storage and similarity search functionality using PostgreSQL with pgvector extension
    """
    
    def __init__(self, datasource_id: int, embedding_model_id: Optional[int] = None):
        """
        Initialize PgVector store
        
        Args:
            datasource_id: Database datasource ID
            embedding_model_id: Embedding model ID (optional)
        """
        self.datasource_id = datasource_id
        self.embedding_model_id = embedding_model_id

        # Initialize database connection
        settings = get_settings()
        # Use a default database URL if not configured
        database_url = getattr(settings, 'DATABASE_URL', 'postgresql://localhost:5432/aolei_db')
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # In-memory storage for training data (following ti-flow VannaEmbedding structure)
        # In production, this would be stored in the actual database
        self._vanna_embeddings = []  # List of VannaEmbedding-like records

        logger.info(f"Initialized PgVectorStore for datasource {datasource_id}")
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate hash for content to enable incremental updates"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text (following ti-flow logic)"""
        try:
            embedding = embed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            raise

    def _calculate_cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings (following ti-flow's vec_cosine_distance logic)

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0-1, higher is more similar)
        """
        try:
            import numpy as np

            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return float(similarity)

        except Exception as e:
            logger.error(f"Failed to calculate cosine similarity: {e}")
            return 0.0
    
    def add_ddl(self, ddl: str, **kwargs) -> str:
        """
        Add DDL statement to vector store

        Args:
            ddl: DDL statement
            **kwargs: Additional metadata (database_name, table_name, etc.)

        Returns:
            Record ID
        """
        try:
            from src.config.database import get_database_connection, get_database_config
            from src.utils.sql_parser import sql_parser

            content_hash = self._generate_content_hash(ddl)
            database_name = kwargs.get('database_name')
            table_name = kwargs.get('table_name')

            # Extract table names from DDL using SQL parser
            table_names = sql_parser.extract_table_names(ddl)
            primary_table = sql_parser.get_primary_table(ddl)

            # If no table name provided and we can extract from DDL, use extracted name
            if not table_name and primary_table:
                table_name = primary_table

            # Get current database name if not provided
            if not database_name:
                db_config = get_database_config()
                database_name = db_config.get("database", "aolei_db")

            # Generate embedding for the DDL
            try:
                embedding = self._get_embedding(ddl)
                embedding_dimension = len(embedding)
                logger.info(f"Generated embedding with dimension: {embedding_dimension}")
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")
                embedding = []
                embedding_dimension = 0

            # Store in actual database
            def _store_ddl():
                with get_database_connection() as conn:
                    with conn.cursor() as cursor:
                        # Check if already exists
                        cursor.execute("""
                            SELECT id FROM text2sql.vanna_embeddings
                            WHERE datasource_id = %s AND content_hash = %s
                        """, (self.datasource_id, content_hash))

                        existing = cursor.fetchone()
                        if existing:
                            logger.debug(f"DDL already exists: {content_hash}")
                            return content_hash

                        # Prepare metadata with table information
                        import json
                        enhanced_metadata = kwargs.copy() if kwargs else {}
                        enhanced_metadata.update({
                            'all_tables': table_names,
                            'table_count': len(table_names),
                            'database_name': database_name,
                            'auto_extracted': True
                        })

                        cursor.execute("""
                            INSERT INTO text2sql.vanna_embeddings
                            (datasource_id, content_type, content, content_hash,
                             embedding_vector, table_name, metadata, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                            RETURNING id
                        """, (
                            self.datasource_id,
                            'DDL',  # Following ti-flow's VannaContentType.DDL
                            ddl,
                            content_hash,
                            embedding,
                            table_name,
                            json.dumps(enhanced_metadata)
                        ))

                        result = cursor.fetchone()
                        if result:
                            record_id = result[0] if isinstance(result, (tuple, list)) else result
                        else:
                            record_id = None

                        conn.commit()

                        logger.info(f"Added DDL embedding: {content_hash}, table: {table_name}, all_tables: {table_names}, record_id: {record_id}")
                        return content_hash

            # Run in thread to avoid blocking
            return _store_ddl()

        except Exception as e:
            logger.error(f"Failed to add DDL: {e}")
            raise
    
    def add_documentation(self, documentation: str, **kwargs) -> str:
        """
        Add documentation to vector store

        Args:
            documentation: Documentation content
            **kwargs: Additional metadata

        Returns:
            Content hash of the added documentation
        """
        try:
            from src.config.database import get_database_connection, get_database_config

            content_hash = self._generate_content_hash(documentation)

            # Get current database name
            db_config = get_database_config()
            database_name = db_config.get("database", "aolei_db")

            # Generate embedding for the documentation
            try:
                embedding = self._get_embedding(documentation)
                embedding_dimension = len(embedding) if embedding else 0
                logger.info(f"Generated embedding with dimension: {embedding_dimension}")
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")
                embedding = None
                embedding_dimension = 0

            # Store in PostgreSQL database
            with get_database_connection() as conn:
                with conn.cursor() as cursor:
                    # Check if already exists
                    cursor.execute("""
                        SELECT id FROM text2sql.vanna_embeddings
                        WHERE datasource_id = %s AND content_hash = %s
                    """, (self.datasource_id, content_hash))

                    existing = cursor.fetchone()
                    if existing:
                        logger.debug(f"Documentation already exists: {content_hash}")
                        return content_hash

                    # Prepare metadata
                    import json
                    enhanced_metadata = kwargs.copy() if kwargs else {}
                    enhanced_metadata.update({
                        'database_name': database_name,
                        'content_type': 'documentation',
                        'auto_extracted': False
                    })

                    cursor.execute("""
                        INSERT INTO text2sql.vanna_embeddings
                        (datasource_id, content_type, content, content_hash,
                         embedding_vector, metadata, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                        RETURNING id
                    """, (
                        self.datasource_id,
                        'DOCUMENTATION',  # Following ti-flow's VannaContentType.DOCUMENTATION
                        documentation,
                        content_hash,
                        embedding,
                        json.dumps(enhanced_metadata)
                    ))

                    result = cursor.fetchone()
                    if result:
                        record_id = result[0] if isinstance(result, (tuple, list)) else result
                    else:
                        record_id = None

                    conn.commit()

                    logger.info(f"Added documentation embedding: {content_hash}, record_id: {record_id}")
                    return content_hash

        except Exception as e:
            logger.error(f"Failed to add documentation: {e}")
            raise
    
    def add_question_sql(self, question: str, sql: str, **kwargs) -> str:
        """
        Add question-SQL pair to vector store (following ti-flow implementation)

        Args:
            question: Natural language question
            sql: Corresponding SQL query
            **kwargs: Additional metadata

        Returns:
            Content hash of the added Q&A pair
        """
        try:
            from src.config.database import get_database_connection, get_database_config
            from src.utils.sql_parser import sql_parser

            # Combine question and SQL for embedding (following ti-flow logic)
            combined_content = f"Question: {question}\nSQL: {sql}"
            content_hash = self._generate_content_hash(combined_content)

            # Extract table names from SQL using SQL parser
            table_names = sql_parser.extract_table_names(sql)
            primary_table = sql_parser.get_primary_table(sql)

            # Get current database name
            db_config = get_database_config()
            database_name = db_config.get("database", "aolei_db")

            # Generate embedding for the combined content (following ti-flow logic)
            try:
                embedding = self._get_embedding(combined_content)
                embedding_dimension = len(embedding) if embedding else 0
                logger.debug(f"Generated embedding with dimension: {embedding_dimension}")
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")
                embedding = None
                embedding_dimension = 0

            # Store in PostgreSQL database (adapted from ti-flow's Session logic)
            with get_database_connection() as conn:
                with conn.cursor() as cursor:
                    # Check if already exists (following ti-flow's duplicate check)
                    cursor.execute("""
                        SELECT id FROM text2sql.vanna_embeddings
                        WHERE datasource_id = %s AND content_hash = %s
                    """, (self.datasource_id, content_hash))

                    existing = cursor.fetchone()
                    if existing:
                        logger.debug(f"Question-SQL pair already exists: {content_hash}")
                        return content_hash

                    # Prepare metadata with table information
                    import json
                    enhanced_metadata = kwargs.copy() if kwargs else {}
                    enhanced_metadata.update({
                        'all_tables': table_names,
                        'table_count': len(table_names),
                        'database_name': database_name,
                        'auto_extracted': True
                    })

                    cursor.execute("""
                        INSERT INTO text2sql.vanna_embeddings
                        (datasource_id, content_type, content, content_hash,
                         question, sql_query, table_name, embedding_vector, metadata, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                        RETURNING id
                    """, (
                        self.datasource_id,
                        'SQL',  # Following ti-flow's VannaContentType.SQL
                        combined_content,  # Combined content for embedding
                        content_hash,
                        question,  # Store question separately (like ti-flow)
                        sql,       # Store SQL separately (like ti-flow)
                        primary_table,  # Store primary table name
                        embedding,
                        json.dumps(enhanced_metadata)  # Enhanced metadata with table info
                    ))

                    result = cursor.fetchone()
                    if result:
                        record_id = result[0] if isinstance(result, (tuple, list)) else result
                    else:
                        record_id = None

                    conn.commit()

                    logger.info(f"Added question-SQL embedding: {content_hash}, table: {primary_table}, all_tables: {table_names}, record_id: {record_id}")
                    return content_hash

        except Exception as e:
            logger.error(f"Failed to add question-SQL: {e}")
            raise
    
    def get_similar_ddl(self, question: str, **kwargs) -> List[str]:
        """
        Get similar DDL statements for a question from actual database training data

        Args:
            question: Natural language question
            **kwargs: Additional parameters (limit, threshold, etc.)

        Returns:
            List of similar DDL statements from actual database
        """
        try:
            limit = kwargs.get('limit', 5)

            # Generate embedding for the question
            embedding = self._get_embedding(question)
            if not embedding:
                logger.warning(f"Failed to generate embedding for question: {question}")
                return self._get_all_ddl_statements(limit)

            # Query database for DDL training data using vector similarity
            import psycopg2
            from psycopg2.extras import RealDictCursor
            from src.config.database import get_database_config

            db_config = get_database_config()

            try:
                conn = psycopg2.connect(
                    host=db_config["host"],
                    port=db_config["port"],
                    database=db_config["database"],
                    user=db_config["user"],
                    password=db_config["password"],
                    cursor_factory=RealDictCursor
                )

                with conn.cursor() as cursor:
                    # Use pgvector similarity search for DDL content
                    cursor.execute("""
                        SELECT content
                        FROM text2sql.vanna_embeddings
                        WHERE datasource_id = %s
                        AND content_type = 'DDL'
                        AND content IS NOT NULL
                        AND embedding_vector IS NOT NULL
                        ORDER BY embedding_vector <=> %s::vector
                        LIMIT %s
                    """, (self.datasource_id, embedding, limit))

                    results = cursor.fetchall()
                    similar_ddls = [row['content'] for row in results if row['content']]

                    if similar_ddls:
                        logger.info(f"Found {len(similar_ddls)} similar DDL statements using vector similarity")
                        return similar_ddls
                    else:
                        # Fallback: get all DDL statements if no vector matches
                        logger.info("No vector matches found, falling back to all DDL statements")
                        return self._get_all_ddl_statements(limit)

            except Exception as e:
                logger.error(f"Database query failed: {e}")
                return self._get_all_ddl_statements(limit)
            finally:
                if 'conn' in locals():
                    conn.close()

        except Exception as e:
            logger.error(f"Failed to get similar DDL: {e}")
            return []

    def _get_all_ddl_statements(self, limit: int = 5) -> List[str]:
        """Get all DDL statements for the datasource as fallback"""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            from src.config.database import get_database_config

            db_config = get_database_config()

            conn = psycopg2.connect(
                host=db_config["host"],
                port=db_config["port"],
                database=db_config["database"],
                user=db_config["user"],
                password=db_config["password"],
                cursor_factory=RealDictCursor
            )

            with conn.cursor() as cursor:
                # Get all DDL statements for this datasource
                cursor.execute("""
                    SELECT content
                    FROM text2sql.vanna_embeddings
                    WHERE datasource_id = %s
                    AND content_type = 'DDL'
                    AND content IS NOT NULL
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (self.datasource_id, limit))

                results = cursor.fetchall()
                ddl_statements = [row['content'] for row in results if row['content']]

                logger.info(f"Retrieved {len(ddl_statements)} DDL statements as fallback")
                return ddl_statements

        except Exception as e:
            logger.error(f"Failed to get all DDL statements: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()
    
    def get_similar_question_sql(self, question: str, **kwargs) -> List[str]:
        """
        Get similar question-SQL pairs based on question (following ti-flow logic exactly)

        Args:
            question: Natural language question
            **kwargs: Additional parameters (limit, etc.)

        Returns:
            List of similar SQL queries
        """
        try:
            # Generate embedding for the question (following ti-flow logic)
            embedding = self._get_embedding(question)
            if not embedding:
                logger.warning(f"Failed to generate embedding for question: {question}")
                return []

            limit = kwargs.get('limit', 3)

            # Query database directly for SQL training data (like ti-flow)
            import psycopg2
            from psycopg2.extras import RealDictCursor
            from src.config.database import get_database_config

            db_config = get_database_config()

            try:
                conn = psycopg2.connect(
                    host=db_config["host"],
                    port=db_config["port"],
                    database=db_config["database"],
                    user=db_config["user"],
                    password=db_config["password"],
                    cursor_factory=RealDictCursor
                )

                with conn.cursor() as cursor:
                    # Use pgvector similarity search (similar to ti-flow's vec_cosine_distance)
                    cursor.execute("""
                        SELECT sql_query
                        FROM text2sql.vanna_embeddings
                        WHERE datasource_id = %s
                        AND content_type = 'SQL'
                        AND sql_query IS NOT NULL
                        AND embedding_vector IS NOT NULL
                        ORDER BY embedding_vector <=> %s::vector
                        LIMIT %s
                    """, (self.datasource_id, embedding, limit))

                    results = cursor.fetchall()
                    similar_sqls = [row['sql_query'] for row in results if row['sql_query']]

                    logger.info(f"Found {len(similar_sqls)} similar SQL queries using vector similarity for question: {question[:50]}...")
                    return similar_sqls

            except Exception as e:
                logger.error(f"Database query failed: {e}")
                # Fallback to in-memory search if database fails
                return self._fallback_similarity_search(question, limit)
            finally:
                if 'conn' in locals():
                    conn.close()

        except Exception as e:
            logger.error(f"Failed to get similar question SQL: {e}")
            return []

    def _fallback_similarity_search(self, question: str, limit: int = 3) -> List[str]:
        """Fallback similarity search using in-memory data"""
        try:
            # Search in our in-memory VannaEmbedding records
            sql_records = [
                record for record in self._vanna_embeddings
                if record["content_type"] == "SQL"
                and record.get("sql_query")
                and record.get("embedding")
            ]

            if not sql_records:
                logger.info(f"No SQL training data found for fallback similarity search")
                return []

            # For fallback, just return the first few SQL queries
            similar_sqls = [record["sql_query"] for record in sql_records[:limit]]
            logger.info(f"Fallback: Found {len(similar_sqls)} SQL queries for question: {question[:50]}...")
            return similar_sqls

        except Exception as e:
            logger.error(f"Fallback similarity search failed: {e}")
            return []
    
    def remove_training_data(self, id: str) -> bool:
        """
        Remove training data by ID or content hash

        Args:
            id: Record ID or content hash

        Returns:
            True if successful, False otherwise
        """
        try:
            from src.config.database import get_database_connection

            logger.info(f"Removing training data with ID/hash: {id}")

            with get_database_connection() as conn:
                with conn.cursor() as cursor:
                    # Try to remove by record ID first
                    cursor.execute("""
                        DELETE FROM text2sql.vanna_embeddings
                        WHERE datasource_id = %s AND id = %s
                    """, (self.datasource_id, id))

                    rows_affected = cursor.rowcount

                    # If no rows affected, try to remove by content hash
                    if rows_affected == 0:
                        cursor.execute("""
                            DELETE FROM text2sql.vanna_embeddings
                            WHERE datasource_id = %s AND content_hash = %s
                        """, (self.datasource_id, id))

                        rows_affected = cursor.rowcount

                    conn.commit()

                    if rows_affected > 0:
                        logger.info(f"Successfully removed {rows_affected} training data record(s) with ID/hash: {id}")
                        return True
                    else:
                        logger.warning(f"No training data found with ID/hash: {id}")
                        return False

        except Exception as e:
            logger.error(f"Failed to remove training data: {e}")
            return False

    def remove_training_data_by_type(self, content_type: str) -> int:
        """
        Remove all training data of a specific type

        Args:
            content_type: Content type ('DDL', 'SQL', 'DOCUMENTATION')

        Returns:
            Number of records removed
        """
        try:
            from src.config.database import get_database_connection

            logger.info(f"Removing all training data of type: {content_type}")

            with get_database_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM text2sql.vanna_embeddings
                        WHERE datasource_id = %s AND content_type = %s
                    """, (self.datasource_id, content_type))

                    rows_affected = cursor.rowcount
                    conn.commit()

                    logger.info(f"Successfully removed {rows_affected} training data records of type: {content_type}")
                    return rows_affected

        except Exception as e:
            logger.error(f"Failed to remove training data by type: {e}")
            return 0

    def get_training_data_stats(self) -> Dict[str, int]:
        """
        Get statistics about training data

        Returns:
            Dictionary with counts by content type
        """
        try:
            from src.config.database import get_database_connection

            with get_database_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT content_type, COUNT(*) as count
                        FROM text2sql.vanna_embeddings
                        WHERE datasource_id = %s
                        GROUP BY content_type
                    """, (self.datasource_id,))

                    stats = {}
                    for row in cursor.fetchall():
                        stats[row[0]] = row[1]

                    # Add total count
                    stats['TOTAL'] = sum(stats.values())

                    logger.info(f"Training data stats: {stats}")
                    return stats

        except Exception as e:
            logger.error(f"Failed to get training data stats: {e}")
            return {}
