#!/usr/bin/env python3
"""
Check database structure and data
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_database():
    """Check database structure and data"""
    
    # Get database configuration from environment
    db_config = {
        "host": os.getenv("DATABASE_HOST", "localhost"),
        "port": int(os.getenv("DATABASE_PORT", "5432")),
        "database": os.getenv("POSTGRES_DB", "aolei_db"),
        "user": os.getenv("POSTGRES_USER", "aolei"),
        "password": os.getenv("POSTGRES_PASSWORD", "aolei123456")
    }
    
    # Connect and check
    conn = psycopg2.connect(
        host=db_config["host"],
        port=db_config["port"],
        database=db_config["database"],
        user=db_config["user"],
        password=db_config["password"],
        cursor_factory=RealDictCursor
    )
    
    try:
        with conn.cursor() as cursor:
            print("=== Checking vanna_embeddings table structure ===")
            cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_schema = 'text2sql' AND table_name = 'vanna_embeddings'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
            
            print("\n=== Sample data from vanna_embeddings ===")
            cursor.execute("""
                SELECT id, content_type, content, question, sql_query, table_name
                FROM text2sql.vanna_embeddings 
                ORDER BY created_at DESC 
                LIMIT 3
            """)
            rows = cursor.fetchall()
            for row in rows:
                print(f"ID: {row['id']}")
                print(f"  Type: {row['content_type']}")
                print(f"  Content: {row['content'][:100]}...")
                print(f"  Question: {row['question']}")
                print(f"  SQL Query: {row['sql_query']}")
                print(f"  Table Name: {row['table_name']}")
                print()
                
    finally:
        conn.close()

if __name__ == "__main__":
    check_database()
