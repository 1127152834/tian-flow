#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前后端集成测试脚本
测试前端调用后端 API 的实际情况
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_missing_backend_endpoints():
    """测试前端需要但后端缺失的接口"""
    print("🔍 测试缺失的后端接口...")
    
    missing_endpoints = [
        ("GET", "/api/admin/api-definitions/count", "计数接口"),
        ("POST", "/api/admin/api-definitions/1/toggle", "切换启用状态"),
        ("GET", "/api/admin/api-definitions/recent/list", "获取最近API"),
        ("POST", "/api/admin/api-definitions/bulk/update", "批量更新"),
    ]
    
    async with httpx.AsyncClient() as client:
        for method, endpoint, description in missing_endpoints:
            try:
                if method == "GET":
                    response = await client.get(f"{BASE_URL}{endpoint}")
                else:
                    response = await client.post(f"{BASE_URL}{endpoint}", json={})
                
                if response.status_code == 404:
                    print(f"❌ {description}: {endpoint} - 接口不存在 (404)")
                elif response.status_code == 405:
                    print(f"❌ {description}: {endpoint} - 方法不允许 (405)")
                else:
                    print(f"✅ {description}: {endpoint} - 接口存在 ({response.status_code})")
                    
            except Exception as e:
                print(f"❌ {description}: {endpoint} - 请求失败: {e}")

async def test_data_type_consistency():
    """测试数据类型一致性"""
    print("\n🔍 测试数据类型一致性...")
    
    async with httpx.AsyncClient() as client:
        try:
            # 获取API列表
            response = await client.get(f"{BASE_URL}/api/admin/api-definitions")
            if response.status_code == 200:
                data = response.json()
                if data:
                    api_item = data[0]
                    print(f"✅ 获取到API数据")
                    print(f"   method 字段类型: {type(api_item.get('method'))} (值: {api_item.get('method')})")
                    print(f"   auth_config 字段类型: {type(api_item.get('auth_config'))}")
                    print(f"   parameters 字段类型: {type(api_item.get('parameters'))}")
                    print(f"   response_config 字段类型: {type(api_item.get('response_config'))}")
                    print(f"   rate_limit 字段类型: {type(api_item.get('rate_limit'))}")
                    
                    # 检查是否需要类型转换
                    if isinstance(api_item.get('method'), int):
                        print("⚠️  method 字段是 int，前端需要转换为 HTTPMethod enum")
                    
                    if isinstance(api_item.get('auth_config'), dict):
                        print("⚠️  auth_config 字段是 dict，前端需要转换为 AuthConfig 类型")
                else:
                    print("ℹ️  API列表为空，无法测试数据类型")
            else:
                print(f"❌ 获取API列表失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 数据类型测试失败: {e}")

async def test_curl_parser_integration():
    """测试 curl 解析器集成"""
    print("\n🔍 测试 curl 解析器集成...")
    
    test_curl = 'curl -X GET "https://httpbin.org/get?test=value" -H "User-Agent: Test"'
    
    async with httpx.AsyncClient() as client:
        try:
            # 测试解析
            response = await client.post(
                f"{BASE_URL}/api/admin/curl-parse/parse",
                json={"curl_command": test_curl}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ curl 解析成功")
                print(f"   返回字段: {list(data.keys())}")
                
                # 检查返回格式是否符合前端期望
                expected_fields = ["success", "api_definition", "message"]
                for field in expected_fields:
                    if field in data:
                        print(f"   ✅ {field} 字段存在")
                    else:
                        print(f"   ❌ {field} 字段缺失")
            else:
                print(f"❌ curl 解析失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ curl 解析测试失败: {e}")

async def test_api_execution_integration():
    """测试 API 执行集成"""
    print("\n🔍 测试 API 执行集成...")
    
    async with httpx.AsyncClient() as client:
        try:
            # 先获取一个API定义
            response = await client.get(f"{BASE_URL}/api/admin/api-definitions")
            if response.status_code == 200:
                apis = response.json()
                if apis:
                    api_id = apis[0]['id']
                    
                    # 测试执行API
                    exec_response = await client.post(
                        f"{BASE_URL}/api/admin/api-definitions/{api_id}/execute",
                        json={
                            "parameters": {},
                            "session_id": "test_session"
                        }
                    )
                    
                    if exec_response.status_code == 200:
                        exec_data = exec_response.json()
                        print(f"✅ API 执行成功")
                        print(f"   返回字段: {list(exec_data.keys())}")
                        
                        # 检查返回格式
                        expected_fields = ["success", "api_definition_id", "execution_time_ms", "result"]
                        for field in expected_fields:
                            if field in exec_data:
                                print(f"   ✅ {field} 字段存在")
                            else:
                                print(f"   ❌ {field} 字段缺失")
                    else:
                        print(f"❌ API 执行失败: {exec_response.status_code} - {exec_response.text}")
                else:
                    print("ℹ️  没有可用的API定义进行测试")
            else:
                print(f"❌ 获取API列表失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ API 执行测试失败: {e}")

async def test_api_call_logs_integration():
    """测试 API 调用日志集成"""
    print("\n🔍 测试 API 调用日志集成...")
    
    async with httpx.AsyncClient() as client:
        try:
            # 测试获取日志列表
            response = await client.get(f"{BASE_URL}/api/admin/api-call-logs")
            
            if response.status_code == 200:
                logs = response.json()
                print(f"✅ 获取调用日志成功")
                print(f"   日志数量: {len(logs)}")
                
                if logs:
                    log_item = logs[0]
                    print(f"   日志字段: {list(log_item.keys())}")
                    
                    # 测试获取单个日志
                    log_id = log_item['id']
                    detail_response = await client.get(f"{BASE_URL}/api/admin/api-call-logs/{log_id}")
                    
                    if detail_response.status_code == 200:
                        print(f"   ✅ 获取单个日志成功")
                    else:
                        print(f"   ❌ 获取单个日志失败: {detail_response.status_code}")
                        
            else:
                print(f"❌ 获取调用日志失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ 调用日志测试失败: {e}")

async def main():
    """主测试函数"""
    print("🚀 开始前后端集成测试...")
    print("=" * 60)
    
    # 1. 测试缺失的后端接口
    await test_missing_backend_endpoints()
    
    # 2. 测试数据类型一致性
    await test_data_type_consistency()
    
    # 3. 测试 curl 解析器集成
    await test_curl_parser_integration()
    
    # 4. 测试 API 执行集成
    await test_api_execution_integration()
    
    # 5. 测试 API 调用日志集成
    await test_api_call_logs_integration()
    
    print("\n" + "=" * 60)
    print("🎉 前后端集成测试完成！")
    print("\n📋 总结:")
    print("1. 检查上述输出中的 ❌ 标记，这些是需要修复的问题")
    print("2. ⚠️ 标记表示需要注意的兼容性问题")
    print("3. ✅ 标记表示工作正常的功能")

if __name__ == "__main__":
    asyncio.run(main())
