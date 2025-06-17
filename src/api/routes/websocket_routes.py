"""
WebSocket路由
用于实时进度推送
"""

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.services.websocket.progress_manager import progress_ws_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/progress/{task_id}")
async def websocket_progress_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket端点，用于实时接收任务进度更新

    Args:
        websocket: WebSocket连接
        task_id: 任务ID
    """
    await progress_ws_manager.connect(websocket, task_id)

    try:
        # 保持连接活跃，监听客户端消息
        while True:
            # 接收客户端消息（如果有的话）
            data = await websocket.receive_text()
            logger.debug(f"收到WebSocket消息: task_id={task_id}, data={data}")

            # 可以在这里处理客户端发送的消息
            # 比如客户端请求当前进度、取消任务等

    except WebSocketDisconnect:
        logger.info(f"WebSocket客户端断开连接: task_id={task_id}")
    except Exception as e:
        logger.error(f"WebSocket连接异常: task_id={task_id}, error={e}")
    finally:
        await progress_ws_manager.disconnect(websocket, task_id)


@router.websocket("/ws/progress/global_listener")
async def websocket_global_listener_endpoint(websocket: WebSocket):
    """
    全局WebSocket端点，用于接收所有类型的消息（图表、任务进度等）

    Args:
        websocket: WebSocket连接
    """
    # 使用特殊的全局监听器ID
    global_listener_id = "global_listener"
    await progress_ws_manager.connect(websocket, global_listener_id)

    try:
        # 保持连接活跃，监听客户端消息
        while True:
            # 接收客户端消息（如果有的话）
            data = await websocket.receive_text()
            logger.debug(f"收到全局WebSocket消息: data={data}")

            # 可以在这里处理客户端发送的消息

    except WebSocketDisconnect:
        logger.info(f"全局WebSocket客户端断开连接")
    except Exception as e:
        logger.error(f"全局WebSocket连接异常: error={e}")
    finally:
        await progress_ws_manager.disconnect(websocket, global_listener_id)


@router.get("/ws/stats")
async def get_websocket_stats():
    """获取WebSocket连接统计信息"""
    return {
        "success": True,
        "data": {
            "total_connections": progress_ws_manager.get_total_connections(),
            "active_tasks": len(progress_ws_manager.active_connections),
            "task_connections": {
                task_id: progress_ws_manager.get_connection_count(task_id)
                for task_id in progress_ws_manager.active_connections.keys()
            }
        },
        "message": "WebSocket统计信息"
    }
