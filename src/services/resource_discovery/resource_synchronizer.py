"""
资源同步器

基于 Ti-Flow 的 IncrementalVectorizer 设计，实现智能资源同步和增量更新
"""

import logging
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.models.resource_discovery import (
    ResourceRegistry,
    ResourceRegistryCreate,
    VectorizationStatus,
    SystemStatus,
    SystemStatusCreate,
    OperationType,
    SystemStatusType
)
from .resource_discovery_service import ResourceDiscoveryService
from .resource_vectorizer import ResourceVectorizer

logger = logging.getLogger(__name__)


class ResourceSynchronizer:
    """资源同步器 - 智能资源同步和增量更新"""

    def __init__(self, embedding_service=None):
        """
        初始化同步器

        Args:
            embedding_service: 嵌入服务（已弃用，使用统一的嵌入服务）
        """
        self.discovery_service = ResourceDiscoveryService()
        self.vectorizer = ResourceVectorizer()
        
        # 影响向量化的字段
        self.vectorization_fields = {
            'resource_name', 'description', 'capabilities', 'tags', 'metadata'
        }
        
        logger.info("初始化资源同步器")
    
    async def sync_and_vectorize_incremental(
        self, 
        session: Session,
        force_full_sync: bool = False
    ) -> Dict[str, Any]:
        """执行增量同步和向量化"""
        start_time = datetime.utcnow()
        operation_id = await self._create_operation_status(
            session, OperationType.SYNC, SystemStatusType.RUNNING
        )
        
        logger.info(f"🚀 开始增量同步: force_full={force_full_sync}")
        
        try:
            if force_full_sync:
                # 强制全量同步
                return await self._execute_full_sync(session, operation_id, start_time)
            else:
                # 智能增量同步
                return await self._execute_incremental_sync(session, operation_id, start_time)
                
        except Exception as e:
            logger.error(f"❌ 增量同步失败: {e}")
            await self._update_operation_status(
                session, operation_id, SystemStatusType.FAILED, error_message=str(e)
            )
            return {
                "success": False,
                "message": f"增量同步失败: {str(e)}",
                "total_processing_time": str(datetime.utcnow() - start_time)
            }

    async def incremental_sync(self, force_full_sync: bool = False) -> Dict[str, Any]:
        """增量同步资源 (API 适配方法)"""
        from src.database import get_db_session

        session = next(get_db_session())
        try:
            return await self.sync_and_vectorize_incremental(session, force_full_sync)
        finally:
            session.close()

    async def _execute_incremental_sync(
        self, 
        session: Session,
        operation_id: int,
        start_time: datetime
    ) -> Dict[str, Any]:
        """执行智能增量同步"""
        logger.info("🔄 执行智能增量同步...")
        
        # 1. 检测资源变更
        changes = await self._detect_resource_changes(session)
        
        # 2. 处理资源变更
        logger.info(f"🔄 处理 {len(changes)} 个资源变更...")
        result = await self._process_resource_changes(session, changes)
        
        # 3. 更新操作状态
        processing_time = datetime.utcnow() - start_time
        await self._update_operation_status(
            session, operation_id, SystemStatusType.COMPLETED,
            total_items=len(changes),
            successful_items=result["successful_changes"],
            failed_items=result["failed_changes"],
            duration_seconds=int(processing_time.total_seconds()),
            result_data=result
        )
        
        return {
            "success": True,
            "message": f"增量同步完成，处理了 {len(changes)} 个变更",
            "processed_changes": result["change_summary"],
            "total_processing_time": str(processing_time),
            "performance_improvement": self._calculate_performance_improvement(
                len(changes), result["total_resources"]
            ),
            "detailed_results": result
        }
    
    async def _execute_full_sync(
        self, 
        session: Session,
        operation_id: int,
        start_time: datetime
    ) -> Dict[str, Any]:
        """执行强制全量同步"""
        logger.info("🔄 执行强制全量同步...")
        
        # 1. 清理现有数据
        await self._cleanup_existing_data(session)
        
        # 2. 重新发现所有资源
        resources = await self.discovery_service.discover_all_resources(session)
        
        # 3. 注册所有资源
        registered_count = 0
        for resource in resources:
            if await self._register_resource_to_db(session, resource):
                registered_count += 1
        
        # 4. 向量化所有资源
        vectorized_resources = await self.vectorizer.batch_vectorize_resources(session, resources)
        vectorized_count = sum(1 for r in vectorized_resources if r.get("vectorization_status") == "completed")
        
        # 5. 更新操作状态
        processing_time = datetime.utcnow() - start_time
        await self._update_operation_status(
            session, operation_id, SystemStatusType.COMPLETED,
            total_items=len(resources),
            successful_items=vectorized_count,
            failed_items=len(resources) - vectorized_count,
            duration_seconds=int(processing_time.total_seconds()),
            result_data={
                "total_discovered": len(resources),
                "total_registered": registered_count,
                "total_vectorized": vectorized_count
            }
        )
        
        return {
            "success": True,
            "message": f"全量同步完成，处理了 {len(resources)} 个资源",
            "total_discovered": len(resources),
            "total_registered": registered_count,
            "total_vectorized": vectorized_count,
            "total_processing_time": str(processing_time)
        }
    
    async def _detect_resource_changes(self, session: Session) -> List[Dict[str, Any]]:
        """检测资源变更"""
        changes = []
        
        try:
            # 1. 发现当前所有资源
            current_resources = await self.discovery_service.discover_all_resources(session)
            
            # 2. 获取已注册的资源
            registered_resources = await self._get_registered_resources(session)
            
            # 3. 比较变更
            current_resource_map = {r["resource_id"]: r for r in current_resources}
            registered_resource_map = {r["resource_id"]: r for r in registered_resources}
            
            # 检测新增资源
            for resource_id, resource in current_resource_map.items():
                if resource_id not in registered_resource_map:
                    changes.append({
                        "change_type": "added",
                        "resource_id": resource_id,
                        "resource": resource
                    })
            
            # 检测修改资源
            for resource_id, current_resource in current_resource_map.items():
                if resource_id in registered_resource_map:
                    registered_resource = registered_resource_map[resource_id]
                    if self._has_resource_changed(current_resource, registered_resource):
                        changes.append({
                            "change_type": "modified",
                            "resource_id": resource_id,
                            "resource": current_resource,
                            "old_resource": registered_resource
                        })
            
            # 检测删除资源
            for resource_id, registered_resource in registered_resource_map.items():
                if resource_id not in current_resource_map:
                    changes.append({
                        "change_type": "deleted",
                        "resource_id": resource_id,
                        "resource": registered_resource
                    })
            
            logger.info(f"检测到 {len(changes)} 个资源变更")
            return changes
            
        except Exception as e:
            logger.error(f"检测资源变更失败: {e}")
            return []
    
    async def _get_registered_resources(self, session: Session) -> List[Dict[str, Any]]:
        """获取已注册的资源"""
        try:
            query = text("""
                SELECT resource_id, resource_name, resource_type, description, 
                       capabilities, tags, metadata, is_active, status,
                       source_table, source_id, vectorization_status,
                       usage_count, success_rate, avg_response_time,
                       created_at, updated_at
                FROM resource_discovery.resource_registry
                ORDER BY resource_id
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
                    "metadata": row.metadata,
                    "is_active": row.is_active,
                    "status": row.status,
                    "source_table": row.source_table,
                    "source_id": row.source_id,
                    "vectorization_status": row.vectorization_status,
                    "usage_count": row.usage_count,
                    "success_rate": row.success_rate,
                    "avg_response_time": row.avg_response_time,
                    "created_at": row.created_at,
                    "updated_at": row.updated_at
                }
                resources.append(resource)
            
            return resources
            
        except Exception as e:
            logger.error(f"获取已注册资源失败: {e}")
            return []
    
    def _has_resource_changed(self, current: Dict[str, Any], registered: Dict[str, Any]) -> bool:
        """检查资源是否发生变更"""
        try:
            # 检查影响向量化的字段
            for field in self.vectorization_fields:
                current_value = current.get(field)
                registered_value = registered.get(field)
                
                # 对于 JSON 字段，需要特殊处理
                if field in ['capabilities', 'tags', 'metadata']:
                    current_hash = self._get_json_hash(current_value)
                    registered_hash = self._get_json_hash(registered_value)
                    if current_hash != registered_hash:
                        return True
                else:
                    if current_value != registered_value:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"检查资源变更失败: {e}")
            return True  # 出错时认为有变更，确保安全
    
    def _get_json_hash(self, data: Any) -> str:
        """获取 JSON 数据的哈希值"""
        try:
            if data is None:
                return ""
            json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
            return hashlib.md5(json_str.encode()).hexdigest()
        except Exception:
            return str(hash(str(data)))
    
    async def _process_resource_changes(
        self, 
        session: Session, 
        changes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """处理资源变更"""
        successful_changes = 0
        failed_changes = 0
        change_summary = {"added": 0, "modified": 0, "deleted": 0}
        
        for change in changes:
            try:
                change_type = change["change_type"]
                resource_id = change["resource_id"]
                
                if change_type == "added":
                    # 新增资源
                    if await self._register_resource_to_db(session, change["resource"]):
                        await self.vectorizer.vectorize_resource(session, change["resource"])
                        successful_changes += 1
                        change_summary["added"] += 1
                    else:
                        failed_changes += 1
                
                elif change_type == "modified":
                    # 修改资源
                    if await self._update_resource_in_db(session, change["resource"]):
                        await self.vectorizer.vectorize_resource(session, change["resource"])
                        successful_changes += 1
                        change_summary["modified"] += 1
                    else:
                        failed_changes += 1
                
                elif change_type == "deleted":
                    # 删除资源
                    if await self._delete_resource_from_db(session, resource_id):
                        successful_changes += 1
                        change_summary["deleted"] += 1
                    else:
                        failed_changes += 1
                
            except Exception as e:
                logger.error(f"处理变更失败 {change.get('resource_id')}: {e}")
                failed_changes += 1
        
        return {
            "successful_changes": successful_changes,
            "failed_changes": failed_changes,
            "change_summary": change_summary,
            "total_resources": len(changes)
        }
    
    async def _register_resource_to_db(self, session: Session, resource: Dict[str, Any]) -> bool:
        """注册资源到数据库"""
        try:
            import json
            insert_query = text("""
                INSERT INTO resource_discovery.resource_registry
                (resource_id, resource_name, resource_type, description, capabilities,
                 tags, metadata, is_active, status, source_table, source_id, vectorization_status)
                VALUES (:resource_id, :resource_name, :resource_type, :description, :capabilities,
                        :tags, :metadata, :is_active, :status, :source_table, :source_id, :vectorization_status)
                ON CONFLICT (resource_id) DO NOTHING
            """)

            session.execute(insert_query, {
                "resource_id": resource["resource_id"],
                "resource_name": resource["resource_name"],
                "resource_type": resource["resource_type"],
                "description": resource.get("description"),
                "capabilities": json.dumps(resource.get("capabilities")) if resource.get("capabilities") else None,
                "tags": json.dumps(resource.get("tags")) if resource.get("tags") else None,
                "metadata": json.dumps(resource.get("metadata")) if resource.get("metadata") else None,
                "is_active": resource.get("is_active", True),
                "status": resource.get("status", "active"),
                "source_table": resource.get("source_table"),
                "source_id": resource.get("source_id"),
                "vectorization_status": VectorizationStatus.PENDING.value
            })
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"注册资源失败: {e}")
            return False
    
    async def _update_resource_in_db(self, session: Session, resource: Dict[str, Any]) -> bool:
        """更新数据库中的资源"""
        try:
            import json
            update_query = text("""
                UPDATE resource_discovery.resource_registry
                SET resource_name = :resource_name, description = :description,
                    capabilities = :capabilities, tags = :tags, metadata = :metadata,
                    is_active = :is_active, status = :status,
                    vectorization_status = :vectorization_status,
                    updated_at = CURRENT_TIMESTAMP
                WHERE resource_id = :resource_id
            """)

            session.execute(update_query, {
                "resource_id": resource["resource_id"],
                "resource_name": resource["resource_name"],
                "description": resource.get("description"),
                "capabilities": json.dumps(resource.get("capabilities")) if resource.get("capabilities") else None,
                "tags": json.dumps(resource.get("tags")) if resource.get("tags") else None,
                "metadata": json.dumps(resource.get("metadata")) if resource.get("metadata") else None,
                "is_active": resource.get("is_active", True),
                "status": resource.get("status", "active"),
                "vectorization_status": VectorizationStatus.PENDING.value
            })
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"更新资源失败: {e}")
            return False
    
    async def _delete_resource_from_db(self, session: Session, resource_id: str) -> bool:
        """从数据库中删除资源"""
        try:
            delete_query = text("""
                DELETE FROM resource_discovery.resource_registry 
                WHERE resource_id = :resource_id
            """)
            
            session.execute(delete_query, {"resource_id": resource_id})
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"删除资源失败: {e}")
            return False
    
    async def _cleanup_existing_data(self, session: Session):
        """清理现有数据"""
        try:
            # 删除所有向量数据
            session.execute(text("DELETE FROM resource_discovery.resource_vectors"))
            # 删除所有资源注册数据
            session.execute(text("DELETE FROM resource_discovery.resource_registry"))
            session.commit()
            logger.info("清理现有数据完成")
        except Exception as e:
            session.rollback()
            logger.error(f"清理数据失败: {e}")
    
    def _calculate_performance_improvement(self, processed_count: int, total_count: int) -> str:
        """计算性能提升"""
        if total_count == 0:
            return "N/A"
        
        improvement = (1 - processed_count / total_count) * 100
        return f"{improvement:.1f}% (处理 {processed_count}/{total_count} 个资源)"
    
    async def _create_operation_status(
        self, 
        session: Session, 
        operation_type: OperationType, 
        status: SystemStatusType
    ) -> int:
        """创建操作状态记录"""
        try:
            insert_query = text("""
                INSERT INTO resource_discovery.system_status 
                (operation_type, status, started_at)
                VALUES (:operation_type, :status, :started_at)
                RETURNING id
            """)
            
            result = session.execute(insert_query, {
                "operation_type": operation_type.value,
                "status": status.value,
                "started_at": datetime.utcnow()
            })
            session.commit()
            
            return result.fetchone()[0]
            
        except Exception as e:
            session.rollback()
            logger.error(f"创建操作状态失败: {e}")
            return 0
    
    async def _update_operation_status(
        self, 
        session: Session, 
        operation_id: int, 
        status: SystemStatusType,
        total_items: int = 0,
        successful_items: int = 0,
        failed_items: int = 0,
        duration_seconds: int = 0,
        error_message: Optional[str] = None,
        result_data: Optional[Dict[str, Any]] = None
    ):
        """更新操作状态"""
        try:
            update_query = text("""
                UPDATE resource_discovery.system_status 
                SET status = :status, total_items = :total_items,
                    successful_items = :successful_items, failed_items = :failed_items,
                    duration_seconds = :duration_seconds, error_message = :error_message,
                    result_data = :result_data, completed_at = :completed_at,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :operation_id
            """)
            
            import json
            session.execute(update_query, {
                "operation_id": operation_id,
                "status": status.value,
                "total_items": total_items,
                "successful_items": successful_items,
                "failed_items": failed_items,
                "duration_seconds": duration_seconds,
                "error_message": error_message,
                "result_data": json.dumps(result_data) if result_data else None,
                "completed_at": datetime.utcnow() if status in [SystemStatusType.COMPLETED, SystemStatusType.FAILED] else None
            })
            session.commit()
            
        except Exception as e:
            session.rollback()
            logger.error(f"更新操作状态失败: {e}")
