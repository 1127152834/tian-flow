"""
资源使用统计模型

基于 Ti-Flow 的 resource_usage_stats 表设计
"""

from datetime import datetime, date
from typing import List, Optional
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import DateTime, Date, ForeignKey


class ResourceUsageStatsBase(SQLModel):
    """资源使用统计基础模型"""
    resource_id: str = Field(max_length=255, description="资源ID")
    
    # 统计数据
    total_matches: int = Field(default=0, description="总匹配次数")
    successful_matches: int = Field(default=0, description="成功匹配次数")
    user_selections: int = Field(default=0, description="用户选择次数")
    positive_feedback: int = Field(default=0, description="正面反馈次数")
    negative_feedback: int = Field(default=0, description="负面反馈次数")
    
    # 性能指标
    avg_similarity_score: Optional[float] = Field(default=None, description="平均相似度得分")
    avg_response_time: Optional[float] = Field(default=None, description="平均响应时间")
    
    # 统计周期
    stats_date: date = Field(sa_column=Column(Date), description="统计日期")


class ResourceUsageStats(ResourceUsageStatsBase, table=True):
    """资源使用统计模型"""
    __tablename__ = "resource_usage_stats"
    __table_args__ = {"schema": "resource_discovery"}
    
    id: Optional[int] = Field(default=None, primary_key=True, description="统计记录ID")
    
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


class ResourceUsageStatsCreate(ResourceUsageStatsBase):
    """创建资源使用统计请求模型"""
    pass


class ResourceUsageStatsUpdate(SQLModel):
    """更新资源使用统计请求模型"""
    total_matches: Optional[int] = Field(default=None, description="总匹配次数")
    successful_matches: Optional[int] = Field(default=None, description="成功匹配次数")
    user_selections: Optional[int] = Field(default=None, description="用户选择次数")
    positive_feedback: Optional[int] = Field(default=None, description="正面反馈次数")
    negative_feedback: Optional[int] = Field(default=None, description="负面反馈次数")
    avg_similarity_score: Optional[float] = Field(default=None, description="平均相似度得分")
    avg_response_time: Optional[float] = Field(default=None, description="平均响应时间")


class ResourceUsageStatsResponse(ResourceUsageStatsBase):
    """资源使用统计响应模型"""
    id: int = Field(description="统计记录ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class UsageStatsQuery(SQLModel):
    """使用统计查询模型"""
    resource_id: Optional[str] = Field(default=None, description="资源ID")
    start_date: Optional[date] = Field(default=None, description="开始日期")
    end_date: Optional[date] = Field(default=None, description="结束日期")
    limit: int = Field(default=100, ge=1, le=1000, description="返回数量限制")
    offset: int = Field(default=0, ge=0, description="偏移量")


class ResourcePerformanceMetrics(SQLModel):
    """资源性能指标模型"""
    resource_id: str = Field(description="资源ID")
    resource_name: str = Field(description="资源名称")
    resource_type: str = Field(description="资源类型")
    
    # 使用统计
    total_matches: int = Field(description="总匹配次数")
    successful_matches: int = Field(description="成功匹配次数")
    user_selections: int = Field(description="用户选择次数")
    
    # 反馈统计
    positive_feedback: int = Field(description="正面反馈次数")
    negative_feedback: int = Field(description="负面反馈次数")
    feedback_ratio: float = Field(description="反馈比例")
    
    # 性能指标
    success_rate: float = Field(description="成功率")
    selection_rate: float = Field(description="选择率")
    avg_similarity_score: float = Field(description="平均相似度得分")
    avg_response_time: float = Field(description="平均响应时间")
    
    # 趋势数据
    trend_direction: str = Field(description="趋势方向")  # 'up', 'down', 'stable'
    trend_percentage: float = Field(description="趋势百分比")


class SystemUsageOverview(SQLModel):
    """系统使用概览模型"""
    total_resources: int = Field(description="总资源数")
    active_resources: int = Field(description="活跃资源数")
    total_queries: int = Field(description="总查询数")
    successful_queries: int = Field(description="成功查询数")
    
    # 今日统计
    today_queries: int = Field(description="今日查询数")
    today_success_rate: float = Field(description="今日成功率")
    
    # 热门资源
    top_resources: List[ResourcePerformanceMetrics] = Field(description="热门资源")
    
    # 性能指标
    avg_response_time: float = Field(description="平均响应时间")
    avg_similarity_score: float = Field(description="平均相似度分数")
    
    # 时间范围
    stats_period: str = Field(description="统计周期")
    last_updated: datetime = Field(description="最后更新时间")


class ResourceTrendData(SQLModel):
    """资源趋势数据模型"""
    resource_id: str = Field(description="资源ID")
    date_points: List[date] = Field(description="日期点")
    match_counts: List[int] = Field(description="匹配次数")
    success_rates: List[float] = Field(description="成功率")
    similarity_scores: List[float] = Field(description="相似度分数")
    response_times: List[float] = Field(description="响应时间")


class DailyStatsAggregation(SQLModel):
    """日统计聚合模型"""
    stats_date: date = Field(description="统计日期")
    total_queries: int = Field(description="总查询数")
    unique_resources_used: int = Field(description="使用的唯一资源数")
    avg_similarity_score: float = Field(description="平均相似度分数")
    avg_response_time: float = Field(description="平均响应时间")
    success_rate: float = Field(description="成功率")
    positive_feedback_rate: float = Field(description="正面反馈率")
