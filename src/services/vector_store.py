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
import hashlib

import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.pool

from src.config.database import get_database_config, get_database_connection
from src.models.text2sql import VannaEmbedding, TrainingDataType
from src.llms.embedding import embed_query, embed_texts, get_embedding_dimension
from src.llms.reranker import rerank_with_metadata

logger = logging.getLogger(__name__)


class PgVectorStore:
    """PostgreSQL with pgvector extension for vector storage"""
    
    def __init__(self):
        self._connection_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        self._schema_initialized = False

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

            logger.info("✅ Vector store connection pool initialized")

        except Exception as e:
            logger.error(f"Failed to initialize vector store connection pool: {e}")
            raise

    async def _ensure_initialized(self):
        """Ensure connection pool and schema are initialized"""
        if self._connection_pool is None:
            self._initialize_pool()

        if not self._schema_initialized:
            await self._ensure_schema()
            self._schema_initialized = True
    
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
    
    def _generate_content_hash(self, content: str, datasource_id: int) -> str:
        """Generate hash for content deduplication"""
        content_str = f"{datasource_id}:{content}"
        return hashlib.sha256(content_str.encode()).hexdigest()

    async def add_embedding(
        self,
        datasource_id: int,
        content: str,
        content_type: TrainingDataType,
        embedding_vector: List[float],
        metadata: Optional[Dict[str, Any]] = None,
        training_data_id: Optional[int] = None
    ) -> int:
        """Add embedding to vector store with content hash for deduplication"""
        try:
            await self._ensure_initialized()
            content_hash = self._generate_content_hash(content, datasource_id)

            connection = self._connection_pool.getconn()
            try:
                with connection.cursor() as cursor:
                    # Check if embedding with this content_hash already exists
                    cursor.execute("""
                        SELECT id FROM text2sql.vanna_embeddings
                        WHERE datasource_id = %s AND content_hash = %s
                    """, (datasource_id, content_hash))

                    existing = cursor.fetchone()
                    if existing:
                        logger.debug(f"Embedding already exists for content_hash {content_hash[:16]}...")
                        return existing[0]

                    # Insert new embedding
                    cursor.execute("""
                        INSERT INTO text2sql.vanna_embeddings
                        (datasource_id, content, content_type, embedding_vector, metadata, content_hash, training_data_id, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id;
                    """, (
                        datasource_id,
                        content,
                        content_type.value,
                        embedding_vector,
                        json.dumps(metadata) if metadata else None,
                        content_hash,
                        training_data_id,
                        datetime.now(timezone.utc)
                    ))

                    embedding_id = cursor.fetchone()[0]
                    connection.commit()

                    logger.debug(f"Added new embedding {embedding_id} for datasource {datasource_id}")
                    return embedding_id

            finally:
                self._connection_pool.putconn(connection)

        except Exception as e:
            logger.error(f"Failed to add embedding: {e}")
            raise

    async def update_embedding(
        self,
        datasource_id: int,
        content: str,
        content_type: TrainingDataType,
        embedding_vector: List[float],
        metadata: Optional[Dict[str, Any]] = None,
        training_data_id: Optional[int] = None
    ) -> int:
        """Update existing embedding or create new one if not exists"""
        try:
            await self._ensure_initialized()
            content_hash = self._generate_content_hash(content, datasource_id)

            connection = self._connection_pool.getconn()
            try:
                with connection.cursor() as cursor:
                    # Try to update existing embedding
                    cursor.execute("""
                        UPDATE text2sql.vanna_embeddings
                        SET content = %s, content_type = %s, embedding_vector = %s,
                            metadata = %s, training_data_id = %s, updated_at = %s
                        WHERE datasource_id = %s AND content_hash = %s
                        RETURNING id;
                    """, (
                        content,
                        content_type.value,
                        embedding_vector,
                        json.dumps(metadata) if metadata else None,
                        training_data_id,
                        datetime.now(timezone.utc),
                        datasource_id,
                        content_hash
                    ))

                    result = cursor.fetchone()
                    if result:
                        embedding_id = result[0]
                        connection.commit()
                        logger.debug(f"Updated embedding {embedding_id} for content_hash {content_hash[:16]}...")
                        return embedding_id
                    else:
                        # If no existing embedding found, create new one
                        return await self.add_embedding(
                            datasource_id=datasource_id,
                            content=content,
                            content_type=content_type,
                            embedding_vector=embedding_vector,
                            metadata=metadata,
                            training_data_id=training_data_id
                        )

            finally:
                self._connection_pool.putconn(connection)

        except Exception as e:
            logger.error(f"Failed to update embedding: {e}")
            raise

    async def check_embedding_exists(
        self,
        datasource_id: int,
        content: str
    ) -> Optional[int]:
        """Check if embedding exists for given content"""
        try:
            await self._ensure_initialized()
            content_hash = self._generate_content_hash(content, datasource_id)

            connection = self._connection_pool.getconn()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id FROM text2sql.vanna_embeddings
                        WHERE datasource_id = %s AND content_hash = %s
                    """, (datasource_id, content_hash))

                    result = cursor.fetchone()
                    return result[0] if result else None

            finally:
                self._connection_pool.putconn(connection)

        except Exception as e:
            logger.error(f"Failed to check embedding existence: {e}")
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
            await self._ensure_initialized()
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

    async def search_similar_by_text(
        self,
        datasource_id: int,
        query_text: str,
        content_type: Optional[TrainingDataType] = None,
        limit: int = 5,
        similarity_threshold: float = 0.7,
        use_rerank: bool = True
    ) -> List[Tuple[VannaEmbedding, float]]:
        """
        Search for similar embeddings using query text with optional reranking.
        This method generates an embedding for the query text and searches for similar content.
        """
        try:
            # Generate embedding for the query using configured embedding model
            try:
                query_embedding = embed_query(query_text, "BASE_EMBEDDING")
                logger.debug(f"Generated query embedding (dim: {len(query_embedding)})")
            except Exception as e:
                logger.warning(f"Failed to generate query embedding, falling back to simple embedding: {e}")
                query_embedding = self._generate_simple_embedding(query_text)

            # Get initial candidates using vector similarity
            search_limit = limit * 3 if use_rerank else limit
            candidates = await self.search_similar(
                datasource_id=datasource_id,
                query_vector=query_embedding,
                content_type=content_type,
                limit=search_limit,
                similarity_threshold=similarity_threshold
            )

            # Apply reranking if enabled and we have candidates
            if use_rerank and candidates and len(candidates) > 1:
                try:
                    # Prepare documents for reranking
                    documents_with_metadata = []
                    for emb, sim_score in candidates:
                        documents_with_metadata.append({
                            "content": emb.content,
                            "embedding_obj": emb,
                            "similarity_score": sim_score
                        })

                    # Rerank using configured rerank model
                    reranked = rerank_with_metadata(
                        query=query_text,
                        documents_with_metadata=documents_with_metadata,
                        text_field="content",
                        model_type="BASE_RERANK",
                        top_k=limit
                    )

                    # Extract reranked embeddings with combined scores
                    results = []
                    for doc in reranked:
                        emb = doc["embedding_obj"]
                        rerank_score = doc.get("rerank_score", 0.0)
                        similarity_score = doc.get("similarity_score", 0.0)
                        # Combine scores: 70% rerank + 30% similarity
                        combined_score = 0.7 * rerank_score + 0.3 * similarity_score
                        results.append((emb, combined_score))

                    logger.debug(f"Reranked {len(candidates)} candidates to {len(results)} results")
                    return results

                except Exception as e:
                    logger.warning(f"Reranking failed, using vector similarity results: {e}")
                    return candidates[:limit]
            else:
                return candidates[:limit]

        except Exception as e:
            logger.error(f"Failed to search similar embeddings by text: {e}")
            raise

    async def delete_embeddings(
        self,
        datasource_id: int,
        content_type: Optional[TrainingDataType] = None
    ) -> int:
        """Delete embeddings for a datasource"""
        try:
            await self._ensure_initialized()
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
            await self._ensure_initialized()
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

    def _generate_simple_embedding(self, text: str, dimension: int = 1024) -> List[float]:
        """
        Generate a simple hash-based embedding for text.
        This is a placeholder implementation for development/testing.
        In production, you should use a proper embedding model like OpenAI, Sentence Transformers, etc.
        """
        # Create a hash of the text
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()

        # Convert hash to numbers and normalize
        hash_numbers = [ord(c) for c in text_hash[:dimension//8]]

        # Pad or truncate to desired dimension
        while len(hash_numbers) < dimension:
            hash_numbers.extend(hash_numbers[:min(len(hash_numbers), dimension - len(hash_numbers))])

        hash_numbers = hash_numbers[:dimension]

        # Normalize to [-1, 1] range
        embedding = [(x - 128) / 128.0 for x in hash_numbers]

        # Add some randomness based on text length and content
        text_len_factor = len(text) / 1000.0
        for i in range(len(embedding)):
            embedding[i] += (hash(text + str(i)) % 100 - 50) / 10000.0 * text_len_factor

        # Normalize the vector
        magnitude = sum(x*x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]

        return embedding

    async def add_training_data(
        self,
        datasource_id: int,
        content: str,
        content_type: TrainingDataType,
        metadata: Optional[Dict[str, Any]] = None,
        training_data_id: Optional[int] = None,
        force_update: bool = False
    ) -> int:
        """
        Add training data with generated embedding.
        This method generates an embedding for the content and stores it.
        Supports incremental updates based on content hash.
        """
        try:
            # Check if embedding already exists (unless force_update is True)
            if not force_update:
                existing_id = await self.check_embedding_exists(datasource_id, content)
                if existing_id:
                    logger.debug(f"Embedding already exists for content, skipping generation")
                    return existing_id

            # Generate embedding for the content using configured embedding model
            try:
                embedding_vector = embed_query(content, "BASE_EMBEDDING")
                logger.debug(f"Generated embedding for content (dim: {len(embedding_vector)})")
            except Exception as e:
                logger.warning(f"Failed to generate embedding, falling back to simple embedding: {e}")
                embedding_vector = self._generate_simple_embedding(content)

            # Add or update the embedding in the vector store
            if force_update:
                embedding_id = await self.update_embedding(
                    datasource_id=datasource_id,
                    content=content,
                    content_type=content_type,
                    embedding_vector=embedding_vector,
                    metadata=metadata,
                    training_data_id=training_data_id
                )
            else:
                embedding_id = await self.add_embedding(
                    datasource_id=datasource_id,
                    content=content,
                    content_type=content_type,
                    embedding_vector=embedding_vector,
                    metadata=metadata,
                    training_data_id=training_data_id
                )

            logger.debug(f"Added/updated training data embedding {embedding_id} for datasource {datasource_id}")
            return embedding_id

        except Exception as e:
            logger.error(f"Failed to add training data: {e}")
            raise

    async def build_index(self, datasource_id: int):
        """
        Build or rebuild vector index for a datasource.
        This is a placeholder for index optimization.
        """
        try:
            connection = self._connection_pool.getconn()
            try:
                with connection.cursor() as cursor:
                    # Refresh the vector index statistics
                    cursor.execute("""
                        ANALYZE text2sql.vanna_embeddings;
                    """)

                    # Get count of embeddings for this datasource
                    cursor.execute("""
                        SELECT COUNT(*) FROM text2sql.vanna_embeddings
                        WHERE datasource_id = %s;
                    """, (datasource_id,))

                    count = cursor.fetchone()[0]
                    connection.commit()

                    logger.info(f"Built vector index for datasource {datasource_id} with {count} embeddings")

            finally:
                self._connection_pool.putconn(connection)

        except Exception as e:
            logger.error(f"Failed to build vector index: {e}")
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
