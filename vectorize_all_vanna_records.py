#!/usr/bin/env python3

import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.config.database import DATABASE_URL
from src.config.resource_discovery import ResourceDiscoveryConfig
from src.services.resource_discovery.resource_vectorizer import ResourceVectorizer

async def vectorize_all_vanna_records():
    """为每条 vanna_embeddings 记录创建一个资源并向量化"""
    
    # 创建数据库连接
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("=== 为每条 vanna_embeddings 记录创建资源 ===")
        
        # 加载配置
        config = ResourceDiscoveryConfig()
        vectorizer = ResourceVectorizer(config)
        
        # 查询所有 vanna_embeddings 记录
        query = text("""
            SELECT id, datasource_id, content, sql_query, question, table_name, 
                   content_type, database_name, column_name, created_at
            FROM text2sql.vanna_embeddings
            ORDER BY datasource_id, id
        """)
        
        result = session.execute(query)
        records = result.fetchall()
        
        print(f"✅ 查询到 {len(records)} 条 vanna_embeddings 记录")
        
        # 统计现有的向量数据
        existing_query = text("""
            SELECT resource_id 
            FROM resource_discovery.resource_vectors 
            WHERE resource_id LIKE 'vanna_embedding_%'
        """)
        existing_result = session.execute(existing_query)
        existing_resources = {row[0] for row in existing_result.fetchall()}
        
        print(f"✅ 现有向量资源: {len(existing_resources)} 个")
        
        # 为每条记录创建资源并向量化
        vectorized_count = 0
        skipped_count = 0
        failed_count = 0
        
        for i, record in enumerate(records, 1):
            resource_id = f"vanna_embedding_{record.id}"
            
            # 检查是否已经存在
            if resource_id in existing_resources:
                skipped_count += 1
                if i % 50 == 0:
                    print(f"进度: {i}/{len(records)} (跳过: {skipped_count}, 成功: {vectorized_count}, 失败: {failed_count})")
                continue
            
            # 构建记录数据
            record_data = {
                'id': record.id,
                'datasource_id': record.datasource_id,
                'content': record.content or '',
                'sql_query': record.sql_query or '',
                'question': record.question or '',
                'table_name': record.table_name or '',
                'content_type': record.content_type or '',
                'database_name': record.database_name or '',
                'column_name': record.column_name or '',
                'created_at': record.created_at
            }
            
            # 使用配置驱动的向量化
            try:
                result = await vectorizer.vectorize_resource_from_config(
                    session, "text2sql.vanna_embeddings", record_data
                )
                
                if result.get('success'):
                    vectorized_count += 1
                else:
                    failed_count += 1
                    if failed_count <= 5:  # 只显示前5个失败的详情
                        print(f"   ❌ 向量化失败 {resource_id}: {result.get('error')}")
                
            except Exception as e:
                failed_count += 1
                if failed_count <= 5:
                    print(f"   ❌ 向量化异常 {resource_id}: {e}")
            
            # 每处理50条记录显示一次进度
            if i % 50 == 0:
                print(f"进度: {i}/{len(records)} (跳过: {skipped_count}, 成功: {vectorized_count}, 失败: {failed_count})")
        
        print(f"\n🎉 处理完成!")
        print(f"   总记录数: {len(records)}")
        print(f"   跳过 (已存在): {skipped_count}")
        print(f"   成功向量化: {vectorized_count}")
        print(f"   失败: {failed_count}")
        
        # 检查最终结果
        print("\n=== 检查最终向量化结果 ===")
        final_query = text("""
            SELECT COUNT(*) as count
            FROM resource_discovery.resource_vectors 
            WHERE resource_id LIKE 'vanna_embedding_%'
        """)
        
        final_result = session.execute(final_query)
        final_count = final_result.fetchone()[0]
        
        print(f"✅ 最终向量资源数量: {final_count}")
        
        if final_count == len(records):
            print("🎉 所有 vanna_embeddings 记录都已成功向量化!")
        else:
            print(f"⚠️  还有 {len(records) - final_count} 条记录未向量化")
            
    except Exception as e:
        print(f"❌ 向量化失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    asyncio.run(vectorize_all_vanna_records())
