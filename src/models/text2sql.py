# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Text2SQL models for Olight.

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
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


class TrainingDataType(str, Enum):
    """Training data content type"""
    DDL = "DDL"  # Data Definition Language (CREATE TABLE, etc.)
    DOCUMENTATION = "DOCUMENTATION"  # Documentation and descriptions
    SQL = "SQL"  # SQL query examples
    SCHEMA = "SCHEMA"  # Database schema information


class QueryComplexity(str, Enum):
    """Query complexity levels"""
    SIMPLE = "SIMPLE"
    MEDIUM = "MEDIUM"
    COMPLEX = "COMPLEX"


class TrainingSessionStatus(str, Enum):
    """Training session status"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class QueryHistory(BaseModel):
    """Query history model - matches database table structure"""
    id: int = Field(..., description="Query ID")
    user_question: str = Field(..., description="Natural language question")
    generated_sql: str = Field(..., description="Generated SQL query")
    datasource_id: int = Field(..., description="Database datasource ID")

    # Execution details
    status: QueryStatus = Field(default=QueryStatus.PENDING, description="Query status")
    execution_time_ms: Optional[int] = Field(None, description="Execution time in milliseconds")
    result_rows: Optional[int] = Field(None, description="Number of result rows")
    result_data: Optional[Dict[str, Any]] = Field(None, description="Query results (limited)")
    error_message: Optional[str] = Field(None, description="Error message if failed")

    # AI/ML details
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    model_used: Optional[str] = Field(None, description="AI model used")
    explanation: Optional[str] = Field(None, description="SQL explanation")
    similar_examples: Optional[Dict[str, Any]] = Field(None, description="Similar training examples used")

    # User feedback
    user_rating: Optional[int] = Field(None, ge=1, le=5, description="User rating (1-5)")
    user_feedback: Optional[str] = Field(None, description="User feedback text")

    # Timestamps
    created_at: datetime = Field(..., description="Creation time")


# TrainingData model removed - using VannaEmbedding directly


class SQLQueryCache(BaseModel):
    """SQL query cache model - matches database table structure"""
    id: int = Field(..., description="Cache ID")
    query_text: str = Field(..., description="Natural language query")
    sql_text: str = Field(..., description="Generated SQL")
    datasource_id: int = Field(..., description="Database datasource ID")

    # Query metadata
    table_names: Optional[List[str]] = Field(None, description="Tables used in the query")
    query_complexity: QueryComplexity = Field(default=QueryComplexity.SIMPLE, description="Query complexity")

    # Vector embedding
    embedding_model: Optional[str] = Field(None, description="Model used for embedding")

    # Usage statistics
    usage_count: int = Field(default=0, description="Usage count")
    last_used_at: Optional[datetime] = Field(None, description="Last used time")
    average_execution_time_ms: Optional[int] = Field(None, description="Average execution time")
    success_rate: float = Field(default=1.0, description="Success rate")

    # Timestamps
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")


class TrainingSession(BaseModel):
    """Training session model - matches database table structure"""
    id: int = Field(..., description="Session ID")
    datasource_id: int = Field(..., description="Database datasource ID")

    # Training details
    session_name: Optional[str] = Field(None, description="Session name")
    training_data_count: int = Field(default=0, description="Training data count")
    model_version: Optional[str] = Field(None, description="Model version")
    training_parameters: Optional[Dict[str, Any]] = Field(None, description="Training parameters")

    # Results
    status: TrainingSessionStatus = Field(default=TrainingSessionStatus.PENDING, description="Session status")
    accuracy_score: Optional[float] = Field(None, description="Accuracy score")
    validation_score: Optional[float] = Field(None, description="Validation score")
    training_time_seconds: Optional[int] = Field(None, description="Training time in seconds")

    # Metadata
    notes: Optional[str] = Field(None, description="Notes")
    error_message: Optional[str] = Field(None, description="Error message")

    # Timestamps
    started_at: datetime = Field(..., description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")


class VannaEmbedding(BaseModel):
    """Vanna embedding model for vector storage - matches ti-flow design"""
    id: int = Field(..., description="Embedding ID")
    datasource_id: int = Field(..., description="Database datasource ID")
    content: str = Field(..., description="Original content")
    content_type: TrainingDataType = Field(..., description="Content type")
    content_hash: str = Field(..., description="Content hash for deduplication")

    # Separate fields for different content types (like ti-flow)
    question: Optional[str] = Field(None, description="Natural language question (for SQL type)")
    sql_query: Optional[str] = Field(None, description="SQL query (for SQL type)")
    table_name: Optional[str] = Field(None, description="Table name (for DDL type)")
    column_name: Optional[str] = Field(None, description="Column name (for DDL type)")

    # Vector and metadata
    embedding_vector: Optional[List[float]] = Field(None, description="Embedding vector")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    # Timestamps
    created_at: datetime = Field(..., description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Update time")


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


class QuestionAnswerRequest(BaseModel):
    """Question answer request - combines SQL generation and execution"""
    question: str = Field(..., min_length=1, max_length=1000, description="Natural language question")
    datasource_id: int = Field(..., gt=0, description="Database datasource ID")
    execute_sql: bool = Field(default=True, description="Whether to execute the generated SQL")
    format_result: bool = Field(default=True, description="Whether to format the result")
    include_explanation: bool = Field(default=True, description="Whether to include explanation")
    embedding_model_id: Optional[int] = Field(None, description="Embedding model ID (optional)")


class QuestionAnswerResponse(BaseModel):
    """Question answer response"""
    question: str = Field(..., description="Original question")
    generated_sql: str = Field(..., description="Generated SQL query")
    explanation: Optional[str] = Field(None, description="SQL explanation")
    confidence_score: float = Field(..., description="AI confidence score")
    execution_result: Optional[SQLExecutionResponse] = Field(None, description="Execution result if executed")
    formatted_answer: Optional[str] = Field(None, description="Natural language answer")
    generation_time_ms: int = Field(..., description="Total processing time")


class SQLPair(BaseModel):
    """SQL question-answer pair for training"""
    question: str = Field(..., min_length=1, description="Natural language question")
    sql: str = Field(..., min_length=1, description="Corresponding SQL query")
    explanation: Optional[str] = Field(None, description="Optional explanation")


class BatchTrainingRequest(BaseModel):
    """Batch training request for SQL pairs"""
    datasource_id: int = Field(..., gt=0, description="Database datasource ID")
    database_name: Optional[str] = Field(None, description="Database name (for multi-database scenarios)")
    sql_pairs: List[SQLPair] = Field(..., min_length=1, description="List of SQL question-answer pairs")
    embedding_model_id: Optional[int] = Field(None, description="Embedding model ID (optional)")
    overwrite_existing: bool = Field(default=False, description="Whether to overwrite existing training data")


class TrainingDataRequest(BaseModel):
    """Training data request - matches VannaEmbedding structure"""
    datasource_id: int = Field(..., gt=0, description="Database datasource ID")
    content_type: TrainingDataType = Field(..., description="Training data type")
    content: str = Field(..., min_length=1, description="Training content")
    question: Optional[str] = Field(None, description="Natural language question (for SQL type)")
    sql_query: Optional[str] = Field(None, description="Corresponding SQL query (for SQL type)")
    table_name: Optional[str] = Field(None, description="Table name (for DDL type)")
    column_name: Optional[str] = Field(None, description="Column name (for DDL type)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class TrainingDataResponse(BaseModel):
    """Training data response - matches VannaEmbedding structure"""
    id: int = Field(..., description="Training data ID")
    datasource_id: int = Field(..., description="Database datasource ID")
    content: str = Field(..., description="Original content")
    content_type: TrainingDataType = Field(..., description="Content type")
    content_hash: str = Field(..., description="Content hash for deduplication")

    # Separate fields for different content types (like VannaEmbedding)
    question: Optional[str] = Field(None, description="Natural language question (for SQL type)")
    sql_query: Optional[str] = Field(None, description="SQL query (for SQL type)")
    table_name: Optional[str] = Field(None, description="Table name (for DDL type)")
    column_name: Optional[str] = Field(None, description="Column name (for DDL type)")

    # Vector and metadata
    embedding_vector: Optional[List[float]] = Field(None, description="Embedding vector")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    # Timestamps
    created_at: datetime = Field(..., description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Update time")


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


class TrainingSessionRequest(BaseModel):
    """Training session request"""
    datasource_id: int = Field(..., gt=0, description="Database datasource ID")
    session_name: Optional[str] = Field(None, description="Session name")
    model_version: Optional[str] = Field(None, description="Model version")
    training_parameters: Optional[Dict[str, Any]] = Field(None, description="Training parameters")
    notes: Optional[str] = Field(None, description="Notes")


class TrainingSessionResponse(BaseModel):
    """Training session response"""
    id: int = Field(..., description="Session ID")
    datasource_id: int = Field(..., description="Database datasource ID")
    session_name: Optional[str] = Field(None, description="Session name")
    training_data_count: int = Field(..., description="Training data count")
    model_version: Optional[str] = Field(None, description="Model version")
    training_parameters: Optional[Dict[str, Any]] = Field(None, description="Training parameters")
    status: TrainingSessionStatus = Field(..., description="Session status")
    accuracy_score: Optional[float] = Field(None, description="Accuracy score")
    validation_score: Optional[float] = Field(None, description="Validation score")
    training_time_seconds: Optional[int] = Field(None, description="Training time in seconds")
    notes: Optional[str] = Field(None, description="Notes")
    error_message: Optional[str] = Field(None, description="Error message")
    started_at: datetime = Field(..., description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")


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
