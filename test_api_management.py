#!/usr/bin/env python3
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Test script for API Management module
测试API管理模块的功能
"""

import asyncio
import json
from typing import Dict, Any

from src.models.api_tools import (
    APIDefinitionCreate, HTTPMethod, AuthConfig, AuthType,
    Parameter, ParameterType, DataType, RateLimit, ResponseConfig
)
from src.services.api_tools import APIDefinitionService, CurlParser
from src.database import get_db_session


def test_curl_parser():
    """测试curl解析器"""
    print("🔧 测试curl解析器...")
    
    parser = CurlParser()
    
    # 测试用例1: 简单GET请求
    curl1 = "curl -X GET 'https://api.github.com/users/octocat'"
    result1 = parser.parse_curl_command(curl1)
    print(f"✅ 简单GET请求解析: {result1.success}")
    if result1.success:
        print(f"   方法: {result1.method.name}, URL: {result1.url}")
    
    # 测试用例2: 带认证的POST请求
    curl2 = """curl -X POST 'https://api.example.com/data' \
               -H 'Authorization: Bearer token123' \
               -H 'Content-Type: application/json' \
               -d '{"name": "test", "value": 123}'"""
    result2 = parser.parse_curl_command(curl2)
    print(f"✅ 带认证POST请求解析: {result2.success}")
    if result2.success:
        print(f"   方法: {result2.method.name}, 认证类型: {result2.auth_config.auth_type if result2.auth_config else 'None'}")
    
    # 测试用例3: 带查询参数的请求
    curl3 = "curl 'https://api.example.com/search?q=test&limit=10'"
    result3 = parser.parse_curl_command(curl3)
    print(f"✅ 带查询参数请求解析: {result3.success}")
    if result3.success:
        print(f"   参数数量: {len(result3.parameters)}")


def test_api_definition_models():
    """测试API定义模型"""
    print("\n📊 测试API定义模型...")
    
    # 创建认证配置
    auth_config = AuthConfig(
        auth_type=AuthType.BEARER,
        bearer_token="test_token_123"
    )
    
    # 创建参数
    parameters = [
        Parameter(
            name="query",
            description="搜索查询",
            parameter_type=ParameterType.QUERY,
            data_type=DataType.STRING,
            required=True,
            example="test search"
        ),
        Parameter(
            name="limit",
            description="结果数量限制",
            parameter_type=ParameterType.QUERY,
            data_type=DataType.INTEGER,
            default_value=10,
            minimum=1,
            maximum=100
        )
    ]
    
    # 创建限流配置
    rate_limit = RateLimit.create_per_minute(60)
    
    # 创建响应配置
    response_config = ResponseConfig.create_rest_api_config()
    
    # 创建API定义
    api_def_create = APIDefinitionCreate(
        name="测试搜索API",
        description="用于测试的搜索API",
        category="search",
        method=HTTPMethod.GET,
        url="https://api.example.com/search",
        headers={"User-Agent": "DeerFlow/1.0"},
        timeout_seconds=30,
        auth_config=auth_config,
        parameters=parameters,
        response_config=response_config,
        rate_limit=rate_limit,
        enabled=True
    )
    
    print(f"✅ API定义创建成功: {api_def_create.name}")
    print(f"   方法: {api_def_create.method}")
    print(f"   参数数量: {len(api_def_create.parameters)}")
    print(f"   认证类型: {api_def_create.auth_config.auth_type}")
    print(f"   限流: {api_def_create.rate_limit.get_description()}")
    
    return api_def_create


async def test_api_execution():
    """测试API执行"""
    print("\n⚡ 测试API执行...")
    
    # 创建一个简单的测试API定义
    auth_config = AuthConfig(auth_type=AuthType.NONE)
    rate_limit = RateLimit.create_default()
    response_config = ResponseConfig.create_default_json()
    
    from src.models.api_tools import APIDefinition
    
    # 创建一个测试用的API定义（使用httpbin.org进行测试）
    api_def = APIDefinition(
        id=1,
        name="测试GET请求",
        description="使用httpbin.org测试GET请求",
        category="test",
        method=HTTPMethod.GET,
        url="https://httpbin.org/get",
        headers={},
        timeout_seconds=30,
        auth_config=auth_config,
        parameters=[],
        response_config=response_config,
        rate_limit=rate_limit,
        enabled=True
    )
    
    # 执行API
    from src.services.api_tools import APIExecutor
    executor = APIExecutor()
    
    try:
        result = await executor.execute_api(
            api_def=api_def,
            parameters={},
            session_id="test_session"
        )
        
        print(f"✅ API执行成功: {result.success}")
        print(f"   执行时间: {result.execution_time_ms}ms")
        print(f"   状态码: {result.result.status_code}")
        
        if result.result.parsed_data:
            print(f"   响应数据类型: {type(result.result.parsed_data)}")
    
    except Exception as e:
        print(f"❌ API执行失败: {str(e)}")


async def test_parameter_validation():
    """测试参数验证"""
    print("\n🔍 测试参数验证...")
    
    # 创建带参数验证的API定义
    parameters = [
        Parameter(
            name="email",
            description="邮箱地址",
            parameter_type=ParameterType.QUERY,
            data_type=DataType.STRING,
            required=True,
            pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        ),
        Parameter(
            name="age",
            description="年龄",
            parameter_type=ParameterType.QUERY,
            data_type=DataType.INTEGER,
            required=True,
            minimum=0,
            maximum=150
        )
    ]
    
    from src.services.api_tools import ParameterMapper
    mapper = ParameterMapper()
    
    # 创建模拟API定义
    from src.models.api_tools import APIDefinition
    api_def = APIDefinition(
        id=1,
        name="参数验证测试",
        description="测试参数验证功能",
        category="test",
        method=HTTPMethod.GET,
        url="https://httpbin.org/get",
        headers={},
        timeout_seconds=30,
        auth_config=AuthConfig(auth_type=AuthType.NONE),
        parameters=parameters,
        response_config=ResponseConfig.create_default_json(),
        rate_limit=RateLimit.create_default(),
        enabled=True
    )
    
    # 测试有效参数
    valid_params = {
        "email": "test@example.com",
        "age": 25
    }
    
    try:
        mapped = mapper.map_parameters(api_def, valid_params)
        print(f"✅ 有效参数验证通过")
        print(f"   查询参数: {mapped.query_params}")
    except Exception as e:
        print(f"❌ 有效参数验证失败: {str(e)}")
    
    # 测试无效参数
    invalid_params = {
        "email": "invalid_email",
        "age": 200
    }
    
    try:
        mapped = mapper.map_parameters(api_def, invalid_params)
        print(f"❌ 无效参数验证应该失败但通过了")
    except Exception as e:
        print(f"✅ 无效参数验证正确失败: {str(e)}")


def test_rate_limiter():
    """测试限流器"""
    print("\n🚦 测试限流器...")
    
    from src.services.api_tools import RateLimiter
    limiter = RateLimiter()
    
    # 创建限流配置
    rate_limit = RateLimit(
        enabled=True,
        rate_limit_type=1,  # PER_MINUTE
        max_requests=5,
        time_window_seconds=60
    )
    
    # 获取限流状态
    status = limiter.get_rate_limit_status(1, rate_limit)
    print(f"✅ 限流状态获取成功")
    print(f"   启用: {status['enabled']}")
    print(f"   当前请求数: {status['current_requests']}")
    print(f"   最大请求数: {status['max_requests']}")
    print(f"   剩余请求数: {status['remaining_requests']}")


async def main():
    """主测试函数"""
    print("🚀 开始测试API管理模块...")
    
    # 1. 测试curl解析器
    test_curl_parser()
    
    # 2. 测试API定义模型
    api_def_create = test_api_definition_models()
    
    # 3. 测试API执行
    await test_api_execution()
    
    # 4. 测试参数验证
    await test_parameter_validation()
    
    # 5. 测试限流器
    test_rate_limiter()
    
    print("\n✅ API管理模块测试完成！")


if __name__ == "__main__":
    asyncio.run(main())
