#!/usr/bin/env python3
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Test script for database connection and pgvector functionality.
Run this to verify that the PostgreSQL database is properly configured.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.database import (
    test_database_connection,
    test_pgvector_extension,
    get_database_connection,
    execute_vector_search,
    insert_with_embedding
)


def test_basic_connection():
    """Test basic database connectivity."""
    print("🔍 Testing basic database connection...")
    
    if test_database_connection():
        print("✅ Database connection successful!")
        return True
    else:
        print("❌ Database connection failed!")
        return False


def test_pgvector():
    """Test pgvector extension."""
    print("\n🔍 Testing pgvector extension...")
    
    if test_pgvector_extension():
        print("✅ pgvector extension is available!")
        return True
    else:
        print("❌ pgvector extension not found!")
        return False


def test_schemas():
    """Test if required schemas exist."""
    print("\n🔍 Testing database schemas...")
    
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                # Check for required schemas
                cursor.execute("""
                    SELECT schema_name
                    FROM information_schema.schemata
                    WHERE schema_name IN ('database_management', 'text2sql', 'api_tools', 'intent_recognition', 'system')
                    ORDER BY schema_name
                """)

                schemas = [row['schema_name'] for row in cursor.fetchall()]

                expected_schemas = ['database_management', 'text2sql', 'api_tools', 'intent_recognition', 'users', 'chat', 'system']
                missing_schemas = [s for s in expected_schemas if s not in schemas]
                
                if not missing_schemas:
                    print(f"✅ All required schemas found: {', '.join(schemas)}")
                    return True
                else:
                    print(f"❌ Missing schemas: {', '.join(missing_schemas)}")
                    print(f"   Found schemas: {', '.join(schemas)}")
                    return False
                    
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False


def test_tables():
    """Test if required tables exist."""
    print("\n🔍 Testing database tables...")
    
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                # Check for required tables
                cursor.execute("""
                    SELECT schemaname, tablename
                    FROM pg_tables
                    WHERE schemaname IN ('database_management', 'text2sql', 'api_tools', 'intent_recognition', 'users', 'chat', 'system')
                    ORDER BY schemaname, tablename
                """)
                
                tables = cursor.fetchall()
                
                if tables:
                    print("✅ Found tables:")
                    for table in tables:
                        print(f"   - {table['schemaname']}.{table['tablename']}")
                    return True
                else:
                    print("❌ No tables found in required schemas!")
                    return False
                    
    except Exception as e:
        print(f"❌ Table test failed: {e}")
        return False


def test_vector_operations():
    """Test basic vector operations."""
    print("\n🔍 Testing vector operations...")
    
    try:
        # Test vector search on training data
        sample_embedding = [0.1] * 1024  # Sample 1024-dimensional vector
        
        results = execute_vector_search(
            table_name="text2sql.training_data",
            embedding_column="embedding",
            query_embedding=sample_embedding,
            limit=5,
            similarity_threshold=0.0  # Low threshold for testing
        )
        
        print(f"✅ Vector search completed. Found {len(results)} results.")
        
        if results:
            print("   Sample results:")
            for i, result in enumerate(results[:3]):
                print(f"   - {i+1}. Question: {result.get('question', 'N/A')[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector operations test failed: {e}")
        return False


def test_sample_data():
    """Test if sample data exists."""
    print("\n🔍 Testing sample data...")

    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                # Check training data
                cursor.execute("SELECT COUNT(*) as count FROM text2sql.training_data")
                training_count = cursor.fetchone()['count']

                print(f"✅ Found {training_count} training data records")

                if training_count > 0:
                    cursor.execute("SELECT question, sql_query FROM text2sql.training_data LIMIT 3")
                    samples = cursor.fetchall()
                    print("   Sample training data:")
                    for i, sample in enumerate(samples):
                        print(f"   - {i+1}. Q: {sample['question']}")
                        print(f"        SQL: {sample['sql_query']}")

                # Check API definitions
                cursor.execute("SELECT COUNT(*) as count FROM api_tools.api_definitions")
                api_count = cursor.fetchone()['count']
                print(f"✅ Found {api_count} API definitions")

                # Check system configurations
                cursor.execute("SELECT COUNT(*) as count FROM system.configurations")
                config_count = cursor.fetchone()['count']
                print(f"✅ Found {config_count} system configurations")

                # Check users
                cursor.execute("SELECT COUNT(*) as count FROM users.users")
                user_count = cursor.fetchone()['count']
                print(f"✅ Found {user_count} users")

                # Check conversations
                cursor.execute("SELECT COUNT(*) as count FROM chat.conversations")
                conversation_count = cursor.fetchone()['count']
                print(f"✅ Found {conversation_count} conversations")

                return True

    except Exception as e:
        print(f"❌ Sample data test failed: {e}")
        return False


def test_all_tables():
    """Test that all expected tables exist and are accessible."""
    print("\n🔍 Testing all table accessibility...")

    expected_tables = {
        'database_management': ['datasource_logs', 'connection_tests'],
        'text2sql': ['sql_queries', 'training_data', 'query_history'],
        'api_tools': ['api_definitions', 'call_logs'],
        'intent_recognition': ['resource_nodes', 'intent_matches'],
        'users': ['users'],
        'chat': ['conversations', 'messages'],
        'system': ['configurations', 'logs', 'background_tasks']
    }

    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                all_passed = True

                for schema, tables in expected_tables.items():
                    for table in tables:
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
                            count = cursor.fetchone()[0]
                            print(f"   ✅ {schema}.{table}: {count} records")
                        except Exception as e:
                            print(f"   ❌ {schema}.{table}: {e}")
                            all_passed = False

                return all_passed

    except Exception as e:
        print(f"❌ Table accessibility test failed: {e}")
        return False


def main():
    """Run all database tests."""
    print("🚀 Starting deer-flow database tests...\n")
    
    tests = [
        ("Basic Connection", test_basic_connection),
        ("pgvector Extension", test_pgvector),
        ("Database Schemas", test_schemas),
        ("Database Tables", test_tables),
        ("All Tables Accessibility", test_all_tables),
        ("Sample Data", test_sample_data),
        ("Vector Operations", test_vector_operations),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Database is ready for deer-flow.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the database configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
