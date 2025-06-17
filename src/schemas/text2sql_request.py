# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Text2SQL request/response models for Olight API.
Following deer-flow's API pattern with separate request/response files.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from src.models.text2sql import (
    SQLGenerationRequest,
    SQLGenerationResponse,
    SQLExecutionRequest,
    SQLExecutionResponse,
    TrainingDataRequest,
    TrainingDataResponse,
    TrainingDataListResponse,
    QueryHistoryListResponse,
    RetrainRequest,
    RetrainResponse,
    Text2SQLStatistics,
    QueryStatus,
    TrainingDataType,
)


# API Request Models

class Text2SQLGenerationRequest(SQLGenerationRequest):
    """Text2SQL generation API request - inherits from model"""
    pass


class Text2SQLExecutionRequest(SQLExecutionRequest):
    """Text2SQL execution API request - inherits from model"""
    pass


class Text2SQLTrainingDataRequest(TrainingDataRequest):
    """Text2SQL training data API request - inherits from model"""
    pass


class Text2SQLRetrainRequest(RetrainRequest):
    """Text2SQL retrain API request - inherits from model"""
    pass


class Text2SQLQueryHistoryRequest(BaseModel):
    """Text2SQL query history request"""
    datasource_id: Optional[int] = Field(None, description="Filter by datasource ID")
    status: Optional[QueryStatus] = Field(None, description="Filter by query status")
    limit: int = Field(50, ge=1, le=200, description="Items per page")
    offset: int = Field(0, ge=0, description="Offset for pagination")


class Text2SQLTrainingDataListRequest(BaseModel):
    """Text2SQL training data list request"""
    datasource_id: int = Field(..., gt=0, description="Datasource ID")
    content_type: Optional[TrainingDataType] = Field(None, description="Filter by content type")
    limit: int = Field(50, ge=1, le=200, description="Items per page")
    offset: int = Field(0, ge=0, description="Offset for pagination")


class Text2SQLStatisticsRequest(BaseModel):
    """Text2SQL statistics request"""
    datasource_id: Optional[int] = Field(None, description="Filter by datasource ID")


# API Response Models

class Text2SQLGenerationResponse(SQLGenerationResponse):
    """Text2SQL generation API response - inherits from model"""
    pass


class Text2SQLExecutionResponse(SQLExecutionResponse):
    """Text2SQL execution API response - inherits from model"""
    pass


class Text2SQLTrainingDataResponse(TrainingDataResponse):
    """Text2SQL training data API response - inherits from model"""
    pass


class Text2SQLTrainingDataListResponse(TrainingDataListResponse):
    """Text2SQL training data list API response - inherits from model"""
    pass


class Text2SQLQueryHistoryListResponse(QueryHistoryListResponse):
    """Text2SQL query history list API response - inherits from model"""
    pass


class Text2SQLRetrainResponse(RetrainResponse):
    """Text2SQL retrain API response - inherits from model"""
    pass


class Text2SQLStatisticsResponse(Text2SQLStatistics):
    """Text2SQL statistics API response - inherits from model"""
    pass


class Text2SQLDeleteResponse(BaseModel):
    """Text2SQL delete response"""
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Status message")


# Bulk operation models

class Text2SQLBulkTrainingRequest(BaseModel):
    """Bulk training data request"""
    datasource_id: int = Field(..., gt=0, description="Datasource ID")
    training_items: List[TrainingDataRequest] = Field(..., description="List of training data items")
    auto_retrain: bool = Field(default=False, description="Automatically retrain after adding data")


class Text2SQLBulkTrainingResponse(BaseModel):
    """Bulk training data response"""
    success_count: int = Field(..., description="Number of successfully added items")
    failed_count: int = Field(..., description="Number of failed items")
    training_data_ids: List[int] = Field(..., description="IDs of successfully added training data")
    errors: List[str] = Field(default_factory=list, description="Error messages for failed items")
    retrain_task_id: Optional[str] = Field(None, description="Retrain task ID if auto_retrain was enabled")


# Schema extraction models

class Text2SQLSchemaExtractionRequest(BaseModel):
    """Schema extraction request for training"""
    datasource_id: int = Field(..., gt=0, description="Datasource ID")
    include_sample_data: bool = Field(default=False, description="Include sample data in training")
    max_samples_per_table: int = Field(default=3, ge=0, le=10, description="Max sample rows per table")


class Text2SQLSchemaExtractionResponse(BaseModel):
    """Schema extraction response"""
    training_data_id: int = Field(..., description="Generated training data ID")
    tables_processed: int = Field(..., description="Number of tables processed")
    content_preview: str = Field(..., description="Preview of generated training content")


# Query suggestion models

class Text2SQLSuggestionRequest(BaseModel):
    """Query suggestion request"""
    datasource_id: int = Field(..., gt=0, description="Datasource ID")
    partial_question: str = Field(..., min_length=1, max_length=500, description="Partial question")
    max_suggestions: int = Field(default=5, ge=1, le=10, description="Maximum number of suggestions")


class Text2SQLSuggestionResponse(BaseModel):
    """Query suggestion response"""
    suggestions: List[str] = Field(..., description="List of suggested questions")
    confidence_scores: List[float] = Field(..., description="Confidence scores for suggestions")


# Model performance models

class Text2SQLPerformanceRequest(BaseModel):
    """Performance metrics request"""
    datasource_id: int = Field(..., gt=0, description="Datasource ID")
    start_date: Optional[str] = Field(None, description="Start date for metrics (ISO format)")
    end_date: Optional[str] = Field(None, description="End date for metrics (ISO format)")


class Text2SQLPerformanceResponse(BaseModel):
    """Performance metrics response"""
    total_queries: int = Field(..., description="Total queries in period")
    success_rate: float = Field(..., description="Success rate (0.0 to 1.0)")
    average_execution_time_ms: Optional[float] = Field(None, description="Average execution time")
    average_confidence_score: Optional[float] = Field(None, description="Average confidence score")
    most_common_errors: List[str] = Field(..., description="Most common error messages")
    query_complexity_distribution: dict = Field(..., description="Distribution of query complexity")


# Export request models

class Text2SQLExportRequest(BaseModel):
    """Export request for training data or queries"""
    datasource_id: int = Field(..., gt=0, description="Datasource ID")
    export_type: str = Field(..., description="Export type: 'training_data' or 'query_history'")
    format: str = Field(default="json", description="Export format: 'json' or 'csv'")
    include_metadata: bool = Field(default=True, description="Include metadata in export")


class Text2SQLExportResponse(BaseModel):
    """Export response"""
    download_url: str = Field(..., description="URL to download the exported file")
    file_size_bytes: int = Field(..., description="File size in bytes")
    record_count: int = Field(..., description="Number of records exported")
    expires_at: str = Field(..., description="Download URL expiration time")
