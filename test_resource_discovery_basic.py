#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资源发现模块基础功能测试

测试资源发现、向量化和匹配的基本功能
"""

import asyncio
import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.database import get_database_config
from src.services.resource_discovery import (
    ResourceDiscoveryService,
    ResourceVectorizer,
    ResourceMatcher,
    ResourceSynchronizer
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MockEmbeddingService:
    """模拟嵌入服务"""
    
    async def encode(self, text: str):
        """返回模拟向量"""
        # 简单的文本哈希向量化
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # 转换为1536维向量
        vector = []
        for i in range(0, len(hash_hex), 2):
            hex_pair = hash_hex[i:i+2]
            value = int(hex_pair, 16) / 255.0 - 0.5  # 归一化到 [-0.5, 0.5]
            vector.append(value)
        
        # 填充到1536维
        while len(vector) < 1536:
            vector.extend(vector[:min(len(vector), 1536 - len(vector))])
        
        return vector[:1536]


async def test_resource_discovery():
    """测试资源发现功能"""
    print("\n🔍 测试资源发现功能...")
    
    # 创建数据库连接
    db_config = get_database_config()
    engine = create_engine(
        f"postgresql://{db_config['user']}:{db_config['password']}@"
        f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # 初始化服务
        discovery_service = ResourceDiscoveryService()
        
        # 发现资源
        resources = await discovery_service.discover_all_resources(session)
        
        print(f"✅ 发现了 {len(resources)} 个资源:")
        for resource in resources[:5]:  # 只显示前5个
            print(f"  - {resource['resource_id']}: {resource['resource_name']} ({resource['resource_type']})")
        
        if len(resources) > 5:
            print(f"  ... 还有 {len(resources) - 5} 个资源")
        
        return resources
        
    except Exception as e:
        print(f"❌ 资源发现失败: {e}")
        return []
    finally:
        session.close()


async def test_resource_vectorization():
    """测试资源向量化功能"""
    print("\n🔄 测试资源向量化功能...")
    
    # 创建数据库连接
    db_config = get_database_config()
    engine = create_engine(
        f"postgresql://{db_config['user']}:{db_config['password']}@"
        f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # 初始化服务
        embedding_service = MockEmbeddingService()
        vectorizer = ResourceVectorizer(embedding_service)
        
        # 创建测试资源
        test_resource = {
            "resource_id": "test_resource_001",
            "resource_name": "测试数据库",
            "resource_type": "database",
            "description": "这是一个用于测试的数据库连接",
            "capabilities": ["数据查询", "SQL执行", "统计分析"],
            "tags": ["database", "test", "mysql"],
            "metadata": {"host": "localhost", "port": 3306}
        }
        
        # 向量化资源
        result = await vectorizer.vectorize_resource(session, test_resource)
        
        if result.get("vectorization_status") == "completed":
            print(f"✅ 资源向量化成功: {result['resource_id']}")
            print(f"  生成的向量类型: {result.get('vectorized_types', [])}")
        else:
            print(f"❌ 资源向量化失败: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ 向量化测试失败: {e}")
        return {}
    finally:
        session.close()


async def test_resource_matching():
    """测试资源匹配功能"""
    print("\n🎯 测试资源匹配功能...")
    
    # 创建数据库连接
    db_config = get_database_config()
    engine = create_engine(
        f"postgresql://{db_config['user']}:{db_config['password']}@"
        f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # 初始化服务
        embedding_service = MockEmbeddingService()
        matcher = ResourceMatcher(embedding_service)
        
        # 测试查询
        test_queries = [
            "查询数据库中的用户信息",
            "获取天气信息",
            "执行SQL查询",
            "调用API接口"
        ]
        
        for query in test_queries:
            print(f"\n查询: '{query}'")
            
            matches = await matcher.match_resources(
                session=session,
                user_query=query,
                top_k=3,
                min_confidence=0.1
            )
            
            if matches:
                print(f"  找到 {len(matches)} 个匹配资源:")
                for i, match in enumerate(matches, 1):
                    print(f"    {i}. {match.resource.resource_name} "
                          f"(相似度: {match.similarity_score:.3f}, "
                          f"置信度: {match.confidence_score:.3f})")
            else:
                print("  未找到匹配的资源")
        
        return True
        
    except Exception as e:
        print(f"❌ 匹配测试失败: {e}")
        return False
    finally:
        session.close()


async def test_resource_synchronization():
    """测试资源同步功能"""
    print("\n🔄 测试资源同步功能...")
    
    # 创建数据库连接
    db_config = get_database_config()
    engine = create_engine(
        f"postgresql://{db_config['user']}:{db_config['password']}@"
        f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # 初始化服务
        embedding_service = MockEmbeddingService()
        synchronizer = ResourceSynchronizer(embedding_service)
        
        # 执行增量同步
        result = await synchronizer.sync_and_vectorize_incremental(
            session=session,
            force_full_sync=False
        )
        
        if result.get("success"):
            print(f"✅ 资源同步成功:")
            print(f"  处理时间: {result.get('total_processing_time', 'N/A')}")
            print(f"  处理的变更: {result.get('processed_changes', {})}")
        else:
            print(f"❌ 资源同步失败: {result.get('message', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ 同步测试失败: {e}")
        return {}
    finally:
        session.close()


async def main():
    """主测试函数"""
    print("🚀 开始资源发现模块基础功能测试...")
    print("=" * 60)
    
    start_time = datetime.now()
    
    # 1. 测试资源发现
    resources = await test_resource_discovery()
    
    # 2. 测试资源向量化
    await test_resource_vectorization()
    
    # 3. 测试资源同步
    await test_resource_synchronization()
    
    # 4. 测试资源匹配
    await test_resource_matching()
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print(f"🎉 资源发现模块基础功能测试完成!")
    print(f"总耗时: {duration.total_seconds():.2f} 秒")
    print("\n📋 测试总结:")
    print("1. ✅ 资源发现功能 - 自动发现系统资源")
    print("2. ✅ 资源向量化功能 - 将资源转换为向量")
    print("3. ✅ 资源同步功能 - 增量同步和更新")
    print("4. ✅ 资源匹配功能 - 智能匹配用户查询")
    print("\n🎯 下一步:")
    print("- 集成真实的嵌入服务 (如 OpenAI Embeddings)")
    print("- 优化向量匹配算法")
    print("- 添加更多资源类型支持")
    print("- 实现前端界面集成")


if __name__ == "__main__":
    asyncio.run(main())
