#!/usr/bin/env python3
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Run database migration script.
"""

import sys
import os
import psycopg2

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.database import get_database_connection


def run_migration():
    """Run the database migration"""
    try:
        # Get database connection directly
        connection = get_database_connection()
        
        # Read migration file
        migration_file = "src/database/migrations/001_create_database_management_schema.sql"
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        with connection.cursor() as cursor:
            cursor.execute(migration_sql)
            connection.commit()
        
        print("✅ Database migration completed successfully!")
        
        # Verify tables were created
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'database_management'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            print(f"📋 Created tables in database_management schema:")
            for table in tables:
                print(f"   • {table[0]}")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
