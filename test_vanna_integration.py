#!/usr/bin/env python3
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Test script for Vanna AI integration in DeerFlow
"""

import asyncio
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.services.vanna import vanna_service_manager
    print("✅ Successfully imported vanna_service_manager")
except ImportError as e:
    print(f"❌ Failed to import vanna_service_manager: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_vanna_integration():
    """Test Vanna AI integration"""
    print("🧪 Testing Vanna AI integration...")
    
    try:
        # Test 1: Generate SQL
        print("\n📋 1. Testing SQL generation...")
        result = await vanna_service_manager.generate_sql(
            datasource_id=1,
            question="Show me all users",
            embedding_model_id=None
        )
        
        print(f"   SQL Generation Result: {result}")
        
        if result["success"]:
            print("   ✅ SQL generation successful")
            print(f"   Generated SQL: {result['sql']}")
        else:
            print(f"   ❌ SQL generation failed: {result.get('error')}")
        
        # Test 2: Execute SQL (if generation was successful)
        if result["success"] and result["sql"]:
            print("\n📋 2. Testing SQL execution...")
            exec_result = await vanna_service_manager.execute_sql(
                datasource_id=1,
                sql=result["sql"]
            )
            
            print(f"   SQL Execution Result: {exec_result}")
            
            if exec_result["success"]:
                print("   ✅ SQL execution successful")
                print(f"   Rows returned: {exec_result['data']['row_count']}")
            else:
                print(f"   ❌ SQL execution failed: {exec_result.get('error')}")
        
        # Test 3: Complete question answering
        print("\n📋 3. Testing complete question answering...")
        qa_result = await vanna_service_manager.ask_question(
            datasource_id=1,
            question="How many users are there?",
            execute=True,
            embedding_model_id=None
        )
        
        print(f"   Question Answering Result: {qa_result}")
        
        if qa_result["success"]:
            print("   ✅ Question answering successful")
            print(f"   Generated SQL: {qa_result['sql']}")
            if "data" in qa_result:
                print(f"   Execution result: {qa_result['data']['row_count']} rows")
        else:
            print(f"   ❌ Question answering failed: {qa_result.get('error')}")
        
        # Test 4: Training with DDL
        print("\n📋 4. Testing DDL training...")
        ddl_statements = [
            "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100))",
            "CREATE TABLE orders (id INT PRIMARY KEY, user_id INT, amount DECIMAL(10,2))"
        ]
        
        train_result = await vanna_service_manager.train_from_ddl(
            datasource_id=1,
            ddl_statements=ddl_statements,
            embedding_model_id=None,
            database_name="test_db",
            skip_existing=True
        )
        
        print(f"   DDL Training Result: {train_result}")
        
        if train_result["success"]:
            print("   ✅ DDL training successful")
            print(f"   Trained {train_result['successful']} DDL statements")
        else:
            print(f"   ❌ DDL training failed: {train_result.get('error')}")
        
        print("\n🎉 Vanna integration test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_vanna_integration())
