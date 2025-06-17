#!/usr/bin/env python3
"""
检查vanna_embeddings表中的数据
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.database import get_database_connection


def check_vanna_data():
    """检查vanna_embeddings表中的数据"""
    
    print("🔍 检查vanna_embeddings表中的数据")
    print("=" * 50)
    
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                # 1. 查看所有数据
                cursor.execute("""
                    SELECT id, datasource_id, content_type, table_name, 
                           LEFT(content, 100) as content_preview,
                           created_at
                    FROM text2sql.vanna_embeddings
                    ORDER BY created_at DESC
                    LIMIT 20
                """)
                rows = cursor.fetchall()
                
                print(f"📊 最近的 {len(rows)} 条记录:")
                for row in rows:
                    print(f"   ID: {row['id']}, 数据源: {row['datasource_id']}, "
                          f"类型: {row['content_type']}, 表名: {row['table_name']}")
                    print(f"      内容: {row['content_preview']}...")
                    print(f"      时间: {row['created_at']}")
                    print()
                
                # 2. 按表名分组统计
                cursor.execute("""
                    SELECT table_name, COUNT(*) as count
                    FROM text2sql.vanna_embeddings
                    WHERE content_type = 'DDL'
                    GROUP BY table_name
                    ORDER BY count DESC
                """)
                table_stats = cursor.fetchall()
                
                print(f"📋 DDL记录按表名统计:")
                for stat in table_stats:
                    table_name = stat['table_name'] or '(NULL)'
                    print(f"   {table_name}: {stat['count']} 条记录")
                
                # 3. 检查重复内容
                cursor.execute("""
                    SELECT content_hash, COUNT(*) as count
                    FROM text2sql.vanna_embeddings
                    WHERE content_hash IS NOT NULL
                    GROUP BY content_hash
                    HAVING COUNT(*) > 1
                    ORDER BY count DESC
                """)
                duplicates = cursor.fetchall()
                
                if duplicates:
                    print(f"\n⚠️ 发现 {len(duplicates)} 个重复的content_hash:")
                    for dup in duplicates:
                        print(f"   Hash: {dup['content_hash']}, 重复次数: {dup['count']}")
                else:
                    print(f"\n✅ 没有发现重复的content_hash")
                
                # 4. 测试跳过逻辑的查询
                datasource_id = 1
                cursor.execute("""
                    SELECT DISTINCT table_name 
                    FROM text2sql.vanna_embeddings 
                    WHERE datasource_id = %s 
                    AND content_type = 'DDL' 
                    AND table_name IS NOT NULL
                """, (datasource_id,))
                
                existing_tables = cursor.fetchall()
                print(f"\n🔍 数据源 {datasource_id} 的已训练表:")
                for table in existing_tables:
                    print(f"   - {table['table_name']}")
                
                return True
                
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = check_vanna_data()
    
    if success:
        print("\n✅ 数据检查完成！")
    else:
        print("\n❌ 数据检查失败！")
