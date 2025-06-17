#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资源发现模块简化测试

测试基础的数据库连接和表结构
"""

import asyncio
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.config.database import get_database_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_database_connection():
    """测试数据库连接"""
    print("\n🔗 测试数据库连接...")
    
    try:
        # 创建数据库连接
        db_config = get_database_config()
        engine = create_engine(
            f"postgresql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # 测试连接
        result = session.execute(text("SELECT 1"))
        if result.fetchone():
            print("✅ 数据库连接成功")
            return True
        else:
            print("❌ 数据库连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    finally:
        session.close()


async def test_pgvector_extension():
    """测试 pgvector 扩展"""
    print("\n🔧 测试 pgvector 扩展...")
    
    try:
        # 创建数据库连接
        db_config = get_database_config()
        engine = create_engine(
            f"postgresql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # 检查 pgvector 扩展
        result = session.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector'"))
        if result.fetchone():
            print("✅ pgvector 扩展已安装")
            
            # 测试向量操作
            session.execute(text("SELECT '[1,2,3]'::vector"))
            print("✅ 向量操作测试成功")
            return True
        else:
            print("❌ pgvector 扩展未安装")
            print("请运行: CREATE EXTENSION vector;")
            return False
            
    except Exception as e:
        print(f"❌ pgvector 扩展测试失败: {e}")
        return False
    finally:
        session.close()


async def test_resource_discovery_schema():
    """测试资源发现模式"""
    print("\n📋 测试资源发现模式...")
    
    try:
        # 创建数据库连接
        db_config = get_database_config()
        engine = create_engine(
            f"postgresql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # 检查模式是否存在
        result = session.execute(text("""
            SELECT schema_name FROM information_schema.schemata 
            WHERE schema_name = 'resource_discovery'
        """))
        
        if result.fetchone():
            print("✅ resource_discovery 模式存在")
            
            # 检查表是否存在
            tables_query = text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'resource_discovery'
                ORDER BY table_name
            """)
            
            result = session.execute(tables_query)
            tables = [row[0] for row in result.fetchall()]
            
            expected_tables = [
                'resource_registry',
                'resource_vectors', 
                'resource_match_history',
                'resource_usage_stats',
                'system_status'
            ]
            
            print(f"发现的表: {tables}")
            
            missing_tables = set(expected_tables) - set(tables)
            if missing_tables:
                print(f"❌ 缺少表: {missing_tables}")
                return False
            else:
                print("✅ 所有必需的表都存在")
                return True
        else:
            print("❌ resource_discovery 模式不存在")
            return False
            
    except Exception as e:
        print(f"❌ 模式测试失败: {e}")
        return False
    finally:
        session.close()


async def test_existing_data_sources():
    """测试现有数据源"""
    print("\n📊 测试现有数据源...")
    
    try:
        # 创建数据库连接
        db_config = get_database_config()
        engine = create_engine(
            f"postgresql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # 检查数据库管理模式
        result = session.execute(text("""
            SELECT schema_name FROM information_schema.schemata 
            WHERE schema_name = 'database_management'
        """))
        
        if result.fetchone():
            print("✅ database_management 模式存在")
            
            # 检查数据源表
            try:
                result = session.execute(text("""
                    SELECT COUNT(*) FROM database_management.database_datasources
                """))
                count = result.scalar()
                print(f"✅ 数据源表存在，包含 {count} 条记录")
            except Exception as e:
                print(f"❌ 数据源表查询失败: {e}")
        else:
            print("❌ database_management 模式不存在")
        
        # 检查 API 工具模式
        result = session.execute(text("""
            SELECT schema_name FROM information_schema.schemata 
            WHERE schema_name = 'api_tools'
        """))
        
        if result.fetchone():
            print("✅ api_tools 模式存在")
            
            # 检查 API 定义表
            try:
                result = session.execute(text("""
                    SELECT COUNT(*) FROM api_tools.api_definitions
                """))
                count = result.scalar()
                print(f"✅ API 定义表存在，包含 {count} 条记录")
            except Exception as e:
                print(f"❌ API 定义表查询失败: {e}")
        else:
            print("❌ api_tools 模式不存在")
        
        # 检查 Text2SQL 模式
        result = session.execute(text("""
            SELECT schema_name FROM information_schema.schemata 
            WHERE schema_name = 'text2sql'
        """))
        
        if result.fetchone():
            print("✅ text2sql 模式存在")
            
            # 检查 vanna_embeddings 表
            try:
                result = session.execute(text("""
                    SELECT COUNT(*) FROM text2sql.vanna_embeddings
                """))
                count = result.scalar()
                print(f"✅ vanna_embeddings 表存在，包含 {count} 条记录")
            except Exception as e:
                print(f"❌ vanna_embeddings 表查询失败: {e}")
        else:
            print("❌ text2sql 模式不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据源测试失败: {e}")
        return False
    finally:
        session.close()


async def test_simple_resource_insertion():
    """测试简单的资源插入"""
    print("\n➕ 测试简单的资源插入...")
    
    try:
        # 创建数据库连接
        db_config = get_database_config()
        engine = create_engine(
            f"postgresql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # 清理测试数据
        session.execute(text("DELETE FROM resource_discovery.resource_registry WHERE resource_id LIKE 'test_%'"))
        session.commit()
        
        # 插入测试资源
        insert_query = text("""
            INSERT INTO resource_discovery.resource_registry 
            (resource_id, resource_name, resource_type, description, capabilities, 
             tags, metadata, is_active, status, source_table, source_id, vectorization_status)
            VALUES (:resource_id, :resource_name, :resource_type, :description, :capabilities,
                    :tags, :metadata, :is_active, :status, :source_table, :source_id, :vectorization_status)
        """)
        
        import json
        test_resource = {
            "resource_id": "test_simple_resource",
            "resource_name": "测试资源",
            "resource_type": "database",
            "description": "这是一个测试资源",
            "capabilities": json.dumps(["测试功能1", "测试功能2"]),
            "tags": json.dumps(["test", "simple"]),
            "metadata": json.dumps({"test": True, "version": "1.0"}),
            "is_active": True,
            "status": "active",
            "source_table": "test_table",
            "source_id": 1,
            "vectorization_status": "pending"
        }
        
        session.execute(insert_query, test_resource)
        session.commit()
        
        # 验证插入
        result = session.execute(text("""
            SELECT resource_id, resource_name FROM resource_discovery.resource_registry 
            WHERE resource_id = 'test_simple_resource'
        """))
        
        row = result.fetchone()
        if row:
            print(f"✅ 资源插入成功: {row.resource_id} - {row.resource_name}")
            
            # 清理测试数据
            session.execute(text("DELETE FROM resource_discovery.resource_registry WHERE resource_id = 'test_simple_resource'"))
            session.commit()
            print("✅ 测试数据清理完成")
            
            return True
        else:
            print("❌ 资源插入失败")
            return False
        
    except Exception as e:
        print(f"❌ 资源插入测试失败: {e}")
        return False
    finally:
        session.close()


async def main():
    """主测试函数"""
    print("🚀 开始资源发现模块简化测试...")
    print("=" * 60)
    
    start_time = datetime.now()
    
    # 1. 测试数据库连接
    db_ok = await test_database_connection()
    
    # 2. 测试 pgvector 扩展
    vector_ok = await test_pgvector_extension()
    
    # 3. 测试资源发现模式
    schema_ok = await test_resource_discovery_schema()
    
    # 4. 测试现有数据源
    data_ok = await test_existing_data_sources()
    
    # 5. 测试简单资源插入
    insert_ok = await test_simple_resource_insertion()
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print(f"🎉 资源发现模块简化测试完成!")
    print(f"总耗时: {duration.total_seconds():.2f} 秒")
    print("\n📋 测试结果:")
    print(f"1. {'✅' if db_ok else '❌'} 数据库连接")
    print(f"2. {'✅' if vector_ok else '❌'} pgvector 扩展")
    print(f"3. {'✅' if schema_ok else '❌'} 资源发现模式")
    print(f"4. {'✅' if data_ok else '❌'} 现有数据源")
    print(f"5. {'✅' if insert_ok else '❌'} 资源插入测试")
    
    all_ok = all([db_ok, vector_ok, schema_ok, data_ok, insert_ok])
    
    if all_ok:
        print("\n🎯 所有基础测试通过！可以继续进行完整功能测试")
    else:
        print("\n⚠️  部分测试失败，请检查上述问题后再进行完整测试")
    
    return all_ok


if __name__ == "__main__":
    asyncio.run(main())
