#!/usr/bin/env python3
"""
Update existing vanna_embeddings records with table_name and database_name
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import sys
import json
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')
from utils.sql_parser import sql_parser

# Load environment variables
load_dotenv()

def update_table_names():
    """Update existing records with table_name and database_name"""
    
    # Get database configuration from environment
    db_config = {
        "host": os.getenv("DATABASE_HOST", "localhost"),
        "port": int(os.getenv("DATABASE_PORT", "5432")),
        "database": os.getenv("POSTGRES_DB", "aolei_db"),
        "user": os.getenv("POSTGRES_USER", "aolei"),
        "password": os.getenv("POSTGRES_PASSWORD", "aolei123456")
    }
    
    # Connect and update
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
            print("=== Updating vanna_embeddings with table_name and database_name ===")
            
            # Get all SQL type records that need updating
            cursor.execute("""
                SELECT id, content, sql_query, metadata, datasource_id
                FROM text2sql.vanna_embeddings 
                WHERE content_type = 'SQL'
                AND (table_name IS NULL OR table_name = '')
                ORDER BY id
            """)
            
            records = cursor.fetchall()
            print(f"Found {len(records)} records to update")
            
            updated_count = 0
            
            for record in records:
                try:
                    record_id = record['id']
                    sql_query = record['sql_query']
                    content = record['content']
                    metadata = record['metadata'] or {}
                    datasource_id = record['datasource_id']
                    
                    # Extract SQL from content if sql_query is empty
                    if not sql_query and content:
                        # Try to extract SQL from content (format: "Question: ...\nSQL: ...")
                        import re
                        sql_match = re.search(r'SQL:\s*(.+?)(?:\n|$)', content, re.DOTALL | re.IGNORECASE)
                        if sql_match:
                            sql_query = sql_match.group(1).strip()
                    
                    if not sql_query:
                        print(f"  Skipping record {record_id}: No SQL query found")
                        continue
                    
                    # Extract table names using SQL parser
                    table_names = sql_parser.extract_table_names(sql_query)
                    primary_table = sql_parser.get_primary_table(sql_query)
                    
                    # Update metadata with all table names
                    if table_names:
                        metadata['all_tables'] = table_names
                        metadata['table_count'] = len(table_names)
                    
                    # Set database name to current database
                    database_name = db_config["database"]
                    metadata['database_name'] = database_name
                    
                    # Update the record
                    cursor.execute("""
                        UPDATE text2sql.vanna_embeddings
                        SET 
                            table_name = %s,
                            metadata = %s,
                            updated_at = NOW()
                        WHERE id = %s
                    """, (
                        primary_table,  # Use primary table as table_name
                        json.dumps(metadata),
                        record_id
                    ))
                    
                    updated_count += 1
                    print(f"  Updated record {record_id}: table_name='{primary_table}', all_tables={table_names}")
                    
                except Exception as e:
                    print(f"  Error updating record {record['id']}: {e}")
                    continue
            
            # Commit all changes
            conn.commit()
            print(f"\n✅ Successfully updated {updated_count} records")
            
            # Show sample of updated data
            print("\n=== Sample of updated data ===")
            cursor.execute("""
                SELECT id, table_name, metadata->>'database_name' as database_name, 
                       metadata->>'all_tables' as all_tables, sql_query
                FROM text2sql.vanna_embeddings 
                WHERE content_type = 'SQL'
                AND table_name IS NOT NULL
                ORDER BY updated_at DESC
                LIMIT 5
            """)
            
            samples = cursor.fetchall()
            for sample in samples:
                print(f"  ID: {sample['id']}")
                print(f"    Table: {sample['table_name']}")
                print(f"    Database: {sample['database_name']}")
                print(f"    All Tables: {sample['all_tables']}")
                print(f"    SQL: {sample['sql_query'][:100]}...")
                print()
                
    except Exception as e:
        print(f"❌ Update failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    update_table_names()
