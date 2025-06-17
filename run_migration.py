#!/usr/bin/env python3
"""
Database migration runner for deer-flow.
Runs SQL migration files against the PostgreSQL database.
"""

import sys
import os
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def ensure_database_exists(db_config):
    """Ensure the target database exists, create if not"""
    try:
        # Connect to postgres database to create target database
        conn = psycopg2.connect(
            host=db_config["host"],
            port=db_config["port"],
            database="postgres",
            user=db_config["user"],
            password=db_config["password"]
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_config["database"],))
        exists = cursor.fetchone()

        if not exists:
            print(f"📦 Creating database: {db_config['database']}")
            cursor.execute(f'CREATE DATABASE "{db_config["database"]}"')
            print(f"✅ Database created successfully")
        else:
            print(f"✅ Database already exists: {db_config['database']}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Failed to ensure database exists: {e}")
        return False


def run_migration(migration_file: str):
    """Run a single migration file"""

    # Get database configuration from environment
    db_config = {
        "host": os.getenv("DATABASE_HOST", "localhost"),
        "port": int(os.getenv("DATABASE_PORT", "5432")),
        "database": os.getenv("POSTGRES_DB", "aolei_db"),
        "user": os.getenv("POSTGRES_USER", "aolei"),
        "password": os.getenv("POSTGRES_PASSWORD", "aolei123456")
    }

    # Ensure database exists
    if not ensure_database_exists(db_config):
        return False

    # Read migration file
    migration_path = Path(migration_file)
    if not migration_path.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False

    print(f"📄 Reading migration: {migration_path.name}")
    migration_sql = migration_path.read_text()

    # Connect to database
    try:
        print(f"🔌 Connecting to database: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        conn = psycopg2.connect(
            host=db_config["host"],
            port=db_config["port"],
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"]
        )

        print(f"✅ Connected to database successfully")

        # Execute migration
        print(f"🚀 Executing migration...")
        cursor = conn.cursor()
        cursor.execute(migration_sql)
        conn.commit()

        print(f"✅ Migration completed successfully: {migration_path.name}")

        # Close connection
        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python run_migration.py <migration_file>")
        print("Example: python run_migration.py src/database/migrations/002_create_text2sql_schema.sql")
        sys.exit(1)

    migration_file = sys.argv[1]
    success = run_migration(migration_file)

    if success:
        print("🎉 Migration completed successfully!")
        sys.exit(0)
    else:
        print("💥 Migration failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
