"""
资源发现模块数据模型

基于 Ti-Flow 意图识别模块设计，为 DeerFlow 提供统一的资源发现和匹配功能
"""

from .resource_registry import (
    ResourceRegistry,
    ResourceRegistryCreate,
    ResourceRegistryUpdate,
    ResourceRegistryResponse,
    ResourceType,
    ResourceStatus,
    VectorizationStatus,
    ResourceMatch,
    ResourceDiscoveryRequest,
    ResourceDiscoveryResponse,
    BatchVectorizationRequest,
    BatchVectorizationResponse
)

from .resource_vectors import (
    ResourceVector,
    ResourceVectorCreate,
    VectorType
)

from .resource_match_history import (
    ResourceMatchHistory,
    ResourceMatchHistoryCreate,
    UserFeedback
)

from .resource_usage_stats import (
    ResourceUsageStats,
    ResourceUsageStatsCreate
)

from .system_status import (
    SystemStatus,
    SystemStatusCreate,
    OperationType,
    SystemStatusType
)

__all__ = [
    # 资源注册表
    "ResourceRegistry",
    "ResourceRegistryCreate",
    "ResourceRegistryUpdate",
    "ResourceRegistryResponse",
    "ResourceType",
    "ResourceStatus",
    "VectorizationStatus",
    "ResourceMatch",
    "ResourceDiscoveryRequest",
    "ResourceDiscoveryResponse",
    "BatchVectorizationRequest",
    "BatchVectorizationResponse",
    
    # 资源向量
    "ResourceVector",
    "ResourceVectorCreate",
    "VectorType",
    
    # 匹配历史
    "ResourceMatchHistory",
    "ResourceMatchHistoryCreate",
    "UserFeedback",
    
    # 使用统计
    "ResourceUsageStats",
    "ResourceUsageStatsCreate",
    
    # 系统状态
    "SystemStatus",
    "SystemStatusCreate",
    "OperationType",
    "SystemStatusType",
]
