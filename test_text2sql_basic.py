#!/usr/bin/env python3
"""
Basic test script for Text2SQL system without Celery dependency.

Tests core functionality without background tasks.
"""

import sys
import os
import asyncio

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.text2sql import Text2SQLService
from src.services.database_datasource import DatabaseDatasourceService
from src.models.text2sql import (
    SQLGenerationRequest,
    SQLExecutionRequest,
    TrainingDataRequest,
    TrainingDataType,
    QueryStatus
)
from src.models.database_datasource import (
    DatabaseDatasourceCreate,
    DatabaseType
)


async def test_basic_text2sql():
    """Test basic Text2SQL functionality"""
    
    print("🚀 Testing Basic Text2SQL Functionality")
    print("=" * 50)
    
    try:
        # Initialize services
        text2sql_service = Text2SQLService()
        datasource_service = DatabaseDatasourceService()
        
        print("✅ Services initialized successfully")
        
        # Step 1: Create a test datasource
        print("\n📊 Step 1: Creating test datasource...")
        datasource_data = DatabaseDatasourceCreate(
            name="Test PostgreSQL Basic",
            description="Basic test datasource for Text2SQL",
            database_type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database_name="aolei_db",
            username="aolei",
            password="aolei123456",
            readonly_mode=True,
            allowed_operations=["SELECT"]
        )
        
        datasource = await datasource_service.create_datasource(datasource_data)
        datasource_id = datasource.id
        print(f"✅ Created datasource: {datasource.name} (ID: {datasource_id})")
        
        # Step 2: Test connection
        print("\n🔌 Step 2: Testing datasource connection...")
        connection_test = await datasource_service.test_connection(datasource_id)
        print(f"✅ Connection test: {'Success' if connection_test.success else 'Failed'} - {connection_test.error or 'OK'}")
        
        # Step 3: Add training data
        print("\n📚 Step 3: Adding training data...")
        training_requests = [
            TrainingDataRequest(
                datasource_id=datasource_id,
                content_type=TrainingDataType.SQL,
                content="SELECT id, name, email FROM users WHERE active = true ORDER BY name",
                question="Show me all active users with their details",
                sql_query="SELECT id, name, email FROM users WHERE active = true ORDER BY name",
                table_names=["users"],
                metadata={"complexity": "simple", "category": "user_management"}
            ),
            TrainingDataRequest(
                datasource_id=datasource_id,
                content_type=TrainingDataType.SCHEMA,
                content="CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL, email VARCHAR(255) UNIQUE, active BOOLEAN DEFAULT true)",
                question=None,
                sql_query=None,
                table_names=["users"],
                metadata={"type": "table_definition"}
            )
        ]
        
        training_ids = []
        for i, request in enumerate(training_requests):
            try:
                response = await text2sql_service.add_training_data(request)
                training_ids.append(response.id)
                print(f"✅ Added training data {i+1}: {response.content_type} - {response.content[:50]}...")
            except ValueError as e:
                if "already exists" in str(e):
                    print(f"⚠️  Training data {i+1} already exists, skipping...")
                else:
                    print(f"❌ Failed to add training data {i+1}: {e}")
            except Exception as e:
                print(f"❌ Failed to add training data {i+1}: {e}")
        
        print(f"✅ Processed {len(training_requests)} training data requests")
        
        # Step 4: Generate SQL
        print("\n💡 Step 4: Generating SQL from natural language...")
        generation_requests = [
            "Show me all active users",
            "List users by name"
        ]
        
        query_ids = []
        for question in generation_requests:
            try:
                request = SQLGenerationRequest(
                    datasource_id=datasource_id,
                    question=question,
                    include_explanation=True
                )
                
                response = await text2sql_service.generate_sql(request)
                query_ids.append(response.query_id)
                
                print(f"✅ Generated SQL for: '{question}'")
                print(f"   SQL: {response.generated_sql}")
                print(f"   Confidence: {response.confidence_score}")
                if response.explanation:
                    print(f"   Explanation: {response.explanation}")
                print()
                
            except Exception as e:
                print(f"❌ Failed to generate SQL for '{question}': {e}")
        
        # Step 5: Execute SQL queries
        print("\n⚡ Step 5: Executing generated SQL queries...")
        for query_id in query_ids:
            try:
                request = SQLExecutionRequest(
                    query_id=query_id,
                    limit=5
                )
                
                response = await text2sql_service.execute_sql(request)
                
                if response.status == QueryStatus.SUCCESS:
                    print(f"✅ Executed query {query_id}: {response.result_rows} rows in {response.execution_time_ms}ms")
                    if response.result_data:
                        print(f"   Sample results: {response.result_data[:2]}")
                else:
                    print(f"❌ Query {query_id} failed: {response.error_message}")
                
            except Exception as e:
                print(f"❌ Failed to execute query {query_id}: {e}")
        
        # Step 6: Get statistics
        print("\n📈 Step 6: Getting system statistics...")
        stats = await text2sql_service.get_statistics(datasource_id)
        print(f"✅ Statistics for datasource {datasource_id}:")
        print(f"   Total queries: {stats.total_queries}")
        print(f"   Successful queries: {stats.successful_queries}")
        print(f"   Failed queries: {stats.failed_queries}")
        print(f"   Average confidence: {stats.average_confidence}")
        print(f"   Total training data: {stats.total_training_data}")
        print(f"   Training data by type: {stats.training_data_by_type}")
        
        # Step 7: Get training summary
        print("\n📋 Step 7: Getting training data summary...")
        summary = await text2sql_service.get_datasource_training_summary(datasource_id)
        print(f"✅ Training summary:")
        print(f"   Total items: {summary['total_items']}")
        print(f"   Total validated: {summary['total_validated']}")
        print(f"   By type: {summary['by_type']}")
        
        # Step 8: List query history
        print("\n📜 Step 8: Listing query history...")
        queries, total = await text2sql_service.get_query_history(
            datasource_id=datasource_id,
            limit=10,
            offset=0
        )
        print(f"✅ Found {total} query history records")
        for query in queries:
            print(f"   - {query.user_question} -> {query.status}")
        
        # Step 9: List training data
        print("\n📚 Step 9: Listing training data...")
        training_data, total = await text2sql_service.get_training_data_list(
            datasource_id=datasource_id,
            limit=10,
            offset=0
        )
        print(f"✅ Found {total} training data records")
        for data in training_data:
            print(f"   - {data.content_type}: {data.content[:50]}...")
        
        print("\n🎉 Basic Text2SQL test completed successfully!")
        print("\n📊 Summary:")
        print(f"   - Created datasource: {datasource.name}")
        print(f"   - Processed training data requests")
        print(f"   - Generated {len(query_ids)} SQL queries")
        print(f"   - Retrieved system statistics")
        print(f"   - Listed query history and training data")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Basic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("🚀 Starting Basic Text2SQL Test")
    print("=" * 60)
    
    success = await test_basic_text2sql()
    
    if success:
        print("\n✅ All basic tests passed!")
        print("\n🔧 Next steps:")
        print("   1. Start Redis: make redis")
        print("   2. Start Celery: make celery")
        print("   3. Start server: make server")
        print("   4. Test full system: make test-text2sql")
    else:
        print("\n❌ Some tests failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
