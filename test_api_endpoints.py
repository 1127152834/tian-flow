#!/usr/bin/env python3
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Test script for database datasource API endpoints.
This script tests the REST API endpoints to ensure they work correctly.
"""

import asyncio
import json
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_api_endpoints():
    """Test all database datasource API endpoints"""
    print("🧪 Testing Database Datasource API Endpoints")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test 1: List datasources (should be empty initially)
        print("\n1. Testing GET /api/database-datasources")
        try:
            response = await client.get(f"{BASE_URL}/api/database-datasources")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {data['total']} datasources")
                print(f"Response: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Test 2: Create a new datasource
        print("\n2. Testing POST /api/database-datasources")
        create_data = {
            "name": "Test MySQL Database",
            "description": "A test MySQL database for API testing",
            "database_type": "MYSQL",
            "host": "localhost",
            "port": 3306,
            "database_name": "test_db",
            "username": "test_user",
            "password": "test_password",
            "readonly_mode": True,
            "allowed_operations": ["SELECT", "SHOW"]
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/database-datasources",
                json=create_data
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                datasource = response.json()
                datasource_id = datasource["id"]
                print(f"✅ Created datasource with ID: {datasource_id}")
                print(f"Name: {datasource['name']}")
                print(f"Type: {datasource['database_type']}")
                print(f"Status: {datasource['connection_status']}")
            else:
                print(f"❌ Error: {response.text}")
                return
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return
        
        # Test 3: Get specific datasource
        print(f"\n3. Testing GET /api/database-datasources/{datasource_id}")
        try:
            response = await client.get(f"{BASE_URL}/api/database-datasources/{datasource_id}")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                datasource = response.json()
                print(f"✅ Retrieved datasource: {datasource['name']}")
                print(f"Host: {datasource['host']}:{datasource['port']}")
                print(f"Database: {datasource['database_name']}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Test 4: Update datasource
        print(f"\n4. Testing PUT /api/database-datasources/{datasource_id}")
        update_data = {
            "description": "Updated description for test database",
            "port": 3307,
            "allowed_operations": ["SELECT", "SHOW", "DESCRIBE"]
        }
        
        try:
            response = await client.put(
                f"{BASE_URL}/api/database-datasources/{datasource_id}",
                json=update_data
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                datasource = response.json()
                print(f"✅ Updated datasource: {datasource['name']}")
                print(f"New port: {datasource['port']}")
                print(f"New description: {datasource['description']}")
                print(f"Allowed operations: {datasource['allowed_operations']}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Test 5: Test connection (will fail since it's a fake database)
        print(f"\n5. Testing POST /api/database-datasources/{datasource_id}/test")
        try:
            response = await client.post(
                f"{BASE_URL}/api/database-datasources/{datasource_id}/test",
                json={"timeout": 5}
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    print(f"✅ Connection test successful")
                    print(f"Details: {result.get('details', {})}")
                else:
                    print(f"⚠️ Connection test failed (expected for fake database)")
                    print(f"Error: {result.get('error', 'Unknown error')}")
                print(f"Tested at: {result['tested_at']}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Test 6: Get database schema (will fail since connection doesn't work)
        print(f"\n6. Testing GET /api/database-datasources/{datasource_id}/schema")
        try:
            response = await client.get(f"{BASE_URL}/api/database-datasources/{datasource_id}/schema")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                schema = response.json()
                print(f"✅ Retrieved schema with {schema['total_tables']} tables")
                print(f"Schema extracted at: {schema['schema_extracted_at']}")
            else:
                print(f"⚠️ Schema extraction failed (expected for fake database)")
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Test 7: List datasources with filters
        print("\n7. Testing GET /api/database-datasources with filters")
        try:
            response = await client.get(
                f"{BASE_URL}/api/database-datasources",
                params={
                    "database_type": "MYSQL",
                    "search": "test"
                }
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {len(data['datasources'])} MySQL datasources matching 'test'")
                for ds in data['datasources']:
                    print(f"   - {ds['name']} ({ds['database_type']})")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Test 8: Delete datasource
        print(f"\n8. Testing DELETE /api/database-datasources/{datasource_id}")
        try:
            response = await client.delete(f"{BASE_URL}/api/database-datasources/{datasource_id}")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result['message']}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Test 9: Verify deletion
        print(f"\n9. Verifying deletion - GET /api/database-datasources/{datasource_id}")
        try:
            response = await client.get(f"{BASE_URL}/api/database-datasources/{datasource_id}")
            print(f"Status: {response.status_code}")
            if response.status_code == 404:
                print(f"✅ Datasource successfully deleted (404 as expected)")
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Test 10: Final list check
        print("\n10. Final check - GET /api/database-datasources")
        try:
            response = await client.get(f"{BASE_URL}/api/database-datasources")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Final count: {data['total']} datasources")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API endpoint tests completed!")


async def test_server_health():
    """Test if the server is running"""
    print("🔍 Checking server health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/config")
            if response.status_code == 200:
                print("✅ Server is running and responding")
                return True
            else:
                print(f"⚠️ Server responded with status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Server is not responding: {e}")
        print("Make sure to start the server with: uv run server.py")
        return False


if __name__ == "__main__":
    print("🚀 Starting Database Datasource API Tests")
    print("This will test all the REST API endpoints for database management")
    print(f"Server URL: {BASE_URL}")
    
    async def main():
        if await test_server_health():
            await test_api_endpoints()
        else:
            print("\n❌ Cannot run tests - server is not available")
            print("Please start the server first with: uv run server.py")
    
    asyncio.run(main())
    print("\n✨ All tests completed!")
