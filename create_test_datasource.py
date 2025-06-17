#!/usr/bin/env python3
"""
Create test datasource for SQL validation testing
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.database import get_database_connection

async def create_test_datasource():
    """Create a test datasource"""
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                # First check if the table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'database_management'
                        AND table_name = 'database_datasources'
                    )
                """)

                table_exists = cursor.fetchone()[0]
                if not table_exists:
                    print("database_management.database_datasources table does not exist")
                    print("Please run database migrations first")
                    return None

                # Check if datasource already exists
                cursor.execute("""
                    SELECT id FROM database_management.database_datasources
                    WHERE name = 'Test Database'
                """)

                existing = cursor.fetchone()
                if existing:
                    print(f"Test datasource already exists with ID: {existing[0]}")
                    return existing[0]
                
                # Create test datasource
                cursor.execute("""
                    INSERT INTO database_management.database_datasources
                    (name, database_type, host, port, database_name, username, password, readonly_mode, allowed_operations, connection_status, created_at, updated_at)
                    VALUES
                    ('Test Database', 'POSTGRESQL', 'localhost', 5432, 'aolei_db', 'aolei', 'aolei123456', true, ARRAY['SELECT'], 'DISCONNECTED', NOW(), NOW())
                    RETURNING id
                """)
                
                result = cursor.fetchone()
                datasource_id = result[0]
                conn.commit()
                
                print(f"Created test datasource with ID: {datasource_id}")
                
                # Add some test DDL training data
                cursor.execute("""
                    INSERT INTO text2sql.vanna_embeddings
                    (datasource_id, content_type, content, content_hash, table_name, metadata, created_at, updated_at)
                    VALUES 
                    (%s, 'DDL', 'CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(100), email VARCHAR(100), created_at TIMESTAMP)', 
                     'test_users_ddl', 'users', '{"database_name": "aolei_db"}', NOW(), NOW()),
                    (%s, 'DDL', 'CREATE TABLE orders (id SERIAL PRIMARY KEY, user_id INTEGER, amount DECIMAL(10,2), status VARCHAR(50), created_at TIMESTAMP)', 
                     'test_orders_ddl', 'orders', '{"database_name": "aolei_db"}', NOW(), NOW()),
                    (%s, 'SQL', 'SELECT * FROM users WHERE email LIKE %email%', 
                     'test_sql_1', 'users', '{"question": "查询用户邮箱", "database_name": "aolei_db"}', NOW(), NOW())
                    ON CONFLICT (content_hash) DO NOTHING
                """, (datasource_id, datasource_id, datasource_id))
                
                conn.commit()
                print("Added test training data")
                
                return datasource_id
                
    except Exception as e:
        print(f"Error creating test datasource: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    datasource_id = asyncio.run(create_test_datasource())
    if datasource_id:
        print(f"\nTest datasource created successfully!")
        print(f"You can now test with datasource_id: {datasource_id}")
    else:
        print("Failed to create test datasource")
