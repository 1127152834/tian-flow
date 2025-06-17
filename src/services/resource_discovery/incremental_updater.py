# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
增量更新器

基于触发器的实时增量向量化更新
"""

import logging
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.config.resource_discovery import ResourceDiscoveryConfig
from src.database import get_db_session
from src.services.resource_discovery.resource_vectorizer import ResourceVectorizer

logger = logging.getLogger(__name__)


class IncrementalUpdater:
    """增量更新器 - 处理实时数据变更的向量化更新"""
    
    def __init__(self, config: Optional[ResourceDiscoveryConfig] = None):
        from src.config.resource_discovery import get_resource_discovery_config
        
        self.config = config or get_resource_discovery_config()
        self.vectorizer = ResourceVectorizer(self.config)
        self.batch_size = self.config.vector_config.batch_size
        self.batch_delay_ms = self.config.trigger_config.batch_delay_ms
        
        # 批处理队列
        self.pending_updates: List[Dict[str, Any]] = []
        self.processing = False
        
        logger.info(f"初始化增量更新器:")
        logger.info(f"  批处理大小: {self.batch_size}")
        logger.info(f"  批处理延迟: {self.batch_delay_ms}ms")
    
    async def handle_trigger_notification(self, payload: str) -> Dict[str, Any]:
        """处理触发器通知"""
        try:
            # 解析通知载荷
            notification_data = json.loads(payload)
            
            table_name = notification_data.get("table_name")
            operation = notification_data.get("operation")
            record_data = notification_data.get("record_data", {})
            fields = notification_data.get("fields", {})
            
            logger.info(f"收到触发器通知: {table_name} - {operation}")
            
            # 检查是否是配置的表
            resource_config = self.config.get_resource_by_table(table_name)
            if not resource_config:
                logger.debug(f"表 {table_name} 不在配置中，跳过处理")
                return {"success": True, "action": "skipped", "reason": "not_configured"}
            
            # 根据操作类型处理
            if operation == "DELETE":
                return await self._handle_delete(table_name, record_data)
            elif operation in ["INSERT", "UPDATE"]:
                return await self._handle_insert_or_update(table_name, record_data, operation)
            else:
                logger.warning(f"未知操作类型: {operation}")
                return {"success": False, "error": f"未知操作类型: {operation}"}
                
        except Exception as e:
            logger.error(f"处理触发器通知失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_delete(self, table_name: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理删除操作"""
        try:
            resource_id = f"{table_name}_{record_data.get('id', 'unknown')}"
            
            session = next(get_db_session())
            try:
                # 删除对应的向量
                delete_query = text("""
                    DELETE FROM resource_discovery.resource_vectors 
                    WHERE resource_id = :resource_id
                """)
                result = session.execute(delete_query, {"resource_id": resource_id})
                deleted_count = result.rowcount
                
                # 删除资源注册表记录
                delete_registry_query = text("""
                    DELETE FROM resource_discovery.resource_registry 
                    WHERE resource_id = :resource_id
                """)
                session.execute(delete_registry_query, {"resource_id": resource_id})
                
                session.commit()
                
                logger.info(f"删除向量成功: {resource_id} (删除 {deleted_count} 个向量)")
                return {
                    "success": True,
                    "action": "deleted",
                    "resource_id": resource_id,
                    "deleted_vectors": deleted_count
                }
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"处理删除操作失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_insert_or_update(
        self, 
        table_name: str, 
        record_data: Dict[str, Any], 
        operation: str
    ) -> Dict[str, Any]:
        """处理插入或更新操作"""
        try:
            session = next(get_db_session())
            try:
                # 使用配置驱动的向量化
                result = await self.vectorizer.vectorize_resource_from_config(
                    session, table_name, record_data
                )
                
                if result.get("success"):
                    # 更新或创建资源注册表记录
                    await self._upsert_resource_registry(session, result, operation)
                    
                    logger.info(f"{operation} 向量化成功: {result.get('resource_id')}")
                    return {
                        "success": True,
                        "action": f"vectorized_{operation.lower()}",
                        "resource_id": result.get("resource_id"),
                        "tool": result.get("tool")
                    }
                else:
                    logger.warning(f"{operation} 向量化失败: {result.get('error')}")
                    return result
                    
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"处理 {operation} 操作失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _upsert_resource_registry(
        self, 
        session: Session, 
        vectorization_result: Dict[str, Any], 
        operation: str
    ):
        """更新或插入资源注册表记录"""
        try:
            resource_id = vectorization_result.get("resource_id")
            table_name = vectorization_result.get("table_name")
            tool = vectorization_result.get("tool")
            
            # 检查记录是否存在
            check_query = text("""
                SELECT id FROM resource_discovery.resource_registry 
                WHERE resource_id = :resource_id
            """)
            existing = session.execute(check_query, {"resource_id": resource_id}).fetchone()
            
            if existing:
                # 更新现有记录
                update_query = text("""
                    UPDATE resource_discovery.resource_registry 
                    SET vectorization_status = 'completed',
                        vector_updated_at = :updated_at,
                        updated_at = :updated_at
                    WHERE resource_id = :resource_id
                """)
                session.execute(update_query, {
                    "resource_id": resource_id,
                    "updated_at": datetime.now()
                })
            else:
                # 插入新记录
                insert_query = text("""
                    INSERT INTO resource_discovery.resource_registry 
                    (resource_id, resource_name, resource_type, description, 
                     source_table, source_id, vectorization_status, 
                     vector_updated_at, created_at, updated_at, is_active)
                    VALUES (:resource_id, :resource_name, :resource_type, :description,
                            :source_table, :source_id, 'completed',
                            :updated_at, :updated_at, :updated_at, true)
                """)
                
                # 从表名推断资源类型
                resource_type = self._infer_resource_type(table_name)
                
                session.execute(insert_query, {
                    "resource_id": resource_id,
                    "resource_name": f"{table_name} 资源",
                    "resource_type": resource_type,
                    "description": f"来自 {table_name} 的资源，工具: {tool}",
                    "source_table": table_name,
                    "source_id": resource_id.split('_')[-1],
                    "updated_at": datetime.now()
                })
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            logger.error(f"更新资源注册表失败: {e}")
            raise
    
    def _infer_resource_type(self, table_name: str) -> str:
        """从表名推断资源类型"""
        if "api" in table_name.lower():
            return "API"
        elif "text2sql" in table_name.lower() or "vanna" in table_name.lower():
            return "TEXT2SQL"
        elif "database" in table_name.lower() or "datasource" in table_name.lower():
            return "DATABASE"
        else:
            return "TOOL"
    
    async def batch_process_updates(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量处理更新"""
        if not updates:
            return {"success": True, "processed": 0}
        
        logger.info(f"开始批量处理 {len(updates)} 个更新")
        
        results = {
            "success": True,
            "processed": 0,
            "failed": 0,
            "details": []
        }
        
        for update in updates:
            try:
                result = await self.handle_trigger_notification(update.get("payload", ""))
                if result.get("success"):
                    results["processed"] += 1
                else:
                    results["failed"] += 1
                results["details"].append(result)
                
            except Exception as e:
                results["failed"] += 1
                results["details"].append({"success": False, "error": str(e)})
        
        if results["failed"] > 0:
            results["success"] = False
        
        logger.info(f"批量处理完成: 成功 {results['processed']}, 失败 {results['failed']}")
        return results
    
    async def start_listening(self):
        """开始监听数据库通知（示例实现）"""
        logger.info("开始监听数据库通知...")
        
        # 这里应该实现实际的PostgreSQL LISTEN逻辑
        # 由于复杂性，这里只提供框架
        
        try:
            # 示例：监听所有配置的通知通道
            channels = []
            for resource in self.config.get_enabled_resources():
                channel = f"{self.config.trigger_config.notify_channel_prefix}{resource.table.replace('.', '_')}"
                channels.append(channel)
            
            logger.info(f"监听通道: {channels}")
            
            # 实际的监听逻辑应该在这里实现
            # 可以使用 asyncpg 或其他异步PostgreSQL库
            
        except Exception as e:
            logger.error(f"启动监听失败: {e}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """获取增量更新器状态"""
        return {
            "config_enabled": self.config.enable_triggers,
            "batch_size": self.batch_size,
            "batch_delay_ms": self.batch_delay_ms,
            "pending_updates": len(self.pending_updates),
            "processing": self.processing,
            "configured_resources": len(self.config.get_enabled_resources())
        }
