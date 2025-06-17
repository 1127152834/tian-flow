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

    async def get_database_connection(self, datasource_id: int):
        """Get database connection for a datasource"""
        datasource = await self.get_datasource(datasource_id)
        if not datasource:
            raise ValueError(f"Datasource {datasource_id} not found")

        if datasource.database_type == DatabaseType.MYSQL:
            return pymysql.connect(
                host=datasource.host,
                port=datasource.port,
                user=datasource.username,
                password=datasource.password,
                database=datasource.database_name,
            )
        elif datasource.database_type == DatabaseType.POSTGRESQL:
            return psycopg2.connect(
                host=datasource.host,
                port=datasource.port,
                user=datasource.username,
                password=datasource.password,
                database=datasource.database_name,
            )
        else:
            raise ValueError(f"Unsupported database type: {datasource.database_type}")

    async def extract_ddl_statements(self, datasource_id: int, database_name: Optional[str] = None) -> List[str]:
        """Extract DDL statements from database"""
        datasource = await self.get_datasource(datasource_id)
        if not datasource:
            raise ValueError(f"Datasource {datasource_id} not found")

        try:
            if datasource.database_type == DatabaseType.MYSQL:
                return await asyncio.to_thread(self._extract_mysql_ddl, datasource, database_name)
            elif datasource.database_type == DatabaseType.POSTGRESQL:
                return await asyncio.to_thread(self._extract_postgresql_ddl, datasource, database_name)
            else:
                raise ValueError(f"Unsupported database type: {datasource.database_type}")
        except Exception as e:
            logger.error(f"Failed to extract DDL from datasource {datasource_id}: {e}")
            raise

    def _extract_mysql_ddl(self, datasource: DatabaseDatasource, database_name: Optional[str] = None) -> List[str]:
        """Extract DDL statements from MySQL database"""
        connection = pymysql.connect(
            host=datasource.host,
            port=datasource.port,
            user=datasource.username,
            password=datasource.password,
            database=database_name or datasource.database_name,
        )

        ddl_statements = []
        try:
            with connection.cursor() as cursor:
                # Get all databases accessible to this user (excluding system databases)
                cursor.execute("""
                    SHOW DATABASES
                """)
                databases = [row[0] for row in cursor.fetchall()
                           if row[0] not in ('information_schema', 'performance_schema', 'mysql', 'sys')]

                # If specific database is requested, only use that one
                if database_name:
                    databases = [db for db in databases if db == database_name]
                else:
                    # Use the connected database
                    databases = [datasource.database_name]

                for db_name in databases:
                    # Switch to the database
                    cursor.execute(f"USE `{db_name}`")

                    # Get all table names in this database
                    cursor.execute("SHOW TABLES")
                    tables = [row[0] for row in cursor.fetchall()]

                    # Add database creation statement if multiple databases
                    if len(databases) > 1:
                        ddl_statements.append(f"CREATE DATABASE IF NOT EXISTS `{db_name}`;")
                        ddl_statements.append(f"USE `{db_name}`;")

                    for table in tables:
                        # Get CREATE TABLE statement
                        cursor.execute(f"SHOW CREATE TABLE `{table}`")
                        result = cursor.fetchone()
                        if result:
                            # Clean up the CREATE TABLE statement
                            create_statement = result[1]
                            # Add database prefix if multiple databases
                            if len(databases) > 1:
                                create_statement = create_statement.replace(
                                    f"CREATE TABLE `{table}`",
                                    f"CREATE TABLE `{db_name}`.`{table}`"
                                )
                            ddl_statements.append(create_statement)
        finally:
            connection.close()

        return ddl_statements

    def _extract_postgresql_ddl(self, datasource: DatabaseDatasource, database_name: Optional[str] = None) -> List[str]:
        """Extract DDL statements from PostgreSQL database"""
        connection = psycopg2.connect(
            host=datasource.host,
            port=datasource.port,
            user=datasource.username,
            password=datasource.password,
            database=database_name or datasource.database_name,
        )

        ddl_statements = []
        try:
            with connection.cursor() as cursor:
                # Get all tables from all schemas (excluding system schemas)
                cursor.execute("""
                    SELECT table_schema, table_name
                    FROM information_schema.tables
                    WHERE table_type = 'BASE TABLE'
                    AND table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                    ORDER BY table_schema, table_name
                """)
                tables = cursor.fetchall()

                for schema_name, table_name in tables:
                    # Generate CREATE TABLE statement with schema
                    cursor.execute("""
                        SELECT
                            'CREATE TABLE ' || %s || '.' || table_name || ' (' ||
                            string_agg(
                                column_name || ' ' ||
                                CASE
                                    WHEN data_type = 'character varying' THEN
                                        CASE WHEN character_maximum_length IS NOT NULL
                                             THEN 'VARCHAR(' || character_maximum_length || ')'
                                             ELSE 'VARCHAR'
                                        END
                                    WHEN data_type = 'character' THEN
                                        CASE WHEN character_maximum_length IS NOT NULL
                                             THEN 'CHAR(' || character_maximum_length || ')'
                                             ELSE 'CHAR'
                                        END
                                    WHEN data_type = 'numeric' THEN
                                        CASE WHEN numeric_precision IS NOT NULL AND numeric_scale IS NOT NULL
                                             THEN 'NUMERIC(' || numeric_precision || ',' || numeric_scale || ')'
                                             ELSE 'NUMERIC'
                                        END
                                    WHEN data_type = 'integer' THEN 'INTEGER'
                                    WHEN data_type = 'bigint' THEN 'BIGINT'
                                    WHEN data_type = 'smallint' THEN 'SMALLINT'
                                    WHEN data_type = 'boolean' THEN 'BOOLEAN'
                                    WHEN data_type = 'text' THEN 'TEXT'
                                    WHEN data_type = 'timestamp without time zone' THEN 'TIMESTAMP'
                                    WHEN data_type = 'timestamp with time zone' THEN 'TIMESTAMPTZ'
                                    WHEN data_type = 'date' THEN 'DATE'
                                    WHEN data_type = 'time without time zone' THEN 'TIME'
                                    WHEN data_type = 'uuid' THEN 'UUID'
                                    WHEN data_type = 'json' THEN 'JSON'
                                    WHEN data_type = 'jsonb' THEN 'JSONB'
                                    WHEN data_type = 'ARRAY' THEN 'TEXT[]'
                                    ELSE UPPER(data_type)
                                END ||
                                CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END ||
                                CASE WHEN column_default IS NOT NULL THEN ' DEFAULT ' || column_default ELSE '' END,
                                ', ' ORDER BY ordinal_position
                            ) || ');' as ddl
                        FROM information_schema.columns
                        WHERE table_name = %s AND table_schema = %s
                        GROUP BY table_name
                    """, (schema_name, table_name, schema_name))

                    result = cursor.fetchone()
                    if result:
                        ddl_statements.append(result[0])

                # Also add schema creation statements
                cursor.execute("""
                    SELECT DISTINCT table_schema
                    FROM information_schema.tables
                    WHERE table_type = 'BASE TABLE'
                    AND table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                    AND table_schema != 'public'
                    ORDER BY table_schema
                """)
                schemas = cursor.fetchall()

                # Prepend schema creation statements
                schema_statements = []
                for (schema_name,) in schemas:
                    schema_statements.append(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")

                # Combine schema creation + table creation
                ddl_statements = schema_statements + ddl_statements

        finally:
            connection.close()

        return ddl_statements


# Global service instance
database_datasource_service = DatabaseDatasourceService()
