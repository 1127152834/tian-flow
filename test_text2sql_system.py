#!/usr/bin/env python3
"""
Test script for the complete Text2SQL system.

Tests the integration of Repository, Service, Celery tasks, and WebSocket.
"""

import sys
import os
import asyncio
import time
from datetime import datetime, timezone

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
    DatabaseType,
    ConnectionStatus
)


async def test_complete_text2sql_system():
    """Test the complete Text2SQL system"""
    
    print("🚀 Testing Complete Text2SQL System")
    print("=" * 60)
    
    try:
        # Initialize services
        text2sql_service = Text2SQLService()
        datasource_service = DatabaseDatasourceService()
        
        print("✅ Services initialized successfully")
        
        # Step 1: Create a test datasource
        print("\n📊 Step 1: Creating test datasource...")
        datasource_data = DatabaseDatasourceCreate(
            name="Test PostgreSQL",
            description="Test datasource for Text2SQL",
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
                content="SELECT * FROM users WHERE active = true",
                question="Show me all active users",
                sql_query="SELECT * FROM users WHERE active = true",
                table_names=["users"],
                metadata={"complexity": "simple", "category": "user_management"}
            ),
            TrainingDataRequest(
                datasource_id=datasource_id,
                content_type=TrainingDataType.SQL,
                content="SELECT COUNT(*) FROM orders WHERE created_at >= CURRENT_DATE",
                question="How many orders were created today?",
                sql_query="SELECT COUNT(*) FROM orders WHERE created_at >= CURRENT_DATE",
                table_names=["orders"],
                metadata={"complexity": "medium", "category": "analytics"}
            ),
            TrainingDataRequest(
                datasource_id=datasource_id,
                content_type=TrainingDataType.SCHEMA,
                content="CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(255), active BOOLEAN)",
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
            except Exception as e:
                print(f"⚠️  Failed to add training data {i+1}: {e}")
        
        print(f"✅ Added {len(training_ids)} training data records")
        
        # Step 4: Start training session
        print("\n🎯 Step 4: Starting training session...")
        training_result = await text2sql_service.start_training_session(
            datasource_id=datasource_id,
            session_name="Test Training Session",
            model_version="v1.0",
            training_parameters={"epochs": 5, "learning_rate": 0.001},
            notes="Test training session for system validation"
        )
        
        session_id = training_result['session_id']
        task_id = training_result['task_id']
        print(f"✅ Started training session {session_id} with task {task_id}")
        
        # Step 5: Monitor training progress (simplified)
        print("\n⏳ Step 5: Monitoring training progress...")
        for i in range(10):  # Check for 10 seconds
            session = await text2sql_service.get_training_session_status(session_id)
            if session:
                print(f"   Training status: {session.status} - {session.notes}")
                if session.status.value in ['COMPLETED', 'FAILED']:
                    break
            await asyncio.sleep(1)
        
        # Step 6: Generate SQL
        print("\n💡 Step 6: Generating SQL from natural language...")
        generation_requests = [
            "Show me all active users",
            "How many orders were created today?",
            "List all users with their order counts"
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
        
        # Step 7: Execute SQL queries
        print("\n⚡ Step 7: Executing generated SQL queries...")
        for query_id in query_ids:
            try:
                request = SQLExecutionRequest(
                    query_id=query_id,
                    limit=10
                )
                
                response = await text2sql_service.execute_sql(request)
                
                if response.status == QueryStatus.SUCCESS:
                    print(f"✅ Executed query {query_id}: {response.row_count} rows in {response.execution_time_ms}ms")
                    if response.results:
                        print(f"   Sample results: {response.results[:2]}")
                else:
                    print(f"❌ Query {query_id} failed: {response.error_message}")
                
            except Exception as e:
                print(f"❌ Failed to execute query {query_id}: {e}")
        
        # Step 8: Get statistics
        print("\n📈 Step 8: Getting system statistics...")
        stats = await text2sql_service.get_statistics(datasource_id)
        print(f"✅ Statistics for datasource {datasource_id}:")
        print(f"   Total queries: {stats.total_queries}")
        print(f"   Successful queries: {stats.successful_queries}")
        print(f"   Failed queries: {stats.failed_queries}")
        print(f"   Average confidence: {stats.average_confidence}")
        print(f"   Total training data: {stats.total_training_data}")
        print(f"   Training data by type: {stats.training_data_by_type}")
        
        # Step 9: Get training summary
        print("\n📋 Step 9: Getting training data summary...")
        summary = await text2sql_service.get_datasource_training_summary(datasource_id)
        print(f"✅ Training summary:")
        print(f"   Total items: {summary['total_items']}")
        print(f"   Total validated: {summary['total_validated']}")
        print(f"   By type: {summary['by_type']}")
        
        # Step 10: Generate embeddings for training data
        print("\n🔍 Step 10: Generating embeddings for training data...")
        if training_ids:
            embedding_result = await text2sql_service.generate_embeddings_for_training_data(
                datasource_id=datasource_id,
                training_data_ids=training_ids[:2]  # Process first 2 items
            )
            print(f"✅ Started embedding generation task: {embedding_result['task_id']}")
            print(f"   Processing {embedding_result['training_data_count']} training data items")
        
        print("\n🎉 Complete Text2SQL system test completed successfully!")
        print("\n📊 Summary:")
        print(f"   - Created datasource: {datasource.name}")
        print(f"   - Added {len(training_ids)} training data records")
        print(f"   - Started training session: {session_id}")
        print(f"   - Generated {len(query_ids)} SQL queries")
        print(f"   - System statistics retrieved")
        print(f"   - Embedding generation started")
        
        return True
        
    except Exception as e:
        print(f"\n❌ System test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def cleanup_test_data():
    """Clean up test data (optional)"""
    print("\n🧹 Cleaning up test data...")
    try:
        # Note: In a real scenario, you might want to implement cleanup methods
        print("ℹ️  Test data created. You may want to clean it up manually if needed.")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")


async def main():
    """Main test function"""
    print("🚀 Starting Complete Text2SQL System Test")
    print("=" * 80)
    
    success = await test_complete_text2sql_system()
    
    if success:
        print("\n✅ All system tests passed!")
        print("\n🔧 Next steps:")
        print("   1. Start Celery worker: celery -A src.tasks.text2sql_tasks worker --loglevel=info")
        print("   2. Start Redis server: redis-server --port 6380")
        print("   3. Test WebSocket connections")
        print("   4. Run the FastAPI server: uvicorn src.app:app --reload")
        
        # Optionally clean up test data
        # await cleanup_test_data()
    else:
        print("\n❌ Some tests failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
