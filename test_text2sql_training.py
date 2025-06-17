#!/usr/bin/env python3
"""
Test script for Text2SQL training functionality.
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.text2sql import Text2SQLService
from src.repositories.text2sql import Text2SQLRepository
from src.models.text2sql import TrainingDataRequest, TrainingDataType


async def test_training_workflow():
    """Test the complete training workflow"""
    
    print("🧪 Testing Text2SQL Training Workflow")
    print("=" * 50)
    
    try:
        # Initialize services
        service = Text2SQLService()
        repository = Text2SQLRepository()
        
        # Test datasource ID (assuming it exists)
        datasource_id = 1
        
        print(f"📊 Testing with datasource ID: {datasource_id}")
        
        # Step 1: Add some training data
        print("\n1️⃣ Adding training data...")
        
        training_examples = [
            {
                "content_type": TrainingDataType.SQL,
                "content": "SELECT * FROM users WHERE active = true",
                "question": "Show me all active users",
                "sql_query": "SELECT * FROM users WHERE active = true",
                "table_names": ["users"],
                "metadata": {"example": "basic_select"}
            },
            {
                "content_type": TrainingDataType.SCHEMA,
                "content": "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), active BOOLEAN)",
                "table_names": ["users"],
                "metadata": {"example": "table_schema"}
            },
            {
                "content_type": TrainingDataType.DOCUMENTATION,
                "content": "The users table contains information about system users. The active column indicates if the user account is currently enabled.",
                "table_names": ["users"],
                "metadata": {"example": "documentation"}
            }
        ]
        
        training_data_ids = []
        for i, example in enumerate(training_examples):
            try:
                request = TrainingDataRequest(
                    datasource_id=datasource_id,
                    **example
                )
                
                training_data = await service.add_training_data(request)
                training_data_ids.append(training_data.id)
                print(f"   ✅ Added training data {training_data.id}: {example['content_type'].value}")
                
            except Exception as e:
                print(f"   ❌ Failed to add training data {i+1}: {e}")
        
        if not training_data_ids:
            print("❌ No training data was added. Cannot proceed with training.")
            return
        
        print(f"   📝 Added {len(training_data_ids)} training examples")
        
        # Step 2: Start training
        print("\n2️⃣ Starting model training...")
        
        try:
            result = await service.retrain_model(
                datasource_id=datasource_id,
                force_rebuild=True
            )
            
            task_id = result['task_id']
            print(f"   🚀 Training task started: {task_id}")
            print(f"   📄 Message: {result['message']}")
            
            # Wait a bit for the task to start
            await asyncio.sleep(2)
            
            # Check task status
            print("\n3️⃣ Checking training progress...")
            
            # Get training sessions
            sessions_result = await service.get_training_sessions(
                datasource_id=datasource_id,
                limit=5
            )
            
            if sessions_result['sessions']:
                latest_session = sessions_result['sessions'][0]
                print(f"   📊 Latest session: {latest_session.id}")
                print(f"   📈 Status: {latest_session.status.value}")
                print(f"   📅 Started: {latest_session.started_at}")
                
                if latest_session.training_data_count:
                    print(f"   📝 Training data count: {latest_session.training_data_count}")
                
                if latest_session.accuracy_score:
                    print(f"   🎯 Accuracy score: {latest_session.accuracy_score:.2%}")
            
        except Exception as e:
            print(f"   ❌ Training failed: {e}")
        
        # Step 3: Test statistics
        print("\n4️⃣ Checking statistics...")
        
        try:
            stats = await service.get_statistics(datasource_id)
            print(f"   📊 Total training data: {stats.total_training_data}")
            print(f"   📈 Training data by type: {stats.training_data_by_type}")
            
        except Exception as e:
            print(f"   ❌ Failed to get statistics: {e}")
        
        # Step 4: Test embedding generation
        print("\n5️⃣ Testing embedding generation...")
        
        try:
            embedding_result = await service.generate_embeddings_for_training_data(
                datasource_id=datasource_id,
                training_data_ids=training_data_ids[:2]  # Test with first 2 items
            )
            
            print(f"   🔄 Embedding task started: {embedding_result['task_id']}")
            print(f"   📝 Processing {embedding_result['training_data_count']} items")
            
        except Exception as e:
            print(f"   ❌ Embedding generation failed: {e}")
        
        print("\n✅ Training workflow test completed!")
        print("\n💡 Tips:")
        print("   - Check Celery worker logs for detailed task progress")
        print("   - Use the web interface to monitor training sessions")
        print("   - Training tasks run asynchronously in the background")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


async def test_basic_functionality():
    """Test basic Text2SQL functionality"""
    
    print("\n🔧 Testing Basic Functionality")
    print("=" * 30)
    
    try:
        service = Text2SQLService()
        
        # Test health check
        print("🏥 Health check...")
        health = await service.health_check()
        print(f"   Status: {health['status']}")
        
        # Test statistics
        print("📊 Statistics...")
        stats = await service.get_statistics()
        print(f"   Total training data: {stats.total_training_data}")
        
        print("✅ Basic functionality test passed!")
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")


if __name__ == "__main__":
    print("🦌 DeerFlow Text2SQL Training Test")
    print("=" * 40)
    
    # Run basic tests first
    asyncio.run(test_basic_functionality())
    
    # Run training workflow test
    asyncio.run(test_training_workflow())
    
    print("\n🎉 All tests completed!")
    print("Check the Celery worker logs for background task progress.")
