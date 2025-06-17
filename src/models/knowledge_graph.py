# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Knowledge Graph models for DeerFlow.

Provides data models for knowledge graph entities, relations, queries, and statistics.
Inspired by graph-rag-agent architecture with DeerFlow-specific adaptations.
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


# Enums for status and types
class QueryStatus(str, Enum):
    """Knowledge graph query status"""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


class QueryType(str, Enum):
    """Knowledge graph query types"""
    GRAPH_QA = "GRAPH_QA"           # Graph-based question answering
    LOCAL_SEARCH = "LOCAL_SEARCH"   # Local vector search
    GLOBAL_SEARCH = "GLOBAL_SEARCH" # Global community search
    HYBRID_SEARCH = "HYBRID_SEARCH" # Hybrid search strategy
    DEEP_RESEARCH = "DEEP_RESEARCH" # Deep research with reasoning


class BuildTaskStatus(str, Enum):
    """Build task status"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ConflictStrategy(str, Enum):
    """Conflict resolution strategies"""
    MANUAL_FIRST = "manual_first"   # Prioritize manual edits
    AUTO_FIRST = "auto_first"       # Prioritize automatic updates
    MERGE = "merge"                 # Attempt to merge


# Core data models
class KnowledgeGraphEntity(BaseModel):
    """Knowledge graph entity model"""
    id: Optional[int] = None
    datasource_id: int = Field(..., gt=0, description="Database datasource ID")
    entity_id: str = Field(..., min_length=1, max_length=255, description="Unique entity identifier")
    entity_type: str = Field(..., min_length=1, max_length=100, description="Entity type")
    entity_name: str = Field(..., min_length=1, max_length=500, description="Entity display name")
    entity_label: Optional[str] = Field(None, max_length=500, description="Alternative label")
    
    # Properties and metadata
    properties: Dict[str, Any] = Field(default_factory=dict, description="Entity properties")
    description: Optional[str] = Field(None, description="Human-readable description")
    
    # Vector embedding info
    embedding: Optional[List[float]] = Field(None, description="Vector embedding")
    embedding_model: Optional[str] = Field(None, max_length=100, description="Embedding model used")
    
    # Source information
    source_table: Optional[str] = Field(None, max_length=255, description="Source database table")
    source_column: Optional[str] = Field(None, max_length=255, description="Source database column")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    
    # Neo4j integration
    neo4j_node_id: Optional[int] = Field(None, description="Neo4j node ID for synchronization")
    
    # Status
    is_active: bool = Field(default=True, description="Whether entity is active")
    is_verified: bool = Field(default=False, description="Whether entity is verified")
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class KnowledgeGraphRelation(BaseModel):
    """Knowledge graph relation model"""
    id: Optional[int] = None
    datasource_id: int = Field(..., gt=0, description="Database datasource ID")
    relation_id: str = Field(..., min_length=1, max_length=255, description="Unique relation identifier")
    relation_type: str = Field(..., min_length=1, max_length=100, description="Relation type")
    relation_name: str = Field(..., min_length=1, max_length=500, description="Relation display name")
    
    # Connected entities
    source_entity_id: int = Field(..., description="Source entity ID")
    target_entity_id: int = Field(..., description="Target entity ID")
    
    # Properties and metadata
    properties: Dict[str, Any] = Field(default_factory=dict, description="Relation properties")
    description: Optional[str] = Field(None, description="Human-readable description")
    weight: float = Field(default=1.0, description="Relation strength/weight")
    
    # Vector embedding info
    embedding: Optional[List[float]] = Field(None, description="Vector embedding")
    embedding_model: Optional[str] = Field(None, max_length=100, description="Embedding model used")
    
    # Source information
    source_table: Optional[str] = Field(None, max_length=255, description="Source database table")
    source_columns: Optional[List[str]] = Field(None, description="Source database columns")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    
    # Neo4j integration
    neo4j_relationship_id: Optional[int] = Field(None, description="Neo4j relationship ID for synchronization")
    
    # Status
    is_active: bool = Field(default=True, description="Whether relation is active")
    is_verified: bool = Field(default=False, description="Whether relation is verified")
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class KnowledgeGraphQuery(BaseModel):
    """Knowledge graph query model"""
    id: Optional[int] = None
    datasource_id: int = Field(..., gt=0, description="Database datasource ID")
    
    # Query information
    user_question: str = Field(..., min_length=1, description="Original user question")
    processed_question: Optional[str] = Field(None, description="Processed/normalized question")
    query_type: QueryType = Field(default=QueryType.GRAPH_QA, description="Type of query")
    
    # Graph query details
    graph_query: Optional[Dict[str, Any]] = Field(None, description="Graph traversal query")
    entities_involved: Optional[List[int]] = Field(None, description="Entity IDs involved")
    relations_involved: Optional[List[int]] = Field(None, description="Relation IDs involved")
    
    # Results
    answer: Optional[str] = Field(None, description="Generated answer")
    result_entities: Optional[Dict[str, Any]] = Field(None, description="Entities in result")
    result_relations: Optional[Dict[str, Any]] = Field(None, description="Relations in result")
    result_paths: Optional[Dict[str, Any]] = Field(None, description="Graph paths found")
    reasoning_chain: Optional[Dict[str, Any]] = Field(None, description="Step-by-step reasoning process")
    
    # Execution details
    status: QueryStatus = Field(default=QueryStatus.PENDING, description="Query status")
    execution_time_ms: Optional[int] = Field(None, description="Execution time in milliseconds")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    
    # AI/ML details
    model_used: Optional[str] = Field(None, max_length=100, description="Model used for generation")
    explanation: Optional[str] = Field(None, description="Explanation of answer derivation")
    evidence_sources: Optional[Dict[str, Any]] = Field(None, description="Sources of evidence used")
    
    # Vector embedding
    question_embedding: Optional[List[float]] = Field(None, description="Question embedding")
    embedding_model: Optional[str] = Field(None, max_length=100, description="Embedding model used")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class KnowledgeGraphCommunity(BaseModel):
    """Knowledge graph community model"""
    id: Optional[int] = None
    datasource_id: int = Field(..., gt=0, description="Database datasource ID")
    
    # Community information
    community_id: str = Field(..., min_length=1, max_length=255, description="Unique community identifier")
    community_name: Optional[str] = Field(None, max_length=500, description="Human-readable name")
    community_type: Optional[str] = Field(None, max_length=100, description="Type of community")
    
    # Community content
    entity_ids: Optional[List[int]] = Field(None, description="Array of entity IDs in this community")
    summary: Optional[str] = Field(None, description="Community summary")
    keywords: Optional[List[str]] = Field(None, description="Key terms representing this community")
    
    # Statistics
    entity_count: int = Field(default=0, description="Number of entities in community")
    relation_count: int = Field(default=0, description="Number of relations in community")
    centrality_score: Optional[float] = Field(None, description="Community importance score")
    
    # Vector embedding
    embedding: Optional[List[float]] = Field(None, description="Community embedding")
    embedding_model: Optional[str] = Field(None, max_length=100, description="Embedding model used")
    
    # Neo4j integration
    neo4j_community_id: Optional[int] = Field(None, description="Neo4j community ID")
    
    # Detection metadata
    algorithm_used: Optional[str] = Field(None, max_length=50, description="Algorithm used for detection")
    detection_parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters used in detection")
    
    # Status
    is_active: bool = Field(default=True, description="Whether community is active")
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class KnowledgeGraphBuildTask(BaseModel):
    """Knowledge graph build task model"""
    id: Optional[int] = None
    task_id: str = Field(..., min_length=1, max_length=255, description="UUID for task tracking")
    datasource_id: int = Field(..., gt=0, description="Database datasource ID")

    # Task configuration
    entity_types: List[str] = Field(..., min_items=1, description="Entity types to extract")
    relation_types: List[str] = Field(..., min_items=1, description="Relation types to extract")
    chunk_size: int = Field(default=500, ge=100, le=2000, description="Text chunk size")
    overlap: int = Field(default=100, ge=0, le=500, description="Chunk overlap")
    similarity_threshold: float = Field(default=0.9, ge=0.0, le=1.0, description="Similarity threshold")
    conflict_strategy: ConflictStrategy = Field(default=ConflictStrategy.MANUAL_FIRST)

    # Processing options
    enable_community_detection: bool = Field(default=True, description="Enable community detection")
    community_algorithm: str = Field(default="leiden", description="Community detection algorithm")
    incremental_update: bool = Field(default=False, description="Incremental update mode")

    # Progress tracking
    status: BuildTaskStatus = Field(default=BuildTaskStatus.PENDING, description="Task status")
    total_chunks: Optional[int] = Field(None, description="Total chunks to process")
    processed_chunks: int = Field(default=0, description="Processed chunks")
    entities_extracted: int = Field(default=0, description="Entities extracted")
    relations_extracted: int = Field(default=0, description="Relations extracted")
    communities_detected: int = Field(default=0, description="Communities detected")

    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None

    # Results
    build_summary: Optional[Dict[str, Any]] = Field(None, description="Summary of build results")
    error_message: Optional[str] = Field(None, description="Error message if failed")

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class KnowledgeGraphStatistics(BaseModel):
    """Knowledge graph statistics model"""
    id: Optional[int] = None
    datasource_id: int = Field(..., gt=0, description="Database datasource ID")

    # Graph statistics
    total_entities: int = Field(default=0, description="Total number of entities")
    total_relations: int = Field(default=0, description="Total number of relations")
    total_communities: int = Field(default=0, description="Total number of communities")
    entity_types: Optional[Dict[str, int]] = Field(None, description="Count by entity type")
    relation_types: Optional[Dict[str, int]] = Field(None, description="Count by relation type")

    # Quality metrics
    verified_entities: int = Field(default=0, description="Number of verified entities")
    verified_relations: int = Field(default=0, description="Number of verified relations")
    avg_confidence_score: Optional[float] = Field(None, description="Average confidence score")

    # Query statistics
    total_queries: int = Field(default=0, description="Total number of queries")
    successful_queries: int = Field(default=0, description="Number of successful queries")
    avg_query_time_ms: Optional[float] = Field(None, description="Average query time")
    query_types_distribution: Optional[Dict[str, int]] = Field(None, description="Distribution of query types")

    # Performance metrics
    avg_local_search_time_ms: Optional[float] = Field(None, description="Average local search time")
    avg_global_search_time_ms: Optional[float] = Field(None, description="Average global search time")
    avg_hybrid_search_time_ms: Optional[float] = Field(None, description="Average hybrid search time")
    avg_deep_research_time_ms: Optional[float] = Field(None, description="Average deep research time")

    # Timestamp
    calculated_at: Optional[datetime] = None


# Request/Response models for API
class KnowledgeGraphQueryRequest(BaseModel):
    """Knowledge graph query request"""
    question: str = Field(..., min_length=1, max_length=1000, description="User question")
    datasource_id: int = Field(..., gt=0, description="Database datasource ID")
    query_type: QueryType = Field(default=QueryType.GRAPH_QA, description="Query type")
    include_explanation: bool = Field(default=True, description="Include explanation")
    include_paths: bool = Field(default=True, description="Include graph paths")
    max_entities: int = Field(default=10, ge=1, le=100, description="Max entities to return")
    max_relations: int = Field(default=10, ge=1, le=100, description="Max relations to return")


class KnowledgeGraphQueryResponse(BaseModel):
    """Knowledge graph query response"""
    query_id: int = Field(..., description="Query ID")
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="Generated answer")
    query_type: QueryType = Field(..., description="Query type used")

    # Results
    entities_found: List[Dict[str, Any]] = Field(default_factory=list, description="Entities found")
    relations_found: List[Dict[str, Any]] = Field(default_factory=list, description="Relations found")
    graph_paths: Optional[List[Dict[str, Any]]] = Field(None, description="Graph paths")
    reasoning_chain: Optional[List[Dict[str, Any]]] = Field(None, description="Reasoning steps")

    # Execution details
    execution_time_ms: int = Field(..., description="Execution time")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    explanation: Optional[str] = Field(None, description="Explanation")

    # Metadata
    model_used: Optional[str] = Field(None, description="Model used")
    entities_count: int = Field(..., description="Number of entities involved")
    relations_count: int = Field(..., description="Number of relations involved")


class GraphBuildRequest(BaseModel):
    """Knowledge graph build request"""
    datasource_id: int = Field(..., gt=0, description="Database datasource ID")
    entity_types: List[str] = Field(..., min_items=1, description="Entity types to extract")
    relation_types: List[str] = Field(..., min_items=1, description="Relation types to extract")

    # Processing options
    chunk_size: int = Field(default=500, ge=100, le=2000, description="Text chunk size")
    overlap: int = Field(default=100, ge=0, le=500, description="Chunk overlap")
    similarity_threshold: float = Field(default=0.9, ge=0.0, le=1.0, description="Similarity threshold")
    conflict_strategy: ConflictStrategy = Field(default=ConflictStrategy.MANUAL_FIRST)

    # Advanced options
    enable_community_detection: bool = Field(default=True, description="Enable community detection")
    community_algorithm: str = Field(default="leiden", description="Community detection algorithm")
    incremental_update: bool = Field(default=False, description="Incremental update mode")


class GraphBuildResponse(BaseModel):
    """Knowledge graph build response"""
    task_id: str = Field(..., description="Build task ID")
    datasource_id: int = Field(..., description="Database datasource ID")
    status: str = Field(..., description="Build status")

    # Progress information
    total_chunks: Optional[int] = Field(None, description="Total text chunks to process")
    processed_chunks: Optional[int] = Field(None, description="Processed chunks")
    entities_extracted: Optional[int] = Field(None, description="Entities extracted")
    relations_extracted: Optional[int] = Field(None, description="Relations extracted")
    communities_detected: Optional[int] = Field(None, description="Communities detected")

    # Timing
    started_at: datetime = Field(..., description="Build start time")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")

    # Results (when completed)
    build_summary: Optional[Dict[str, Any]] = Field(None, description="Build summary")
    error_message: Optional[str] = Field(None, description="Error message if failed")
