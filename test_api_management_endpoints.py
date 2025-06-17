#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 管理端点测试脚本
测试已迁移的 API 管理功能
"""

import asyncio
import httpx
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

async def test_server_health():
    """测试服务器是否可用"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/")
            print(f"✅ 服务器运行正常 (状态码: {response.status_code})")
            return True
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        return False

async def test_api_definitions_list():
    """测试获取 API 定义列表"""
    print("\n🔍 测试 API 定义列表...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/admin/api-definitions")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功获取 API 定义列表")
                print(f"   API 数量: {len(data)}")
                if data:
                    print(f"   第一个 API: {data[0].get('name', 'N/A')}")
                return True
            else:
                print(f"❌ 请求失败: {response.text}")
                return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

async def test_api_statistics():
    """测试获取 API 统计信息"""
    print("\n📊 测试 API 统计信息...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/admin/api-definitions/statistics/summary")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功获取统计信息")
                print(f"   总 API 数: {data.get('total_apis', 0)}")
                print(f"   启用的 API: {data.get('enabled_apis', 0)}")
                print(f"   分类分布: {data.get('category_distribution', {})}")
                return True
            else:
                print(f"❌ 请求失败: {response.text}")
                return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

async def test_api_categories():
    """测试获取 API 分类"""
    print("\n🏷️ 测试 API 分类...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/admin/api-definitions/categories/list")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功获取分类列表")
                print(f"   分类: {data.get('categories', [])}")
                return True
            else:
                print(f"❌ 请求失败: {response.text}")
                return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

async def test_create_api_definition():
    """测试创建 API 定义"""
    print("\n➕ 测试创建 API 定义...")
    
    # 构建测试 API 定义
    api_data = {
        "name": "测试 API - httpbin",
        "description": "用于测试的 httpbin API",
        "category": "test",
        "method": 0,  # GET
        "url": "https://httpbin.org/get",
        "headers": {},
        "timeout_seconds": 30,
        "auth_config": {
            "auth_type": 0,  # NONE
            "api_key": None,
            "api_key_header": "X-API-Key",
            "bearer_token": None,
            "username": None,
            "password": None,
            "oauth2_token": None,
            "oauth2_token_url": None,
            "oauth2_client_id": None,
            "oauth2_client_secret": None,
            "oauth2_scope": None,
            "custom_headers": {},
            "custom_params": {}
        },
        "parameters": [],
        "response_schema": None,
        "response_config": {
            "response_type": 1,  # JSON
            "content_type": "application/json",
            "encoding": "utf-8",
            "fields": [],
            "primary_data_field": None,
            "status_field": None,
            "message_field": None,
            "success_conditions": {}
        },
        "rate_limit": {
            "enabled": False,
            "rate_limit_type": 0,  # NONE
            "max_requests": 100,
            "time_window_seconds": 60,
            "burst_size": None,
            "block_on_limit": True,
            "retry_after_seconds": None
        },
        "enabled": True
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/admin/api-definitions",
                json=api_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功创建 API 定义")
                print(f"   API ID: {data.get('id')}")
                print(f"   API 名称: {data.get('name')}")
                return data.get('id')
            else:
                print(f"❌ 创建失败: {response.text}")
                return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

async def test_get_api_definition(api_id: int):
    """测试获取单个 API 定义"""
    print(f"\n🔍 测试获取 API 定义 (ID: {api_id})...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/admin/api-definitions/{api_id}")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功获取 API 定义")
                print(f"   名称: {data.get('name')}")
                print(f"   URL: {data.get('url')}")
                print(f"   启用状态: {data.get('enabled')}")
                return True
            else:
                print(f"❌ 获取失败: {response.text}")
                return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

async def test_delete_api_definition(api_id: int):
    """测试删除 API 定义"""
    print(f"\n🗑️ 测试删除 API 定义 (ID: {api_id})...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{BASE_URL}/api/admin/api-definitions/{api_id}")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ 成功删除 API 定义")
                return True
            else:
                print(f"❌ 删除失败: {response.text}")
                return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始测试 API 管理端点...")
    print("=" * 50)
    
    # 1. 测试服务器健康状态
    if not await test_server_health():
        print("❌ 服务器不可用，停止测试")
        return
    
    # 2. 测试获取 API 列表
    await test_api_definitions_list()
    
    # 3. 测试获取统计信息
    await test_api_statistics()
    
    # 4. 测试获取分类
    await test_api_categories()
    
    # 5. 测试创建 API 定义
    created_api_id = await test_create_api_definition()
    
    if created_api_id:
        # 6. 测试获取单个 API 定义
        await test_get_api_definition(created_api_id)
        
        # 7. 测试删除 API 定义
        await test_delete_api_definition(created_api_id)
    
    print("\n" + "=" * 50)
    print("🎉 API 管理端点测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
