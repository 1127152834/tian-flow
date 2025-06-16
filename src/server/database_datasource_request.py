# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Database datasource request/response models for DeerFlow API.
Following deer-flow's API pattern with separate request/response files.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from src.models.database_datasource import (
    DatabaseDatasource,
    DatabaseDatasourceCreate,
    DatabaseDatasourceUpdate,
    DatabaseDatasourceResponse,
    ConnectionTestRequest,
    ConnectionTestResponse,
    DatabaseSchemaResponse,
    DatabaseType,
    ConnectionStatus,
)


class DatabaseDatasourceListRequest(BaseModel):
    """Request model for listing database datasources"""
    database_type: Optional[DatabaseType] = Field(None, description="Filter by database type")
    connection_status: Optional[ConnectionStatus] = Field(None, description="Filter by connection status")
    search: Optional[str] = Field(None, description="Search keyword for name/description")
    limit: int = Field(20, ge=1, le=100, description="Number of items per page")
    offset: int = Field(0, ge=0, description="Offset for pagination")


class DatabaseDatasourceListResponse(BaseModel):
    """Response model for database datasource list"""
    datasources: List[DatabaseDatasourceResponse] = Field(..., description="List of datasources")
    total: int = Field(..., description="Total number of datasources")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Current offset")


class DatabaseDatasourceCreateRequest(DatabaseDatasourceCreate):
    """Create database datasource request - inherits from model"""
    pass


class DatabaseDatasourceUpdateRequest(DatabaseDatasourceUpdate):
    """Update database datasource request - inherits from model"""
    pass


class DatabaseDatasourceDetailResponse(DatabaseDatasourceResponse):
    """Detailed database datasource response - inherits from model"""
    pass


class DatabaseTablesRequest(BaseModel):
    """Request model for getting database tables"""
    include_columns: bool = Field(True, description="Whether to include column information")


class DatabaseTablesResponse(DatabaseSchemaResponse):
    """Response model for database tables - inherits from schema response"""
    pass
