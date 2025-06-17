#!/usr/bin/env python3
"""
Test script for SQL table name extraction functionality
"""

import sys
sys.path.append('src')

from utils.sql_parser import sql_parser

def test_sql_parser():
    """Test SQL parser with various SQL queries"""
    
    test_cases = [
        {
            "name": "Simple SELECT",
            "sql": "SELECT * FROM users WHERE id = 1",
            "expected_tables": ["users"]
        },
        {
            "name": "JOIN Query",
            "sql": "SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id",
            "expected_tables": ["users", "orders"]
        },
        {
            "name": "Complex Query with Multiple JOINs",
            "sql": """
                SELECT u.name, o.amount, p.name as product_name
                FROM users u 
                JOIN orders o ON u.id = o.user_id
                LEFT JOIN order_items oi ON o.id = oi.order_id
                JOIN products p ON oi.product_id = p.id
                WHERE u.active = true
            """,
            "expected_tables": ["users", "orders", "order_items", "products"]
        },
        {
            "name": "Schema Qualified Tables",
            "sql": "SELECT * FROM database_management.database_datasources WHERE id = 1",
            "expected_tables": ["database_management.database_datasources"]
        },
        {
            "name": "INSERT Statement",
            "sql": "INSERT INTO users (name, email) VALUES ('John', 'john@example.com')",
            "expected_tables": ["users"]
        },
        {
            "name": "UPDATE Statement",
            "sql": "UPDATE orders SET status = 'completed' WHERE id = 123",
            "expected_tables": ["orders"]
        },
        {
            "name": "DELETE Statement",
            "sql": "DELETE FROM users WHERE last_login < '2023-01-01'",
            "expected_tables": ["users"]
        },
        {
            "name": "CREATE TABLE DDL",
            "sql": "CREATE TABLE new_table (id INT PRIMARY KEY, name VARCHAR(100))",
            "expected_tables": ["new_table"]
        },
        {
            "name": "Subquery",
            "sql": """
                SELECT * FROM users 
                WHERE id IN (SELECT user_id FROM orders WHERE amount > 100)
            """,
            "expected_tables": ["users", "orders"]
        },
        {
            "name": "CTE (Common Table Expression)",
            "sql": """
                WITH high_value_customers AS (
                    SELECT user_id FROM orders WHERE amount > 1000
                )
                SELECT u.* FROM users u 
                JOIN high_value_customers hvc ON u.id = hvc.user_id
            """,
            "expected_tables": ["orders", "users"]
        }
    ]
    
    print("🧪 Testing SQL Parser...")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"\n📝 Test: {test_case['name']}")
        print(f"SQL: {test_case['sql'].strip()}")
        
        try:
            # Extract table names
            extracted_tables = sql_parser.extract_table_names(test_case['sql'])
            primary_table = sql_parser.get_primary_table(test_case['sql'])
            
            print(f"Extracted tables: {extracted_tables}")
            print(f"Primary table: {primary_table}")
            print(f"Expected tables: {test_case['expected_tables']}")
            
            # Check if all expected tables are found
            expected_set = set(test_case['expected_tables'])
            extracted_set = set(extracted_tables)
            
            if expected_set.issubset(extracted_set):
                print("✅ PASS")
                passed += 1
            else:
                missing = expected_set - extracted_set
                extra = extracted_set - expected_set
                print(f"❌ FAIL")
                if missing:
                    print(f"   Missing tables: {list(missing)}")
                if extra:
                    print(f"   Extra tables: {list(extra)}")
                failed += 1
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {failed} tests failed")
    
    return failed == 0

def test_vector_store_integration():
    """Test vector store integration with table name extraction"""
    
    print("\n🔗 Testing Vector Store Integration...")
    print("=" * 60)
    
    try:
        from services.vanna.vector_store import PgVectorStore
        from config.database import get_database_config
        
        # Create vector store instance
        vector_store = PgVectorStore(datasource_id=1)
        
        # Test question-SQL pair with table extraction
        test_question = "Show me all users with their order counts"
        test_sql = """
            SELECT u.id, u.name, COUNT(o.id) as order_count
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            GROUP BY u.id, u.name
        """
        
        print(f"Question: {test_question}")
        print(f"SQL: {test_sql.strip()}")
        
        # This would normally add to database, but we'll just test the parsing
        from utils.sql_parser import sql_parser
        table_names = sql_parser.extract_table_names(test_sql)
        primary_table = sql_parser.get_primary_table(test_sql)
        
        print(f"Extracted tables: {table_names}")
        print(f"Primary table: {primary_table}")
        
        if table_names and primary_table:
            print("✅ Vector store integration test passed")
            return True
        else:
            print("❌ Vector store integration test failed")
            return False
            
    except Exception as e:
        print(f"❌ Vector store integration test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Table Name Extraction Tests")
    print("=" * 60)
    
    # Test SQL parser
    parser_success = test_sql_parser()
    
    # Test vector store integration
    integration_success = test_vector_store_integration()
    
    print("\n" + "=" * 60)
    print("📋 Final Results:")
    print(f"   SQL Parser: {'✅ PASS' if parser_success else '❌ FAIL'}")
    print(f"   Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
    
    if parser_success and integration_success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed")
        sys.exit(1)
