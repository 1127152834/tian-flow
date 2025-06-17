#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 管理模块调试测试
"""

import sys
import traceback
from sqlalchemy.orm import Session
from sqlalchemy import text

# 添加项目根目录到 Python 路径
sys.path.insert(0, '.')

def test_database_connection():
    """测试数据库连接"""
    try:
        from src.database import get_db_session
        
        # 获取数据库会话
        db_session = next(get_db_session())
        
        # 测试简单查询
        result = db_session.execute(text("SELECT 1 as test")).fetchone()
        print(f"✅ 数据库连接成功: {result}")

        # 检查 api_tools schema 是否存在
        schema_result = db_session.execute(text("""
            SELECT schema_name FROM information_schema.schemata
            WHERE schema_name = 'api_tools'
        """)).fetchone()

        if schema_result:
            print("✅ api_tools schema 存在")
        else:
            print("❌ api_tools schema 不存在")
            return False

        # 检查表是否存在
        table_result = db_session.execute(text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'api_tools' AND table_name = 'api_definitions'
        """)).fetchone()
        
        if table_result:
            print("✅ api_definitions 表存在")
        else:
            print("❌ api_definitions 表不存在")
            return False
            
        db_session.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        traceback.print_exc()
        return False

def test_api_definition_model():
    """测试 API 定义模型"""
    try:
        from src.models.api_tools import APIDefinition, APIDefinitionCreate, AuthConfig, ResponseConfig, RateLimit
        
        print("✅ API 定义模型导入成功")
        
        # 测试创建简单的 API 定义
        auth_config = AuthConfig(auth_type=0)
        response_config = ResponseConfig(response_type=1, content_type="application/json", encoding="utf-8")
        rate_limit = RateLimit(enabled=False, rate_limit_type=0, max_requests=100, time_window_seconds=60, block_on_limit=True)
        
        api_create = APIDefinitionCreate(
            name="Test API",
            description="Test description",
            category="test",
            method=0,
            url="https://httpbin.org/get",
            headers={},
            timeout_seconds=30,
            auth_config=auth_config,
            parameters=[],
            response_config=response_config,
            rate_limit=rate_limit,
            enabled=True
        )
        
        print("✅ API 定义创建模型构建成功")
        print(f"   - 名称: {api_create.name}")
        print(f"   - 认证配置: {api_create.auth_config}")
        print(f"   - 响应配置: {api_create.response_config}")
        print(f"   - 限流配置: {api_create.rate_limit}")
        
        return True
        
    except Exception as e:
        print(f"❌ API 定义模型测试失败: {e}")
        traceback.print_exc()
        return False

def test_api_definition_repository():
    """测试 API 定义仓库"""
    try:
        from src.repositories.api_tools import APIDefinitionRepository
        from src.models.api_tools import APIDefinitionCreate, AuthConfig, ResponseConfig, RateLimit
        from src.database import get_db_session
        
        print("✅ API 定义仓库导入成功")
        
        # 获取数据库会话
        db_session = next(get_db_session())
        
        # 创建仓库实例
        repo = APIDefinitionRepository()
        
        # 测试获取列表（应该为空）
        api_list = repo.get_all(db_session)
        print(f"✅ 获取 API 列表成功，当前数量: {len(api_list)}")
        
        # 测试创建 API 定义
        auth_config = AuthConfig(auth_type=0)
        response_config = ResponseConfig(response_type=1, content_type="application/json", encoding="utf-8")
        rate_limit = RateLimit(enabled=False, rate_limit_type=0, max_requests=100, time_window_seconds=60, block_on_limit=True)
        
        api_create = APIDefinitionCreate(
            name="Debug Test API",
            description="Debug test description",
            category="debug",
            method=0,
            url="https://httpbin.org/get",
            headers={},
            timeout_seconds=30,
            auth_config=auth_config,
            parameters=[],
            response_config=response_config,
            rate_limit=rate_limit,
            enabled=True
        )
        
        # 尝试创建
        created_api = repo.create(db_session, api_create)
        print(f"✅ API 定义创建成功，ID: {created_api.id}")
        
        # 清理测试数据
        repo.delete(db_session, created_api.id)
        print("✅ 测试数据清理完成")
        
        db_session.close()
        return True
        
    except Exception as e:
        print(f"❌ API 定义仓库测试失败: {e}")
        traceback.print_exc()
        return False

def test_api_definition_service():
    """测试 API 定义服务"""
    try:
        from src.services.api_tools import APIDefinitionService
        from src.database import get_db_session
        
        print("✅ API 定义服务导入成功")
        
        # 获取数据库会话
        db_session = next(get_db_session())
        
        # 创建服务实例
        service = APIDefinitionService()
        
        # 测试获取列表
        api_list = service.get_api_definitions(db_session)
        print(f"✅ 服务获取 API 列表成功，当前数量: {len(api_list)}")
        
        # 测试统计信息
        stats = service.get_api_statistics(db_session)
        print(f"✅ 获取统计信息成功: {stats}")
        
        db_session.close()
        return True
        
    except Exception as e:
        print(f"❌ API 定义服务测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🔍 开始 API 管理模块调试测试")
    print("=" * 50)
    
    # 测试数据库连接
    print("\n1. 测试数据库连接")
    if not test_database_connection():
        print("❌ 数据库连接测试失败，停止后续测试")
        return
    
    # 测试模型
    print("\n2. 测试 API 定义模型")
    if not test_api_definition_model():
        print("❌ 模型测试失败，停止后续测试")
        return
    
    # 测试仓库
    print("\n3. 测试 API 定义仓库")
    if not test_api_definition_repository():
        print("❌ 仓库测试失败，停止后续测试")
        return
    
    # 测试服务
    print("\n4. 测试 API 定义服务")
    if not test_api_definition_service():
        print("❌ 服务测试失败")
        return
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过！API 管理模块基础功能正常")

if __name__ == "__main__":
    main()
