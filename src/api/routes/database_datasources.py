"""
数据库数据源管理 API 路由
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from src.services.database_datasource import database_datasource_service
from src.schemas.database_datasource_request import (
    DatabaseDatasourceListResponse,
    DatabaseDatasourceDetailResponse,
    DatabaseDatasourceCreateRequest,
    DatabaseDatasourceUpdateRequest,
    ConnectionTestRequest,
    ConnectionTestResponse,
    DatabaseTablesResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/database-datasources", tags=["数据库数据源"])

INTERNAL_SERVER_ERROR_DETAIL = "Internal Server Error"


@router.get("", response_model=DatabaseDatasourceListResponse)
async def list_database_datasources(
    database_type: Optional[str] = Query(None, description="Filter by database type"),
    connection_status: Optional[str] = Query(None, description="Filter by connection status"),
    search: Optional[str] = Query(None, description="Search keyword"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """List database datasources with filtering and pagination."""
    try:
        # Build filter parameters
        filters = {}
        if database_type:
            filters["database_type"] = database_type
        if connection_status:
            filters["connection_status"] = connection_status
        if search:
            filters["search"] = search

        datasources = await database_datasource_service.list_datasources(
            database_type=filters.get("database_type"),
            connection_status=filters.get("connection_status"),
            search=filters.get("search"),
            limit=limit,
            offset=offset
        )

        # For now, we'll use the length of returned datasources as total
        # In a real implementation, you'd want a separate count method
        total = len(datasources)
        
        return DatabaseDatasourceListResponse(
            datasources=[ds.model_dump() for ds in datasources],
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.exception(f"Error listing database datasources: {str(e)}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)


@router.post("", response_model=DatabaseDatasourceDetailResponse)
async def create_database_datasource(request: DatabaseDatasourceCreateRequest):
    """Create a new database datasource."""
    try:
        datasource = await database_datasource_service.create_datasource(request)
        return DatabaseDatasourceDetailResponse(**datasource.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error creating database datasource: {str(e)}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)


@router.get("/{datasource_id}", response_model=DatabaseDatasourceDetailResponse)
async def get_database_datasource(datasource_id: int):
    """Get database datasource by ID."""
    try:
        datasource = await database_datasource_service.get_datasource(datasource_id)
        if not datasource:
            raise HTTPException(status_code=404, detail="Datasource not found")
        
        return DatabaseDatasourceDetailResponse(**datasource.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting database datasource: {str(e)}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)


@router.put("/{datasource_id}", response_model=DatabaseDatasourceDetailResponse)
async def update_database_datasource(
    datasource_id: int,
    request: DatabaseDatasourceUpdateRequest
):
    """Update database datasource."""
    try:
        datasource = await database_datasource_service.update_datasource(
            datasource_id, request
        )
        if not datasource:
            raise HTTPException(status_code=404, detail="Datasource not found")
        
        return DatabaseDatasourceDetailResponse(**datasource.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error updating database datasource: {str(e)}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)


@router.delete("/{datasource_id}")
async def delete_database_datasource(datasource_id: int):
    """Delete database datasource."""
    try:
        success = await database_datasource_service.delete_datasource(datasource_id)
        if not success:
            raise HTTPException(status_code=404, detail="Datasource not found")
        
        return {"message": "Datasource deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting database datasource: {str(e)}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)


@router.post("/{datasource_id}/test", response_model=ConnectionTestResponse)
async def test_database_connection(
    datasource_id: int,
    request: ConnectionTestRequest = ConnectionTestRequest()
):
    """Test database connection."""
    try:
        result = await database_datasource_service.test_connection(datasource_id)
        return ConnectionTestResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error testing database connection: {str(e)}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)


@router.get("/{datasource_id}/schema", response_model=DatabaseTablesResponse)
async def get_database_schema(datasource_id: int):
    """Get database schema information."""
    try:
        schema = await database_datasource_service.get_database_schema(datasource_id)
        if not schema:
            raise HTTPException(status_code=404, detail="Datasource not found")

        return DatabaseTablesResponse(**schema.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting database schema: {str(e)}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)
