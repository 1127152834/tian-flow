# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Database configuration for deer-flow.
Handles PostgreSQL connections with pgvector support.
"""

import os
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://aolei:aolei123456@localhost:5432/aolei_db"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_database_config():
    """
    Get database connection configuration as a dictionary.
    """
    # Parse DATABASE_URL to get connection parameters
    url_parts = DATABASE_URL.replace("postgresql+psycopg2://", "").split("@")
    user_pass = url_parts[0].split(":")
    host_db = url_parts[1].split("/")
    host_port = host_db[0].split(":")

    return {
        "host": host_port[0],
        "port": int(host_port[1]) if len(host_port) > 1 else 5432,
        "database": host_db[1],
        "user": user_pass[0],
        "password": user_pass[1]
    }


def get_database_connection():
    """
    Get a direct psycopg2 connection for raw SQL operations.
    Useful for pgvector operations and complex queries.
    """
    config = get_database_config()

    return psycopg2.connect(
        host=config["host"],
        port=config["port"],
        database=config["database"],
        user=config["user"],
        password=config["password"],
        cursor_factory=RealDictCursor
    )


def get_db_session():
    """
    Get a SQLAlchemy database session.
    Use this for ORM operations.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_database_connection() -> bool:
    """
    Test if the database connection is working.
    Returns True if successful, False otherwise.
    """
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False


def test_pgvector_extension() -> bool:
    """
    Test if pgvector extension is available.
    Returns True if available, False otherwise.
    """
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'vector'")
                result = cursor.fetchone()
                return result is not None
    except Exception as e:
        print(f"pgvector extension test failed: {e}")
        return False


def initialize_database():
    """
    Initialize database tables and extensions.
    This should be called on application startup.
    """
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Test connections
        if not test_database_connection():
            raise Exception("Database connection test failed")
            
        if not test_pgvector_extension():
            print("Warning: pgvector extension not found. Vector operations may not work.")
            
        print("Database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False


def execute_vector_search(
    table_name: str,
    embedding_column: str,
    query_embedding: list,
    limit: int = 10,
    similarity_threshold: float = 0.7
) -> list:
    """
    Execute a vector similarity search using pgvector.
    
    Args:
        table_name: Name of the table to search
        embedding_column: Name of the embedding column
        query_embedding: Query vector as a list of floats
        limit: Maximum number of results to return
        similarity_threshold: Minimum similarity score (0-1)
    
    Returns:
        List of matching records with similarity scores
    """
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                # Convert embedding to pgvector format
                embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
                
                query = f"""
                SELECT *, 
                       1 - ({embedding_column} <=> %s::vector) as similarity_score
                FROM {table_name}
                WHERE 1 - ({embedding_column} <=> %s::vector) >= %s
                ORDER BY {embedding_column} <=> %s::vector
                LIMIT %s
                """
                
                cursor.execute(query, (
                    embedding_str, 
                    embedding_str, 
                    similarity_threshold,
                    embedding_str,
                    limit
                ))
                
                return cursor.fetchall()
                
    except Exception as e:
        print(f"Vector search failed: {e}")
        return []


def insert_with_embedding(
    table_name: str,
    data: dict,
    embedding_column: str,
    embedding: list
) -> Optional[int]:
    """
    Insert a record with an embedding vector.
    
    Args:
        table_name: Name of the table
        data: Dictionary of column names and values
        embedding_column: Name of the embedding column
        embedding: Embedding vector as a list of floats
    
    Returns:
        ID of the inserted record, or None if failed
    """
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                # Add embedding to data
                data[embedding_column] = "[" + ",".join(map(str, embedding)) + "]"
                
                # Build INSERT query
                columns = list(data.keys())
                placeholders = ["%s"] * len(columns)
                values = list(data.values())
                
                query = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                RETURNING id
                """
                
                cursor.execute(query, values)
                result = cursor.fetchone()
                conn.commit()
                
                return result['id'] if result else None
                
    except Exception as e:
        print(f"Insert with embedding failed: {e}")
        return None


# Export commonly used functions
__all__ = [
    'DATABASE_URL',
    'engine',
    'SessionLocal',
    'Base',
    'get_database_connection',
    'get_db_session',
    'test_database_connection',
    'test_pgvector_extension',
    'initialize_database',
    'execute_vector_search',
    'insert_with_embedding'
]
