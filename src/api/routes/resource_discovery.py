"""
资源发现模块 API 路由

基于 Ti-Flow 的意图识别 API 设计，为 Olight 提供资源发现和匹配接口
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

router = APIRouter(prefix="/api/resource-discovery", tags=["Resource Discovery"])

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


@router.post("/test-match")
async def test_resource_matching(
    request: dict,
    session: Session = Depends(get_db_session)
):
    """
    资源发现测试接口

    类似 Ti-Flow 的意图识别测试功能，用于测试资源匹配效果
    """
    try:
        import time
        start_time = time.time()

        # 解析请求参数
        query = request.get("query", "").strip()
        top_k = request.get("top_k", 5)
        min_confidence = request.get("min_confidence", 0.1)
        resource_types = request.get("resource_types", None)

        if not query:
            raise HTTPException(status_code=400, detail="查询内容不能为空")

        logger.info(f"🧪 资源匹配测试: '{query}', top_k={top_k}, min_confidence={min_confidence}")

        # 执行资源匹配
        matches = await matcher.match_resources(
            session=session,
            user_query=query,
            top_k=top_k,
            min_confidence=min_confidence,
            resource_types=resource_types
        )

        processing_time = time.time() - start_time

        # 格式化匹配结果
        formatted_matches = []
        for match in matches:
            # 计算置信度级别
            confidence_level = "low"
            if match.confidence_score >= 0.8:
                confidence_level = "high"
            elif match.confidence_score >= 0.6:
                confidence_level = "medium"

            formatted_match = {
                "resource_id": match.resource.resource_id,
                "resource_name": match.resource.resource_name,
                "resource_type": match.resource.resource_type,
                "description": match.resource.description or "",
                "capabilities": match.resource.capabilities or [],
                "similarity_score": round(match.similarity_score, 3),
                "confidence_score": round(match.confidence_score, 3),
                "confidence": confidence_level,
                "reasoning": f"基于向量相似度匹配，相似度: {match.similarity_score:.3f}",
                "detailed_scores": {
                    "similarity": round(match.similarity_score, 3),
                    "confidence": round(match.confidence_score, 3)
                }
            }
            formatted_matches.append(formatted_match)

        # 确定最佳匹配
        best_match = formatted_matches[0] if formatted_matches else None

        response_data = {
            "query": query,
            "total_matches": len(formatted_matches),
            "matches": formatted_matches,
            "best_match": best_match,
            "processing_time": round(processing_time, 3),
            "parameters": {
                "top_k": top_k,
                "min_confidence": min_confidence,
                "resource_types": resource_types
            }
        }

        logger.info(f"✅ 资源匹配测试完成: 找到 {len(formatted_matches)} 个匹配结果, 耗时 {processing_time:.3f}s")

        return {
            "success": True,
            "data": response_data
        }

    except Exception as e:
        logger.error(f"❌ 资源匹配测试失败: {e}")
        raise HTTPException(status_code=500, detail=f"资源匹配测试失败: {str(e)}")


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
    force_full_sync: bool = Query(False, description="是否强制全量同步")
):
    """启动异步资源同步任务"""
    try:
        logger.info(f"🔄 启动异步资源同步: force_full={force_full_sync}")

        # 导入任务函数
        from src.tasks.resource_discovery_tasks import sync_resources_task

        # 启动异步任务
        task = sync_resources_task.delay(force_full_sync)

        logger.info(f"✅ 同步任务已启动: {task.id}")

        return {
            "success": True,
            "message": "资源同步任务已启动",
            "task_id": task.id,
            "status": "started",
            "force_full_sync": force_full_sync
        }

    except Exception as e:
        logger.error(f"启动资源同步任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动资源同步任务失败: {str(e)}")


@router.get("/sync/status/{task_id}", response_model=dict)
async def get_sync_task_status(task_id: str):
    """获取同步任务状态和进度"""
    try:
        from src.celery_app import celery_app

        # 获取任务状态
        task = celery_app.AsyncResult(task_id)

        if task.state == 'PENDING':
            response = {
                "success": True,
                "task_id": task_id,
                "status": "pending",
                "message": "任务等待执行中...",
                "progress": 0
            }
        elif task.state == 'PROGRESS':
            response = {
                "success": True,
                "task_id": task_id,
                "status": "running",
                "message": task.info.get('message', '任务执行中...'),
                "progress": task.info.get('progress', 0),
                "current_step": task.info.get('current_step', ''),
                "total_steps": task.info.get('total_steps', 0),
                "processed_items": task.info.get('processed_items', 0),
                "total_items": task.info.get('total_items', 0)
            }
        elif task.state == 'SUCCESS':
            result = task.result
            response = {
                "success": True,
                "task_id": task_id,
                "status": "completed",
                "message": "同步任务完成",
                "progress": 100,
                "result": result
            }
        elif task.state == 'FAILURE':
            response = {
                "success": False,
                "task_id": task_id,
                "status": "failed",
                "message": f"任务执行失败: {str(task.info)}",
                "progress": 0,
                "error": str(task.info)
            }
        else:
            response = {
                "success": True,
                "task_id": task_id,
                "status": task.state.lower(),
                "message": f"任务状态: {task.state}",
                "progress": 0
            }

        return response

    except Exception as e:
        logger.error(f"获取任务状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")


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


@router.get("/change-detection", response_model=dict)
async def detect_resource_changes(
    preview_only: bool = Query(True, description="是否仅预览变更"),
    session: Session = Depends(get_db_session)
):
    """检测资源变更"""
    try:
        logger.info(f"🔍 开始检测资源变更 (预览模式: {preview_only})")

        # 使用资源发现服务检测变更
        changes = await discovery_service.detect_resource_changes(session, preview_only)

        # 统计变更
        added_count = len(changes.get('added', []))
        modified_count = len(changes.get('modified', []))
        deleted_count = len(changes.get('deleted', []))
        total_changes = added_count + modified_count + deleted_count

        response = {
            "success": True,
            "preview_only": preview_only,
            "total_changes": total_changes,
            "change_summary": {
                "added_count": added_count,
                "modified_count": modified_count,
                "deleted_count": deleted_count
            },
            "changes": changes,
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"✅ 变更检测完成: 新增{added_count}, 修改{modified_count}, 删除{deleted_count}")
        return response

    except Exception as e:
        logger.error(f"❌ 检测资源变更失败: {e}")
        raise HTTPException(status_code=500, detail=f"检测资源变更失败: {str(e)}")


@router.post("/discover", response_model=dict)
async def discover_resources_manual():
    """手动发现系统资源"""
    try:
        logger.info("🔍 手动发现系统资源")

        # 获取数据库会话
        session = next(get_db_session())

        try:
            # 初始化发现服务
            discovery_service = ResourceDiscoveryService()

            # 发现所有资源
            discovered_resources = await discovery_service.discover_all_resources(session)

            # 获取已注册的资源
            existing_query = text("""
                SELECT resource_id, resource_name, resource_type, vectorization_status,
                       created_at, updated_at
                FROM resource_discovery.resource_registry
                WHERE is_active = true
            """)

            result = session.execute(existing_query)
            existing_resources = [dict(row._mapping) for row in result.fetchall()]

            # 分析资源状态
            existing_ids = {r['resource_id'] for r in existing_resources}
            discovered_ids = {r['resource_id'] for r in discovered_resources}

            new_resources = [r for r in discovered_resources if r['resource_id'] not in existing_ids]
            missing_resources = [r for r in existing_resources if r['resource_id'] not in discovered_ids]
            existing_discovered = [r for r in discovered_resources if r['resource_id'] in existing_ids]

            # 统计向量化状态
            vectorization_stats = {}
            for status in ['pending', 'in_progress', 'completed', 'failed']:
                count = len([r for r in existing_resources if r.get('vectorization_status') == status])
                vectorization_stats[status] = count

            return {
                "success": True,
                "message": f"发现了 {len(discovered_resources)} 个资源",
                "discovery_summary": {
                    "total_discovered": len(discovered_resources),
                    "new_resources": len(new_resources),
                    "existing_resources": len(existing_discovered),
                    "missing_resources": len(missing_resources),
                    "vectorization_stats": vectorization_stats
                },
                "resources": {
                    "new": new_resources[:10],  # 限制返回数量
                    "existing": existing_discovered[:10],
                    "missing": missing_resources[:10]
                },
                "timestamp": datetime.utcnow().isoformat()
            }

        finally:
            session.close()

    except Exception as e:
        logger.error(f"手动资源发现失败: {e}")
        raise HTTPException(status_code=500, detail=f"手动资源发现失败: {str(e)}")


@router.post("/incremental-sync", response_model=dict)
async def incremental_sync(
    force_full_sync: bool = Query(False, description="是否强制全量同步"),
    async_mode: bool = Query(True, description="是否异步执行")
):
    """增量同步资源"""
    try:
        logger.info(f"🔄 启动增量同步: force_full={force_full_sync}, async={async_mode}")

        if async_mode:
            # 异步模式：启动后台任务
            from src.tasks.resource_discovery_tasks import incremental_sync_task
            task = incremental_sync_task.delay(force_full_sync)

            return {
                "success": True,
                "message": "增量同步任务已启动",
                "task_id": task.id,
                "status": "started",
                "force_full_sync": force_full_sync,
                "async_mode": True
            }
        else:
            # 同步模式：直接执行
            start_time = datetime.utcnow()

            # 执行增量同步
            result = await synchronizer.incremental_sync(force_full_sync)

            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return {
                "success": True,
                "message": "增量同步完成",
                "result": result,
                "processing_time_ms": processing_time,
                "force_full_sync": force_full_sync,
                "async_mode": False,
                "timestamp": datetime.utcnow().isoformat()
            }

    except Exception as e:
        logger.error(f"❌ 增量同步失败: {e}")
        raise HTTPException(status_code=500, detail=f"增量同步失败: {str(e)}")


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


@router.get("/health", response_model=dict)
async def health_check():
    """健康检查接口"""
    try:
        from src.config.resource_discovery import get_resource_discovery_config
        from src.services.resource_discovery.config_validator import ConfigValidator
        from src.services.resource_discovery.trigger_manager import TriggerManager

        config = get_resource_discovery_config()

        # 检查配置
        validator = ConfigValidator(config)
        validation_results = await validator.validate_all()

        # 检查触发器状态
        trigger_manager = TriggerManager(config)
        trigger_status = await trigger_manager.get_trigger_status()

        # 检查数据库连接
        session = next(get_db_session())
        try:
            from sqlalchemy import text
            session.execute(text("SELECT 1"))
            db_healthy = True
        except Exception:
            db_healthy = False
        finally:
            session.close()

        overall_healthy = (
            validation_results.get("overall_valid", False) and
            db_healthy and
            (not config.enable_triggers or trigger_status.get("total_existing", 0) > 0)
        )

        return {
            "success": True,
            "healthy": overall_healthy,
            "components": {
                "configuration": validation_results.get("overall_valid", False),
                "database": db_healthy,
                "triggers": trigger_status.get("total_existing", 0) > 0 if config.enable_triggers else True,
                "resources": len(config.get_enabled_resources())
            },
            "message": "健康检查完成"
        }

    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "success": False,
            "healthy": False,
            "error": str(e),
            "message": "健康检查失败"
        }
