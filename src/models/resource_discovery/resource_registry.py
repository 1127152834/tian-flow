"""
资源注册表模型

基于 Ti-Flow 的 resource_registry 表设计
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from sqlmodel import SQLModel, Field, Column, JSON
from sqlalchemy import DateTime, Text


class ResourceType(str, Enum):
    """资源类型枚举"""
    DATABASE = "database"
    API = "api"
    TOOL = "tool"
    KNOWLEDGE_BASE = "knowledge_base"
    TEXT2SQL = "text2sql"


class ResourceStatus(str, Enum):
    """资源状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class VectorizationStatus(str, Enum):
    """向量化状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ResourceRegistryBase(SQLModel):
    """资源注册表基础模型"""
    resource_id: str = Field(unique=True, max_length=255, description="资源唯一标识")
    resource_name: str = Field(max_length=255, description="资源名称")
    resource_type: ResourceType = Field(description="资源类型")
    description: Optional[str] = Field(default=None, sa_column=Column(Text), description="资源描述")
    capabilities: Optional[List[str]] = Field(default=None, sa_column=Column(JSON), description="资源能力列表")
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON), description="资源标签")
    resource_metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="资源元数据")
    
    # 资源可用性
    is_active: bool = Field(default=True, description="是否激活")
    status: ResourceStatus = Field(default=ResourceStatus.ACTIVE, description="资源状态")
    
    # 引用关系
    source_table: Optional[str] = Field(default=None, max_length=100, description="原始数据表名")
    source_id: Optional[int] = Field(default=None, description="原始数据ID")
    
    # 向量化状态
    vectorization_status: VectorizationStatus = Field(default=VectorizationStatus.PENDING, description="向量化状态")
    
    # 性能指标
    usage_count: int = Field(default=0, description="使用次数")
    success_rate: float = Field(default=1.0, description="成功率")
    avg_response_time: int = Field(default=0, description="平均响应时间(毫秒)")


class ResourceRegistry(ResourceRegistryBase, table=True):
    """资源注册表模型"""
    __tablename__ = "resource_registry"
    __table_args__ = {"schema": "resource_discovery"}
    
    id: Optional[int] = Field(default=None, primary_key=True, description="资源ID")
    
    # 时间戳
    vector_updated_at: Optional[datetime] = Field(
        default=None, 
        sa_column=Column(DateTime(timezone=True)), 
        description="向量最后更新时间"
    )
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


class ResourceRegistryCreate(ResourceRegistryBase):
    """创建资源注册表请求模型"""
    pass


class ResourceRegistryUpdate(SQLModel):
    """更新资源注册表请求模型"""
    resource_name: Optional[str] = Field(default=None, max_length=255, description="资源名称")
    description: Optional[str] = Field(default=None, description="资源描述")
    capabilities: Optional[List[str]] = Field(default=None, description="资源能力列表")
    tags: Optional[List[str]] = Field(default=None, description="资源标签")
    resource_metadata: Optional[Dict[str, Any]] = Field(default=None, description="资源元数据")
    is_active: Optional[bool] = Field(default=None, description="是否激活")
    status: Optional[ResourceStatus] = Field(default=None, description="资源状态")
    vectorization_status: Optional[VectorizationStatus] = Field(default=None, description="向量化状态")
    usage_count: Optional[int] = Field(default=None, description="使用次数")
    success_rate: Optional[float] = Field(default=None, description="成功率")
    avg_response_time: Optional[int] = Field(default=None, description="平均响应时间(毫秒)")


class ResourceRegistryResponse(ResourceRegistryBase):
    """资源注册表响应模型"""
    id: int = Field(description="资源ID")
    vector_updated_at: Optional[datetime] = Field(description="向量最后更新时间")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class ResourceMatch(SQLModel):
    """资源匹配结果模型"""
    resource: ResourceRegistryResponse = Field(description="匹配的资源")
    similarity_score: float = Field(description="相似度分数")
    confidence_score: float = Field(description="置信度分数")
    reasoning: str = Field(description="匹配推理")
    final_score: float = Field(description="最终综合分数")


class ResourceDiscoveryRequest(SQLModel):
    """资源发现请求模型"""
    user_query: str = Field(description="用户查询")
    max_results: int = Field(default=5, ge=1, le=20, description="最大返回结果数")
    min_confidence: float = Field(default=0.3, ge=0.0, le=1.0, description="最小置信度阈值")
    resource_types: Optional[List[ResourceType]] = Field(default=None, description="限制的资源类型")


class ResourceDiscoveryResponse(SQLModel):
    """资源发现响应模型"""
    query: str = Field(description="用户查询")
    matches: List[ResourceMatch] = Field(description="匹配结果")
    total_resources: int = Field(description="总资源数量")
    processing_time_ms: float = Field(description="处理时间(毫秒)")
    timestamp: datetime = Field(description="响应时间戳")


class BatchVectorizationRequest(SQLModel):
    """批量向量化请求模型"""
    resource_ids: List[str] = Field(description="资源ID列表")
    force_update: bool = Field(default=False, description="是否强制更新")
    vector_types: Optional[List[str]] = Field(default=None, description="向量类型列表")


class BatchVectorizationResponse(SQLModel):
    """批量向量化响应模型"""
    total_resources: int = Field(description="总资源数量")
    successful_resources: int = Field(description="成功处理的资源数量")
    failed_resources: int = Field(description="失败的资源数量")
    results: List[dict] = Field(default=[], description="处理结果详情")
    total_processing_time_ms: float = Field(description="总处理时间(毫秒)")
    timestamp: datetime = Field(description="响应时间戳")
