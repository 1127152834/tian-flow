#!/usr/bin/env python3

import asyncio
from src.services.resource_discovery.resource_discovery_service import ResourceDiscoveryService

async def test_text2sql_discovery():
    """测试 Text2SQL 资源发现"""
    
    print("=== 测试 Text2SQL 资源发现 ===")
    
    # 创建资源发现服务
    service = ResourceDiscoveryService()
    
    try:
        # 调用修改后的 Text2SQL 资源发现方法
        resources = await service._discover_text2sql_resources_with_tools()
        
        print(f"✅ 发现了 {len(resources)} 个 Text2SQL 资源")
        
        # 显示前几个资源的详情
        for i, resource in enumerate(resources[:5]):
            print(f"\n资源 {i+1}:")
            print(f"  ID: {resource['resource_id']}")
            print(f"  名称: {resource['resource_name']}")
            print(f"  描述: {resource['description']}")
            print(f"  元数据: {resource['metadata']}")
        
        if len(resources) > 5:
            print(f"\n... 还有 {len(resources) - 5} 个资源")
        
        # 按内容类型统计
        content_types = {}
        for resource in resources:
            content_type = resource['metadata'].get('content_type', 'UNKNOWN')
            if content_type not in content_types:
                content_types[content_type] = 0
            content_types[content_type] += 1
        
        print(f"\n=== 按内容类型统计 ===")
        for content_type, count in content_types.items():
            print(f"  {content_type}: {count} 个资源")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_text2sql_discovery())
