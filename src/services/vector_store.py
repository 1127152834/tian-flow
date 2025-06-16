# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Vector store service for DeerFlow Text2SQL.

Provides pgvector-based vector storage and similarity search for training data embeddings.
Adapted from ti-flow but uses PostgreSQL with pgvector extension instead of TiDB.
"""

import logging
import asyncio
from typing import List, Optional, Dict, Any, Tuple
import json
import numpy as np
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.pool

from src.config.database import get_database_config, get_database_connection
from src.models.text2sql import VannaEmbedding, TrainingDataType

logger = logging.getLogger(__name__)


class PgVectorStore:
    """PostgreSQL with pgvector extension for vector storage"""
    
    def __init__(self):
        self._connection_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            # Get database connection info
            db_config = get_database_config()

            self._connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                host=db_config["host"],
                port=db_config["port"],
                database=db_config["database"],
                user=db_config["user"],
                password=db_config["password"]
            )
            
            # Ensure pgvector extension and tables exist
            asyncio.create_task(self._ensure_schema())
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store connection pool: {e}")
            raise
    
    async def _ensure_schema(self):
        """Ensure pgvector extension and required tables exist"""
        try:
            connection = self._connection_pool.getconn()
            try:
                with connection.cursor() as cursor:
                    # Enable pgvector extension
                    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                    
                    # Create text2sql schema if not exists
                    cursor.execute("CREATE SCHEMA IF NOT EXISTS text2sql;")
                    
                    # Create embeddings table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS text2sql.vanna_embeddings (
                            id SERIAL PRIMARY KEY,
                            datasource_id INTEGER NOT NULL,
                            content TEXT NOT NULL,
                            content_type VARCHAR(50) NOT NULL,
                            embedding_vector vector(1024),  -- Assuming 1024 dimensions
                            metadata JSONB,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        );
                    """)
                    
                    # Create indexes for better performance
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_vanna_embeddings_datasource 
                        ON text2sql.vanna_embeddings(datasource_id);
                    """)
                    
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_vanna_embeddings_content_type 
                        ON text2sql.vanna_embeddings(content_type);
                    """)
                    
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_vanna_embeddings_vector 
                        ON text2sql.vanna_embeddings 
                        USING ivfflat (embedding_vector vector_cosine_ops)
                        WITH (lists = 100);
                    """)
                    
                    connection.commit()
                    logger.info("✅ Vector store schema initialized successfully")
                    
            finally:
                self._connection_pool.putconn(connection)
                
        except Exception as e:
            logger.error(f"Failed to ensure vector store schema: {e}")
            raise
    
    async def add_embedding(
        self,
        datasource_id: int,
        content: str,
        content_type: TrainingDataType,
        embedding_vector: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Add embedding to vector store"""
        try:
            connection = self._connection_pool.getconn()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO text2sql.vanna_embeddings 
                        (datasource_id, content, content_type, embedding_vector, metadata)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id;
                    """, (
                        datasource_id,
                        content,
                        content_type.value,
                        embedding_vector,
                        json.dumps(metadata) if metadata else None
                    ))
                    
                    embedding_id = cursor.fetchone()[0]
                    connection.commit()
                    
                    logger.debug(f"Added embedding {embedding_id} for datasource {datasource_id}")
                    return embedding_id
                    
            finally:
                self._connection_pool.putconn(connection)
                
        except Exception as e:
            logger.error(f"Failed to add embedding: {e}")
            raise
    
    async def search_similar(
        self,
        datasource_id: int,
        query_vector: List[float],
        content_type: Optional[TrainingDataType] = None,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Tuple[VannaEmbedding, float]]:
        """Search for similar embeddings"""
        try:
            connection = self._connection_pool.getconn()
            try:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Build query with optional content type filter
                    where_clause = "WHERE datasource_id = %s"
                    params = [datasource_id]
                    
                    if content_type:
                        where_clause += " AND content_type = %s"
                        params.append(content_type.value)
                    
                    # Use cosine similarity for search
                    query = f"""
                        SELECT 
                            id, datasource_id, content, content_type, 
                            embedding_vector, metadata, created_at,
                            1 - (embedding_vector <=> %s) as similarity
                        FROM text2sql.vanna_embeddings
                        {where_clause}
                        AND 1 - (embedding_vector <=> %s) >= %s
                        ORDER BY embedding_vector <=> %s
                        LIMIT %s;
                    """
                    
                    params.extend([query_vector, query_vector, similarity_threshold, query_vector, limit])
                    cursor.execute(query, params)
                    
                    results = []
                    for row in cursor.fetchall():
                        embedding = VannaEmbedding(
                            id=row['id'],
                            datasource_id=row['datasource_id'],
                            content=row['content'],
                            content_type=TrainingDataType(row['content_type']),
                            embedding_vector=row['embedding_vector'],
                            metadata=row['metadata'],
                            created_at=row['created_at']
                        )
                        similarity = float(row['similarity'])
                        results.append((embedding, similarity))
                    
                    logger.debug(f"Found {len(results)} similar embeddings for datasource {datasource_id}")
                    return results
                    
            finally:
                self._connection_pool.putconn(connection)
                
        except Exception as e:
            logger.error(f"Failed to search similar embeddings: {e}")
            raise
    
    async def delete_embeddings(
        self,
        datasource_id: int,
        content_type: Optional[TrainingDataType] = None
    ) -> int:
        """Delete embeddings for a datasource"""
        try:
            connection = self._connection_pool.getconn()
            try:
                with connection.cursor() as cursor:
                    if content_type:
                        cursor.execute("""
                            DELETE FROM text2sql.vanna_embeddings 
                            WHERE datasource_id = %s AND content_type = %s;
                        """, (datasource_id, content_type.value))
                    else:
                        cursor.execute("""
                            DELETE FROM text2sql.vanna_embeddings 
                            WHERE datasource_id = %s;
                        """, (datasource_id,))
                    
                    deleted_count = cursor.rowcount
                    connection.commit()
                    
                    logger.info(f"Deleted {deleted_count} embeddings for datasource {datasource_id}")
                    return deleted_count
                    
            finally:
                self._connection_pool.putconn(connection)
                
        except Exception as e:
            logger.error(f"Failed to delete embeddings: {e}")
            raise
    
    async def get_embeddings_count(
        self,
        datasource_id: int,
        content_type: Optional[TrainingDataType] = None
    ) -> int:
        """Get count of embeddings for a datasource"""
        try:
            connection = self._connection_pool.getconn()
            try:
                with connection.cursor() as cursor:
                    if content_type:
                        cursor.execute("""
                            SELECT COUNT(*) FROM text2sql.vanna_embeddings 
                            WHERE datasource_id = %s AND content_type = %s;
                        """, (datasource_id, content_type.value))
                    else:
                        cursor.execute("""
                            SELECT COUNT(*) FROM text2sql.vanna_embeddings 
                            WHERE datasource_id = %s;
                        """, (datasource_id,))
                    
                    count = cursor.fetchone()[0]
                    return count
                    
            finally:
                self._connection_pool.putconn(connection)
                
        except Exception as e:
            logger.error(f"Failed to get embeddings count: {e}")
            raise
    
    async def close(self):
        """Close connection pool"""
        if self._connection_pool:
            self._connection_pool.closeall()
            logger.info("Vector store connection pool closed")


# Global vector store instance
_vector_store: Optional[PgVectorStore] = None


def get_vector_store() -> PgVectorStore:
    """Get global vector store instance"""
    global _vector_store
    if _vector_store is None:
        _vector_store = PgVectorStore()
    return _vector_store
