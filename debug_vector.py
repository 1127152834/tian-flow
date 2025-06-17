#!/usr/bin/env python3
"""
Debug script to check vector data in database
"""
import psycopg2
import json
from psycopg2.extras import RealDictCursor

def check_vector_data():
    """Check vector data in vanna_embeddings table"""
    try:
        # Database connection
        conn = psycopg2.connect(
            host="localhost",
            database="aolei_db",
            user="aolei",
            password="aolei123456"
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Check table structure
            print("=== Table Structure ===")
            cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_schema = 'text2sql' 
                AND table_name = 'vanna_embeddings'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            for col in columns:
                print(f"{col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
            
            print("\n=== Sample Data ===")
            # Check sample data
            cursor.execute("""
                SELECT
                    id,
                    datasource_id,
                    content_type,
                    CASE
                        WHEN embedding_vector IS NULL THEN 'NULL'
                        ELSE 'NOT NULL'
                    END as vector_status,
                    LEFT(content, 100) as content_preview
                FROM text2sql.vanna_embeddings
                ORDER BY id DESC
                LIMIT 5;
            """)
            
            rows = cursor.fetchall()
            for row in rows:
                print(f"ID: {row['id']}, DS: {row['datasource_id']}, Type: {row['content_type']}")
                print(f"  Vector: {row['vector_status']}")
                print(f"  Content: {row['content_preview']}...")
                print()
            
            print("=== Vector Statistics ===")
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(embedding_vector) as records_with_vectors,
                    COUNT(*) - COUNT(embedding_vector) as records_without_vectors
                FROM text2sql.vanna_embeddings;
            """)
            
            stats = cursor.fetchone()
            print(f"Total records: {stats['total_records']}")
            print(f"Records with vectors: {stats['records_with_vectors']}")
            print(f"Records without vectors: {stats['records_without_vectors']}")
            
            # Check a specific record with vector data
            print("\n=== Sample Vector Data ===")
            cursor.execute("""
                SELECT id, embedding_vector
                FROM text2sql.vanna_embeddings
                WHERE embedding_vector IS NOT NULL
                LIMIT 1;
            """)

            vector_row = cursor.fetchone()
            if vector_row:
                vector = vector_row['embedding_vector']
                print(f"Record ID: {vector_row['id']}")
                print(f"Vector type: {type(vector)}")
                print(f"Vector length: {len(vector) if vector else 0}")
                if vector and len(vector) > 0:
                    print(f"First 5 values: {vector[:5]}")
            else:
                print("No records with vector data found")

            # Check resource discovery tables
            print("\n=== Resource Discovery Tables ===")
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'resource_discovery'
                ORDER BY table_name;
            """)

            rd_tables = cursor.fetchall()
            if rd_tables:
                print("Resource Discovery tables found:")
                for table in rd_tables:
                    print(f"  - {table['table_name']}")

                # Check resource_registry data
                cursor.execute("""
                    SELECT COUNT(*) as total_resources,
                           COUNT(CASE WHEN is_active = true THEN 1 END) as active_resources
                    FROM resource_discovery.resource_registry;
                """)

                rd_stats = cursor.fetchone()
                print(f"\nResource Registry Statistics:")
                print(f"  Total resources: {rd_stats['total_resources']}")
                print(f"  Active resources: {rd_stats['active_resources']}")

                # Check resource_vectors data
                cursor.execute("""
                    SELECT COUNT(*) as total_vectors,
                           COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as vectors_with_data
                    FROM resource_discovery.resource_vectors;
                """)

                rv_stats = cursor.fetchone()
                print(f"\nResource Vectors Statistics:")
                print(f"  Total vector records: {rv_stats['total_vectors']}")
                print(f"  Records with vector data: {rv_stats['vectors_with_data']}")

                # Check what resources are registered
                print("\n=== Registered Resources ===")
                cursor.execute("""
                    SELECT resource_id, resource_name, resource_type,
                           source_table, source_id, is_active
                    FROM resource_discovery.resource_registry
                    ORDER BY resource_type, resource_name;
                """)

                resources = cursor.fetchall()
                for res in resources:
                    print(f"  {res['resource_type']}: {res['resource_name']} ({res['resource_id']})")
                    print(f"    Source: {res['source_table']}#{res['source_id']}, Active: {res['is_active']}")

                # Check vanna_embeddings related resources
                print("\n=== Vanna Embeddings Resources ===")
                cursor.execute("""
                    SELECT resource_id, resource_name, description
                    FROM resource_discovery.resource_registry
                    WHERE source_table = 'text2sql.vanna_embeddings'
                       OR resource_id LIKE '%vanna%'
                       OR resource_id LIKE '%text2sql%'
                    ORDER BY resource_name;
                """)

                vanna_resources = cursor.fetchall()
                if vanna_resources:
                    for res in vanna_resources:
                        print(f"  - {res['resource_name']} ({res['resource_id']})")
                        print(f"    Description: {res['description']}")
                else:
                    print("  No vanna_embeddings related resources found!")

                # Check vanna_embeddings datasource distribution
                print("\n=== Vanna Embeddings Datasource Distribution ===")
                cursor.execute("""
                    SELECT
                        datasource_id,
                        content_type,
                        COUNT(*) as count
                    FROM text2sql.vanna_embeddings
                    GROUP BY datasource_id, content_type
                    ORDER BY datasource_id, content_type;
                """)

                ds_distribution = cursor.fetchall()
                for ds in ds_distribution:
                    print(f"  数据源 {ds['datasource_id']} - {ds['content_type']}: {ds['count']} 条记录")

                # Check if resources exist for all datasources
                print("\n=== Missing Text2SQL Resources ===")
                cursor.execute("""
                    SELECT DISTINCT ve.datasource_id
                    FROM text2sql.vanna_embeddings ve
                    LEFT JOIN resource_discovery.resource_registry rr
                        ON rr.resource_id = CONCAT('text2sql_', ve.datasource_id)
                    WHERE rr.resource_id IS NULL;
                """)

                missing_ds = cursor.fetchall()
                if missing_ds:
                    print("  缺失的数据源资源:")
                    for ds in missing_ds:
                        print(f"    - text2sql_{ds['datasource_id']}")
                else:
                    print("  所有数据源都有对应的资源")

            else:
                print("No resource discovery tables found")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_vector_data()
