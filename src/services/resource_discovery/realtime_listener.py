"""
实时更新监听器

监听数据库变更通知，自动触发资源同步和向量化
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
import psycopg2
import psycopg2.extensions
from sqlalchemy.orm import Session

from src.config.database import get_database_config
from .resource_synchronizer import ResourceSynchronizer

logger = logging.getLogger(__name__)


class RealtimeListener:
    """实时更新监听器"""
    
    def __init__(self, embedding_service=None):
        """
        初始化监听器
        
        Args:
            embedding_service: 嵌入服务
        """
        self.synchronizer = ResourceSynchronizer(embedding_service)
        self.connection = None
        self.is_listening = False
        self.processed_notifications = set()  # 防止重复处理
        
        # 配置
        self.batch_delay = 5.0  # 批处理延迟（秒）
        self.max_batch_size = 10  # 最大批处理大小
        self.pending_changes = []  # 待处理的变更
        
        logger.info("初始化实时更新监听器")
    
    async def start_listening(self):
        """开始监听数据库通知"""
        try:
            logger.info("🔊 开始监听数据库变更通知...")
            
            # 建立数据库连接
            await self._connect_to_database()
            
            # 订阅通知频道
            await self._subscribe_to_notifications()
            
            # 设置监听状态
            self.is_listening = True
            
            # 启动监听循环
            await self._listen_loop()
            
        except Exception as e:
            logger.error(f"❌ 启动监听器失败: {e}")
            await self.stop_listening()
    
    async def stop_listening(self):
        """停止监听"""
        try:
            logger.info("🔇 停止监听数据库变更通知...")
            
            self.is_listening = False
            
            if self.connection:
                self.connection.close()
                self.connection = None
            
            logger.info("✅ 监听器已停止")
            
        except Exception as e:
            logger.error(f"❌ 停止监听器失败: {e}")
    
    async def _connect_to_database(self):
        """连接到数据库"""
        try:
            db_config = get_database_config()
            
            # 创建异步连接
            self.connection = psycopg2.connect(
                host=db_config["host"],
                port=db_config["port"],
                database=db_config["database"],
                user=db_config["user"],
                password=db_config["password"]
            )
            
            # 设置为异步模式
            self.connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            
            logger.info("✅ 数据库连接建立成功")
            
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            raise
    
    async def _subscribe_to_notifications(self):
        """订阅通知频道"""
        try:
            cursor = self.connection.cursor()
            
            # 订阅资源变更通知
            cursor.execute("LISTEN resource_change;")
            
            logger.info("✅ 已订阅资源变更通知频道")
            
        except Exception as e:
            logger.error(f"❌ 订阅通知频道失败: {e}")
            raise
    
    async def _listen_loop(self):
        """监听循环"""
        logger.info("🔄 开始监听循环...")
        
        while self.is_listening:
            try:
                # 检查是否有通知
                self.connection.poll()
                
                # 处理所有待处理的通知
                while self.connection.notifies:
                    notification = self.connection.notifies.pop(0)
                    await self._handle_notification(notification)
                
                # 处理批量变更
                await self._process_pending_changes()
                
                # 短暂休眠
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ 监听循环错误: {e}")
                await asyncio.sleep(1.0)  # 错误时等待更长时间
    
    async def _handle_notification(self, notification):
        """处理单个通知"""
        try:
            # 解析通知数据
            payload = json.loads(notification.payload)
            
            operation = payload.get("operation")
            table_name = payload.get("table_name")
            schema_name = payload.get("schema_name")
            record_id = payload.get("record_id")
            timestamp = payload.get("timestamp")
            
            logger.info(f"📨 收到通知: {operation} {schema_name}.{table_name} (ID: {record_id})")
            
            # 生成通知ID防止重复处理
            notification_id = f"{operation}_{schema_name}_{table_name}_{record_id}_{timestamp}"
            
            if notification_id in self.processed_notifications:
                logger.debug(f"跳过重复通知: {notification_id}")
                return
            
            # 记录已处理的通知
            self.processed_notifications.add(notification_id)
            
            # 清理旧的通知记录（保留最近1000个）
            if len(self.processed_notifications) > 1000:
                # 移除最旧的500个
                old_notifications = list(self.processed_notifications)[:500]
                for old_id in old_notifications:
                    self.processed_notifications.discard(old_id)
            
            # 添加到待处理变更
            change_info = {
                "operation": operation,
                "table_name": table_name,
                "schema_name": schema_name,
                "record_id": record_id,
                "timestamp": timestamp,
                "received_at": datetime.utcnow()
            }
            
            self.pending_changes.append(change_info)
            
            logger.debug(f"添加待处理变更: {change_info}")
            
        except Exception as e:
            logger.error(f"❌ 处理通知失败: {e}")
    
    async def _process_pending_changes(self):
        """处理待处理的变更"""
        if not self.pending_changes:
            return
        
        # 检查是否达到批处理条件
        should_process = (
            len(self.pending_changes) >= self.max_batch_size or
            (self.pending_changes and 
             (datetime.utcnow() - self.pending_changes[0]["received_at"]).total_seconds() >= self.batch_delay)
        )
        
        if not should_process:
            return
        
        try:
            # 获取当前批次的变更
            current_batch = self.pending_changes.copy()
            self.pending_changes.clear()
            
            logger.info(f"🔄 处理 {len(current_batch)} 个变更...")
            
            # 按表分组变更
            changes_by_table = {}
            for change in current_batch:
                table_key = f"{change['schema_name']}.{change['table_name']}"
                if table_key not in changes_by_table:
                    changes_by_table[table_key] = []
                changes_by_table[table_key].append(change)
            
            # 处理每个表的变更
            for table_key, table_changes in changes_by_table.items():
                await self._process_table_changes(table_key, table_changes)
            
            logger.info(f"✅ 批量变更处理完成")
            
        except Exception as e:
            logger.error(f"❌ 处理待处理变更失败: {e}")
    
    async def _process_table_changes(self, table_key: str, changes: list):
        """处理特定表的变更"""
        try:
            logger.info(f"🔄 处理表 {table_key} 的 {len(changes)} 个变更...")
            
            # 根据表类型决定处理策略
            if "database_datasources" in table_key:
                await self._handle_database_changes(changes)
            elif "api_definitions" in table_key:
                await self._handle_api_changes(changes)
            elif "vanna_embeddings" in table_key:
                await self._handle_text2sql_changes(changes)
            else:
                logger.warning(f"未知的表类型: {table_key}")
            
        except Exception as e:
            logger.error(f"❌ 处理表变更失败 {table_key}: {e}")
    
    async def _handle_database_changes(self, changes: list):
        """处理数据库数据源变更"""
        try:
            logger.info(f"🗄️ 处理数据库数据源变更: {len(changes)} 个")
            
            # 触发增量同步
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            
            db_config = get_database_config()
            engine = create_engine(
                f"postgresql://{db_config['user']}:{db_config['password']}@"
                f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
            )
            SessionLocal = sessionmaker(bind=engine)
            session = SessionLocal()
            
            try:
                result = await self.synchronizer.sync_and_vectorize_incremental(
                    session=session,
                    force_full_sync=False
                )
                
                if result.get("success"):
                    logger.info(f"✅ 数据库资源同步完成")
                else:
                    logger.error(f"❌ 数据库资源同步失败: {result.get('message')}")
                    
            finally:
                session.close()
            
        except Exception as e:
            logger.error(f"❌ 处理数据库变更失败: {e}")
    
    async def _handle_api_changes(self, changes: list):
        """处理 API 定义变更"""
        try:
            logger.info(f"🌐 处理 API 定义变更: {len(changes)} 个")
            
            # 触发增量同步
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            
            db_config = get_database_config()
            engine = create_engine(
                f"postgresql://{db_config['user']}:{db_config['password']}@"
                f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
            )
            SessionLocal = sessionmaker(bind=engine)
            session = SessionLocal()
            
            try:
                result = await self.synchronizer.sync_and_vectorize_incremental(
                    session=session,
                    force_full_sync=False
                )
                
                if result.get("success"):
                    logger.info(f"✅ API 资源同步完成")
                else:
                    logger.error(f"❌ API 资源同步失败: {result.get('message')}")
                    
            finally:
                session.close()
            
        except Exception as e:
            logger.error(f"❌ 处理 API 变更失败: {e}")
    
    async def _handle_text2sql_changes(self, changes: list):
        """处理 Text2SQL 变更"""
        try:
            logger.info(f"📝 处理 Text2SQL 变更: {len(changes)} 个")
            
            # 触发增量同步
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            
            db_config = get_database_config()
            engine = create_engine(
                f"postgresql://{db_config['user']}:{db_config['password']}@"
                f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
            )
            SessionLocal = sessionmaker(bind=engine)
            session = SessionLocal()
            
            try:
                result = await self.synchronizer.sync_and_vectorize_incremental(
                    session=session,
                    force_full_sync=False
                )
                
                if result.get("success"):
                    logger.info(f"✅ Text2SQL 资源同步完成")
                else:
                    logger.error(f"❌ Text2SQL 资源同步失败: {result.get('message')}")
                    
            finally:
                session.close()
            
        except Exception as e:
            logger.error(f"❌ 处理 Text2SQL 变更失败: {e}")


# 全局监听器实例
_global_listener: Optional[RealtimeListener] = None


async def start_global_listener(embedding_service=None):
    """启动全局监听器"""
    global _global_listener
    
    if _global_listener and _global_listener.is_listening:
        logger.warning("全局监听器已在运行")
        return
    
    try:
        _global_listener = RealtimeListener(embedding_service)
        await _global_listener.start_listening()
    except Exception as e:
        logger.error(f"启动全局监听器失败: {e}")


async def stop_global_listener():
    """停止全局监听器"""
    global _global_listener
    
    if _global_listener:
        await _global_listener.stop_listening()
        _global_listener = None


def get_global_listener() -> Optional[RealtimeListener]:
    """获取全局监听器实例"""
    return _global_listener
