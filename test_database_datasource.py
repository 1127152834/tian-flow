#!/usr/bin/env python3
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Test script for database datasource functionality.
This script tests the basic CRUD operations and connection testing.
"""

import asyncio
import json
from datetime import datetime

from src.models.database_datasource import (
    DatabaseDatasourceCreate,
    DatabaseDatasourceUpdate,
    DatabaseType,
    ConnectionStatus,
)
from src.services.database_datasource import database_datasource_service


async def test_database_datasource_crud():
    """Test basic CRUD operations for database datasources"""
    print("🧪 Testing Database Datasource CRUD Operations")
    print("=" * 50)
    
    # Test 1: Create a new datasource
    print("\n1. Creating a new MySQL datasource...")
    create_request = DatabaseDatasourceCreate(
        name="Test MySQL Database",
        description="A test MySQL database for development",
        database_type=DatabaseType.MYSQL,
        host="localhost",
        port=3306,
        database_name="test_db",
        username="test_user",
        password="test_password",
        readonly_mode=True,
        allowed_operations=["SELECT", "SHOW"]
    )
    
    try:
        datasource = await database_datasource_service.create_datasource(create_request)
        print(f"✅ Created datasource: {datasource.name} (ID: {datasource.id})")
        datasource_id = datasource.id
    except Exception as e:
        print(f"❌ Failed to create datasource: {e}")
        return
    
    # Test 2: List datasources
    print("\n2. Listing all datasources...")
    try:
        datasources = await database_datasource_service.list_datasources()
        print(f"✅ Found {len(datasources)} datasources")
        for ds in datasources:
            print(f"   - {ds.name} ({ds.database_type.value}) - {ds.connection_status.value}")
    except Exception as e:
        print(f"❌ Failed to list datasources: {e}")
    
    # Test 3: Get specific datasource
    print(f"\n3. Getting datasource by ID ({datasource_id})...")
    try:
        retrieved_ds = await database_datasource_service.get_datasource(datasource_id)
        if retrieved_ds:
            print(f"✅ Retrieved datasource: {retrieved_ds.name}")
            print(f"   Host: {retrieved_ds.host}:{retrieved_ds.port}")
            print(f"   Database: {retrieved_ds.database_name}")
            print(f"   Status: {retrieved_ds.connection_status.value}")
        else:
            print("❌ Datasource not found")
    except Exception as e:
        print(f"❌ Failed to get datasource: {e}")
    
    # Test 4: Update datasource
    print(f"\n4. Updating datasource ({datasource_id})...")
    update_request = DatabaseDatasourceUpdate(
        description="Updated description for test database",
        port=3307,
        allowed_operations=["SELECT", "SHOW", "DESCRIBE"]
    )
    
    try:
        updated_ds = await database_datasource_service.update_datasource(datasource_id, update_request)
        if updated_ds:
            print(f"✅ Updated datasource: {updated_ds.name}")
            print(f"   New port: {updated_ds.port}")
            print(f"   New description: {updated_ds.description}")
            print(f"   Allowed operations: {updated_ds.allowed_operations}")
        else:
            print("❌ Datasource not found for update")
    except Exception as e:
        print(f"❌ Failed to update datasource: {e}")
    
    # Test 5: Test connection (will fail since it's a fake database)
    print(f"\n5. Testing database connection ({datasource_id})...")
    try:
        test_result = await database_datasource_service.test_connection(datasource_id, timeout=5)
        if test_result.success:
            print(f"✅ Connection test successful")
            print(f"   Details: {test_result.details}")
        else:
            print(f"⚠️ Connection test failed (expected for fake database)")
            print(f"   Error: {test_result.error}")
        print(f"   Tested at: {test_result.tested_at}")
    except Exception as e:
        print(f"❌ Failed to test connection: {e}")
    
    # Test 6: Create PostgreSQL datasource
    print("\n6. Creating a PostgreSQL datasource...")
    pg_create_request = DatabaseDatasourceCreate(
        name="Test PostgreSQL Database",
        description="A test PostgreSQL database",
        database_type=DatabaseType.POSTGRESQL,
        host="localhost",
        port=5432,
        database_name="test_pg_db",
        username="postgres",
        password="postgres",
        readonly_mode=True,
        allowed_operations=["SELECT"]
    )
    
    try:
        pg_datasource = await database_datasource_service.create_datasource(pg_create_request)
        print(f"✅ Created PostgreSQL datasource: {pg_datasource.name} (ID: {pg_datasource.id})")
        pg_datasource_id = pg_datasource.id
    except Exception as e:
        print(f"❌ Failed to create PostgreSQL datasource: {e}")
        pg_datasource_id = None
    
    # Test 7: List with filters
    print("\n7. Testing filtered listing...")
    try:
        mysql_datasources = await database_datasource_service.list_datasources(
            database_type=DatabaseType.MYSQL
        )
        print(f"✅ Found {len(mysql_datasources)} MySQL datasources")
        
        if pg_datasource_id:
            pg_datasources = await database_datasource_service.list_datasources(
                database_type=DatabaseType.POSTGRESQL
            )
            print(f"✅ Found {len(pg_datasources)} PostgreSQL datasources")
    except Exception as e:
        print(f"❌ Failed to list filtered datasources: {e}")
    
    # Test 8: Search functionality
    print("\n8. Testing search functionality...")
    try:
        search_results = await database_datasource_service.list_datasources(
            search="test"
        )
        print(f"✅ Found {len(search_results)} datasources matching 'test'")
        for ds in search_results:
            print(f"   - {ds.name}")
    except Exception as e:
        print(f"❌ Failed to search datasources: {e}")
    
    # Test 9: Delete datasources
    print(f"\n9. Cleaning up - deleting test datasources...")
    try:
        success = await database_datasource_service.delete_datasource(datasource_id)
        if success:
            print(f"✅ Deleted MySQL datasource (ID: {datasource_id})")
        else:
            print(f"❌ Failed to delete MySQL datasource")
        
        if pg_datasource_id:
            success = await database_datasource_service.delete_datasource(pg_datasource_id)
            if success:
                print(f"✅ Deleted PostgreSQL datasource (ID: {pg_datasource_id})")
            else:
                print(f"❌ Failed to delete PostgreSQL datasource")
    except Exception as e:
        print(f"❌ Failed to delete datasources: {e}")
    
    # Test 10: Verify deletion
    print("\n10. Verifying deletion...")
    try:
        final_datasources = await database_datasource_service.list_datasources()
        print(f"✅ Final count: {len(final_datasources)} datasources")
    except Exception as e:
        print(f"❌ Failed to verify deletion: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Database Datasource CRUD tests completed!")


async def test_configuration_persistence():
    """Test configuration file persistence"""
    print("\n🧪 Testing Configuration Persistence")
    print("=" * 50)
    
    # Create a test datasource
    create_request = DatabaseDatasourceCreate(
        name="Persistence Test DB",
        description="Testing configuration persistence",
        database_type=DatabaseType.MYSQL,
        host="test.example.com",
        port=3306,
        database_name="persistence_test",
        username="test_user",
        password="test_password",
        readonly_mode=True,
    )
    
    try:
        datasource = await database_datasource_service.create_datasource(create_request)
        print(f"✅ Created test datasource: {datasource.name}")
        
        # Create a new service instance to test loading from config
        from src.services.database_datasource import DatabaseDatasourceService
        new_service = DatabaseDatasourceService()
        
        # Check if the datasource is loaded
        loaded_datasource = await new_service.get_datasource(datasource.id)
        if loaded_datasource:
            print(f"✅ Datasource persisted and loaded successfully")
            print(f"   Name: {loaded_datasource.name}")
            print(f"   Host: {loaded_datasource.host}")
        else:
            print(f"❌ Datasource not found in new service instance")
        
        # Clean up
        await database_datasource_service.delete_datasource(datasource.id)
        print(f"✅ Cleaned up test datasource")
        
    except Exception as e:
        print(f"❌ Configuration persistence test failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting Database Datasource Tests")
    print("This will test the database datasource management functionality")
    print("Note: Connection tests will fail since we're using fake database credentials")
    
    asyncio.run(test_database_datasource_crud())
    asyncio.run(test_configuration_persistence())
    
    print("\n✨ All tests completed!")
