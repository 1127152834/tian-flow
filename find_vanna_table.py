#!/usr/bin/env python3

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.config.database import DATABASE_URL

def find_vanna_table():
    """查找 vanna 相关的表"""
    
    # 创建数据库连接
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("=== 查找 vanna 相关的表 ===")
        
        # 查询所有包含 vanna 的表
        query = text("""
            SELECT schemaname, tablename 
            FROM pg_tables 
            WHERE tablename LIKE '%vanna%' 
            ORDER BY schemaname, tablename
        """)
        
        result = session.execute(query)
        tables = result.fetchall()
        
        if not tables:
            print("❌ 没有找到包含 'vanna' 的表")
        else:
            print(f"✅ 找到 {len(tables)} 个包含 'vanna' 的表:")
            for table in tables:
                print(f"  - {table.schemaname}.{table.tablename}")
        
        print("\n=== 查找所有 schema ===")
        schema_query = text("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY schema_name
        """)
        
        schema_result = session.execute(schema_query)
        schemas = schema_result.fetchall()
        
        for schema in schemas:
            print(f"  - {schema.schema_name}")
            
        # 尝试查询每个 schema 中的表
        print("\n=== 各 schema 中的表 ===")
        for schema in schemas:
            schema_name = schema.schema_name
            table_query = text(f"""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = :schema_name
                ORDER BY tablename
            """)
            
            table_result = session.execute(table_query, {"schema_name": schema_name})
            schema_tables = table_result.fetchall()
            
            print(f"\n{schema_name} schema:")
            for table in schema_tables:
                print(f"  - {table.tablename}")
                
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    find_vanna_table()
