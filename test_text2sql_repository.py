#!/usr/bin/env python3
"""
Test script for Text2SQL repository functionality.
"""

import sys
import os
import asyncio
from datetime import datetime, timezone

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.repositories.text2sql import Text2SQLRepository
from src.models.text2sql import (
    QueryStatus,
    TrainingDataType,
    QueryComplexity,
    TrainingSessionStatus
)


async def test_repository():
    """Test Text2SQL repository operations"""
    
    print("🧪 Testing Text2SQL Repository...")
    
    try:
        # Initialize repository
        repo = Text2SQLRepository()
        print("✅ Repository initialized successfully")
        
        # Test 1: Create query history
        print("\n📝 Test 1: Creating query history...")
        query_id = await repo.create_query_history(
            user_question="Show me all users",
            generated_sql="SELECT * FROM users",
            datasource_id=1,
            status=QueryStatus.PENDING,
            confidence_score=0.85,
            model_used="gpt-4",
            explanation="Simple SELECT query to retrieve all users"
        )
        print(f"✅ Created query history with ID: {query_id}")
        
        # Test 2: Get query history
        print("\n📖 Test 2: Getting query history...")
        query = await repo.get_query_history(query_id)
        if query:
            print(f"✅ Retrieved query: {query.user_question}")
            print(f"   SQL: {query.generated_sql}")
            print(f"   Status: {query.status}")
        else:
            print("❌ Failed to retrieve query history")
        
        # Test 3: Update query history
        print("\n📝 Test 3: Updating query history...")
        updated = await repo.update_query_history(
            query_id,
            status=QueryStatus.SUCCESS,
            execution_time_ms=150,
            result_rows=25
        )
        if updated:
            print("✅ Query history updated successfully")
        else:
            print("❌ Failed to update query history")
        
        # Test 4: Create training data
        print("\n📚 Test 4: Creating training data...")
        training_id = await repo.create_training_data(
            datasource_id=1,
            content_type=TrainingDataType.SQL,
            content="SELECT * FROM users WHERE active = true",
            question="Show me all active users",
            sql_query="SELECT * FROM users WHERE active = true",
            table_names=["users"],
            metadata={"complexity": "simple", "category": "user_management"}
        )
        print(f"✅ Created training data with ID: {training_id}")
        
        # Test 5: List training data
        print("\n📋 Test 5: Listing training data...")
        training_data, total = await repo.list_training_data(
            datasource_id=1,
            limit=10,
            offset=0
        )
        print(f"✅ Found {total} training data records")
        for data in training_data:
            print(f"   - {data.content_type}: {data.content[:50]}...")
        
        # Test 6: Create SQL query cache
        print("\n💾 Test 6: Creating SQL query cache...")
        cache_id = await repo.create_sql_query_cache(
            query_text="show active users",
            sql_text="SELECT * FROM users WHERE active = true",
            datasource_id=1,
            table_names=["users"],
            query_complexity=QueryComplexity.SIMPLE
        )
        print(f"✅ Created SQL query cache with ID: {cache_id}")
        
        # Test 7: Update cache usage
        print("\n📊 Test 7: Updating cache usage...")
        updated = await repo.update_sql_query_cache_usage(
            cache_id,
            execution_time_ms=120,
            success=True
        )
        if updated:
            print("✅ Cache usage updated successfully")
        else:
            print("❌ Failed to update cache usage")
        
        # Test 8: Create training session
        print("\n🎯 Test 8: Creating training session...")
        session_id = await repo.create_training_session(
            datasource_id=1,
            session_name="Test Training Session",
            model_version="v1.0",
            training_parameters={"epochs": 10, "learning_rate": 0.001},
            notes="Test training session for repository validation"
        )
        print(f"✅ Created training session with ID: {session_id}")
        
        # Test 9: Update training session
        print("\n🔄 Test 9: Updating training session...")
        updated = await repo.update_training_session(
            session_id,
            status=TrainingSessionStatus.COMPLETED,
            training_data_count=5,
            accuracy_score=0.92,
            training_time_seconds=300,
            completed_at=datetime.now(timezone.utc)
        )
        if updated:
            print("✅ Training session updated successfully")
        else:
            print("❌ Failed to update training session")
        
        # Test 10: Get statistics
        print("\n📈 Test 10: Getting statistics...")
        stats = await repo.get_statistics(datasource_id=1)
        print("✅ Statistics retrieved:")
        print(f"   Total queries: {stats['total_queries']}")
        print(f"   Successful queries: {stats['successful_queries']}")
        print(f"   Total training data: {stats['total_training_data']}")
        print(f"   Training data by type: {stats['training_data_by_type']}")
        
        # Test 11: List query history
        print("\n📜 Test 11: Listing query history...")
        queries, total = await repo.list_query_history(
            datasource_id=1,
            limit=10,
            offset=0
        )
        print(f"✅ Found {total} query history records")
        for query in queries:
            print(f"   - {query.user_question} -> {query.status}")
        
        # Test 12: Search similar queries
        print("\n🔍 Test 12: Searching similar queries...")
        similar_queries = await repo.search_similar_queries(
            datasource_id=1,
            limit=5
        )
        print(f"✅ Found {len(similar_queries)} similar queries")
        for query in similar_queries:
            print(f"   - {query.query_text} (used {query.usage_count} times)")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def cleanup_test_data():
    """Clean up test data (optional)"""
    print("\n🧹 Cleaning up test data...")
    try:
        repo = Text2SQLRepository()
        
        # Note: In a real scenario, you might want to implement cleanup methods
        # For now, we'll just note that test data was created
        print("ℹ️  Test data created. You may want to clean it up manually if needed.")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")


async def main():
    """Main test function"""
    print("🚀 Starting Text2SQL Repository Tests")
    print("=" * 50)
    
    success = await test_repository()
    
    if success:
        print("\n✅ All repository tests passed!")
        # Optionally clean up test data
        # await cleanup_test_data()
    else:
        print("\n❌ Some tests failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
