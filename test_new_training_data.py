#!/usr/bin/env python3
"""
Test script to verify new training data automatically gets table_name and database_name filled
"""

import sys
import json
sys.path.append('src')

from services.vanna.vector_store import PgVectorStore
from config.database import get_database_connection
import psycopg2
from psycopg2.extras import RealDictCursor

def test_new_training_data():
    """Test adding new training data with automatic table name extraction"""
    
    print("🧪 Testing New Training Data with Table Name Extraction")
    print("=" * 60)
    
    try:
        # Create vector store instance
        vector_store = PgVectorStore(datasource_id=1)
        
        # Test cases with different SQL patterns
        test_cases = [
            {
                "question": "How many users are active?",
                "sql": "SELECT COUNT(*) FROM users WHERE active = true",
                "expected_table": "users"
            },
            {
                "question": "Show recent orders with customer info",
                "sql": """
                    SELECT o.id, o.amount, u.name as customer_name
                    FROM orders o
                    JOIN users u ON o.user_id = u.id
                    WHERE o.created_at >= CURRENT_DATE - INTERVAL '7 days'
                """,
                "expected_table": "orders"
            },
            {
                "question": "Get product inventory",
                "sql": "SELECT p.name, i.quantity FROM products p LEFT JOIN inventory i ON p.id = i.product_id",
                "expected_table": "products"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}: {test_case['question']}")
            print(f"SQL: {test_case['sql'].strip()}")
            print(f"Expected primary table: {test_case['expected_table']}")
            
            try:
                # Add question-SQL pair to vector store
                content_hash = vector_store.add_question_sql(
                    question=test_case['question'],
                    sql=test_case['sql'],
                    test_case_id=i
                )
                
                print(f"✅ Added training data with hash: {content_hash}")
                
                # Verify the data was stored correctly
                with get_database_connection() as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                        cursor.execute("""
                            SELECT table_name, metadata, question, sql_query
                            FROM text2sql.vanna_embeddings
                            WHERE content_hash = %s
                        """, (content_hash,))
                        
                        record = cursor.fetchone()
                        if record:
                            print(f"   Stored table_name: {record['table_name']}")
                            
                            # Parse metadata
                            metadata = json.loads(record['metadata']) if record['metadata'] else {}
                            print(f"   Database name: {metadata.get('database_name')}")
                            print(f"   All tables: {metadata.get('all_tables')}")
                            print(f"   Table count: {metadata.get('table_count')}")
                            
                            # Verify expected table
                            if record['table_name'] == test_case['expected_table']:
                                print("   ✅ Primary table extraction: CORRECT")
                            else:
                                print(f"   ❌ Primary table extraction: WRONG (got {record['table_name']})")
                            
                            # Verify database name
                            if metadata.get('database_name') == 'aolei_db':
                                print("   ✅ Database name: CORRECT")
                            else:
                                print(f"   ❌ Database name: WRONG (got {metadata.get('database_name')})")
                        else:
                            print("   ❌ Record not found in database")
                            
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n{'='*60}")
        print("🎉 Test completed! Check the results above.")
        
        # Show current state of vanna_embeddings table
        print(f"\n📊 Current vanna_embeddings records:")
        with get_database_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, table_name, 
                           metadata->>'database_name' as database_name,
                           metadata->>'all_tables' as all_tables,
                           LEFT(question, 50) as question_preview,
                           LEFT(sql_query, 50) as sql_preview
                    FROM text2sql.vanna_embeddings
                    WHERE datasource_id = 1
                    ORDER BY id DESC
                    LIMIT 10
                """)
                
                records = cursor.fetchall()
                for record in records:
                    print(f"   ID {record['id']}: table={record['table_name']}, "
                          f"db={record['database_name']}, "
                          f"all_tables={record['all_tables']}")
                    print(f"      Q: {record['question_preview']}...")
                    print(f"      SQL: {record['sql_preview']}...")
                    print()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_new_training_data()
    sys.exit(0 if success else 1)
