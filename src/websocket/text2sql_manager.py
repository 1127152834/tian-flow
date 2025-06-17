# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
WebSocket manager for Text2SQL real-time updates.

Provides real-time communication for training progress, query execution status,
and other Text2SQL operations.
"""

import logging
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, Set, Any, Optional, List
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types"""
    TRAINING_PROGRESS = "training_progress"
    TRAINING_COMPLETED = "training_completed"
    TRAINING_FAILED = "training_failed"
    QUERY_EXECUTION = "query_execution"
    EMBEDDING_PROGRESS = "embedding_progress"
    SYSTEM_STATUS = "system_status"
    ERROR = "error"


class Text2SQLWebSocketManager:
    """Manages WebSocket connections for Text2SQL operations"""
    
    def __init__(self):
        # Store active connections by datasource_id
        self.connections: Dict[int, Set[WebSocket]] = {}
        # Store connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        
        logger.info("Text2SQL WebSocket manager initialized")
    
    async def connect(self, websocket: WebSocket, datasource_id: int, client_info: Optional[Dict] = None):
        """Accept a new WebSocket connection"""
        try:
            await websocket.accept()
            
            # Add to connections
            if datasource_id not in self.connections:
                self.connections[datasource_id] = set()
            
            self.connections[datasource_id].add(websocket)
            
            # Store metadata
            self.connection_metadata[websocket] = {
                'datasource_id': datasource_id,
                'connected_at': datetime.now(timezone.utc),
                'client_info': client_info or {}
            }
            
            logger.info(f"WebSocket connected for datasource {datasource_id}")
            
            # Send welcome message
            await self.send_to_websocket(websocket, {
                'type': MessageType.SYSTEM_STATUS,
                'message': 'Connected to Text2SQL WebSocket',
                'datasource_id': datasource_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to connect WebSocket: {e}")
            raise
    
    async def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection"""
        try:
            metadata = self.connection_metadata.get(websocket)
            if metadata:
                datasource_id = metadata['datasource_id']
                
                # Remove from connections
                if datasource_id in self.connections:
                    self.connections[datasource_id].discard(websocket)
                    
                    # Clean up empty sets
                    if not self.connections[datasource_id]:
                        del self.connections[datasource_id]
                
                # Remove metadata
                del self.connection_metadata[websocket]
                
                logger.info(f"WebSocket disconnected for datasource {datasource_id}")
            
        except Exception as e:
            logger.error(f"Error during WebSocket disconnect: {e}")
    
    async def send_to_websocket(self, websocket: WebSocket, data: Dict[str, Any]):
        """Send data to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
            # Remove broken connection
            await self.disconnect(websocket)
    
    async def broadcast_to_datasource(self, datasource_id: int, data: Dict[str, Any]):
        """Broadcast data to all connections for a specific datasource"""
        if datasource_id not in self.connections:
            return
        
        # Get all connections for this datasource
        connections = self.connections[datasource_id].copy()
        
        # Send to all connections
        for websocket in connections:
            try:
                await self.send_to_websocket(websocket, data)
            except Exception as e:
                logger.error(f"Failed to broadcast to WebSocket: {e}")
                # Remove broken connection
                await self.disconnect(websocket)
    
    async def broadcast_training_progress(
        self,
        datasource_id: int,
        session_id: int,
        task_id: str,
        progress: int,
        message: str,
        details: Optional[Dict] = None
    ):
        """Broadcast training progress update"""
        data = {
            'type': MessageType.TRAINING_PROGRESS,
            'datasource_id': datasource_id,
            'session_id': session_id,
            'task_id': task_id,
            'progress': progress,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        await self.broadcast_to_datasource(datasource_id, data)
        logger.info(f"Broadcast training progress: {progress}% - {message}")
    
    async def broadcast_training_completed(
        self,
        datasource_id: int,
        session_id: int,
        task_id: str,
        results: Dict[str, Any]
    ):
        """Broadcast training completion"""
        data = {
            'type': MessageType.TRAINING_COMPLETED,
            'datasource_id': datasource_id,
            'session_id': session_id,
            'task_id': task_id,
            'results': results,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        await self.broadcast_to_datasource(datasource_id, data)
        logger.info(f"Broadcast training completed for session {session_id}")
    
    async def broadcast_training_failed(
        self,
        datasource_id: int,
        session_id: int,
        task_id: str,
        error_message: str
    ):
        """Broadcast training failure"""
        data = {
            'type': MessageType.TRAINING_FAILED,
            'datasource_id': datasource_id,
            'session_id': session_id,
            'task_id': task_id,
            'error_message': error_message,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        await self.broadcast_to_datasource(datasource_id, data)
        logger.error(f"Broadcast training failed for session {session_id}: {error_message}")
    
    async def broadcast_query_execution(
        self,
        datasource_id: int,
        query_id: int,
        status: str,
        execution_time_ms: Optional[int] = None,
        row_count: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        """Broadcast query execution status"""
        data = {
            'type': MessageType.QUERY_EXECUTION,
            'datasource_id': datasource_id,
            'query_id': query_id,
            'status': status,
            'execution_time_ms': execution_time_ms,
            'row_count': row_count,
            'error_message': error_message,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        await self.broadcast_to_datasource(datasource_id, data)
        logger.info(f"Broadcast query execution: {query_id} - {status}")
    
    async def broadcast_embedding_progress(
        self,
        datasource_id: int,
        task_id: str,
        processed: int,
        total: int,
        current_item: Optional[str] = None
    ):
        """Broadcast embedding generation progress"""
        progress = int((processed / total) * 100) if total > 0 else 0
        
        data = {
            'type': MessageType.EMBEDDING_PROGRESS,
            'datasource_id': datasource_id,
            'task_id': task_id,
            'processed': processed,
            'total': total,
            'progress': progress,
            'current_item': current_item,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        await self.broadcast_to_datasource(datasource_id, data)
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        total_connections = sum(len(connections) for connections in self.connections.values())
        
        datasource_stats = {}
        for datasource_id, connections in self.connections.items():
            datasource_stats[datasource_id] = {
                'connection_count': len(connections),
                'connections': [
                    {
                        'connected_at': self.connection_metadata[ws]['connected_at'].isoformat(),
                        'client_info': self.connection_metadata[ws]['client_info']
                    }
                    for ws in connections
                    if ws in self.connection_metadata
                ]
            }
        
        return {
            'total_connections': total_connections,
            'datasource_count': len(self.connections),
            'datasource_stats': datasource_stats,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    async def cleanup_stale_connections(self):
        """Clean up stale WebSocket connections"""
        stale_connections = []
        
        for websocket, metadata in self.connection_metadata.items():
            try:
                # Try to ping the connection
                await websocket.ping()
            except Exception:
                # Connection is stale
                stale_connections.append(websocket)
        
        # Remove stale connections
        for websocket in stale_connections:
            await self.disconnect(websocket)
        
        if stale_connections:
            logger.info(f"Cleaned up {len(stale_connections)} stale WebSocket connections")


# Global WebSocket manager instance
websocket_manager = Text2SQLWebSocketManager()


async def handle_websocket_connection(websocket: WebSocket, datasource_id: int):
    """Handle WebSocket connection lifecycle"""
    try:
        await websocket_manager.connect(websocket, datasource_id)
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle client messages (ping, status requests, etc.)
                await handle_client_message(websocket, datasource_id, message)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket_manager.send_to_websocket(websocket, {
                    'type': MessageType.ERROR,
                    'message': 'Invalid JSON message format'
                })
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket_manager.send_to_websocket(websocket, {
                    'type': MessageType.ERROR,
                    'message': f'Error processing message: {str(e)}'
                })
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    
    finally:
        await websocket_manager.disconnect(websocket)


async def handle_client_message(websocket: WebSocket, datasource_id: int, message: Dict[str, Any]):
    """Handle messages from WebSocket clients"""
    message_type = message.get('type')
    
    if message_type == 'ping':
        await websocket_manager.send_to_websocket(websocket, {
            'type': 'pong',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    elif message_type == 'get_stats':
        stats = await websocket_manager.get_connection_stats()
        await websocket_manager.send_to_websocket(websocket, {
            'type': 'stats',
            'data': stats
        })
    
    else:
        logger.warning(f"Unknown message type: {message_type}")


# Export the manager and handler
__all__ = ['websocket_manager', 'handle_websocket_connection', 'MessageType']
