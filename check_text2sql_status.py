#!/usr/bin/env python3

import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.config.database import DATABASE_URL

def check_text2sql_status():
    """检查 Text2SQL 资源状态"""
    
    # 创建数据库连接
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("=== Text2SQL 资源注册状态 ===")
        
        # 查询 Text2SQL 资源
        query = text("""
            SELECT resource_id, resource_name, resource_type, description, 
                   is_active, status, vectorization_status, source_table, source_id,
                   created_at, updated_at
            FROM resource_discovery.resource_registry 
            WHERE resource_type = 'TEXT2SQL'
            ORDER BY resource_id
        """)
        
        result = session.execute(query)
        resources = result.fetchall()
        
        if not resources:
            print("❌ 没有找到任何 Text2SQL 资源")
            return
            
        for resource in resources:
            print(f"  - {resource.resource_id}: {resource.resource_name}")
            print(f"    描述: {resource.description}")
            print(f"    状态: active={resource.is_active}, status={resource.status}")
            print(f"    向量化状态: {resource.vectorization_status}")
            print(f"    数据源: table={resource.source_table}, id={resource.source_id}")
            print(f"    时间: 创建={resource.created_at}, 更新={resource.updated_at}")
            print()
        
        print("=== Text2SQL 向量数据状态 ===")
        
        # 查询 Text2SQL 向量数据
        vector_query = text("""
            SELECT resource_id, vector_type, content,
                   CASE
                       WHEN embedding IS NOT NULL THEN vector_dims(embedding)
                       ELSE 0
                   END as vector_dimension,
                   created_at
            FROM resource_discovery.resource_vectors
            WHERE resource_id LIKE 'text2sql_%'
            ORDER BY resource_id, vector_type
        """)
        
        vector_result = session.execute(vector_query)
        vectors = vector_result.fetchall()
        
        if not vectors:
            print("❌ 没有找到任何 Text2SQL 向量数据")
        else:
            print(f"✅ 找到 {len(vectors)} 条 Text2SQL 向量数据")
            for vector in vectors:
                print(f"  - {vector.resource_id} ({vector.vector_type}): {vector.vector_dimension}维")
                print(f"    内容: {vector.content[:100]}...")
                print(f"    时间: {vector.created_at}")
                print()
        
        print("=== Vanna Embeddings 数据源分布 ===")

        # 先查询表结构
        structure_query = text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'text2sql' AND table_name = 'vanna_embeddings'
            ORDER BY ordinal_position
        """)

        structure_result = session.execute(structure_query)
        columns = structure_result.fetchall()

        print("表结构:")
        for col in columns:
            print(f"  - {col.column_name}: {col.data_type}")

        # 查询 vanna_embeddings 数据源分布
        vanna_query = text("""
            SELECT datasource_id, COUNT(*) as count
            FROM text2sql.vanna_embeddings
            GROUP BY datasource_id
            ORDER BY datasource_id
        """)

        vanna_result = session.execute(vanna_query)
        vanna_data = vanna_result.fetchall()

        print("\n数据源分布:")
        for row in vanna_data:
            print(f"  数据源 {row.datasource_id}: {row.count} 条记录")
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_text2sql_status()
