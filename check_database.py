#!/usr/bin/env python3
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Check database structure.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.database import get_database_connection


def check_database():
    """Check the database structure"""
    try:
        # Get database connection
        connection = get_database_connection()
        
        # Check schemas
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY schema_name;
            """)
            schemas = cursor.fetchall()
            
            print("📁 Database schemas:")
            for schema in schemas:
                print(f"   • {schema['schema_name']}")
        
        # Check tables in database_management schema
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'database_management'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            print(f"\n📋 Tables in database_management schema:")
            for table in tables:
                print(f"   • {table['table_name']}")
        
        # Check database_datasources table structure
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_schema = 'database_management' 
                AND table_name = 'database_datasources'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            
            print(f"\n🔍 database_datasources table structure:")
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                print(f"   • {col['column_name']}: {col['data_type']} {nullable}{default}")
        
        # Check existing data
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, database_type, host, port, connection_status, created_at
                FROM database_management.database_datasources 
                WHERE deleted_at IS NULL
                ORDER BY created_at DESC;
            """)
            datasources = cursor.fetchall()
            
            print(f"\n💾 Existing datasources ({len(datasources)}):")
            for ds in datasources:
                print(f"   • ID: {ds['id']}, Name: {ds['name']}, Type: {ds['database_type']}, Status: {ds['connection_status']}")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = check_database()
    sys.exit(0 if success else 1)
