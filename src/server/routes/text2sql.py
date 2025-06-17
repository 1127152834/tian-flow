# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Text2SQL API routes for DeerFlow.

Provides REST API endpoints for Text2SQL functionality including SQL generation,
training data management, and real-time WebSocket connections.
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, WebSocket, Query, Path, Body

from src.services.text2sql import Text2SQLService
from src.models.text2sql import (
    QueryStatus,
    TrainingDataType,
    SQLGenerationRequest,
    SQLGenerationResponse,
    SQLExecutionRequest,
    SQLExecutionResponse,
    TrainingDataRequest,
    TrainingDataResponse,
    Text2SQLStatistics,
    QuestionAnswerRequest,
    QuestionAnswerResponse,
    BatchTrainingRequest
)
from src.websocket.text2sql_manager import handle_websocket_connection

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/text2sql", tags=["Text2SQL"])

# Initialize service
text2sql_service = Text2SQLService()


# SQL Generation and Execution Endpoints

@router.post("/generate", response_model=SQLGenerationResponse)
async def generate_sql(request: SQLGenerationRequest):
    """Generate SQL from natural language question"""
    try:
        response = await text2sql_service.generate_sql(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate SQL: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/execute", response_model=SQLExecutionResponse)
async def execute_sql(request: SQLExecutionRequest):
    """Execute generated SQL query"""
    try:
        response = await text2sql_service.execute_sql(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to execute SQL: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Query History Endpoints

@router.get("/history")
async def get_query_history(
    datasource_id: Optional[int] = Query(None, description="Filter by datasource ID"),
    status: Optional[QueryStatus] = Query(None, description="Filter by query status"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip")
):
    """Get query history with pagination"""
    try:
        queries, total = await text2sql_service.get_query_history(
            datasource_id=datasource_id,
            status=status,
            limit=limit,
            offset=offset
        )
        
        return {
            "queries": [query.model_dump() for query in queries],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Failed to get query history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Training Data Endpoints

@router.post("/training", response_model=TrainingDataResponse)
async def add_training_data(request: TrainingDataRequest):
    """Add training data for model improvement"""
    try:
        response = await text2sql_service.add_training_data(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to add training data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/training")
async def get_training_data(
    datasource_id: Optional[int] = Query(None, description="Filter by datasource ID"),
    content_type: Optional[TrainingDataType] = Query(None, description="Filter by content type"),
    is_active: bool = Query(True, description="Filter by active status"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip")
):
    """Get training data with pagination"""
    try:
        training_data, total = await text2sql_service.get_training_data_list(
            datasource_id=datasource_id,
            content_type=content_type,
            is_active=is_active,
            limit=limit,
            offset=offset
        )
        
        return {
            "training_data": [data.model_dump() for data in training_data],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Failed to get training data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/training/{training_id}", response_model=TrainingDataResponse)
async def update_training_data(
    training_id: int = Path(..., description="Training data ID"),
    request: TrainingDataRequest = Body(..., description="Updated training data")
):
    """Update training data"""
    try:
        # Get existing training data
        existing_data = await text2sql_service.repository.get_training_data(training_id)
        if not existing_data:
            raise HTTPException(status_code=404, detail="Training data not found")

        # Update the training data
        updated = await text2sql_service.repository.update_training_data(
            training_id=training_id,
            content_type=request.content_type,
            content=request.content,
            question=request.question,
            sql_query=request.sql_query,
            table_names=request.table_names,
            database_schema=request.database_schema,
            metadata=request.metadata
        )

        if not updated:
            raise HTTPException(status_code=404, detail="Training data not found")

        # Get updated training data
        updated_data = await text2sql_service.repository.get_training_data(training_id)

        # Trigger embedding regeneration for updated data
        try:
            await text2sql_service.generate_embeddings_for_training_data(
                datasource_id=updated_data.datasource_id,
                training_data_ids=[training_id]
            )
            logger.info(f"Started embedding regeneration for updated training data {training_id}")
        except Exception as e:
            logger.warning(f"Failed to start embedding regeneration for training data {training_id}: {e}")

        return TrainingDataResponse(
            id=updated_data.id,
            datasource_id=updated_data.datasource_id,
            content_type=updated_data.content_type,
            question=updated_data.question,
            sql_query=updated_data.sql_query,
            content=updated_data.content,
            table_names=updated_data.table_names,
            database_schema=updated_data.database_schema,
            metadata=updated_data.metadata,
            content_hash=updated_data.content_hash,
            is_active=updated_data.is_active,
            is_validated=updated_data.is_validated,
            validation_score=updated_data.validation_score,
            created_at=updated_data.created_at,
            updated_at=updated_data.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update training data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/training/{training_id}")
async def delete_training_data(
    training_id: int = Path(..., description="Training data ID"),
    soft_delete: bool = Query(True, description="Perform soft delete")
):
    """Delete training data"""
    try:
        deleted = await text2sql_service.delete_training_data(training_id, soft_delete)
        if not deleted:
            raise HTTPException(status_code=404, detail="Training data not found")

        return {"message": "Training data deleted successfully", "training_id": training_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete training data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Training Session and Model Management Endpoints

@router.post("/retrain/{datasource_id}")
async def retrain_model(
    datasource_id: int = Path(..., description="Datasource ID"),
    force_rebuild: bool = Query(False, description="Force rebuild all embeddings")
):
    """Start model retraining for a datasource"""
    try:
        task_id = await text2sql_service.retrain_model(datasource_id, force_rebuild)
        return {
            "message": "Model retraining started",
            "task_id": task_id,
            "datasource_id": datasource_id,
            "force_rebuild": force_rebuild
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start retraining: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/training-session")
async def start_training_session(
    datasource_id: int = Body(..., description="Datasource ID"),
    session_name: Optional[str] = Body(None, description="Session name"),
    model_version: Optional[str] = Body(None, description="Model version"),
    training_parameters: Optional[Dict[str, Any]] = Body(None, description="Training parameters"),
    notes: Optional[str] = Body(None, description="Session notes")
):
    """Start a new training session"""
    try:
        result = await text2sql_service.start_training_session(
            datasource_id=datasource_id,
            session_name=session_name,
            model_version=model_version,
            training_parameters=training_parameters,
            notes=notes
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start training session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/training-sessions")
async def get_training_sessions(
    datasource_id: Optional[int] = Query(None, description="Filter by datasource ID"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip")
):
    """Get training sessions with pagination"""
    try:
        sessions, total = await text2sql_service.list_training_sessions(
            datasource_id=datasource_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "sessions": [session.model_dump() for session in sessions],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Failed to get training sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/training-session/{session_id}")
async def get_training_session_status(
    session_id: int = Path(..., description="Training session ID")
):
    """Get training session status"""
    try:
        session = await text2sql_service.get_training_session_status(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Training session not found")
        
        return session.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get training session status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/embeddings")
async def generate_embeddings(
    datasource_id: int = Body(..., description="Datasource ID"),
    training_data_ids: List[int] = Body(..., description="Training data IDs to process")
):
    """Generate embeddings for specific training data"""
    try:
        result = await text2sql_service.generate_embeddings_for_training_data(
            datasource_id=datasource_id,
            training_data_ids=training_data_ids
        )
        return result
    except Exception as e:
        logger.error(f"Failed to start embedding generation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Statistics and Utility Endpoints

@router.get("/statistics", response_model=Text2SQLStatistics)
async def get_statistics(
    datasource_id: Optional[int] = Query(None, description="Filter by datasource ID")
):
    """Get Text2SQL statistics"""
    try:
        stats = await text2sql_service.get_statistics(datasource_id)
        return stats
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/datasource/{datasource_id}/training-summary")
async def get_datasource_training_summary(
    datasource_id: int = Path(..., description="Datasource ID")
):
    """Get training data summary for a specific datasource"""
    try:
        summary = await text2sql_service.get_datasource_training_summary(datasource_id)
        return summary
    except Exception as e:
        logger.error(f"Failed to get training summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/cleanup")
async def cleanup_old_data(
    days_to_keep: int = Body(30, ge=1, le=365, description="Number of days to keep data")
):
    """Start cleanup task for old data"""
    try:
        result = await text2sql_service.cleanup_old_data(days_to_keep)
        return result
    except Exception as e:
        logger.error(f"Failed to start cleanup task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# WebSocket Endpoint

@router.websocket("/ws/{datasource_id}")
async def websocket_endpoint(websocket: WebSocket, datasource_id: int):
    """WebSocket endpoint for real-time Text2SQL updates"""
    await handle_websocket_connection(websocket, datasource_id)


# Training Endpoints - DDL, Documentation, SQL

@router.post("/train-ddl")
async def train_ddl(
    datasource_id: int = Body(..., description="Datasource ID"),
    auto_extract: bool = Body(False, description="Auto extract database schema"),
    database_name: Optional[str] = Body(None, description="Database name"),
    ddl_content: Optional[str] = Body(None, description="DDL content"),
    skip_existing: bool = Body(True, description="Skip existing tables")
):
    """Train model with DDL (Data Definition Language) statements"""
    try:
        result = await text2sql_service.train_ddl(
            datasource_id=datasource_id,
            auto_extract=auto_extract,
            database_name=database_name,
            ddl_content=ddl_content,
            skip_existing=skip_existing
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to train DDL: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/train-documentation")
async def train_documentation(
    datasource_id: int = Body(..., description="Datasource ID"),
    documentation: str = Body(..., description="Documentation content"),
    doc_type: str = Body("general", description="Documentation type"),
    metadata: Optional[Dict[str, Any]] = Body(None, description="Additional metadata")
):
    """Train model with documentation content"""
    try:
        result = await text2sql_service.train_documentation(
            datasource_id=datasource_id,
            documentation=documentation,
            doc_type=doc_type,
            metadata=metadata or {}
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to train documentation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/train-sql")
async def train_sql(
    datasource_id: int = Body(..., description="Datasource ID"),
    sql_pairs: List[Dict[str, str]] = Body(..., description="SQL question-answer pairs")
):
    """Train model with SQL question-answer pairs"""
    try:
        result = await text2sql_service.train_sql_pairs(
            datasource_id=datasource_id,
            sql_pairs=sql_pairs
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to train SQL pairs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Advanced Features - Question Answer Mode

@router.post("/answer", response_model=QuestionAnswerResponse)
async def answer_question(request: QuestionAnswerRequest):
    """Answer natural language question with SQL generation and optional execution"""
    try:
        response = await text2sql_service.answer_question(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to answer question: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/batch-train")
async def batch_train_sql_pairs(request: BatchTrainingRequest):
    """Batch training with SQL question-answer pairs"""
    try:
        result = await text2sql_service.batch_train_sql_pairs(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to batch train SQL pairs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/generate-embeddings")
async def generate_embeddings(
    datasource_id: int = Body(..., description="Datasource ID"),
    training_data_ids: List[int] = Body(None, description="Specific training data IDs (optional)")
):
    """Generate embeddings for training data"""
    try:
        if training_data_ids:
            # Generate embeddings for specific training data
            result = await text2sql_service.generate_embeddings_for_training_data(
                datasource_id=datasource_id,
                training_data_ids=training_data_ids
            )
        else:
            # Generate embeddings for all training data of this datasource
            training_data, _ = await text2sql_service.get_training_data_list(
                datasource_id=datasource_id,
                limit=1000  # Get all training data
            )

            if not training_data:
                return {
                    "success": False,
                    "message": "No training data found for this datasource",
                    "task_id": None
                }

            result = await text2sql_service.generate_embeddings_for_training_data(
                datasource_id=datasource_id,
                training_data_ids=[data.id for data in training_data]
            )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/retrain-model")
async def retrain_model(
    datasource_id: int = Body(..., description="Datasource ID"),
    force_rebuild: bool = Body(False, description="Force rebuild all embeddings")
):
    """Retrain model for a datasource"""
    try:
        task_id = await text2sql_service.retrain_model(
            datasource_id=datasource_id,
            force_rebuild=force_rebuild
        )
        return {
            "success": True,
            "message": "Model retraining started",
            "task_id": task_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start model retraining: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Health Check Endpoint

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        health_status = await text2sql_service.health_check()
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "text2sql",
            "error": str(e)
        }
