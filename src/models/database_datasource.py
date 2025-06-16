# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Database datasource models for DeerFlow.

Adapted from ti-flow but removed ChatEngine dependencies and user-related fields.
Uses configuration-based resource management instead.
"""

from datetime import datetime
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, Field


class DatabaseType(str, Enum):
    """Database type enumeration (compatible with ti-flow)"""
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"
    TIDB = "TIDB"  # Added for ti-flow compatibility


class ConnectionStatus(str, Enum):
    """Connection status enumeration"""
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"
    TESTING = "TESTING"


class IndexStatus(str, Enum):
    """Index status enumeration (ti-flow compatibility)"""
    NOT_STARTED = "NOT_STARTED"
    CONNECTING = "CONNECTING"
    SCHEMA_ANALYSIS = "SCHEMA_ANALYSIS"
    TABLE_INDEXING = "TABLE_INDEXING"
    COLUMN_INDEXING = "COLUMN_INDEXING"
    SAMPLE_DATA_INDEXING = "SAMPLE_DATA_INDEXING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DatabaseDatasource(BaseModel):
    """Database datasource model - adapted for deer-flow config-based architecture"""
    
    # Basic information
    id: Optional[int] = Field(default=None, description="Datasource ID")
    name: str = Field(..., max_length=256, description="Datasource name")
    description: Optional[str] = Field(default=None, max_length=4096, description="Datasource description")
    
    # Database connection information  
    database_type: DatabaseType = Field(..., description="Database type")
    host: str = Field(..., max_length=256, description="Host address")
    port: int = Field(..., description="Port")
    database_name: str = Field(..., max_length=256, description="Database name")
    username: str = Field(..., max_length=256, description="Username")
    password: str = Field(..., max_length=512, description="Password")
    
    # Security configuration
    readonly_mode: bool = Field(default=True, description="Read-only mode")
    allowed_operations: List[str] = Field(
        default_factory=lambda: ["SELECT"],
        description="Allowed SQL operation types"
    )
    
    # Connection status
    connection_status: ConnectionStatus = Field(
        default=ConnectionStatus.DISCONNECTED,
        description="Connection status"
    )
    last_tested_at: Optional[datetime] = Field(default=None, description="Last test time")
    connection_error: Optional[str] = Field(default=None, max_length=2048, description="Connection error message")
    
    # Timestamps
    created_at: Optional[datetime] = Field(default=None, description="Creation time")
    updated_at: Optional[datetime] = Field(default=None, description="Update time")
    deleted_at: Optional[datetime] = Field(default=None, description="Deletion time")
    
    class Config:
        """Pydantic configuration"""
        arbitrary_types_allowed = True


class DatabaseDatasourceCreate(BaseModel):
    """Create database datasource request model"""
    name: str = Field(..., max_length=256, description="Datasource name")
    description: Optional[str] = Field(None, max_length=4096, description="Datasource description")
    database_type: DatabaseType = Field(..., description="Database type")
    host: str = Field(..., max_length=256, description="Host address")
    port: int = Field(..., ge=1, le=65535, description="Port")
    database_name: str = Field(..., max_length=256, description="Database name")
    username: str = Field(..., max_length=256, description="Username")
    password: str = Field(..., max_length=512, description="Password")
    readonly_mode: bool = Field(True, description="Read-only mode")
    allowed_operations: Optional[List[str]] = Field(["SELECT"], description="Allowed SQL operations")


class DatabaseDatasourceUpdate(BaseModel):
    """Update database datasource request model"""
    name: Optional[str] = Field(None, max_length=256, description="Datasource name")
    description: Optional[str] = Field(None, max_length=4096, description="Datasource description")
    host: Optional[str] = Field(None, max_length=256, description="Host address")
    port: Optional[int] = Field(None, ge=1, le=65535, description="Port")
    database_name: Optional[str] = Field(None, max_length=256, description="Database name")
    username: Optional[str] = Field(None, max_length=256, description="Username")
    password: Optional[str] = Field(None, max_length=512, description="Password")
    readonly_mode: Optional[bool] = Field(None, description="Read-only mode")
    allowed_operations: Optional[List[str]] = Field(None, description="Allowed SQL operations")


class DatabaseDatasourceResponse(BaseModel):
    """Database datasource response model"""
    id: int = Field(..., description="Datasource ID")
    name: str = Field(..., description="Datasource name")
    description: Optional[str] = Field(None, description="Datasource description")
    database_type: DatabaseType = Field(..., description="Database type")
    host: str = Field(..., description="Host address")
    port: int = Field(..., description="Port")
    database_name: str = Field(..., description="Database name")
    username: str = Field(..., description="Username")
    readonly_mode: bool = Field(..., description="Read-only mode")
    allowed_operations: List[str] = Field(..., description="Allowed SQL operations")
    connection_status: ConnectionStatus = Field(..., description="Connection status")
    last_tested_at: Optional[datetime] = Field(None, description="Last test time")
    connection_error: Optional[str] = Field(None, description="Connection error message")
    created_at: Optional[datetime] = Field(None, description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Update time")

    class Config:
        from_attributes = True


class ConnectionTestRequest(BaseModel):
    """Connection test request model"""
    timeout: Optional[int] = Field(10, ge=1, le=60, description="Timeout in seconds")


class ConnectionTestResponse(BaseModel):
    """Connection test response model"""
    success: bool = Field(..., description="Whether test was successful")
    error: Optional[str] = Field(None, description="Error message")
    details: Optional[dict] = Field(None, description="Connection details")
    tested_at: datetime = Field(..., description="Test time")


class DatabaseSchemaResponse(BaseModel):
    """Database schema response model"""
    tables: List[dict] = Field(..., description="Database tables information")
    total_tables: int = Field(..., description="Total number of tables")
    schema_extracted_at: datetime = Field(..., description="Schema extraction time")
