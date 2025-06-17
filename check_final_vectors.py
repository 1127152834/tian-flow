#!/usr/bin/env python3

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.config.database import DATABASE_URL

def check_final_vectors():
    """检查最终的向量数据"""
    
    # 创建数据库连接
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("=== 最终向量数据统计 ===")
        
        # 查询所有向量数据
        query = text("""
            SELECT resource_id, vector_type, 
                   CASE 
                       WHEN embedding IS NOT NULL THEN vector_dims(embedding)
                       ELSE 0 
                   END as vector_dimension,
                   created_at
            FROM resource_discovery.resource_vectors 
            ORDER BY resource_id, vector_type
        """)
        
        result = session.execute(query)
        vectors = result.fetchall()
        
        print(f"✅ 总向量数据: {len(vectors)} 条")
        
        # 按资源类型分组
        resource_types = {}
        for vector in vectors:
            resource_id = vector.resource_id
            
            # 判断资源类型
            if resource_id.startswith('database_'):
                resource_type = 'DATABASE'
            elif resource_id.startswith('api_'):
                resource_type = 'API'
            elif resource_id.startswith('tool_'):
                resource_type = 'TOOL'
            elif resource_id.startswith('text2sql') or 'vanna_embeddings' in resource_id:
                resource_type = 'TEXT2SQL'
            else:
                resource_type = 'OTHER'
            
            if resource_type not in resource_types:
                resource_types[resource_type] = []
            resource_types[resource_type].append(vector)
        
        print("\n=== 按资源类型分组 ===")
        for resource_type, vectors_list in resource_types.items():
            print(f"{resource_type}: {len(vectors_list)} 条向量")
            
            # 显示前几个资源
            unique_resources = set()
            for vector in vectors_list:
                unique_resources.add(vector.resource_id)
            
            print(f"  资源数量: {len(unique_resources)}")
            for resource_id in sorted(list(unique_resources))[:3]:
                print(f"    - {resource_id}")
            if len(unique_resources) > 3:
                print(f"    ... 还有 {len(unique_resources) - 3} 个")
            print()
        
        print("=== Text2SQL 详细信息 ===")
        text2sql_vectors = resource_types.get('TEXT2SQL', [])
        if text2sql_vectors:
            text2sql_resources = {}
            for vector in text2sql_vectors:
                resource_id = vector.resource_id
                if resource_id not in text2sql_resources:
                    text2sql_resources[resource_id] = []
                text2sql_resources[resource_id].append(vector)
            
            for resource_id, vectors_list in text2sql_resources.items():
                print(f"  {resource_id}:")
                for vector in vectors_list:
                    print(f"    - {vector.vector_type}: {vector.vector_dimension}维 ({vector.created_at})")
        else:
            print("  没有找到 Text2SQL 向量数据")
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    check_final_vectors()
