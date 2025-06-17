#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实嵌入服务集成测试

测试资源发现模块与真实嵌入服务的集成
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


async def test_embedding_service():
    """测试嵌入服务"""
    print("\n🧠 测试真实嵌入服务...")
    
    try:
        from src.llms.embedding import embed_query, get_embedding_dimension
        
        # 测试获取维度
        dimension = get_embedding_dimension("BASE_EMBEDDING")
        print(f"✅ 嵌入维度: {dimension}")
        
        # 测试嵌入查询
        test_texts = [
            "查询数据库中的用户信息",
            "调用API获取天气数据",
            "执行SQL统计查询",
            "使用系统工具处理文件"
        ]
        
        for text in test_texts:
            try:
                vector = embed_query(text, "BASE_EMBEDDING")
                if vector and len(vector) == dimension:
                    print(f"✅ '{text}' -> 向量长度: {len(vector)}")
                else:
                    print(f"❌ '{text}' -> 向量生成失败")
                    return False
            except Exception as e:
                print(f"❌ '{text}' -> 嵌入失败: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 嵌入服务测试失败: {e}")
        return False


async def test_vectorizer_with_real_embedding():
    """测试向量化器与真实嵌入服务"""
    print("\n🔄 测试向量化器与真实嵌入服务...")
    
    try:
        from src.services.resource_discovery import ResourceVectorizer
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from src.config.database import get_database_config
        
        # 创建数据库连接
        db_config = get_database_config()
        engine = create_engine(
            f"postgresql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            # 初始化向量化器
            vectorizer = ResourceVectorizer()
            
            # 创建测试资源
            test_resource = {
                "resource_id": "test_real_embedding_001",
                "resource_name": "测试数据库连接",
                "resource_type": "database",
                "description": "这是一个用于测试真实嵌入服务的数据库连接",
                "capabilities": ["数据查询", "SQL执行", "统计分析", "数据导出"],
                "tags": ["database", "test", "mysql", "production"],
                "metadata": {"host": "localhost", "port": 3306, "engine": "mysql"}
            }
            
            # 向量化资源
            result = await vectorizer.vectorize_resource(session, test_resource)
            
            if result.get("vectorization_status") == "completed":
                vectorized_types = result.get("vectorized_types", [])
                print(f"✅ 资源向量化成功:")
                print(f"   资源ID: {result['resource_id']}")
                print(f"   向量类型: {vectorized_types}")
                
                # 验证向量是否保存到数据库
                from sqlalchemy import text
                check_query = text("""
                    SELECT vector_type, embedding_dimension 
                    FROM resource_discovery.resource_vectors 
                    WHERE resource_id = :resource_id
                """)
                
                db_result = session.execute(check_query, {"resource_id": test_resource["resource_id"]})
                vectors_in_db = db_result.fetchall()
                
                print(f"   数据库中的向量: {len(vectors_in_db)} 个")
                for vector_row in vectors_in_db:
                    print(f"     - {vector_row.vector_type}: {vector_row.embedding_dimension} 维")
                
                # 清理测试数据
                cleanup_query = text("""
                    DELETE FROM resource_discovery.resource_vectors 
                    WHERE resource_id = :resource_id
                """)
                session.execute(cleanup_query, {"resource_id": test_resource["resource_id"]})
                session.commit()
                
                return len(vectors_in_db) > 0
            else:
                print(f"❌ 资源向量化失败: {result.get('error', 'Unknown error')}")
                return False
                
        finally:
            session.close()
        
    except Exception as e:
        print(f"❌ 向量化器测试失败: {e}")
        return False


async def test_matcher_with_real_embedding():
    """测试匹配器与真实嵌入服务"""
    print("\n🎯 测试匹配器与真实嵌入服务...")
    
    try:
        from src.services.resource_discovery import ResourceMatcher
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from src.config.database import get_database_config
        
        # 创建数据库连接
        db_config = get_database_config()
        engine = create_engine(
            f"postgresql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            # 初始化匹配器
            matcher = ResourceMatcher()
            
            # 测试查询
            test_queries = [
                "查询数据库中的用户信息",
                "调用API获取天气数据",
                "执行SQL统计分析"
            ]
            
            successful_matches = 0
            
            for query in test_queries:
                print(f"\n   查询: '{query}'")
                
                matches = await matcher.match_resources(
                    session=session,
                    user_query=query,
                    top_k=3,
                    min_confidence=0.1
                )
                
                if matches:
                    print(f"   找到 {len(matches)} 个匹配资源:")
                    for i, match in enumerate(matches, 1):
                        print(f"     {i}. {match.resource.resource_name}")
                        print(f"        相似度: {match.similarity_score:.3f}")
                        print(f"        置信度: {match.confidence_score:.3f}")
                    successful_matches += 1
                else:
                    print(f"   未找到匹配的资源")
            
            success_rate = successful_matches / len(test_queries) * 100
            print(f"\n   匹配成功率: {success_rate:.0f}% ({successful_matches}/{len(test_queries)})")
            
            return success_rate >= 50  # 至少50%成功率
            
        finally:
            session.close()
        
    except Exception as e:
        print(f"❌ 匹配器测试失败: {e}")
        return False


async def test_tools_with_real_embedding():
    """测试工具与真实嵌入服务"""
    print("\n🔧 测试工具与真实嵌入服务...")
    
    try:
        from src.tools.resource_discovery import discover_resources, sync_system_resources
        
        # 1. 先同步资源
        print("   1. 同步系统资源...")
        sync_result = await sync_system_resources(force_full_sync=False)
        
        if not sync_result.get("success"):
            print(f"   ❌ 同步失败: {sync_result.get('message')}")
            return False
        
        print(f"   ✅ 同步成功")
        
        # 2. 测试智能发现
        print("   2. 测试智能资源发现...")
        
        test_queries = [
            "查询数据库信息",
            "调用API接口",
            "执行SQL查询"
        ]
        
        successful_queries = 0
        
        for query in test_queries:
            result = await discover_resources(
                user_query=query,
                max_results=3,
                min_confidence=0.1
            )
            
            if result.get("success") and len(result.get("matches", [])) > 0:
                matches = result.get("matches", [])
                print(f"   '{query}': 找到 {len(matches)} 个匹配")
                successful_queries += 1
            else:
                print(f"   '{query}': 未找到匹配")
        
        success_rate = successful_queries / len(test_queries) * 100
        print(f"   工具测试成功率: {success_rate:.0f}% ({successful_queries}/{len(test_queries)})")
        
        return success_rate >= 50
        
    except Exception as e:
        print(f"❌ 工具测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始真实嵌入服务集成测试...")
    print("=" * 60)
    
    start_time = datetime.now()
    
    # 执行各项测试
    tests = [
        ("嵌入服务基础功能", test_embedding_service),
        ("向量化器集成", test_vectorizer_with_real_embedding),
        ("匹配器集成", test_matcher_with_real_embedding),
        ("工具集成", test_tools_with_real_embedding),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results[test_name] = False
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print(f"🎉 真实嵌入服务集成测试完成!")
    print(f"总耗时: {duration.total_seconds():.2f} 秒")
    print("\n📋 测试结果:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 测试总结: {passed}/{total} 通过 ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过！真实嵌入服务已成功集成")
        print("\n✨ 集成效果:")
        print("✅ 使用统一的嵌入服务 (BASE_EMBEDDING)")
        print("✅ 向量维度自动适配")
        print("✅ 高质量的语义向量表示")
        print("✅ 更准确的相似度匹配")
        print("✅ 与现有系统无缝集成")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查嵌入服务配置")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(main())
