# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Celery tasks for Resource Discovery operations.

Provides background task processing for resource synchronization, vectorization,
and discovery with real-time progress updates.
"""

import logging
import time
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure

from src.services.resource_discovery import ResourceSynchronizer, ResourceVectorizer
from src.database import get_db_session

logger = logging.getLogger(__name__)

# 使用统一的Celery应用
from ..celery_app import celery_app


class TaskProgressManager:
    """Manages task progress and status updates"""

    def __init__(self, task_id: str, operation_type: str):
        self.task_id = task_id
        self.operation_type = operation_type
        self.start_time = time.time()

    def update_progress(self, progress: int, message: str, details: Dict[str, Any] = None):
        """Update task progress in database"""
        try:
            import json
            from sqlalchemy import text

            session = next(get_db_session())

            # Update or insert system status
            update_query = text("""
                UPDATE resource_discovery.system_status
                SET status = 'running',
                    total_items = :total_items,
                    successful_items = :successful_items,
                    failed_items = :failed_items,
                    error_message = :message,
                    result_data = :details,
                    updated_at = NOW()
                WHERE operation_type = :operation_type
            """)

            result = session.execute(update_query, {
                'operation_type': self.operation_type,
                'total_items': details.get('total_items', 0) if details else 0,
                'successful_items': details.get('successful_items', 0) if details else 0,
                'failed_items': details.get('failed_items', 0) if details else 0,
                'message': message,
                'details': json.dumps(details or {})
            })

            # If no record was updated, insert a new one
            if result.rowcount == 0:
                insert_query = text("""
                    INSERT INTO resource_discovery.system_status
                    (operation_type, status, total_items, successful_items, failed_items,
                     error_message, result_data, started_at, created_at, updated_at)
                    VALUES (:operation_type, 'running', :total_items, :successful_items, :failed_items,
                            :message, :details, :started_at, NOW(), NOW())
                """)

                session.execute(insert_query, {
                    'operation_type': self.operation_type,
                    'total_items': details.get('total_items', 0) if details else 0,
                    'successful_items': details.get('successful_items', 0) if details else 0,
                    'failed_items': details.get('failed_items', 0) if details else 0,
                    'message': message,
                    'details': json.dumps(details or {}),
                    'started_at': datetime.fromtimestamp(self.start_time, timezone.utc)
                })

            session.commit()
            session.close()

        except Exception as e:
            logger.error(f"Failed to update task progress: {e}")

    def complete_task(self, result: Dict[str, Any]):
        """Mark task as completed"""
        try:
            import json
            from sqlalchemy import text

            duration = int(time.time() - self.start_time)
            session = next(get_db_session())

            query = text("""
                UPDATE resource_discovery.system_status
                SET status = 'completed',
                    completed_at = NOW(),
                    duration_seconds = :duration,
                    result_data = :result,
                    updated_at = NOW()
                WHERE operation_type = :operation_type
            """)

            session.execute(query, {
                'operation_type': self.operation_type,
                'duration': duration,
                'result': json.dumps(result)
            })
            session.commit()
            session.close()

        except Exception as e:
            logger.error(f"Failed to complete task: {e}")

    def fail_task(self, error_message: str):
        """Mark task as failed"""
        try:
            from sqlalchemy import text

            duration = int(time.time() - self.start_time)
            session = next(get_db_session())

            query = text("""
                UPDATE resource_discovery.system_status
                SET status = 'failed',
                    completed_at = NOW(),
                    duration_seconds = :duration,
                    error_message = :error_message,
                    updated_at = NOW()
                WHERE operation_type = :operation_type
            """)

            session.execute(query, {
                'operation_type': self.operation_type,
                'duration': duration,
                'error_message': error_message
            })
            session.commit()
            session.close()

        except Exception as e:
            logger.error(f"Failed to mark task as failed: {e}")


@celery_app.task(bind=True, name='resource_discovery.sync_resources')
def sync_resources_task(self, force_full_sync: bool = False):
    """
    Background task for synchronizing and vectorizing resources.

    Args:
        force_full_sync: Whether to force full synchronization
    """
    import asyncio
    from src.database import get_db_session
    from src.services.resource_discovery import ResourceSynchronizer

    # WebSocket进度推送函数
    async def send_websocket_progress(progress: int, message: str, current_step: str = '',
                                    total_steps: int = 4, processed_items: int = 0, total_items: int = 0):
        """发送WebSocket进度更新"""
        try:
            from src.services.websocket.progress_manager import progress_ws_manager
            await progress_ws_manager.send_task_progress(
                task_id=self.request.id,
                progress=progress,
                message=message,
                current_step=current_step,
                total_steps=total_steps,
                processed_items=processed_items,
                total_items=total_items
            )
        except Exception as e:
            logger.warning(f"WebSocket进度推送失败: {e}")

    def sync_send_websocket_progress(progress: int, message: str, current_step: str = '',
                                   total_steps: int = 4, processed_items: int = 0, total_items: int = 0):
        """同步方式发送WebSocket进度（在同步上下文中调用）"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(send_websocket_progress(
                    progress, message, current_step, total_steps, processed_items, total_items
                ))
            finally:
                loop.close()
        except Exception as e:
            logger.warning(f"同步WebSocket进度推送失败: {e}")

    try:
        logger.info(f"🔄 Starting resource synchronization task: {self.request.id}")

        # 发送任务开始通知
        sync_send_websocket_progress(0, '任务已开始', '初始化')

        # 更新任务状态为开始
        self.update_state(
            state='PROGRESS',
            meta={
                'message': '开始资源同步...',
                'progress': 10,
                'current_step': '初始化',
                'total_steps': 4,
                'processed_items': 0,
                'total_items': 0
            }
        )

        synchronizer = ResourceSynchronizer()
        session = next(get_db_session())

        try:
            # 步骤1: 检测资源变更
            sync_send_websocket_progress(25, '检测资源变更...', '检测变更', 4, 1, 4)
            self.update_state(
                state='PROGRESS',
                meta={
                    'message': '检测资源变更...',
                    'progress': 25,
                    'current_step': '检测变更',
                    'total_steps': 4,
                    'processed_items': 1,
                    'total_items': 4
                }
            )

            # 步骤2: 处理资源变更
            sync_send_websocket_progress(50, '处理资源变更...', '处理变更', 4, 2, 4)
            self.update_state(
                state='PROGRESS',
                meta={
                    'message': '处理资源变更...',
                    'progress': 50,
                    'current_step': '处理变更',
                    'total_steps': 4,
                    'processed_items': 2,
                    'total_items': 4
                }
            )

            # 执行同步
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                result = loop.run_until_complete(
                    synchronizer.sync_and_vectorize_incremental(
                        session=session,
                        force_full_sync=force_full_sync
                    )
                )
            finally:
                loop.close()

            # 步骤3: 向量化资源
            sync_send_websocket_progress(75, '向量化资源...', '向量化', 4, 3, 4)
            self.update_state(
                state='PROGRESS',
                meta={
                    'message': '向量化资源...',
                    'progress': 75,
                    'current_step': '向量化',
                    'total_steps': 4,
                    'processed_items': 3,
                    'total_items': 4
                }
            )

            # 步骤4: 完成同步
            sync_send_websocket_progress(90, '完成同步...', '完成', 4, 4, 4)
            self.update_state(
                state='PROGRESS',
                meta={
                    'message': '完成同步...',
                    'progress': 90,
                    'current_step': '完成',
                    'total_steps': 4,
                    'processed_items': 4,
                    'total_items': 4
                }
            )

            logger.info(f"✅ Resource synchronization completed: {result}")

            # 发送完成通知
            async def send_completion_notification():
                """发送任务完成通知"""
                try:
                    from src.services.websocket.progress_manager import progress_ws_manager
                    await progress_ws_manager.send_task_completed(
                        task_id=self.request.id,
                        result=result
                    )
                except Exception as e:
                    logger.warning(f"WebSocket完成通知发送失败: {e}")

            # 同步方式发送完成通知
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(send_completion_notification())
                finally:
                    loop.close()
            except Exception as e:
                logger.warning(f"同步WebSocket完成通知发送失败: {e}")

            return {
                'success': True,
                'message': '资源同步完成',
                'result': result,
                'task_id': self.request.id
            }

        finally:
            session.close()

    except Exception as e:
        error_msg = f"Resource synchronization failed: {str(e)}"
        logger.error(error_msg)

        # 发送WebSocket失败通知
        async def send_failure_notification():
            """发送任务失败通知"""
            try:
                from src.services.websocket.progress_manager import progress_ws_manager
                await progress_ws_manager.send_task_failed(
                    task_id=self.request.id,
                    error=error_msg
                )
            except Exception as e:
                logger.warning(f"WebSocket失败通知发送失败: {e}")

        # 同步方式发送失败通知
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(send_failure_notification())
            finally:
                loop.close()
        except Exception as e:
            logger.warning(f"同步WebSocket失败通知发送失败: {e}")

        # 更新任务状态为失败
        self.update_state(
            state='FAILURE',
            meta={
                'message': error_msg,
                'progress': 0,
                'error': str(e)
            }
        )

        raise Exception(error_msg)


@celery_app.task(bind=True, name='incremental_sync_task', time_limit=1800, soft_time_limit=1500)
def incremental_sync_task(self, force_full_sync: bool = False):
    """增量同步任务"""
    logger.info(f"🔄 Starting incremental sync task: force_full={force_full_sync}")

    try:
        # 获取数据库会话
        session = next(get_db_session())

        try:
            # 创建同步器
            from src.services.resource_discovery.resource_synchronizer import ResourceSynchronizer
            synchronizer = ResourceSynchronizer()

            # 发送WebSocket进度通知
            def sync_send_websocket_progress(progress, message, current_step, total_steps, processed_items, total_items):
                """同步发送WebSocket进度通知"""
                async def send_progress():
                    try:
                        from src.services.websocket.progress_manager import progress_ws_manager
                        await progress_ws_manager.send_task_progress(
                            task_id=self.request.id,
                            progress=progress,
                            message=message,
                            current_step=current_step,
                            total_steps=total_steps,
                            processed_items=processed_items,
                            total_items=total_items
                        )
                    except Exception as e:
                        logger.warning(f"WebSocket进度通知发送失败: {e}")

                # 同步方式发送进度通知
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(send_progress())
                    finally:
                        loop.close()
                except Exception as e:
                    logger.warning(f"同步WebSocket进度通知发送失败: {e}")

            # 步骤1: 检测变更
            sync_send_websocket_progress(25, '检测资源变更...', '检测变更', 4, 1, 4)
            self.update_state(
                state='PROGRESS',
                meta={
                    'message': '检测资源变更...',
                    'progress': 25,
                    'current_step': '检测变更',
                    'total_steps': 4,
                    'processed_items': 1,
                    'total_items': 4
                }
            )

            # 步骤2: 执行同步
            sync_send_websocket_progress(50, '执行增量同步...', '同步资源', 4, 2, 4)
            self.update_state(
                state='PROGRESS',
                meta={
                    'message': '执行增量同步...',
                    'progress': 50,
                    'current_step': '同步资源',
                    'total_steps': 4,
                    'processed_items': 2,
                    'total_items': 4
                }
            )

            # 执行增量同步
            logger.info("🔄 开始执行增量同步...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # 添加中间进度更新
                sync_send_websocket_progress(60, '正在处理资源变更...', '处理变更', 4, 2, 4)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'message': '正在处理资源变更...',
                        'progress': 60,
                        'current_step': '处理变更',
                        'total_steps': 4,
                        'processed_items': 2,
                        'total_items': 4
                    }
                )

                result = loop.run_until_complete(
                    synchronizer.sync_and_vectorize_incremental(
                        session=session,
                        force_full_sync=force_full_sync
                    )
                )

                logger.info(f"✅ 增量同步执行完成: {result}")

                # 步骤3: 向量化
                sync_send_websocket_progress(80, '完成资源同步...', '向量化', 4, 3, 4)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'message': '完成资源同步...',
                        'progress': 80,
                        'current_step': '向量化',
                        'total_steps': 4,
                        'processed_items': 3,
                        'total_items': 4
                    }
                )

            except Exception as sync_error:
                logger.error(f"❌ 增量同步执行失败: {sync_error}")
                sync_send_websocket_progress(50, f'同步失败: {str(sync_error)}', '错误', 4, 2, 4)
                raise sync_error
            finally:
                loop.close()

            # 步骤4: 完成
            sync_send_websocket_progress(100, '增量同步完成', '完成', 4, 4, 4)
            self.update_state(
                state='PROGRESS',
                meta={
                    'message': '增量同步完成',
                    'progress': 100,
                    'current_step': '完成',
                    'total_steps': 4,
                    'processed_items': 4,
                    'total_items': 4
                }
            )

            logger.info(f"✅ Incremental sync completed: {result}")

            return {
                'success': True,
                'message': '增量同步完成',
                'result': result,
                'task_id': self.request.id
            }

        finally:
            session.close()

    except Exception as e:
        error_msg = f"Incremental sync failed: {str(e)}"
        logger.error(error_msg)

        # 更新任务状态为失败
        self.update_state(
            state='FAILURE',
            meta={
                'message': error_msg,
                'progress': 0,
                'error': str(e)
            }
        )

        raise Exception(error_msg)


# Task signal handlers
@task_prerun.connect
def task_prerun_handler(task_id=None, task=None, **_kwargs):
    """Handle task pre-run"""
    logger.info(f"🚀 Starting task: {task.name} [{task_id}]")


@task_postrun.connect
def task_postrun_handler(task_id=None, task=None, state=None, **_kwargs):
    """Handle task post-run"""
    logger.info(f"✅ Completed task: {task.name} [{task_id}] - State: {state}")


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **_kwargs):
    """Handle task failure"""
    logger.error(f"❌ Task failed: {sender.name} [{task_id}] - Error: {exception}")