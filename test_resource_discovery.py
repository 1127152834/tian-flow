#!/usr/bin/env python3
"""
Test resource discovery service
"""
import asyncio
import json
from src.services.resource_discovery.resource_discovery_service import ResourceDiscoveryService

async def test_text2sql_discovery():
    """Test Text2SQL resource discovery"""
    try:
        print("=== Testing Text2SQL Resource Discovery ===")
        
        service = ResourceDiscoveryService()
        
        # Test the _discover_text2sql_resources_with_tools method
        resources = await service._discover_text2sql_resources_with_tools()
        
        print(f"Discovered {len(resources)} Text2SQL resources:")
        
        for resource in resources:
            print(f"  - {resource['resource_id']}: {resource['resource_name']}")
            print(f"    Description: {resource['description']}")
            print(f"    Metadata: {resource['metadata']}")
            print()
            
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_text2sql_discovery())
