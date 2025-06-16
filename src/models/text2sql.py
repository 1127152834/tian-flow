# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Text2SQL models for DeerFlow.

Provides data models for SQL query generation, training data management,
and query history tracking. Adapted from ti-flow but uses configuration-based storage.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class QueryStatus(str, Enum):
    """Query execution status"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    CANCELLED = "CANCELLED"


class TrainingDataType(str, Enum):
    """Training data type"""
    DDL = "DDL"  # Database schema/structure
    DOCUMENTATION = "DOCUMENTATION"  # Business documentation
    SQL_PAIR = "SQL_PAIR"  # Question-SQL pairs


class SQLQuery(BaseModel):
    """SQL query model"""
    id: int = Field(..., description="Query ID")
    question: str = Field(..., max_length=2000, description="Natural language question")
    generated_sql: str = Field(..., description="Generated SQL query")
    datasource_id: int = Field(..., description="Database datasource ID")
    status: QueryStatus = Field(default=QueryStatus.PENDING, description="Query status")
    execution_time_ms: Optional[int] = Field(None, description="Execution time in milliseconds")
    result_rows: Optional[int] = Field(None, description="Number of result rows")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    explanation: Optional[str] = Field(None, description="SQL explanation")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    created_at: datetime = Field(..., description="Creation time")
    executed_at: Optional[datetime] = Field(None, description="Execution time")


class QueryHistory(BaseModel):
    """Query history model"""
    id: int = Field(..., description="History ID")
    query_id: int = Field(..., description="Related query ID")
    question: str = Field(..., description="Original question")
    generated_sql: str = Field(..., description="Generated SQL")
    datasource_id: int = Field(..., description="Database datasource ID")
    datasource_name: str = Field(..., description="Database datasource name")
    status: QueryStatus = Field(..., description="Query status")
    execution_time_ms: Optional[int] = Field(None, description="Execution time")
    result_rows: Optional[int] = Field(None, description="Number of result rows")
    error_message: Optional[str] = Field(None, description="Error message")
    confidence_score: Optional[float] = Field(None, description="Confidence score")
    created_at: datetime = Field(..., description="Creation time")


class TrainingData(BaseModel):
    """Training data model"""
    id: int = Field(..., description="Training data ID")
    datasource_id: int = Field(..., description="Database datasource ID")
    content_type: TrainingDataType = Field(..., description="Training data type")
    content: str = Field(..., description="Training content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    is_active: bool = Field(default=True, description="Whether this training data is active")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")


class VannaEmbedding(BaseModel):
    """Vanna embedding model for vector storage"""
    id: int = Field(..., description="Embedding ID")
    datasource_id: int = Field(..., description="Database datasource ID")
    content: str = Field(..., description="Original content")
    content_type: TrainingDataType = Field(..., description="Content type")
    embedding_vector: List[float] = Field(..., description="Embedding vector")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation time")


# Request/Response Models

class SQLGenerationRequest(BaseModel):
    """SQL generation request"""
    question: str = Field(..., min_length=1, max_length=2000, description="Natural language question")
    datasource_id: int = Field(..., gt=0, description="Database datasource ID")
    include_explanation: bool = Field(default=True, description="Include SQL explanation")
    max_examples: int = Field(default=5, ge=1, le=20, description="Maximum training examples to use")


class SQLGenerationResponse(BaseModel):
    """SQL generation response"""
    query_id: int = Field(..., description="Generated query ID")
    question: str = Field(..., description="Original question")
    generated_sql: str = Field(..., description="Generated SQL query")
    explanation: Optional[str] = Field(None, description="SQL explanation")
    confidence_score: Optional[float] = Field(None, description="Confidence score")
    similar_examples: List[Dict[str, Any]] = Field(default_factory=list, description="Similar training examples used")
    generation_time_ms: int = Field(..., description="Generation time in milliseconds")


class SQLExecutionRequest(BaseModel):
    """SQL execution request"""
    query_id: int = Field(..., gt=0, description="Query ID to execute")
    limit: int = Field(default=100, ge=1, le=10000, description="Result limit")


class SQLExecutionResponse(BaseModel):
    """SQL execution response"""
    query_id: int = Field(..., description="Query ID")
    status: QueryStatus = Field(..., description="Execution status")
    result_data: Optional[List[Dict[str, Any]]] = Field(None, description="Query results")
    result_rows: Optional[int] = Field(None, description="Number of result rows")
    execution_time_ms: Optional[int] = Field(None, description="Execution time")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class TrainingDataRequest(BaseModel):
    """Training data request"""
    datasource_id: int = Field(..., gt=0, description="Database datasource ID")
    content_type: TrainingDataType = Field(..., description="Training data type")
    content: str = Field(..., min_length=1, description="Training content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class TrainingDataResponse(BaseModel):
    """Training data response"""
    id: int = Field(..., description="Training data ID")
    datasource_id: int = Field(..., description="Database datasource ID")
    content_type: TrainingDataType = Field(..., description="Training data type")
    content: str = Field(..., description="Training content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    is_active: bool = Field(..., description="Whether active")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")


class TrainingDataListResponse(BaseModel):
    """Training data list response"""
    training_data: List[TrainingDataResponse] = Field(..., description="Training data list")
    total: int = Field(..., description="Total count")
    limit: int = Field(..., description="Page limit")
    offset: int = Field(..., description="Page offset")


class QueryHistoryListResponse(BaseModel):
    """Query history list response"""
    queries: List[QueryHistory] = Field(..., description="Query history list")
    total: int = Field(..., description="Total count")
    limit: int = Field(..., description="Page limit")
    offset: int = Field(..., description="Page offset")


class RetrainRequest(BaseModel):
    """Model retrain request"""
    datasource_id: int = Field(..., gt=0, description="Database datasource ID")
    force_rebuild: bool = Field(default=False, description="Force rebuild all embeddings")


class RetrainResponse(BaseModel):
    """Model retrain response"""
    task_id: str = Field(..., description="Background task ID")
    message: str = Field(..., description="Status message")
    estimated_time_minutes: Optional[int] = Field(None, description="Estimated completion time")


class Text2SQLStatistics(BaseModel):
    """Text2SQL statistics"""
    total_queries: int = Field(..., description="Total queries generated")
    successful_queries: int = Field(..., description="Successful queries")
    failed_queries: int = Field(..., description="Failed queries")
    average_confidence: Optional[float] = Field(None, description="Average confidence score")
    total_training_data: int = Field(..., description="Total training data items")
    training_data_by_type: Dict[str, int] = Field(..., description="Training data count by type")
    last_query_time: Optional[datetime] = Field(None, description="Last query time")
    last_training_time: Optional[datetime] = Field(None, description="Last training time")
