# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Database adapter for Vanna AI
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.models.database_datasource import DatabaseDatasource, DatabaseType
from src.services.database_datasource import DatabaseDatasourceService

logger = logging.getLogger(__name__)


class DatabaseAdapter:
    """
    Database adapter for Vanna AI
    
    Provides database connection and query execution functionality
    """
    
    def __init__(self, datasource_id: int):
        """
        Initialize database adapter
        
        Args:
            datasource_id: Database datasource ID
        """
        self.datasource_id = datasource_id
        self._datasource = None
        self._engine = None
        self.db_service = DatabaseDatasourceService()
        
        logger.info(f"Initialized DatabaseAdapter for datasource {datasource_id}")
    
    async def _get_datasource(self) -> DatabaseDatasource:
        """Get datasource configuration"""
        if self._datasource is None:
            self._datasource = await self.db_service.get_datasource(self.datasource_id)
            if not self._datasource:
                raise ValueError(f"Datasource {self.datasource_id} not found")
        return self._datasource
    
    async def _get_engine(self):
        """Get database engine"""
        if self._engine is None:
            datasource = await self._get_datasource()
            
            # Build connection URL based on database type
            if datasource.database_type == DatabaseType.MYSQL:
                url = f"mysql+pymysql://{datasource.username}:{datasource.password}@{datasource.host}:{datasource.port}/{datasource.database_name}"
            elif datasource.database_type == DatabaseType.POSTGRESQL:
                url = f"postgresql+psycopg2://{datasource.username}:{datasource.password}@{datasource.host}:{datasource.port}/{datasource.database_name}"
            else:
                raise ValueError(f"Unsupported database type: {datasource.database_type}")
            
            self._engine = create_engine(url)
        
        return self._engine
    
    def to_vanna_config(self) -> Dict[str, Any]:
        """
        Convert to Vanna configuration format

        Returns:
            Vanna configuration dictionary
        """
        # Return a basic config without async calls for now
        # This will be enhanced when we have proper datasource management
        config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'aolei_db',
            'user': 'postgres',
            'password': 'password',
            'database_type': 'postgresql',
            'readonly_mode': True,
            'allowed_operations': ['SELECT']
        }

        logger.info(f"Using default database config for datasource {self.datasource_id}")
        return config
    
    async def execute_sql_async(self, sql: str, limit: int = 1000) -> pd.DataFrame:
        """
        Execute SQL query asynchronously and return pandas DataFrame
        
        Args:
            sql: SQL query statement
            limit: Result limit (default 1000 rows)
            
        Returns:
            Query result DataFrame
        """
        try:
            datasource = await self._get_datasource()
            
            # Check readonly mode and operation permissions
            if datasource.readonly_mode:
                sql_upper = sql.upper().strip()
                allowed_ops = [op.upper() for op in datasource.allowed_operations]
                
                is_allowed = any(sql_upper.startswith(op) for op in allowed_ops)
                if not is_allowed:
                    raise ValueError(f"Operation not allowed. Only allowed: {datasource.allowed_operations}")
            
            # Add LIMIT restriction
            if limit and 'LIMIT' not in sql.upper():
                sql = f"{sql.rstrip(';')} LIMIT {limit}"
            
            # Get engine and execute query
            engine = await self._get_engine()
            
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                
                # Get column names
                columns = list(result.keys()) if result.keys() else []
                
                # Get data
                rows = result.fetchall()
                
                # Create DataFrame
                df = pd.DataFrame(rows, columns=columns)
                
                logger.info(f"SQL async execution successful, returned {len(df)} rows")
                return df
                
        except Exception as e:
            logger.error(f"SQL async execution failed: {e}")
            raise
    
    def execute_sql_sync(self, sql: str, limit: int = 1000) -> pd.DataFrame:
        """
        Execute SQL query synchronously and return pandas DataFrame

        This is a simplified implementation for testing

        Args:
            sql: SQL query statement
            limit: Result limit (default 1000 rows)

        Returns:
            Query result DataFrame
        """
        try:
            # Return mock data for now
            logger.info(f"Mock SQL execution: {sql[:50]}...")

            # Create mock DataFrame
            mock_data = {
                'id': [1, 2, 3],
                'name': ['User 1', 'User 2', 'User 3'],
                'email': ['user1@example.com', 'user2@example.com', 'user3@example.com']
            }

            df = pd.DataFrame(mock_data)
            logger.info(f"Mock SQL execution successful, returned {len(df)} rows")
            return df

        except Exception as e:
            logger.error(f"SQL sync execution failed: {e}")
            raise
    
    async def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        Get table schema information
        
        Args:
            table_name: Table name
            
        Returns:
            Table schema information
        """
        try:
            datasource = await self._get_datasource()
            engine = await self._get_engine()
            
            if datasource.database_type == DatabaseType.MYSQL:
                query = text("""
                    SELECT 
                        COLUMN_NAME as column_name,
                        DATA_TYPE as data_type,
                        IS_NULLABLE as is_nullable,
                        COLUMN_DEFAULT as column_default,
                        COLUMN_COMMENT as column_comment
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = :database_name 
                    AND TABLE_NAME = :table_name
                    ORDER BY ORDINAL_POSITION
                """)
                
                with engine.connect() as conn:
                    result = conn.execute(query, {
                        'database_name': datasource.database_name,
                        'table_name': table_name
                    })
                    
                    columns = []
                    for row in result.fetchall():
                        columns.append({
                            'name': row[0],
                            'type': row[1],
                            'nullable': row[2] == 'YES',
                            'default': row[3],
                            'comment': row[4]
                        })
                    
                    return {
                        'table_name': table_name,
                        'columns': columns
                    }
            
            elif datasource.database_type == DatabaseType.POSTGRESQL:
                query = text("""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns 
                    WHERE table_catalog = :database_name 
                    AND table_name = :table_name
                    ORDER BY ordinal_position
                """)
                
                with engine.connect() as conn:
                    result = conn.execute(query, {
                        'database_name': datasource.database_name,
                        'table_name': table_name
                    })
                    
                    columns = []
                    for row in result.fetchall():
                        columns.append({
                            'name': row[0],
                            'type': row[1],
                            'nullable': row[2] == 'YES',
                            'default': row[3],
                            'comment': None
                        })
                    
                    return {
                        'table_name': table_name,
                        'columns': columns
                    }
            
            else:
                raise ValueError(f"Unsupported database type: {datasource.database_type}")
                
        except Exception as e:
            logger.error(f"Failed to get table schema: {e}")
            raise
    
    async def get_database_schema(self) -> List[Dict[str, Any]]:
        """
        Get complete database schema
        
        Returns:
            List of table schemas
        """
        try:
            datasource = await self._get_datasource()
            engine = await self._get_engine()
            
            # Get all table names first
            if datasource.database_type == DatabaseType.MYSQL:
                query = text("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_SCHEMA = :database_name 
                    AND TABLE_TYPE = 'BASE TABLE'
                """)
            elif datasource.database_type == DatabaseType.POSTGRESQL:
                query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_catalog = :database_name 
                    AND table_type = 'BASE TABLE'
                    AND table_schema = 'public'
                """)
            else:
                raise ValueError(f"Unsupported database type: {datasource.database_type}")
            
            with engine.connect() as conn:
                result = conn.execute(query, {'database_name': datasource.database_name})
                table_names = [row[0] for row in result.fetchall()]
            
            # Get schema for each table
            schemas = []
            for table_name in table_names:
                try:
                    schema = await self.get_table_schema(table_name)
                    schemas.append(schema)
                except Exception as e:
                    logger.warning(f"Failed to get schema for table {table_name}: {e}")
                    continue
            
            logger.info(f"Retrieved schema for {len(schemas)} tables")
            return schemas
            
        except Exception as e:
            logger.error(f"Failed to get database schema: {e}")
            raise
