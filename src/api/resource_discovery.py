"""
资源发现模块 API 路由

基于 Ti-Flow 的意图识别 API 设计，为 DeerFlow 提供资源发现和匹配接口
"""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db_session
from src.models.resource_discovery import (
    ResourceDiscoveryRequest,
    ResourceDiscoveryResponse,
    ResourceRegistryResponse,
    ResourceMatch,
    ResourceType,
    VectorizationStatus,
    BatchVectorizationRequest,
    BatchVectorizationResponse,
    SystemStatus,
    OperationType,
    SystemStatusType
)
from src.services.resource_discovery import (
    ResourceDiscoveryService,
    ResourceVectorizer,
    ResourceMatcher,
    ResourceSynchronizer
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/resource-discovery", tags=["Resource Discovery"])

# 初始化服务
discovery_service = ResourceDiscoveryService()
vectorizer = ResourceVectorizer()
matcher = ResourceMatcher()
synchronizer = ResourceSynchronizer()


@router.post("/discover", response_model=ResourceDiscoveryResponse)
async def discover_resources(
    request: ResourceDiscoveryRequest,
    session: Session = Depends(get_db_session)
):
    """
    智能资源发现
    
    根据用户查询找到最匹配的系统资源
    """
    try:
        start_time = datetime.utcnow()
        
        logger.info(f"🔍 资源发现请求: '{request.user_query}'")
        
        # 执行资源匹配
        matches = await matcher.match_resources(
            session=session,
            user_query=request.user_query,
            top_k=request.max_results,
            resource_types=[rt.value for rt in request.resource_types] if request.resource_types else None,
            min_confidence=request.min_confidence
        )
        
        # 获取总资源数量
        from sqlalchemy import text
        count_query = text("SELECT COUNT(*) FROM resource_discovery.resource_registry WHERE is_active = true")
        total_resources = session.execute(count_query).scalar()
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        response = ResourceDiscoveryResponse(
            query=request.user_query,
            matches=matches,
            total_resources=total_resources,
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"✅ 资源发现完成: 找到 {len(matches)} 个匹配资源，耗时 {processing_time:.0f}ms")
        return response
        
    except Exception as e:
        logger.error(f"❌ 资源发现失败: {e}")
        raise HTTPException(status_code=500, detail=f"资源发现失败: {str(e)}")


@router.get("/resources", response_model=List[ResourceRegistryResponse])
async def list_resources(
    resource_type: Optional[ResourceType] = Query(None, description="资源类型过滤"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    vectorization_status: Optional[VectorizationStatus] = Query(None, description="向量化状态"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(50, ge=1, le=1000, description="返回数量"),
    session: Session = Depends(get_db_session)
):
    """获取资源列表"""
    try:
        from sqlalchemy import text
        
        # 构建查询条件
        conditions = ["1=1"]
        params = {"skip": skip, "limit": limit}
        
        if resource_type:
            conditions.append("resource_type = :resource_type")
            params["resource_type"] = resource_type.value
        
        if is_active is not None:
            conditions.append("is_active = :is_active")
            params["is_active"] = is_active
        
        if vectorization_status:
            conditions.append("vectorization_status = :vectorization_status")
            params["vectorization_status"] = vectorization_status.value
        
        where_clause = " AND ".join(conditions)
        
        query = text(f"""
            SELECT id, resource_id, resource_name, resource_type, description,
                   capabilities, tags, metadata, is_active, status,
                   source_table, source_id, vectorization_status,
                   usage_count, success_rate, avg_response_time,
                   vector_updated_at, created_at, updated_at
            FROM resource_discovery.resource_registry
            WHERE {where_clause}
            ORDER BY created_at DESC
            OFFSET :skip LIMIT :limit
        """)
        
        result = session.execute(query, params)
        resources = []
        
        for row in result.fetchall():
            resource = ResourceRegistryResponse(
                id=row.id,
                resource_id=row.resource_id,
                resource_name=row.resource_name,
                resource_type=row.resource_type,
                description=row.description,
                capabilities=row.capabilities,
                tags=row.tags,
                metadata=row.metadata,
                is_active=row.is_active,
                status=row.status,
                source_table=row.source_table,
                source_id=row.source_id,
                vectorization_status=row.vectorization_status,
                usage_count=row.usage_count,
                success_rate=row.success_rate,
                avg_response_time=row.avg_response_time,
                vector_updated_at=row.vector_updated_at,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            resources.append(resource)
        
        return resources
        
    except Exception as e:
        logger.error(f"获取资源列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取资源列表失败: {str(e)}")


@router.get("/resources/{resource_id}", response_model=ResourceRegistryResponse)
async def get_resource(
    resource_id: str,
    session: Session = Depends(get_db_session)
):
    """获取单个资源详情"""
    try:
        from sqlalchemy import text
        
        query = text("""
            SELECT id, resource_id, resource_name, resource_type, description,
                   capabilities, tags, metadata, is_active, status,
                   source_table, source_id, vectorization_status,
                   usage_count, success_rate, avg_response_time,
                   vector_updated_at, created_at, updated_at
            FROM resource_discovery.resource_registry
            WHERE resource_id = :resource_id
        """)
        
        result = session.execute(query, {"resource_id": resource_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"资源不存在: {resource_id}")
        
        resource = ResourceRegistryResponse(
            id=row.id,
            resource_id=row.resource_id,
            resource_name=row.resource_name,
            resource_type=row.resource_type,
            description=row.description,
            capabilities=row.capabilities,
            tags=row.tags,
            metadata=row.metadata,
            is_active=row.is_active,
            status=row.status,
            source_table=row.source_table,
            source_id=row.source_id,
            vectorization_status=row.vectorization_status,
            usage_count=row.usage_count,
            success_rate=row.success_rate,
            avg_response_time=row.avg_response_time,
            vector_updated_at=row.vector_updated_at,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
        
        return resource
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取资源详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取资源详情失败: {str(e)}")


@router.post("/sync", response_model=dict)
async def sync_resources(
    force_full_sync: bool = Query(False, description="是否强制全量同步"),
    session: Session = Depends(get_db_session)
):
    """同步和向量化资源"""
    try:
        logger.info(f"🔄 开始资源同步: force_full={force_full_sync}")
        
        result = await synchronizer.sync_and_vectorize_incremental(
            session=session,
            force_full_sync=force_full_sync
        )
        
        return result
        
    except Exception as e:
        logger.error(f"资源同步失败: {e}")
        raise HTTPException(status_code=500, detail=f"资源同步失败: {str(e)}")


@router.post("/vectorize", response_model=BatchVectorizationResponse)
async def vectorize_resources(
    request: BatchVectorizationRequest,
    session: Session = Depends(get_db_session)
):
    """批量向量化资源"""
    try:
        start_time = datetime.utcnow()
        
        logger.info(f"🔄 开始批量向量化: {len(request.resource_ids)} 个资源")
        
        # 获取资源信息
        from sqlalchemy import text
        
        resource_ids_str = "', '".join(request.resource_ids)
        query = text(f"""
            SELECT resource_id, resource_name, resource_type, description,
                   capabilities, tags, metadata
            FROM resource_discovery.resource_registry
            WHERE resource_id IN ('{resource_ids_str}')
        """)
        
        result = session.execute(query)
        resources = []
        
        for row in result.fetchall():
            resource = {
                "resource_id": row.resource_id,
                "resource_name": row.resource_name,
                "resource_type": row.resource_type,
                "description": row.description,
                "capabilities": row.capabilities,
                "tags": row.tags,
                "metadata": row.metadata
            }
            resources.append(resource)
        
        # 执行向量化
        vectorized_results = await vectorizer.batch_vectorize_resources(session, resources)
        
        # 统计结果
        successful_count = sum(1 for r in vectorized_results if r.get("vectorization_status") == "completed")
        failed_count = len(vectorized_results) - successful_count
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        response = BatchVectorizationResponse(
            total_resources=len(request.resource_ids),
            successful_resources=successful_count,
            failed_resources=failed_count,
            results=[],  # 简化返回结果
            total_processing_time_ms=processing_time,
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"✅ 批量向量化完成: 成功 {successful_count}, 失败 {failed_count}")
        return response
        
    except Exception as e:
        logger.error(f"批量向量化失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量向量化失败: {str(e)}")


@router.get("/status", response_model=List[SystemStatus])
async def get_system_status(
    operation_type: Optional[OperationType] = Query(None, description="操作类型"),
    status: Optional[SystemStatusType] = Query(None, description="状态"),
    limit: int = Query(10, ge=1, le=100, description="返回数量"),
    session: Session = Depends(get_db_session)
):
    """获取系统状态"""
    try:
        from sqlalchemy import text
        
        conditions = ["1=1"]
        params = {"limit": limit}
        
        if operation_type:
            conditions.append("operation_type = :operation_type")
            params["operation_type"] = operation_type.value
        
        if status:
            conditions.append("status = :status")
            params["status"] = status.value
        
        where_clause = " AND ".join(conditions)
        
        query = text(f"""
            SELECT id, operation_type, status, total_items, successful_items,
                   failed_items, error_message, result_data, started_at,
                   completed_at, duration_seconds, created_at, updated_at
            FROM resource_discovery.system_status
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit
        """)
        
        result = session.execute(query, params)
        statuses = []
        
        for row in result.fetchall():
            status_obj = SystemStatus(
                id=row.id,
                operation_type=row.operation_type,
                status=row.status,
                total_items=row.total_items,
                successful_items=row.successful_items,
                failed_items=row.failed_items,
                error_message=row.error_message,
                result_data=row.result_data,
                started_at=row.started_at,
                completed_at=row.completed_at,
                duration_seconds=row.duration_seconds,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            statuses.append(status_obj)
        
        return statuses
        
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取系统状态失败: {str(e)}")


@router.get("/statistics", response_model=dict)
async def get_statistics(
    session: Session = Depends(get_db_session)
):
    """获取资源发现统计信息"""
    try:
        from sqlalchemy import text
        
        # 资源统计
        resource_stats_query = text("""
            SELECT 
                resource_type,
                COUNT(*) as total_count,
                COUNT(*) FILTER (WHERE is_active = true) as active_count,
                COUNT(*) FILTER (WHERE vectorization_status = 'completed') as vectorized_count
            FROM resource_discovery.resource_registry
            GROUP BY resource_type
        """)
        
        resource_result = session.execute(resource_stats_query)
        resource_stats = {}
        
        for row in resource_result.fetchall():
            resource_stats[row.resource_type] = {
                "total": row.total_count,
                "active": row.active_count,
                "vectorized": row.vectorized_count
            }
        
        # 匹配统计
        match_stats_query = text("""
            SELECT 
                COUNT(*) as total_queries,
                AVG(response_time) as avg_response_time,
                COUNT(*) FILTER (WHERE user_feedback = 'positive') as positive_feedback,
                COUNT(*) FILTER (WHERE user_feedback = 'negative') as negative_feedback
            FROM resource_discovery.resource_match_history
            WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
        """)
        
        match_result = session.execute(match_stats_query)
        match_row = match_result.fetchone()
        
        match_stats = {
            "total_queries": match_row.total_queries or 0,
            "avg_response_time": float(match_row.avg_response_time or 0),
            "positive_feedback": match_row.positive_feedback or 0,
            "negative_feedback": match_row.negative_feedback or 0
        }
        
        return {
            "resource_statistics": resource_stats,
            "match_statistics": match_stats,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")
