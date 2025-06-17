# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Database datasource repository for Olight.

Provides database persistence layer for datasource management using PostgreSQL.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import asyncio

import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.pool

from src.config.database import get_database_config, get_database_connection
from src.models.database_datasource import (
    DatabaseDatasource,
    DatabaseType,
    ConnectionStatus,
    DatabaseDatasourceCreate,
    DatabaseDatasourceUpdate,
)

logger = logging.getLogger(__name__)


class DatabaseDatasourceRepository:
    """Repository for database datasource persistence"""
    
    def __init__(self):
        self._connection_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        self._schema_initialized = False
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize database connection pool"""
        try:
            db_config = get_database_config()

            self._connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                host=db_config["host"],
                port=db_config["port"],
                database=db_config["database"],
                user=db_config["user"],
                password=db_config["password"]
            )

        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
    
    async def _ensure_schema(self):
        """Ensure database schema exists"""
        try:
            connection = self._connection_pool.getconn()
            try:
                with connection.cursor() as cursor:
                    # Read and execute migration script
                    migration_file = "src/database/migrations/001_create_database_management_schema.sql"
                    try:
                        with open(migration_file, 'r') as f:
                            migration_sql = f.read()
                        cursor.execute(migration_sql)
                        connection.commit()
                        logger.info("✅ Database schema initialized successfully")
                    except FileNotFoundError:
                        logger.warning(f"Migration file not found: {migration_file}")
                        # Create basic schema if migration file is missing
                        cursor.execute("CREATE SCHEMA IF NOT EXISTS database_management;")
                        connection.commit()
                    except psycopg2.errors.DuplicateObject as e:
                        # Objects already exist, this is fine
                        connection.rollback()
                        logger.debug(f"Database objects already exist: {e}")

            finally:
                self._connection_pool.putconn(connection)

        except Exception as e:
            logger.error(f"Failed to ensure database schema: {e}")
            raise

    async def _table_exists(self) -> bool:
        """Check if the database_datasources table exists"""
        try:
            connection = self._connection_pool.getconn()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables
                            WHERE table_schema = 'database_management'
                            AND table_name = 'database_datasources'
                        );
                    """)
                    result = cursor.fetchone()
                    return result[0] if result else False
            finally:
                self._connection_pool.putconn(connection)
        except Exception as e:
            logger.warning(f"Failed to check table existence: {e}")
            return False

    async def _ensure_schema_if_needed(self):
        """Ensure schema is initialized (called lazily)"""
        if not self._schema_initialized:
            # Check if table already exists before running migration
            if not await self._table_exists():
                await self._ensure_schema()
            self._schema_initialized = True

    async def create_datasource(self, datasource_data: DatabaseDatasourceCreate) -> DatabaseDatasource:
        """Create a new datasource"""
        await self._ensure_schema_if_needed()
        try:
            connection = self._connection_pool.getconn()
            try:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        INSERT INTO database_management.database_datasources
                        (name, description, database_type, host, port, database_name,
                         username, password, readonly_mode, allowed_operations)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING *;
                    """, (
                        datasource_data.name,
                        datasource_data.description,
                        datasource_data.database_type.value,
                        datasource_data.host,
                        datasource_data.port,
                        datasource_data.database_name,
                        datasource_data.username,
                        datasource_data.password,
                        datasource_data.readonly_mode,
                        datasource_data.allowed_operations or ["SELECT"]
                    ))

                    row = cursor.fetchone()
                    connection.commit()

                    logger.info(f"Created datasource: {datasource_data.name} (ID: {row['id']})")
                    return self._row_to_datasource(row)

            finally:
                self._connection_pool.putconn(connection)

        except psycopg2.IntegrityError as e:
            if "unique constraint" in str(e).lower():
                raise ValueError(f"Datasource name '{datasource_data.name}' already exists")
            raise
        except Exception as e:
            logger.error(f"Failed to create datasource: {e}")
            raise
    
    async def get_datasource(self, datasource_id: int) -> Optional[DatabaseDatasource]:
        """Get datasource by ID"""
        await self._ensure_schema_if_needed()
        try:
            connection = self._connection_pool.getconn()
            try:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM database_management.database_datasources 
                        WHERE id = %s AND deleted_at IS NULL;
                    """, (datasource_id,))
                    
                    row = cursor.fetchone()
                    return self._row_to_datasource(row) if row else None
                    
            finally:
                self._connection_pool.putconn(connection)
                
        except Exception as e:
            logger.error(f"Failed to get datasource {datasource_id}: {e}")
            raise
    
    async def list_datasources(
        self,
        database_type: Optional[DatabaseType] = None,
        connection_status: Optional[ConnectionStatus] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[DatabaseDatasource]:
        """List datasources with filtering"""
        await self._ensure_schema_if_needed()
        try:
            connection = self._connection_pool.getconn()
            try:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Build dynamic query
                    where_conditions = ["deleted_at IS NULL"]
                    params = []
                    
                    if database_type:
                        where_conditions.append("database_type = %s")
                        params.append(database_type.value)
                    
                    if connection_status:
                        where_conditions.append("connection_status = %s")
                        params.append(connection_status.value)
                    
                    if search:
                        where_conditions.append("(name ILIKE %s OR description ILIKE %s OR database_name ILIKE %s)")
                        search_pattern = f"%{search}%"
                        params.extend([search_pattern, search_pattern, search_pattern])
                    
                    where_clause = " AND ".join(where_conditions)
                    
                    query = f"""
                        SELECT * FROM database_management.database_datasources 
                        WHERE {where_clause}
                        ORDER BY created_at DESC
                        LIMIT %s OFFSET %s;
                    """
                    
                    params.extend([limit, offset])
                    cursor.execute(query, params)
                    
                    rows = cursor.fetchall()
                    return [self._row_to_datasource(row) for row in rows]
                    
            finally:
                self._connection_pool.putconn(connection)
                
        except Exception as e:
            logger.error(f"Failed to list datasources: {e}")
            raise
    
    async def update_datasource(
        self,
        datasource_id: int,
        update_data: DatabaseDatasourceUpdate
    ) -> Optional[DatabaseDatasource]:
        """Update datasource"""
        try:
            connection = self._connection_pool.getconn()
            try:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Build dynamic update query
                    update_fields = []
                    params = []
                    
                    update_dict = update_data.model_dump(exclude_unset=True)
                    for field, value in update_dict.items():
                        update_fields.append(f"{field} = %s")
                        params.append(value)
                    
                    if not update_fields:
                        # No fields to update
                        return await self.get_datasource(datasource_id)
                    
                    params.append(datasource_id)
                    
                    query = f"""
                        UPDATE database_management.database_datasources 
                        SET {', '.join(update_fields)}
                        WHERE id = %s AND deleted_at IS NULL
                        RETURNING *;
                    """
                    
                    cursor.execute(query, params)
                    row = cursor.fetchone()
                    connection.commit()
                    
                    return self._row_to_datasource(row) if row else None
                    
            finally:
                self._connection_pool.putconn(connection)
                
        except psycopg2.IntegrityError as e:
            if "unique constraint" in str(e).lower():
                raise ValueError("Datasource name already exists")
            raise
        except Exception as e:
            logger.error(f"Failed to update datasource {datasource_id}: {e}")
            raise
    
    async def delete_datasource(self, datasource_id: int) -> bool:
        """Soft delete datasource"""
        try:
            connection = self._connection_pool.getconn()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE database_management.database_datasources 
                        SET deleted_at = NOW()
                        WHERE id = %s AND deleted_at IS NULL;
                    """, (datasource_id,))
                    
                    connection.commit()
                    return cursor.rowcount > 0
                    
            finally:
                self._connection_pool.putconn(connection)
                
        except Exception as e:
            logger.error(f"Failed to delete datasource {datasource_id}: {e}")
            raise
    
    async def update_connection_status(
        self,
        datasource_id: int,
        status: ConnectionStatus,
        error_message: Optional[str] = None,
        tested_at: Optional[datetime] = None
    ) -> bool:
        """Update connection status"""
        try:
            connection = self._connection_pool.getconn()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE database_management.database_datasources 
                        SET connection_status = %s, 
                            connection_error = %s,
                            last_tested_at = %s
                        WHERE id = %s AND deleted_at IS NULL;
                    """, (
                        status.value,
                        error_message,
                        tested_at or datetime.now(timezone.utc),
                        datasource_id
                    ))
                    
                    connection.commit()
                    return cursor.rowcount > 0
                    
            finally:
                self._connection_pool.putconn(connection)
                
        except Exception as e:
            logger.error(f"Failed to update connection status for datasource {datasource_id}: {e}")
            raise
    
    def _row_to_datasource(self, row: Dict[str, Any]) -> DatabaseDatasource:
        """Convert database row to DatabaseDatasource model"""
        return DatabaseDatasource(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            database_type=DatabaseType(row['database_type']),
            host=row['host'],
            port=row['port'],
            database_name=row['database_name'],
            username=row['username'],
            password=row['password'],
            readonly_mode=row['readonly_mode'],
            allowed_operations=row['allowed_operations'] if isinstance(row['allowed_operations'], list) else ["SELECT"],
            connection_status=ConnectionStatus(row['connection_status']),
            connection_error=row['connection_error'],
            last_tested_at=row['last_tested_at'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            deleted_at=row['deleted_at']
        )
    
    async def close(self):
        """Close connection pool"""
        if self._connection_pool:
            self._connection_pool.closeall()
            logger.info("Database connection pool closed")


# Global repository instance
database_datasource_repository = DatabaseDatasourceRepository()
