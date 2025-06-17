# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
API Definition Routes
API定义路由 - 严格按照ti-flow实现
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends

from src.models.api_tools import (
    APIDefinition, APIDefinitionCreate, APIDefinitionUpdate,
    APIDefinitionResponse, APIExecutionRequest, APIExecutionResponse,
    APITestRequest, BulkUpdateRequest, CountResponse, MessageResponse,
    CategoriesResponse, SearchResponse, RecentResponse, BulkUpdateResponse,
    APIStatisticsResponse
)
from src.services.api_tools import APIDefinitionService
from src.database import get_db_session

router = APIRouter(prefix="/api/admin/api-definitions", tags=["API定义管理"])


def convert_api_definition_to_response(api_def: APIDefinition) -> APIDefinitionResponse:
    """转换 SQLAlchemy 模型到 Pydantic 响应模型"""
    # 直接使用 JSONB 字段，它们已经是字典格式
    return APIDefinitionResponse(
        id=api_def.id,
        name=api_def.name,
        description=api_def.description,
        category=api_def.category,
        method=api_def.method,
        url=api_def.url,
        headers=api_def.headers,
        timeout_seconds=api_def.timeout_seconds,
        auth_config=api_def.auth_config,
        parameters=api_def.parameters,
        response_schema=api_def.response_schema,
        response_config=api_def.response_config,
        rate_limit=api_def.rate_limit,
        enabled=api_def.enabled,
        created_at=api_def.created_at,
        updated_at=api_def.updated_at,
    )


@router.get("", response_model=List[APIDefinitionResponse])
def list_api_definitions(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    category: Optional[str] = Query(None, description="按分类过滤"),
    enabled: Optional[bool] = Query(None, description="按启用状态过滤"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db_session=Depends(get_db_session)
):
    """获取API定义列表"""
    service = APIDefinitionService()
    api_defs = service.get_api_definitions(
        db_session=db_session,
        skip=skip,
        limit=limit,
        category=category,
        enabled=enabled,
        search=search
    )
    return [convert_api_definition_to_response(api_def) for api_def in api_defs]


@router.get("/count", response_model=CountResponse)
def count_api_definitions(
    category: Optional[str] = Query(None, description="按分类过滤"),
    enabled: Optional[bool] = Query(None, description="按启用状态过滤"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db_session=Depends(get_db_session)
):
    """获取API定义总数"""
    service = APIDefinitionService()
    count = service.count_api_definitions(
        db_session=db_session,
        category=category,
        enabled=enabled,
        search=search
    )
    return CountResponse(count=count)


@router.post("", response_model=APIDefinitionResponse)
def create_api_definition(
    api_def_create: APIDefinitionCreate,
    db_session=Depends(get_db_session)
):
    """创建API定义"""
    service = APIDefinitionService()
    try:
        api_def = service.create_api_definition(db_session, api_def_create)
        return convert_api_definition_to_response(api_def)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{api_id}", response_model=APIDefinitionResponse)
def get_api_definition(
    api_id: int,
    db_session=Depends(get_db_session)
):
    """获取API定义详情"""
    service = APIDefinitionService()
    api_def = service.get_api_definition(db_session, api_id)
    if not api_def:
        raise HTTPException(status_code=404, detail="API定义未找到")
    return convert_api_definition_to_response(api_def)


@router.put("/{api_id}", response_model=APIDefinitionResponse)
def update_api_definition(
    api_id: int,
    api_def_update: APIDefinitionUpdate,
    db_session=Depends(get_db_session)
):
    """更新API定义"""
    service = APIDefinitionService()
    try:
        api_def = service.update_api_definition(db_session, api_id, api_def_update)
        if not api_def:
            raise HTTPException(status_code=404, detail="API定义未找到")
        return convert_api_definition_to_response(api_def)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{api_id}", response_model=MessageResponse)
def delete_api_definition(
    api_id: int,
    db_session=Depends(get_db_session)
):
    """删除API定义"""
    service = APIDefinitionService()
    success = service.delete_api_definition(db_session, api_id)
    if not success:
        raise HTTPException(status_code=404, detail="API定义未找到")
    return MessageResponse(message="API定义已删除")


@router.post("/{api_id}/toggle", response_model=APIDefinitionResponse)
def toggle_api_enabled(
    api_id: int,
    db_session=Depends(get_db_session)
):
    """切换API启用状态"""
    service = APIDefinitionService()
    api_def = service.toggle_api_enabled(db_session, api_id)
    if not api_def:
        raise HTTPException(status_code=404, detail="API定义未找到")
    return convert_api_definition_to_response(api_def)


@router.post("/{api_id}/execute", response_model=APIExecutionResponse)
async def execute_api(
    api_id: int,
    request: APIExecutionRequest,
    db_session=Depends(get_db_session)
):
    """执行API调用"""
    service = APIDefinitionService()
    try:
        result = await service.execute_api(
            db_session=db_session,
            api_id=api_id,
            parameters=request.parameters,
            session_id=request.session_id
        )
        return APIExecutionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API执行失败: {str(e)}")


@router.post("/{api_id}/test")
async def test_api_connection(
    api_id: int,
    request: APITestRequest,
    db_session=Depends(get_db_session)
):
    """测试API连接"""
    service = APIDefinitionService()
    try:
        result = await service.test_api_connection(
            db_session=db_session,
            api_id=api_id,
            test_parameters=request.test_parameters
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API测试失败: {str(e)}")


@router.get("/{api_id}/schema")
def get_api_parameter_schema(
    api_id: int,
    db_session=Depends(get_db_session)
):
    """获取API参数模式"""
    service = APIDefinitionService()
    try:
        schema = service.get_parameter_schema(db_session, api_id)
        return schema
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{api_id}/validate")
def validate_api_parameters(
    api_id: int,
    parameters: Dict[str, Any],
    db_session=Depends(get_db_session)
):
    """验证API参数"""
    service = APIDefinitionService()
    try:
        result = service.validate_parameters(db_session, api_id, parameters)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/statistics/summary")
def get_api_statistics(
    db_session=Depends(get_db_session)
):
    """获取API统计信息"""
    service = APIDefinitionService()
    return service.get_api_statistics(db_session)


@router.get("/categories/list")
def get_api_categories(
    db_session=Depends(get_db_session)
):
    """获取所有分类"""
    service = APIDefinitionService()
    categories = service.get_categories(db_session)
    return {"categories": categories}


@router.get("/search/query")
def search_apis(
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(10, ge=1, le=50, description="返回记录数"),
    db_session=Depends(get_db_session)
):
    """搜索API定义"""
    service = APIDefinitionService()
    results = service.search_apis(db_session, q, limit)
    return {"results": results}


@router.get("/recent/list")
def get_recent_apis(
    limit: int = Query(5, ge=1, le=20, description="返回记录数"),
    db_session=Depends(get_db_session)
):
    """获取最近创建的API定义"""
    service = APIDefinitionService()
    results = service.get_recent_apis(db_session, limit)
    return {"results": results}


@router.post("/bulk/update")
def bulk_update_apis(
    request: BulkUpdateRequest,
    db_session=Depends(get_db_session)
):
    """批量更新API定义"""
    service = APIDefinitionService()
    
    if not request.api_ids:
        raise HTTPException(status_code=400, detail="API ID列表不能为空")
    
    updated_count = 0
    
    # 批量更新分类
    if request.category is not None:
        updated_count += service.bulk_update_category(
            db_session, request.api_ids, request.category
        )
    
    # 批量更新启用状态
    if request.enabled is not None:
        updated_count += service.bulk_toggle_enabled(
            db_session, request.api_ids, request.enabled
        )
    
    return {
        "message": f"已更新 {updated_count} 个API定义",
        "updated_count": updated_count
    }
