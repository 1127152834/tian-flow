#!/usr/bin/env python3
"""
Test script for training data editing functionality
"""

import asyncio
import json
from src.repositories.text2sql import Text2SQLRepository
from src.services.text2sql import Text2SQLService

async def test_training_data_edit():
    """Test training data editing functionality"""
    
    # Initialize repository and service
    repository = Text2SQLRepository()
    service = Text2SQLService(repository)
    
    print("🧪 Testing Training Data Edit Functionality")
    print("=" * 50)
    
    try:
        # First, let's check if we have any training data
        training_data = await repository.list_training_data(limit=5)
        
        if not training_data:
            print("❌ No training data found. Please add some training data first.")
            return
        
        print(f"✅ Found {len(training_data)} training data items")
        
        # Test updating the first item
        first_item = training_data[0]
        print(f"\n📝 Testing update for training data ID: {first_item.id}")
        print(f"   Original content type: {first_item.content_type}")
        print(f"   Original content: {first_item.content[:100]}...")
        
        # Update the content
        updated_content = first_item.content + "\n-- Updated for testing"
        
        success = await repository.update_training_data(
            training_id=first_item.id,
            content=updated_content,
            question=first_item.question or "Updated test question"
        )
        
        if success:
            print("✅ Training data updated successfully")
            
            # Verify the update
            updated_item = await repository.get_training_data(first_item.id)
            if updated_item and updated_content in updated_item.content:
                print("✅ Update verified - content was changed")
            else:
                print("❌ Update verification failed")
        else:
            print("❌ Failed to update training data")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_training_data_edit())
