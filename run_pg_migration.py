#!/usr/bin/env python3
"""
Run PostgreSQL migration to fix vanna_embeddings structure
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run the migration to fix vector dimensions"""

    # Get database configuration from environment
    db_config = {
        "host": os.getenv("DATABASE_HOST", "localhost"),
        "port": int(os.getenv("DATABASE_PORT", "5432")),
        "database": os.getenv("POSTGRES_DB", "aolei_db"),
        "user": os.getenv("POSTGRES_USER", "aolei"),
        "password": os.getenv("POSTGRES_PASSWORD", "aolei123456")
    }
    
    # Read migration SQL
    with open('src/database/migrations/006_fix_vector_dimensions.sql', 'r', encoding='utf-8') as f:
        migration_sql = f.read()

    # Connect and execute
    conn = psycopg2.connect(
        host=db_config["host"],
        port=db_config["port"],
        database=db_config["database"],
        user=db_config["user"],
        password=db_config["password"]
    )

    try:
        with conn.cursor() as cursor:
            print("Running migration: Fix vector dimensions...")
            cursor.execute(migration_sql)
            conn.commit()
            print("✅ Migration completed successfully!")
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
