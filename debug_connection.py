#!/usr/bin/env python3
"""
Debug database connection for Text2SQL repository.
"""

import sys
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.database import get_database_config


def debug_connection():
    """Debug database connection and schema"""
    
    print("🔍 Debugging database connection...")
    
    try:
        # Get config
        db_config = get_database_config()
        print(f"📋 Database config: {db_config}")
        
        # Test connection
        conn = psycopg2.connect(
            host=db_config["host"],
            port=db_config["port"],
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"],
            cursor_factory=RealDictCursor
        )
        
        print("✅ Connection successful")
        
        with conn.cursor() as cursor:
            # Check current database
            cursor.execute("SELECT current_database()")
            current_db = cursor.fetchone()['current_database']
            print(f"📊 Current database: {current_db}")
            
            # Check schemas
            cursor.execute("SELECT schema_name FROM information_schema.schemata ORDER BY schema_name")
            schemas = [row['schema_name'] for row in cursor.fetchall()]
            print(f"📁 Available schemas: {schemas}")
            
            # Check text2sql schema specifically
            if 'text2sql' in schemas:
                print("✅ text2sql schema found")
                
                # Check tables in text2sql schema
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'text2sql'
                    ORDER BY table_name
                """)
                tables = [row['table_name'] for row in cursor.fetchall()]
                print(f"📋 Tables in text2sql schema: {tables}")
                
                # Test a simple query on query_history table
                if 'query_history' in tables:
                    cursor.execute("SELECT COUNT(*) as count FROM text2sql.query_history")
                    count = cursor.fetchone()['count']
                    print(f"📊 Records in query_history: {count}")
                else:
                    print("❌ query_history table not found")
            else:
                print("❌ text2sql schema not found")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    debug_connection()
