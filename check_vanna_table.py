#!/usr/bin/env python3
"""
检查vanna_embeddings表结构
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.database import get_database_connection


def check_vanna_table():
    """检查vanna_embeddings表结构"""
    
    print("🔍 检查vanna_embeddings表结构")
    print("=" * 50)
    
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                # 1. 检查schema是否存在
                cursor.execute("""
                    SELECT schema_name 
                    FROM information_schema.schemata 
                    WHERE schema_name = 'text2sql'
                """)
                schema_exists = cursor.fetchone()
                
                if schema_exists:
                    print("✅ text2sql schema 存在")
                else:
                    print("❌ text2sql schema 不存在")
                    
                    # 创建schema
                    print("🔧 创建 text2sql schema...")
                    cursor.execute("CREATE SCHEMA IF NOT EXISTS text2sql;")
                    conn.commit()
                    print("✅ text2sql schema 创建成功")
                
                # 2. 检查表是否存在
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'text2sql' 
                    AND table_name = 'vanna_embeddings'
                """)
                table_exists = cursor.fetchone()
                
                if table_exists:
                    print("✅ vanna_embeddings 表存在")
                    
                    # 检查表结构
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_schema = 'text2sql' 
                        AND table_name = 'vanna_embeddings'
                        ORDER BY ordinal_position
                    """)
                    columns = cursor.fetchall()
                    
                    print(f"\n📋 表结构 ({len(columns)} 列):")
                    for col in columns:
                        nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                        default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                        print(f"   {col['column_name']}: {col['data_type']} {nullable}{default}")
                    
                    # 检查是否有table_name列
                    table_name_exists = any(col['column_name'] == 'table_name' for col in columns)
                    if table_name_exists:
                        print("\n✅ table_name 列存在")
                    else:
                        print("\n❌ table_name 列不存在")
                        print("🔧 需要添加 table_name 列...")
                        
                        # 添加缺失的列
                        cursor.execute("""
                            ALTER TABLE text2sql.vanna_embeddings 
                            ADD COLUMN IF NOT EXISTS table_name VARCHAR(256)
                        """)
                        cursor.execute("""
                            ALTER TABLE text2sql.vanna_embeddings 
                            ADD COLUMN IF NOT EXISTS database_name VARCHAR(256)
                        """)
                        conn.commit()
                        print("✅ 添加缺失列成功")
                        
                else:
                    print("❌ vanna_embeddings 表不存在")
                    print("🔧 创建 vanna_embeddings 表...")
                    
                    # 创建表
                    cursor.execute("""
                        CREATE TABLE text2sql.vanna_embeddings (
                            id SERIAL PRIMARY KEY,
                            datasource_id INTEGER NOT NULL,
                            content TEXT NOT NULL,
                            content_type VARCHAR(50) NOT NULL DEFAULT 'DDL',
                            embedding_vector VECTOR(1024),
                            metadata JSONB,
                            table_name VARCHAR(256),
                            database_name VARCHAR(256),
                            content_hash VARCHAR(64),
                            training_data_id INTEGER,
                            created_at TIMESTAMPTZ DEFAULT NOW(),
                            updated_at TIMESTAMPTZ DEFAULT NOW()
                        );
                    """)
                    
                    # 创建索引
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_vanna_embeddings_datasource_id 
                        ON text2sql.vanna_embeddings(datasource_id);
                    """)
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_vanna_embeddings_content_type 
                        ON text2sql.vanna_embeddings(content_type);
                    """)
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_vanna_embeddings_table_name 
                        ON text2sql.vanna_embeddings(table_name);
                    """)
                    
                    conn.commit()
                    print("✅ vanna_embeddings 表创建成功")
                
                # 3. 检查数据
                cursor.execute("""
                    SELECT COUNT(*) as total_count,
                           COUNT(CASE WHEN content_type = 'DDL' THEN 1 END) as ddl_count,
                           COUNT(CASE WHEN content_type = 'SQL' THEN 1 END) as sql_count
                    FROM text2sql.vanna_embeddings
                """)
                stats = cursor.fetchone()
                
                print(f"\n📊 数据统计:")
                print(f"   总记录数: {stats['total_count']}")
                print(f"   DDL记录数: {stats['ddl_count']}")
                print(f"   SQL记录数: {stats['sql_count']}")
                
                return True
                
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = check_vanna_table()
    
    if success:
        print("\n✅ vanna_embeddings 表检查/修复完成！")
        print("\n📋 现在可以:")
        print("   1. 重新测试DDL训练")
        print("   2. 验证跳过逻辑")
        print("   3. 测试SQL生成")
    else:
        print("\n❌ 表检查/修复失败！")
