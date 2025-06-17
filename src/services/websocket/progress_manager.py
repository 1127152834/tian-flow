"""
WebSocket进度管理器
用于实时推送Celery任务进度到前端
"""

import json
import asyncio
import logging
import redis
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket
from datetime import datetime

logger = logging.getLogger(__name__)


class ProgressWebSocketManager:
    """WebSocket进度管理器"""

    def __init__(self):
        # 存储活跃的WebSocket连接 {task_id: {websocket_connections}}
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # 存储任务进度缓存 {task_id: progress_data}
        self.progress_cache: Dict[str, Dict[str, Any]] = {}
        # Redis连接用于进程间通信
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        # Redis频道前缀
        self.redis_channel_prefix = "websocket_progress:"
        
    async def connect(self, websocket: WebSocket, task_id: str):
        """建立WebSocket连接"""
        await websocket.accept()

        if task_id not in self.active_connections:
            self.active_connections[task_id] = set()
            # 为新任务启动Redis监听器
            asyncio.create_task(self._start_redis_listener(task_id))

        self.active_connections[task_id].add(websocket)
        logger.info(f"WebSocket连接已建立: task_id={task_id}, 连接数={len(self.active_connections[task_id])}")

        # 如果有缓存的进度数据，立即发送
        if task_id in self.progress_cache:
            await self.send_to_websocket(websocket, self.progress_cache[task_id])
    
    async def disconnect(self, websocket: WebSocket, task_id: str):
        """断开WebSocket连接"""
        if task_id in self.active_connections:
            self.active_connections[task_id].discard(websocket)
            
            # 如果没有连接了，清理
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]
                # 可选：清理进度缓存
                if task_id in self.progress_cache:
                    del self.progress_cache[task_id]
                    
        logger.info(f"WebSocket连接已断开: task_id={task_id}")
    
    async def send_to_websocket(self, websocket: WebSocket, data: Dict[str, Any]):
        """发送数据到单个WebSocket"""
        try:
            await websocket.send_text(json.dumps(data))
        except Exception as e:
            logger.error(f"发送WebSocket消息失败: {e}")
    
    async def broadcast_progress(self, task_id: str, progress_data: Dict[str, Any]):
        """广播进度更新到所有相关的WebSocket连接"""
        # 添加时间戳
        progress_data['timestamp'] = datetime.now().isoformat()

        # 缓存进度数据
        self.progress_cache[task_id] = progress_data

        # 通过Redis发布消息（用于进程间通信）
        try:
            channel = f"{self.redis_channel_prefix}{task_id}"
            message = json.dumps(progress_data)
            self.redis_client.publish(channel, message)
            logger.debug(f"Redis消息已发布: channel={channel}")
        except Exception as e:
            logger.error(f"Redis消息发布失败: {e}")

        # 直接发送到本进程的WebSocket连接
        if task_id not in self.active_connections:
            logger.debug(f"本进程没有活跃的WebSocket连接: task_id={task_id}")
            return

        # 获取连接副本，避免在迭代时修改
        connections = self.active_connections[task_id].copy()

        # 并发发送到所有连接
        tasks = []
        for websocket in connections:
            tasks.append(self.send_to_websocket(websocket, progress_data))

        if tasks:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
                logger.info(f"进度广播完成: task_id={task_id}, 连接数={len(tasks)}")
            except Exception as e:
                logger.error(f"进度广播失败: {e}")
    
    async def send_task_started(self, task_id: str, task_info: Dict[str, Any]):
        """发送任务开始通知"""
        data = {
            'type': 'task_started',
            'task_id': task_id,
            'status': 'started',
            'message': '任务已开始',
            'progress': 0,
            **task_info
        }
        await self.broadcast_progress(task_id, data)
    
    async def send_task_progress(self, task_id: str, progress: int, message: str, 
                               current_step: str = '', total_steps: int = 0,
                               processed_items: int = 0, total_items: int = 0):
        """发送任务进度更新"""
        data = {
            'type': 'task_progress',
            'task_id': task_id,
            'status': 'running',
            'progress': progress,
            'message': message,
            'current_step': current_step,
            'total_steps': total_steps,
            'processed_items': processed_items,
            'total_items': total_items
        }
        await self.broadcast_progress(task_id, data)
    
    async def send_task_completed(self, task_id: str, result: Dict[str, Any]):
        """发送任务完成通知"""
        data = {
            'type': 'task_completed',
            'task_id': task_id,
            'status': 'completed',
            'progress': 100,
            'message': '任务已完成',
            'result': result
        }
        await self.broadcast_progress(task_id, data)
    
    async def send_task_failed(self, task_id: str, error: str):
        """发送任务失败通知"""
        data = {
            'type': 'task_failed',
            'task_id': task_id,
            'status': 'failed',
            'progress': 0,
            'message': '任务执行失败',
            'error': error
        }
        await self.broadcast_progress(task_id, data)

    async def send_chart_data(self, chart_config: dict, thread_id: str = None):
        """发送图表数据到前端"""
        import time
        chart_task_id = f"chart_{int(time.time() * 1000)}"

        data = {
            'type': 'chart',
            'task_id': chart_task_id,
            'thread_id': thread_id,
            'status': 'completed',
            'chart_config': chart_config,
            'message': f'图表已生成：{chart_config.get("title", "数据图表")}',
            'data_points': len(chart_config.get('data', []))
        }

        # 广播到全局监听器
        await self.broadcast_progress("global_listener", data)

        # 为了向后兼容，也广播到特定的图表任务ID
        await self.broadcast_progress(chart_task_id, data)

        logger.info(f"图表数据已通过WebSocket推送: {chart_config.get('title', 'Unknown')}")

    async def send_global_message(self, message_type: str, data: dict):
        """发送全局消息到前端"""
        message_data = {
            'type': message_type,
            'timestamp': datetime.now().isoformat(),
            **data
        }

        # 发送到全局监听器
        await self.broadcast_progress("global_listener", message_data)

        logger.info(f"全局消息已发送: type={message_type}")
    
    def get_connection_count(self, task_id: str) -> int:
        """获取指定任务的连接数"""
        return len(self.active_connections.get(task_id, set()))
    
    def get_total_connections(self) -> int:
        """获取总连接数"""
        return sum(len(connections) for connections in self.active_connections.values())

    async def _start_redis_listener(self, task_id: str):
        """启动Redis监听器，监听特定任务的进度消息"""
        channel = f"{self.redis_channel_prefix}{task_id}"

        try:
            # 创建新的Redis连接用于订阅
            redis_sub = redis.Redis(host='localhost', port=6380, db=0)
            pubsub = redis_sub.pubsub()
            pubsub.subscribe(channel)

            logger.info(f"Redis监听器已启动: channel={channel}")

            # 使用异步方式监听消息，避免阻塞
            while True:
                try:
                    # 使用非阻塞方式获取消息
                    message = pubsub.get_message(timeout=1.0)

                    if message is None:
                        # 检查是否还有活跃连接
                        if task_id not in self.active_connections:
                            logger.info(f"没有活跃连接，停止Redis监听: task_id={task_id}")
                            break
                        # 让出控制权，避免阻塞
                        await asyncio.sleep(0.1)
                        continue

                    if message['type'] == 'message':
                        try:
                            # 解析消息
                            progress_data = json.loads(message['data'].decode('utf-8'))

                            # 发送到WebSocket连接
                            if task_id in self.active_connections:
                                connections = self.active_connections[task_id].copy()
                                tasks = []
                                for websocket in connections:
                                    tasks.append(self.send_to_websocket(websocket, progress_data))

                                if tasks:
                                    await asyncio.gather(*tasks, return_exceptions=True)
                                    logger.debug(f"Redis消息已转发到WebSocket: task_id={task_id}, 连接数={len(tasks)}")

                            # 如果任务完成，停止监听
                            if progress_data.get('status') in ['completed', 'failed']:
                                logger.info(f"任务完成，停止Redis监听: task_id={task_id}")
                                break

                        except Exception as e:
                            logger.error(f"处理Redis消息失败: {e}")

                    # 让出控制权
                    await asyncio.sleep(0.01)

                except Exception as e:
                    logger.error(f"Redis监听循环异常: {e}")
                    await asyncio.sleep(1.0)

            # 清理
            pubsub.unsubscribe(channel)
            pubsub.close()
            redis_sub.close()

        except Exception as e:
            logger.error(f"Redis监听器异常: task_id={task_id}, error={e}")


# 全局WebSocket管理器实例
progress_ws_manager = ProgressWebSocketManager()
