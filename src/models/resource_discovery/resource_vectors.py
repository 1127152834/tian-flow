"""
资源向量存储模型

基于 Ti-Flow 的 resource_vectors 表设计
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import DateTime, Text, ForeignKey
from pgvector.sqlalchemy import Vector


class VectorType(str, Enum):
    """向量类型枚举"""
    NAME = "name"
    DESCRIPTION = "description"
    CAPABILITIES = "capabilities"
    COMPOSITE = "composite"


class ResourceVectorBase(SQLModel):
    """资源向量基础模型"""
    resource_id: str = Field(max_length=255, description="资源ID")
    vector_type: VectorType = Field(description="向量类型")
    content: str = Field(sa_column=Column(Text), description="原始文本内容")
    embedding_dimension: int = Field(default=1536, description="向量维度")
    embedding_model_name: Optional[str] = Field(default=None, max_length=100, description="使用的Embedding模型名称")
    vector_norm: Optional[float] = Field(default=None, description="向量范数")


class ResourceVector(ResourceVectorBase, table=True):
    """资源向量存储模型"""
    __tablename__ = "resource_vectors"
    __table_args__ = {"schema": "resource_discovery"}
    
    id: Optional[int] = Field(default=None, primary_key=True, description="向量记录ID")
    
    # 向量数据 (使用 pgvector)
    embedding: Optional[List[float]] = Field(
        default=None,
        sa_column=Column(Vector(1536)),
        description="向量数据"
    )
    
    # 时间戳
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True)),
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True)),
        description="更新时间"
    )


class ResourceVectorCreate(ResourceVectorBase):
    """创建资源向量请求模型"""
    embedding: List[float] = Field(description="向量数据")


class ResourceVectorResponse(ResourceVectorBase):
    """资源向量响应模型"""
    id: int = Field(description="向量记录ID")
    embedding: Optional[List[float]] = Field(description="向量数据")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class VectorSearchRequest(SQLModel):
    """向量搜索请求模型"""
    query_text: str = Field(description="查询文本")
    vector_types: Optional[List[VectorType]] = Field(default=None, description="搜索的向量类型")
    top_k: int = Field(default=10, ge=1, le=100, description="返回结果数量")
    similarity_threshold: float = Field(default=0.3, ge=0.0, le=1.0, description="相似度阈值")


class VectorSearchResult(SQLModel):
    """向量搜索结果模型"""
    resource_id: str = Field(description="资源ID")
    vector_type: VectorType = Field(description="向量类型")
    content: str = Field(description="原始文本内容")
    similarity_score: float = Field(description="相似度分数")
    embedding_model_name: Optional[str] = Field(description="使用的Embedding模型名称")


class VectorSearchResponse(SQLModel):
    """向量搜索响应模型"""
    query: str = Field(description="查询文本")
    results: List[VectorSearchResult] = Field(description="搜索结果")
    total_results: int = Field(description="总结果数")
    processing_time_ms: float = Field(description="处理时间(毫秒)")


class VectorizationTask(SQLModel):
    """向量化任务模型"""
    resource_id: str = Field(description="资源ID")
    force_update: bool = Field(default=False, description="是否强制更新")
    vector_types: Optional[List[VectorType]] = Field(default=None, description="需要向量化的类型")


class VectorizationResult(SQLModel):
    """向量化结果模型"""
    resource_id: str = Field(description="资源ID")
    success: bool = Field(description="是否成功")
    vectors_created: List[VectorType] = Field(description="创建的向量类型")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    processing_time_ms: float = Field(description="处理时间(毫秒)")


class BatchVectorizationRequest(SQLModel):
    """批量向量化请求模型"""
    resource_ids: List[str] = Field(description="资源ID列表")
    force_update: bool = Field(default=False, description="是否强制更新")
    vector_types: Optional[List[VectorType]] = Field(default=None, description="需要向量化的类型")
    max_concurrent: int = Field(default=5, ge=1, le=20, description="最大并发数")


class BatchVectorizationResponse(SQLModel):
    """批量向量化响应模型"""
    total_resources: int = Field(description="总资源数")
    successful_resources: int = Field(description="成功资源数")
    failed_resources: int = Field(description="失败资源数")
    results: List[VectorizationResult] = Field(description="详细结果")
    total_processing_time_ms: float = Field(description="总处理时间(毫秒)")
    timestamp: datetime = Field(description="完成时间戳")
