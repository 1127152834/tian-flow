#!/usr/bin/env python3
"""
Verify Text2SQL database schema creation.
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def verify_schema():
    """Verify that Text2SQL schema and tables were created correctly"""
    
    # Get database configuration from environment
    db_config = {
        "host": os.getenv("DATABASE_HOST", "localhost"),
        "port": int(os.getenv("DATABASE_PORT", "5432")),
        "database": os.getenv("DATABASE_NAME", "aolei"),
        "user": os.getenv("DATABASE_USER", "aolei"),
        "password": os.getenv("DATABASE_PASSWORD", "aolei123456")
    }
    
    try:
        # Connect to database
        print(f"🔌 Connecting to database: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        conn = psycopg2.connect(
            host=db_config["host"],
            port=db_config["port"],
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"]
        )
        
        cursor = conn.cursor()
        
        # Check if text2sql schema exists
        cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'text2sql'")
        schema_exists = cursor.fetchone()
        
        if schema_exists:
            print("✅ text2sql schema exists")
        else:
            print("❌ text2sql schema does not exist")
            return False
        
        # Check tables in text2sql schema
        expected_tables = [
            'query_history',
            'training_data', 
            'sql_queries',
            'training_sessions'
        ]
        
        print("\n📊 Checking tables:")
        for table in expected_tables:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'text2sql' AND table_name = %s
            """, (table,))
            
            table_exists = cursor.fetchone()
            if table_exists:
                print(f"  ✅ {table}")
                
                # Get column count
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_schema = 'text2sql' AND table_name = %s
                """, (table,))
                column_count = cursor.fetchone()[0]
                print(f"     📋 {column_count} columns")
                
            else:
                print(f"  ❌ {table}")
                return False
        
        # Check indexes
        print("\n🔍 Checking indexes:")
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE schemaname = 'text2sql'
            ORDER BY indexname
        """)
        
        indexes = cursor.fetchall()
        for index in indexes:
            print(f"  ✅ {index[0]}")
        
        # Check vector extension
        print("\n🧮 Checking pgvector extension:")
        cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        vector_ext = cursor.fetchone()
        
        if vector_ext:
            print("  ✅ pgvector extension is installed")
        else:
            print("  ❌ pgvector extension is not installed")
        
        # Check triggers
        print("\n⚡ Checking triggers:")
        cursor.execute("""
            SELECT trigger_name, event_object_table
            FROM information_schema.triggers 
            WHERE trigger_schema = 'text2sql'
            ORDER BY trigger_name
        """)
        
        triggers = cursor.fetchall()
        for trigger in triggers:
            print(f"  ✅ {trigger[0]} on {trigger[1]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Text2SQL schema verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


if __name__ == "__main__":
    success = verify_schema()
    if success:
        print("\n✅ All checks passed!")
    else:
        print("\n❌ Some checks failed!")
