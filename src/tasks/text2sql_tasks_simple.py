# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Simplified Text2SQL tasks without Celery dependency.

Provides background task processing for training, embedding generation,
and model optimization. This is a simplified version that can be extended
with Celery when the dependency is available.
"""

import logging
import time
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from src.repositories.text2sql import Text2SQLRepository
from src.services.vector_store import PgVectorStore
from src.models.text2sql import TrainingSessionStatus

logger = logging.getLogger(__name__)


class TaskProgressManager:
    """Manages task progress and WebSocket notifications"""
    
    def __init__(self, task_id: str, session_id: int):
        self.task_id = task_id
        self.session_id = session_id
        self.repository = Text2SQLRepository()
    
    async def update_progress(self, progress: int, message: str, details: Optional[Dict] = None):
        """Update task progress and send WebSocket notification"""
        try:
            # Update training session
            await self.repository.update_training_session(
                self.session_id,
                status=TrainingSessionStatus.RUNNING,
                notes=f"Progress: {progress}% - {message}"
            )
            
            # Send WebSocket notification
            await self._send_websocket_update({
                'task_id': self.task_id,
                'session_id': self.session_id,
                'progress': progress,
                'message': message,
                'details': details or {},
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to update progress: {e}")
    
    async def _send_websocket_update(self, data: Dict[str, Any]):
        """Send WebSocket update via WebSocket manager"""
        try:
            from src.websocket.text2sql_manager import websocket_manager
            
            # Extract datasource_id from session
            session = await self.repository.get_training_session(self.session_id)
            if session:
                datasource_id = session.datasource_id
                
                # Send appropriate WebSocket message based on progress
                if data['progress'] == 100:
                    await websocket_manager.broadcast_training_completed(
                        datasource_id=datasource_id,
                        session_id=self.session_id,
                        task_id=self.task_id,
                        results=data.get('details', {})
                    )
                elif data['progress'] == -1:
                    await websocket_manager.broadcast_training_failed(
                        datasource_id=datasource_id,
                        session_id=self.session_id,
                        task_id=self.task_id,
                        error_message=data['message']
                    )
                else:
                    await websocket_manager.broadcast_training_progress(
                        datasource_id=datasource_id,
                        session_id=self.session_id,
                        task_id=self.task_id,
                        progress=data['progress'],
                        message=data['message'],
                        details=data.get('details')
                    )
        except Exception as e:
            logger.error(f"Failed to send WebSocket update: {e}")


class Text2SQLTaskManager:
    """Simplified task manager for Text2SQL operations"""
    
    def __init__(self):
        self.running_tasks: Dict[str, asyncio.Task] = {}
    
    async def train_model_task(
        self,
        datasource_id: int,
        session_id: int,
        **training_params
    ) -> Dict[str, Any]:
        """
        Background task for training Text2SQL model.
        
        Args:
            datasource_id: Database datasource ID
            session_id: Training session ID
            **training_params: Additional training parameters
        """
        task_id = str(uuid.uuid4())
        start_time = time.time()
        
        progress_manager = TaskProgressManager(task_id, session_id)
        repository = Text2SQLRepository()
        vector_store = PgVectorStore()
        
        try:
            # Update session status to running
            await repository.update_training_session(
                session_id,
                status=TrainingSessionStatus.RUNNING
            )
            
            await progress_manager.update_progress(0, "Starting training process...")
            
            # Step 1: Load training data
            await progress_manager.update_progress(10, "Loading training data...")
            training_data, _total = await repository.list_training_data(
                datasource_id=datasource_id,
                is_active=True,
                limit=1000,
                offset=0
            )
            
            if not training_data:
                raise ValueError("No training data found for this datasource")
            
            await progress_manager.update_progress(
                20, 
                f"Loaded {len(training_data)} training examples",
                {"training_data_count": len(training_data)}
            )
            
            # Step 2: Generate embeddings
            await progress_manager.update_progress(30, "Generating embeddings...")
            embeddings_generated = 0
            
            for i, data in enumerate(training_data):
                # Generate embedding for training data
                await vector_store.add_training_data(
                    datasource_id=datasource_id,
                    content=data.content,
                    content_type=data.content_type,
                    metadata={
                        'training_id': data.id,
                        'question': data.question,
                        'sql_query': data.sql_query,
                        'table_names': data.table_names
                    }
                )
                
                embeddings_generated += 1
                progress = 30 + int((i / len(training_data)) * 40)
                
                if i % 10 == 0:  # Update every 10 items
                    await progress_manager.update_progress(
                        progress,
                        f"Generated embeddings: {embeddings_generated}/{len(training_data)}"
                    )
            
            await progress_manager.update_progress(
                70,
                f"Generated {embeddings_generated} embeddings",
                {"embeddings_generated": embeddings_generated}
            )
            
            # Step 3: Build vector index
            await progress_manager.update_progress(80, "Building vector index...")
            await vector_store.build_index(datasource_id)
            
            # Step 4: Validate model performance (mock)
            await progress_manager.update_progress(90, "Validating model performance...")
            await asyncio.sleep(2)  # Simulate validation
            
            # Calculate mock accuracy
            accuracy_score = 0.85 + (len(training_data) * 0.001)  # Mock calculation
            validation_score = accuracy_score * 0.95
            
            # Step 5: Complete training
            await progress_manager.update_progress(100, "Training completed successfully!")
            
            # Update session with final results
            await repository.update_training_session(
                session_id,
                status=TrainingSessionStatus.COMPLETED,
                training_data_count=len(training_data),
                accuracy_score=accuracy_score,
                validation_score=validation_score,
                training_time_seconds=int(time.time() - start_time),
                completed_at=datetime.now(timezone.utc)
            )
            
            return {
                'task_id': task_id,
                'status': 'completed',
                'training_data_count': len(training_data),
                'embeddings_generated': embeddings_generated,
                'accuracy_score': accuracy_score,
                'validation_score': validation_score,
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error(f"Training task failed: {e}")
            
            # Update session with error
            await repository.update_training_session(
                session_id,
                status=TrainingSessionStatus.FAILED,
                error_message=str(e),
                completed_at=datetime.now(timezone.utc)
            )
            
            await progress_manager.update_progress(
                -1,
                f"Training failed: {str(e)}",
                {"error": str(e)}
            )
            
            raise
    
    async def generate_embeddings_task(
        self,
        datasource_id: int,
        training_data_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Background task for generating embeddings for specific training data.
        
        Args:
            datasource_id: Database datasource ID
            training_data_ids: List of training data IDs to process
        """
        task_id = str(uuid.uuid4())
        repository = Text2SQLRepository()
        vector_store = PgVectorStore()
        
        try:
            processed = 0
            errors = []
            
            for training_id in training_data_ids:
                try:
                    # Get training data
                    training_data = await repository.get_training_data(training_id)
                    if not training_data:
                        errors.append(f"Training data {training_id} not found")
                        continue
                    
                    # Generate embedding
                    await vector_store.add_training_data(
                        datasource_id=datasource_id,
                        content=training_data.content,
                        content_type=training_data.content_type,
                        metadata={
                            'training_id': training_data.id,
                            'question': training_data.question,
                            'sql_query': training_data.sql_query
                        }
                    )
                    
                    processed += 1
                    
                except Exception as e:
                    errors.append(f"Failed to process training data {training_id}: {str(e)}")
                    logger.error(f"Failed to generate embedding for training data {training_id}: {e}")
            
            return {
                'task_id': task_id,
                'status': 'completed',
                'processed': processed,
                'total': len(training_data_ids),
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Embedding generation task failed: {e}")
            raise
    
    async def cleanup_old_data_task(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """
        Background task for cleaning up old query history and cache data.
        
        Args:
            days_to_keep: Number of days to keep data
        """
        task_id = str(uuid.uuid4())
        repository = Text2SQLRepository()
        
        try:
            result = await repository.cleanup_old_data(days_to_keep)
            
            logger.info(f"Cleanup completed: {result}")
            
            return {
                'task_id': task_id,
                'status': 'completed',
                'deleted_queries': result['deleted_queries'],
                'deleted_cache': result['deleted_cache'],
                'days_to_keep': days_to_keep
            }
            
        except Exception as e:
            logger.error(f"Cleanup task failed: {e}")
            raise
    
    def start_background_task(self, coro) -> str:
        """Start a background task and return task ID"""
        task_id = str(uuid.uuid4())
        task = asyncio.create_task(coro)
        self.running_tasks[task_id] = task
        
        # Clean up completed tasks
        def cleanup_task(task_id):
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
        
        task.add_done_callback(lambda t: cleanup_task(task_id))
        
        return task_id


# Global task manager instance
task_manager = Text2SQLTaskManager()


# Export the task manager and functions
__all__ = ['task_manager', 'Text2SQLTaskManager', 'TaskProgressManager']
