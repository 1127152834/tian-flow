#!/usr/bin/env python3

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.config.database import DATABASE_URL

def analyze_text2sql_resources():
    """分析 Text2SQL 资源的实际构成"""
    
    # 创建数据库连接
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("=== Text2SQL 资源分析 ===")
        
        # 查询 vanna_embeddings 表的数据分布
        query = text("""
            SELECT datasource_id, content_type, COUNT(*) as count
            FROM text2sql.vanna_embeddings 
            GROUP BY datasource_id, content_type
            ORDER BY datasource_id, content_type
        """)
        
        result = session.execute(query)
        data_distribution = result.fetchall()
        
        print("=== 按数据源和内容类型分布 ===")
        total_resources = 0
        datasource_summary = {}
        
        for row in data_distribution:
            datasource_id = row.datasource_id
            content_type = row.content_type
            count = row.count
            
            print(f"数据源 {datasource_id} - {content_type}: {count} 条记录")
            
            if datasource_id not in datasource_summary:
                datasource_summary[datasource_id] = {}
            datasource_summary[datasource_id][content_type] = count
            total_resources += 1
        
        print(f"\n=== 资源总数计算 ===")
        print(f"理论 Text2SQL 资源数量: {total_resources}")
        print("(每个数据源的每种内容类型算作一个资源)")
        
        print(f"\n=== 各数据源资源详情 ===")
        for datasource_id, types in datasource_summary.items():
            resource_count = len(types)
            print(f"数据源 {datasource_id}: {resource_count} 个资源类型")
            for content_type, count in types.items():
                print(f"  - {content_type}: {count} 条记录")
        
        # 查询当前资源注册表中的 Text2SQL 资源
        print(f"\n=== 当前注册的 Text2SQL 资源 ===")
        registry_query = text("""
            SELECT resource_id, resource_name, description, source_table, source_id, 
                   vectorization_status, created_at
            FROM resource_discovery.resource_registry 
            WHERE resource_type = 'TEXT2SQL' OR resource_id LIKE '%text2sql%' OR resource_id LIKE '%vanna%'
            ORDER BY resource_id
        """)
        
        registry_result = session.execute(registry_query)
        registered_resources = registry_result.fetchall()
        
        print(f"已注册的资源数量: {len(registered_resources)}")
        for resource in registered_resources:
            print(f"  - {resource.resource_id}: {resource.resource_name}")
            print(f"    描述: {resource.description}")
            print(f"    来源: {resource.source_table}, ID: {resource.source_id}")
            print(f"    向量化状态: {resource.vectorization_status}")
            print(f"    创建时间: {resource.created_at}")
            print()
        
        # 查询向量数据
        print(f"=== Text2SQL 向量数据 ===")
        vector_query = text("""
            SELECT resource_id, vector_type, 
                   CASE 
                       WHEN embedding IS NOT NULL THEN vector_dims(embedding)
                       ELSE 0 
                   END as vector_dimension
            FROM resource_discovery.resource_vectors 
            WHERE resource_id LIKE '%text2sql%' OR resource_id LIKE '%vanna%'
            ORDER BY resource_id, vector_type
        """)
        
        vector_result = session.execute(vector_query)
        vectors = vector_result.fetchall()
        
        print(f"向量数据数量: {len(vectors)}")
        current_resource = None
        for vector in vectors:
            if vector.resource_id != current_resource:
                current_resource = vector.resource_id
                print(f"\n{current_resource}:")
            print(f"  - {vector.vector_type}: {vector.vector_dimension}维")
        
        print(f"\n=== 建议的正确资源结构 ===")
        print("应该为每个 (数据源ID, 内容类型) 组合创建一个资源:")
        suggested_resources = []
        for datasource_id, types in datasource_summary.items():
            for content_type, count in types.items():
                resource_id = f"text2sql_{datasource_id}_{content_type.lower()}"
                resource_name = f"Text2SQL {content_type} 数据 (数据源 {datasource_id})"
                suggested_resources.append({
                    'resource_id': resource_id,
                    'resource_name': resource_name,
                    'datasource_id': datasource_id,
                    'content_type': content_type,
                    'record_count': count
                })
                print(f"  - {resource_id}: {resource_name} ({count} 条记录)")
        
        print(f"\n建议的总资源数量: {len(suggested_resources)}")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    analyze_text2sql_resources()
