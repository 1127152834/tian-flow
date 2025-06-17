"""
系统状态管理模型

基于 Ti-Flow 的 intent_system_status 表设计
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any
from sqlmodel import SQLModel, Field, Column, JSON
from sqlalchemy import DateTime, Text


class OperationType(str, Enum):
    """操作类型枚举"""
    DISCOVERY = "discovery"
    VECTORIZATION = "vectorization"
    SYNC = "sync"
    CLEANUP = "cleanup"
    MIGRATION = "migration"


class SystemStatusType(str, Enum):
    """系统状态类型枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SystemStatusBase(SQLModel):
    """系统状态基础模型"""
    operation_type: OperationType = Field(description="操作类型")
    status: SystemStatusType = Field(description="状态")
    
    # 操作详情
    total_items: int = Field(default=0, description="总项目数")
    successful_items: int = Field(default=0, description="成功项目数")
    failed_items: int = Field(default=0, description="失败项目数")
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text), description="错误信息")
    
    # 结果数据
    result_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="操作结果数据")
    
    # 时间信息
    started_at: Optional[datetime] = Field(
        default=None, 
        sa_column=Column(DateTime(timezone=True)), 
        description="开始时间"
    )
    completed_at: Optional[datetime] = Field(
        default=None, 
        sa_column=Column(DateTime(timezone=True)), 
        description="完成时间"
    )
    duration_seconds: Optional[int] = Field(default=None, description="持续时间(秒)")


class SystemStatus(SystemStatusBase, table=True):
    """系统状态模型"""
    __tablename__ = "system_status"
    __table_args__ = {"schema": "resource_discovery"}
    
    id: Optional[int] = Field(default=None, primary_key=True, description="状态记录ID")
    
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


class SystemStatusCreate(SystemStatusBase):
    """创建系统状态请求模型"""
    pass


class SystemStatusUpdate(SQLModel):
    """更新系统状态请求模型"""
    status: Optional[SystemStatusType] = Field(default=None, description="状态")
    total_items: Optional[int] = Field(default=None, description="总项目数")
    successful_items: Optional[int] = Field(default=None, description="成功项目数")
    failed_items: Optional[int] = Field(default=None, description="失败项目数")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    result_data: Optional[Dict[str, Any]] = Field(default=None, description="操作结果数据")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    duration_seconds: Optional[int] = Field(default=None, description="持续时间(秒)")


class SystemStatusResponse(SystemStatusBase):
    """系统状态响应模型"""
    id: int = Field(description="状态记录ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    
    # 计算属性
    progress_percentage: Optional[float] = Field(default=None, description="进度百分比")
    is_running: bool = Field(description="是否正在运行")
    is_completed: bool = Field(description="是否已完成")


class OperationProgress(SQLModel):
    """操作进度模型"""
    operation_id: int = Field(description="操作ID")
    operation_type: OperationType = Field(description="操作类型")
    status: SystemStatusType = Field(description="当前状态")
    progress_percentage: float = Field(description="进度百分比")
    current_item: Optional[str] = Field(default=None, description="当前处理项目")
    estimated_remaining_time: Optional[int] = Field(default=None, description="预计剩余时间(秒)")
    last_update: datetime = Field(description="最后更新时间")


class SystemHealthCheck(SQLModel):
    """系统健康检查模型"""
    overall_status: str = Field(description="整体状态")  # 'healthy', 'warning', 'error'
    
    # 各组件状态
    database_status: str = Field(description="数据库状态")
    vector_store_status: str = Field(description="向量存储状态")
    embedding_service_status: str = Field(description="嵌入服务状态")
    
    # 资源统计
    total_resources: int = Field(description="总资源数")
    vectorized_resources: int = Field(description="已向量化资源数")
    failed_resources: int = Field(description="失败资源数")
    
    # 最近操作
    last_discovery: Optional[datetime] = Field(default=None, description="最后发现时间")
    last_vectorization: Optional[datetime] = Field(default=None, description="最后向量化时间")
    last_sync: Optional[datetime] = Field(default=None, description="最后同步时间")
    
    # 性能指标
    avg_query_time: float = Field(description="平均查询时间(毫秒)")
    system_load: float = Field(description="系统负载")
    
    check_time: datetime = Field(description="检查时间")


class OperationLog(SQLModel):
    """操作日志模型"""
    operation_id: int = Field(description="操作ID")
    log_level: str = Field(description="日志级别")  # 'INFO', 'WARNING', 'ERROR'
    message: str = Field(description="日志消息")
    details: Optional[Dict[str, Any]] = Field(default=None, description="详细信息")
    timestamp: datetime = Field(description="时间戳")


class SystemMetrics(SQLModel):
    """系统指标模型"""
    # 资源指标
    total_resources_by_type: Dict[str, int] = Field(description="按类型分组的资源数")
    vectorization_completion_rate: float = Field(description="向量化完成率")
    
    # 性能指标
    avg_discovery_time: float = Field(description="平均发现时间(秒)")
    avg_vectorization_time: float = Field(description="平均向量化时间(秒)")
    avg_query_response_time: float = Field(description="平均查询响应时间(毫秒)")
    
    # 使用指标
    daily_query_count: int = Field(description="日查询数")
    weekly_query_count: int = Field(description="周查询数")
    monthly_query_count: int = Field(description="月查询数")
    
    # 质量指标
    avg_similarity_score: float = Field(description="平均相似度分数")
    user_satisfaction_rate: float = Field(description="用户满意度")
    
    # 时间戳
    metrics_date: datetime = Field(description="指标日期")


class MaintenanceWindow(SQLModel):
    """维护窗口模型"""
    operation_type: OperationType = Field(description="操作类型")
    scheduled_start: datetime = Field(description="计划开始时间")
    scheduled_end: datetime = Field(description="计划结束时间")
    description: str = Field(description="维护描述")
    impact_level: str = Field(description="影响级别")  # 'low', 'medium', 'high'
    status: str = Field(description="维护状态")  # 'scheduled', 'in_progress', 'completed', 'cancelled'
    created_by: str = Field(description="创建者")
    created_at: datetime = Field(description="创建时间")
