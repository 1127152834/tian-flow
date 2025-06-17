#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 执行功能测试脚本
测试 API 定义的执行功能
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def create_test_api():
    """创建一个测试用的 API 定义"""
    print("📝 创建测试 API 定义...")
    
    api_data = {
        "name": "httpbin GET 测试",
        "description": "测试 httpbin.org 的 GET 端点",
        "category": "test",
        "method": 0,  # GET
        "url": "https://httpbin.org/get",
        "headers": {"User-Agent": "DeerFlow-Test"},
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
        "parameters": [
            {
                "name": "test_param",
                "parameter_type": 0,  # QUERY
                "data_type": 0,  # STRING
                "required": False,
                "default_value": "hello",
                "description": "测试参数",
                "validation_rules": {},
                "example_value": "world"
            }
        ],
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
            
            if response.status_code == 200:
                data = response.json()
                api_id = data.get('id')
                print(f"✅ 创建成功，API ID: {api_id}")
                return api_id
            else:
                print(f"❌ 创建失败: {response.text}")
                return None
    except Exception as e:
        print(f"❌ 创建异常: {e}")
        return None

async def test_api_execution(api_id: int):
    """测试 API 执行"""
    print(f"\n⚡ 测试 API 执行 (ID: {api_id})...")
    
    # 执行参数
    execution_data = {
        "parameters": {
            "test_param": "DeerFlow测试"
        },
        "session_id": "test_session_123"
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/admin/api-definitions/{api_id}/execute",
                json=execution_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API 执行成功")
                print(f"   执行时间: {data.get('execution_time_ms', 0)}ms")
                print(f"   成功状态: {data.get('success', False)}")
                
                if data.get('result'):
                    result = data['result']
                    print(f"   HTTP 状态码: {result.get('status_code', 'N/A')}")
                    print(f"   响应大小: {len(str(result.get('raw_data', '')))} 字符")
                    
                    # 显示部分响应数据
                    if result.get('parsed_data'):
                        parsed = result['parsed_data']
                        if isinstance(parsed, dict):
                            print(f"   响应 URL: {parsed.get('url', 'N/A')}")
                            print(f"   请求参数: {parsed.get('args', {})}")
                
                return True
            else:
                print(f"❌ 执行失败: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ 执行异常: {e}")
        return False

async def test_api_test_endpoint(api_id: int):
    """测试 API 测试端点"""
    print(f"\n🧪 测试 API 测试端点 (ID: {api_id})...")
    
    test_data = {
        "parameters": {
            "test_param": "测试值"
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/admin/api-definitions/{api_id}/test",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API 测试成功")
                print(f"   测试结果: {data.get('success', False)}")
                print(f"   执行时间: {data.get('execution_time_ms', 0)}ms")
                return True
            else:
                print(f"❌ 测试失败: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

async def cleanup_test_api(api_id: int):
    """清理测试 API"""
    print(f"\n🧹 清理测试 API (ID: {api_id})...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{BASE_URL}/api/admin/api-definitions/{api_id}")
            
            if response.status_code == 200:
                print("✅ 清理成功")
                return True
            else:
                print(f"❌ 清理失败: {response.text}")
                return False
    except Exception as e:
        print(f"❌ 清理异常: {e}")
        return False

async def test_curl_parser():
    """测试 curl 解析功能"""
    print("\n🔧 测试 curl 解析功能...")
    
    curl_command = 'curl -X GET "https://httpbin.org/get?test=value" -H "User-Agent: Test"'
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/admin/curl-parser/parse",
                json={"curl_command": curl_command},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ curl 解析成功")
                print(f"   解析的 URL: {data.get('url', 'N/A')}")
                print(f"   HTTP 方法: {data.get('method', 'N/A')}")
                print(f"   请求头数量: {len(data.get('headers', {}))}")
                return True
            else:
                print(f"❌ 解析失败: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ 解析异常: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始测试 API 执行功能...")
    print("=" * 50)
    
    # 1. 测试 curl 解析
    await test_curl_parser()
    
    # 2. 创建测试 API
    api_id = await create_test_api()
    
    if api_id:
        # 3. 测试 API 执行
        await test_api_execution(api_id)
        
        # 4. 测试 API 测试端点
        await test_api_test_endpoint(api_id)
        
        # 5. 清理测试数据
        await cleanup_test_api(api_id)
    else:
        print("❌ 无法创建测试 API，跳过执行测试")
    
    print("\n" + "=" * 50)
    print("🎉 API 执行功能测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
