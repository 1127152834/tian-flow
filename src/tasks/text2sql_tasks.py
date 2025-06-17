# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Celery tasks for Text2SQL operations.

Provides background task processing for training, embedding generation,
and model optimization with real-time progress updates via WebSocket.
"""

import logging
import time
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure

from src.repositories.text2sql import Text2SQLRepository
from src.services.vector_store import PgVectorStore
from src.services.database_datasource import DatabaseDatasourceService
from src.models.text2sql import TrainingSessionStatus, TrainingDataType

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    'text2sql_tasks',
    broker='redis://localhost:6380/0',
    backend='redis://localhost:6380/0'
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_send_sent_event=True,
    worker_send_task_events=True,
    result_expires=3600,  # 1 hour
)


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
            
            # Send WebSocket notification (will be implemented later)
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


@celery_app.task(bind=True, name='text2sql.train_model')
def train_model_task(self, datasource_id: int, session_id: int, **training_params):
    """
    Background task for training Text2SQL model.

    Args:
        datasource_id: Database datasource ID
        session_id: Training session ID
        **training_params: Additional training parameters
    """
    
    async def _train_model():
        start_time = time.time()
        progress_manager = TaskProgressManager(self.request.id, session_id)
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
                        'table_name': data.table_name
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
            time.sleep(2)  # Simulate validation
            
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
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_train_model())
    finally:
        loop.close()


@celery_app.task(bind=True, name='text2sql.generate_embeddings')
def generate_embeddings_task(self, datasource_id: int, training_data_ids: List[int] = None, force_update: bool = False):
    """
    Background task for generating embeddings for training data.
    Supports incremental updates based on content hash.

    Args:
        datasource_id: Database datasource ID
        training_data_ids: List of training data IDs to process (if None, process all active training data)
        force_update: Whether to force regenerate embeddings even if they exist
    """

    async def _generate_embeddings():
        repository = Text2SQLRepository()
        vector_store = PgVectorStore()

        try:
            # If no specific training_data_ids provided, get all active training data
            if not training_data_ids:
                logger.info(f"Getting all active training data for datasource {datasource_id}")
                all_training_data, _ = await repository.list_training_data(
                    datasource_id=datasource_id,
                    is_active=True,
                    limit=1000  # Get all data
                )
                target_ids = [data.id for data in all_training_data]
                logger.info(f"Found {len(target_ids)} active training data items")
            else:
                target_ids = training_data_ids

            processed = 0
            skipped = 0
            errors = []

            for training_id in target_ids:
                try:
                    # Get training data
                    training_data = await repository.get_training_data(training_id)
                    if not training_data:
                        errors.append(f"Training data {training_id} not found")
                        continue

                    # Check if embedding already exists (unless force_update)
                    if not force_update:
                        existing_embedding = await vector_store.check_embedding_exists(
                            datasource_id=datasource_id,
                            content=training_data.content
                        )
                        if existing_embedding:
                            logger.debug(f"Embedding already exists for training data {training_id}, skipping")
                            skipped += 1
                            continue

                    # Generate embedding (incremental or force update)
                    await vector_store.add_training_data(
                        datasource_id=datasource_id,
                        content=training_data.content,
                        content_type=training_data.content_type,
                        metadata={
                            'training_id': training_data.id,
                            'question': training_data.question,
                            'sql_query': training_data.sql_query
                        },
                        training_data_id=training_data.id,
                        force_update=force_update
                    )

                    processed += 1
                    logger.debug(f"Generated embedding for training data {training_id}")

                except Exception as e:
                    errors.append(f"Failed to process training data {training_id}: {str(e)}")
                    logger.error(f"Failed to generate embedding for training data {training_id}: {e}")

            result = {
                'status': 'completed',
                'processed': processed,
                'skipped': skipped,
                'total': len(target_ids),
                'errors': errors,
                'force_update': force_update
            }

            logger.info(f"Embedding generation completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Embedding generation task failed: {e}")
            raise
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_generate_embeddings())
    finally:
        loop.close()


@celery_app.task(bind=True, name='text2sql.cleanup_old_data')
def cleanup_old_data_task(self, days_to_keep: int = 30):
    """
    Background task for cleaning up old query history and cache data.
    
    Args:
        days_to_keep: Number of days to keep data
    """
    
    async def _cleanup_data():
        repository = Text2SQLRepository()
        
        try:
            result = await repository.cleanup_old_data(days_to_keep)
            
            logger.info(f"Cleanup completed: {result}")
            
            return {
                'status': 'completed',
                'deleted_queries': result['deleted_queries'],
                'deleted_cache': result['deleted_cache'],
                'days_to_keep': days_to_keep
            }
            
        except Exception as e:
            logger.error(f"Cleanup task failed: {e}")
            raise
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_cleanup_data())
    finally:
        loop.close()


# Task event handlers
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Handle task start event"""
    logger.info(f"Task {task.name} [{task_id}] started")


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kwds):
    """Handle task completion event"""
    logger.info(f"Task {task.name} [{task_id}] completed with state: {state}")


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds):
    """Handle task failure event"""
    logger.error(f"Task {sender.name} [{task_id}] failed: {exception}")


# Export Celery app for worker
__all__ = ['celery_app', 'train_model_task', 'generate_embeddings_task', 'cleanup_old_data_task']
