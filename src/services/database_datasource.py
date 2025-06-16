# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Database datasource service for DeerFlow.

Provides database connection testing, schema extraction, and connection management.
Uses PostgreSQL database for persistence instead of configuration files.
"""

import logging
import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

import pymysql
import psycopg2
from psycopg2.extras import RealDictCursor

from src.models.database_datasource import (
    DatabaseDatasource,
    DatabaseType,
    ConnectionStatus,
    DatabaseDatasourceCreate,
    DatabaseDatasourceUpdate,
    ConnectionTestResponse,
    DatabaseSchemaResponse,
)
from src.repositories.database_datasource import database_datasource_repository

logger = logging.getLogger(__name__)


class DatabaseDatasourceService:
    """Database datasource service - PostgreSQL database storage"""

    def __init__(self):
        self.repository = database_datasource_repository
    
    async def list_datasources(
        self,
        database_type: Optional[DatabaseType] = None,
        connection_status: Optional[ConnectionStatus] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[DatabaseDatasource]:
        """List datasources with filtering"""
        return await self.repository.list_datasources(
            database_type=database_type,
            connection_status=connection_status,
            search=search,
            limit=limit,
            offset=offset
        )

    async def get_datasource(self, datasource_id: int) -> Optional[DatabaseDatasource]:
        """Get datasource by ID"""
        return await self.repository.get_datasource(datasource_id)

    async def create_datasource(self, request: DatabaseDatasourceCreate) -> DatabaseDatasource:
        """Create new datasource"""
        return await self.repository.create_datasource(request)

    async def update_datasource(
        self,
        datasource_id: int,
        request: DatabaseDatasourceUpdate
    ) -> Optional[DatabaseDatasource]:
        """Update existing datasource"""
        return await self.repository.update_datasource(datasource_id, request)

    async def delete_datasource(self, datasource_id: int) -> bool:
        """Delete datasource (soft delete)"""
        return await self.repository.delete_datasource(datasource_id)
    
    async def get_datasource(self, datasource_id: int) -> Optional[DatabaseDatasource]:
        """Get datasource by ID"""
        datasource = self._datasources_cache.get(datasource_id)
        if datasource and datasource.deleted_at is None:
            return datasource
        return None
    
    async def create_datasource(self, request: DatabaseDatasourceCreate) -> DatabaseDatasource:
        """Create new datasource"""
        # Check for name conflicts
        existing = [
            ds for ds in self._datasources_cache.values()
            if ds.name == request.name and ds.deleted_at is None
        ]
        if existing:
            raise ValueError(f"Datasource name '{request.name}' already exists")
        
        # Create new datasource
        now = datetime.now(timezone.utc)
        datasource = DatabaseDatasource(
            id=self._next_id,
            name=request.name,
            description=request.description,
            database_type=request.database_type,
            host=request.host,
            port=request.port,
            database_name=request.database_name,
            username=request.username,
            password=request.password,
            readonly_mode=request.readonly_mode,
            allowed_operations=request.allowed_operations or ["SELECT"],
            connection_status=ConnectionStatus.DISCONNECTED,
            created_at=now,
            updated_at=now,
        )
        
        self._datasources_cache[self._next_id] = datasource
        self._next_id += 1
        
        # Save to config file
        self._save_datasources()
        
        logger.info(f"Created datasource: {datasource.name} (ID: {datasource.id})")
        return datasource

    async def update_datasource(
        self,
        datasource_id: int,
        request: DatabaseDatasourceUpdate
    ) -> Optional[DatabaseDatasource]:
        """Update existing datasource"""
        datasource = await self.get_datasource(datasource_id)
        if not datasource:
            return None

        # Check for name conflicts if name is being changed
        if request.name and request.name != datasource.name:
            existing = [
                ds for ds in self._datasources_cache.values()
                if ds.name == request.name and ds.deleted_at is None and ds.id != datasource_id
            ]
            if existing:
                raise ValueError(f"Datasource name '{request.name}' already exists")

        # Update fields
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(datasource, field, value)

        datasource.updated_at = datetime.now(timezone.utc)

        # Save to config file
        self._save_datasources()

        logger.info(f"Updated datasource: {datasource.name} (ID: {datasource.id})")
        return datasource

    async def delete_datasource(self, datasource_id: int) -> bool:
        """Delete datasource (soft delete)"""
        datasource = await self.get_datasource(datasource_id)
        if not datasource:
            return False

        datasource.deleted_at = datetime.now(timezone.utc)

        # Save to config file
        self._save_datasources()

        logger.info(f"Deleted datasource: {datasource.name} (ID: {datasource.id})")
        return True

    async def test_connection(
        self,
        datasource_id: int,
        timeout: int = 10
    ) -> ConnectionTestResponse:
        """Test database connection"""
        datasource = await self.get_datasource(datasource_id)
        if not datasource:
            return ConnectionTestResponse(
                success=False,
                error="Datasource not found",
                tested_at=datetime.now(timezone.utc)
            )

        return await self._test_database_connection(datasource, timeout)

    async def _test_database_connection(
        self,
        datasource: DatabaseDatasource,
        timeout: int = 10
    ) -> ConnectionTestResponse:
        """Test database connection implementation"""
        tested_at = datetime.now(timezone.utc)

        try:
            if datasource.database_type == DatabaseType.MYSQL:
                await asyncio.wait_for(
                    asyncio.to_thread(self._test_mysql_connection, datasource),
                    timeout=timeout
                )
            elif datasource.database_type == DatabaseType.POSTGRESQL:
                await asyncio.wait_for(
                    asyncio.to_thread(self._test_postgresql_connection, datasource),
                    timeout=timeout
                )
            else:
                raise ValueError(f"Unsupported database type: {datasource.database_type}")

            # Update datasource status in database
            await self.repository.update_connection_status(
                datasource.id,
                ConnectionStatus.CONNECTED,
                error_message=None,
                tested_at=tested_at
            )

            return ConnectionTestResponse(
                success=True,
                details={"database_type": datasource.database_type.value},
                tested_at=tested_at
            )

        except asyncio.TimeoutError:
            error_msg = f"Connection timeout after {timeout} seconds"
            await self.repository.update_connection_status(
                datasource.id,
                ConnectionStatus.ERROR,
                error_message=error_msg,
                tested_at=tested_at
            )

            return ConnectionTestResponse(
                success=False,
                error=error_msg,
                tested_at=tested_at
            )
        except Exception as e:
            error_msg = str(e)
            await self.repository.update_connection_status(
                datasource.id,
                ConnectionStatus.ERROR,
                error_message=error_msg,
                tested_at=tested_at
            )

            return ConnectionTestResponse(
                success=False,
                error=error_msg,
                tested_at=tested_at
            )

    def _test_mysql_connection(self, datasource: DatabaseDatasource):
        """Test MySQL connection"""
        connection = pymysql.connect(
            host=datasource.host,
            port=datasource.port,
            user=datasource.username,
            password=datasource.password,
            database=datasource.database_name,
            connect_timeout=10,
            read_timeout=10,
            write_timeout=10,
        )

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        connection.close()
        return True

    def _test_postgresql_connection(self, datasource: DatabaseDatasource):
        """Test PostgreSQL connection"""
        connection = psycopg2.connect(
            host=datasource.host,
            port=datasource.port,
            user=datasource.username,
            password=datasource.password,
            database=datasource.database_name,
            connect_timeout=10,
        )

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        connection.close()
        return True

    async def get_database_schema(self, datasource_id: int) -> Optional[DatabaseSchemaResponse]:
        """Get database schema information"""
        datasource = await self.get_datasource(datasource_id)
        if not datasource:
            return None

        try:
            if datasource.database_type == DatabaseType.MYSQL:
                tables = await asyncio.to_thread(self._get_mysql_schema, datasource)
            elif datasource.database_type == DatabaseType.POSTGRESQL:
                tables = await asyncio.to_thread(self._get_postgresql_schema, datasource)
            else:
                raise ValueError(f"Unsupported database type: {datasource.database_type}")

            return DatabaseSchemaResponse(
                tables=tables,
                total_tables=len(tables),
                schema_extracted_at=datetime.now(timezone.utc)
            )

        except Exception as e:
            logger.error(f"Failed to extract schema for datasource {datasource_id}: {e}")
            raise

    def _get_mysql_schema(self, datasource: DatabaseDatasource) -> List[dict]:
        """Get MySQL database schema"""
        connection = pymysql.connect(
            host=datasource.host,
            port=datasource.port,
            user=datasource.username,
            password=datasource.password,
            database=datasource.database_name,
        )

        tables = []
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # Get table names
                cursor.execute("SHOW TABLES")
                table_names = [list(row.values())[0] for row in cursor.fetchall()]

                for table_name in table_names:
                    # Get table structure
                    cursor.execute(f"DESCRIBE `{table_name}`")
                    columns = cursor.fetchall()

                    tables.append({
                        "table_name": table_name,
                        "columns": columns,
                        "column_count": len(columns)
                    })
        finally:
            connection.close()

        return tables

    def _get_postgresql_schema(self, datasource: DatabaseDatasource) -> List[dict]:
        """Get PostgreSQL database schema"""
        connection = psycopg2.connect(
            host=datasource.host,
            port=datasource.port,
            user=datasource.username,
            password=datasource.password,
            database=datasource.database_name,
        )

        tables = []
        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get table names from all schemas (excluding system schemas)
                cursor.execute("""
                    SELECT table_schema, table_name
                    FROM information_schema.tables
                    WHERE table_type = 'BASE TABLE'
                    AND table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                    ORDER BY table_schema, table_name
                """)
                table_info = cursor.fetchall()

                for table_row in table_info:
                    schema_name = table_row['table_schema']
                    table_name = table_row['table_name']
                    full_table_name = f"{schema_name}.{table_name}"

                    # Get table structure
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns
                        WHERE table_name = %s AND table_schema = %s
                        ORDER BY ordinal_position
                    """, (table_name, schema_name))
                    columns = cursor.fetchall()

                    tables.append({
                        "table_name": full_table_name,
                        "schema_name": schema_name,
                        "table_name_only": table_name,
                        "columns": [dict(col) for col in columns],
                        "column_count": len(columns)
                    })
        finally:
            connection.close()

        return tables


# Global service instance
database_datasource_service = DatabaseDatasourceService()
