#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资源发现工具集成测试

测试资源发现工具与 DeerFlow Agent 的集成
"""

import asyncio
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_discover_resources_tool():
    """测试资源发现工具"""
    print("\n🔍 测试资源发现工具...")
    
    try:
        from src.tools.resource_discovery import discover_resources
        
        # 测试查询
        test_queries = [
            "查询数据库中的用户信息",
            "获取天气API",
            "执行SQL查询",
            "调用HTTP接口"
        ]
        
        for query in test_queries:
            print(f"\n查询: '{query}'")
            
            result = await discover_resources(
                user_query=query,
                max_results=3,
                min_confidence=0.1
            )
            
            if result.get("success"):
                matches = result.get("matches", [])
                print(f"  找到 {len(matches)} 个匹配资源:")
                
                for i, match in enumerate(matches, 1):
                    print(f"    {i}. {match['resource_name']} ({match['resource_type']})")
                    print(f"       相似度: {match['similarity_score']}, 置信度: {match['confidence_score']}")
                    print(f"       描述: {match['description']}")
            else:
                print(f"  ❌ 查询失败: {result.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 资源发现工具测试失败: {e}")
        return False


async def test_sync_resources_tool():
    """测试资源同步工具"""
    print("\n🔄 测试资源同步工具...")
    
    try:
        from src.tools.resource_discovery import sync_system_resources
        
        # 测试增量同步
        print("执行增量同步...")
        result = await sync_system_resources(force_full_sync=False)
        
        if result.get("success"):
            print(f"✅ 增量同步成功:")
            print(f"  处理时间: {result.get('total_processing_time', 'N/A')}")
            print(f"  处理的变更: {result.get('processed_changes', {})}")
        else:
            print(f"❌ 增量同步失败: {result.get('error', 'Unknown error')}")
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"❌ 资源同步工具测试失败: {e}")
        return False


async def test_statistics_tool():
    """测试统计信息工具"""
    print("\n📊 测试统计信息工具...")
    
    try:
        from src.tools.resource_discovery import get_resource_statistics
        
        result = await get_resource_statistics()
        
        if result.get("success"):
            summary = result.get("summary", {})
            by_type = result.get("by_type", {})
            
            print(f"✅ 统计信息获取成功:")
            print(f"  总资源数: {summary.get('total_resources', 0)}")
            print(f"  活跃资源数: {summary.get('active_resources', 0)}")
            print(f"  已向量化资源数: {summary.get('vectorized_resources', 0)}")
            print(f"  向量化率: {summary.get('vectorization_rate', 0)}%")
            
            print(f"\n  按类型分布:")
            for resource_type, stats in by_type.items():
                print(f"    {resource_type}: {stats['total']} 总数, {stats['active']} 活跃, {stats['vectorized']} 已向量化")
        else:
            print(f"❌ 统计信息获取失败: {result.get('error', 'Unknown error')}")
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"❌ 统计信息工具测试失败: {e}")
        return False


async def test_search_by_type_tool():
    """测试按类型搜索工具"""
    print("\n🔍 测试按类型搜索工具...")
    
    try:
        from src.tools.resource_discovery import search_resources_by_type
        
        # 测试不同类型
        resource_types = ["database", "api", "text2sql"]
        
        for resource_type in resource_types:
            print(f"\n搜索 {resource_type} 类型资源:")
            
            result = await search_resources_by_type(
                resource_type=resource_type,
                limit=5
            )
            
            if result.get("success"):
                resources = result.get("resources", [])
                print(f"  找到 {len(resources)} 个 {resource_type} 资源:")
                
                for i, resource in enumerate(resources, 1):
                    print(f"    {i}. {resource['resource_name']} ({resource['resource_id']})")
                    print(f"       状态: {resource['status']}, 向量化: {resource['vectorization_status']}")
            else:
                print(f"  ❌ 搜索失败: {result.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 按类型搜索工具测试失败: {e}")
        return False


async def test_tool_decorator():
    """测试工具装饰器"""
    print("\n🔧 测试工具装饰器...")
    
    try:
        from src.tools.resource_discovery import discover_resources
        
        # 检查工具是否有正确的属性
        if hasattr(discover_resources, '__tool__') or hasattr(discover_resources, '_tool_name'):
            print("✅ 工具装饰器正常工作")
            return True
        else:
            print("❌ 工具装饰器未正确应用")
            return False
        
    except Exception as e:
        print(f"❌ 工具装饰器测试失败: {e}")
        return False


async def test_integration_scenario():
    """测试完整的集成场景"""
    print("\n🎯 测试完整集成场景...")
    
    try:
        from src.tools.resource_discovery import (
            sync_system_resources,
            discover_resources,
            get_resource_statistics
        )
        
        # 1. 首先同步资源
        print("1. 同步系统资源...")
        sync_result = await sync_system_resources(force_full_sync=False)
        if not sync_result.get("success"):
            print(f"❌ 同步失败: {sync_result.get('error')}")
            return False
        
        # 2. 获取统计信息
        print("2. 获取统计信息...")
        stats_result = await get_resource_statistics()
        if not stats_result.get("success"):
            print(f"❌ 统计获取失败: {stats_result.get('error')}")
            return False
        
        total_resources = stats_result.get("summary", {}).get("total_resources", 0)
        print(f"   系统中共有 {total_resources} 个资源")
        
        # 3. 执行智能查询
        print("3. 执行智能资源查询...")
        query_result = await discover_resources(
            user_query="查询数据库信息",
            max_results=3
        )
        
        if query_result.get("success"):
            matches = query_result.get("matches", [])
            print(f"   找到 {len(matches)} 个匹配资源")
            
            if matches:
                best_match = matches[0]
                print(f"   最佳匹配: {best_match['resource_name']} (置信度: {best_match['confidence_score']})")
        else:
            print(f"❌ 查询失败: {query_result.get('error')}")
            return False
        
        print("✅ 完整集成场景测试成功")
        return True
        
    except Exception as e:
        print(f"❌ 集成场景测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始资源发现工具集成测试...")
    print("=" * 60)
    
    start_time = datetime.now()
    
    # 执行各项测试
    tests = [
        ("工具装饰器", test_tool_decorator),
        ("资源同步工具", test_sync_resources_tool),
        ("统计信息工具", test_statistics_tool),
        ("按类型搜索工具", test_search_by_type_tool),
        ("资源发现工具", test_discover_resources_tool),
        ("完整集成场景", test_integration_scenario),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results[test_name] = False
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print(f"🎉 资源发现工具集成测试完成!")
    print(f"总耗时: {duration.total_seconds():.2f} 秒")
    print("\n📋 测试结果:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 测试总结: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！资源发现工具已成功集成到 DeerFlow Agent")
        print("\n📝 使用说明:")
        print("1. 使用 discover_resources() 进行智能资源发现")
        print("2. 使用 sync_system_resources() 同步系统资源")
        print("3. 使用 get_resource_statistics() 获取统计信息")
        print("4. 使用 search_resources_by_type() 按类型搜索资源")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查相关问题")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(main())
