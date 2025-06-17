#!/usr/bin/env python3

import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.config.database import DATABASE_URL
from src.config.resource_discovery import ResourceDiscoveryConfig
from src.services.resource_discovery.resource_vectorizer import ResourceVectorizer

async def config_based_vectorization():
    """基于配置文件的向量化"""
    
    # 创建数据库连接
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("=== 基于配置文件的向量化 ===")
        
        # 加载配置
        config = ResourceDiscoveryConfig()
        vectorizer = ResourceVectorizer(config)
        
        # 查找 vanna_embeddings 配置
        vanna_config = None
        for resource_config in config.resources:
            if resource_config.table == "text2sql.vanna_embeddings":
                vanna_config = resource_config
                break
        
        if not vanna_config:
            print("❌ 未找到 vanna_embeddings 配置")
            return
        
        print(f"✅ 找到配置: {vanna_config.table}")
        print(f"   字段: {vanna_config.fields}")
        print(f"   工具: {vanna_config.tool}")
        
        # 查询 vanna_embeddings 表数据
        query = text(f"""
            SELECT id, datasource_id, content, sql_query, question, table_name, content_type
            FROM {vanna_config.table}
            ORDER BY datasource_id, id
        """)
        
        result = session.execute(query)
        records = result.fetchall()
        
        print(f"✅ 查询到 {len(records)} 条记录")
        
        # 按数据源分组
        datasource_groups = {}
        for record in records:
            datasource_id = record.datasource_id
            if datasource_id not in datasource_groups:
                datasource_groups[datasource_id] = []
            datasource_groups[datasource_id].append(record)
        
        print(f"✅ 数据源分布:")
        for ds_id, records_list in datasource_groups.items():
            print(f"   数据源 {ds_id}: {len(records_list)} 条记录")
        
        # 为每个数据源创建资源并向量化
        vectorized_count = 0
        for datasource_id, records_list in datasource_groups.items():
            print(f"\n🔄 处理数据源 {datasource_id}...")
            
            # 构建记录数据（使用第一条记录作为代表）
            first_record = records_list[0]
            record_data = {
                'id': datasource_id,  # 使用数据源ID作为资源ID
                'datasource_id': datasource_id,
                'content': first_record.content,
                'sql_query': first_record.sql_query,
                'question': first_record.question,
                'table_name': first_record.table_name,
                'content_type': first_record.content_type,
                'record_count': len(records_list)
            }
            
            # 使用配置驱动的向量化
            result = await vectorizer.vectorize_resource_from_config(
                session, vanna_config.table, record_data
            )
            
            if result.get('success'):
                vectorized_count += 1
                print(f"   ✅ 向量化成功: {result['resource_id']}")
                print(f"      内容长度: {len(result['content'])} 字符")
                print(f"      向量维度: {result['vector_dimension']}")
            else:
                print(f"   ❌ 向量化失败: {result.get('error')}")
        
        print(f"\n🎉 向量化完成!")
        print(f"   成功: {vectorized_count}/{len(datasource_groups)} 个数据源")
        
        # 检查最终结果
        print("\n=== 检查向量化结果 ===")
        vector_query = text("""
            SELECT resource_id, vector_type, 
                   CASE 
                       WHEN embedding IS NOT NULL THEN vector_dims(embedding)
                       ELSE 0 
                   END as vector_dimension
            FROM resource_discovery.resource_vectors 
            WHERE resource_id LIKE 'text2sql.vanna_embeddings_%'
            ORDER BY resource_id, vector_type
        """)
        
        vector_result = session.execute(vector_query)
        vectors = vector_result.fetchall()
        
        if vectors:
            print(f"✅ 找到 {len(vectors)} 条向量记录:")
            for vector in vectors:
                print(f"   - {vector.resource_id} ({vector.vector_type}): {vector.vector_dimension}维")
        else:
            print("❌ 没有找到向量记录")
            
    except Exception as e:
        print(f"❌ 向量化失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    asyncio.run(config_based_vectorization())
