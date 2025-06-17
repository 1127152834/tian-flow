"""
资源匹配历史模型

基于 Ti-Flow 的 intent_match_history 表设计
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from sqlmodel import SQLModel, Field, Column, JSON
from sqlalchemy import DateTime, Text


class UserFeedback(str, Enum):
    """用户反馈枚举"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class ResourceMatchHistoryBase(SQLModel):
    """资源匹配历史基础模型"""
    user_query: str = Field(sa_column=Column(Text), description="用户原始查询")
    query_hash: Optional[str] = Field(default=None, max_length=64, description="查询hash")
    user_context: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="用户上下文信息")
    
    # 匹配结果
    matched_resource_ids: Optional[List[str]] = Field(default=None, sa_column=Column(JSON), description="匹配到的资源ID列表")
    similarity_scores: Optional[List[float]] = Field(default=None, sa_column=Column(JSON), description="相似度得分列表")
    confidence_scores: Optional[List[float]] = Field(default=None, sa_column=Column(JSON), description="置信度得分列表")
    reasoning: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="匹配推理信息")
    
    # 最终选择
    final_selected_resource: Optional[str] = Field(default=None, max_length=255, description="用户最终选择的资源ID")
    
    # 执行结果
    execution_success: Optional[bool] = Field(default=None, description="是否执行成功")
    execution_result: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="执行结果")
    response_time: Optional[float] = Field(default=None, description="响应时间(毫秒)")
    
    # 用户反馈
    user_feedback: Optional[UserFeedback] = Field(default=None, description="用户反馈")
    feedback_note: Optional[str] = Field(default=None, sa_column=Column(Text), description="反馈备注")
    
    # 会话信息
    session_id: Optional[str] = Field(default=None, max_length=128, description="会话ID")
    user_id: Optional[str] = Field(default=None, max_length=128, description="用户ID")


class ResourceMatchHistory(ResourceMatchHistoryBase, table=True):
    """资源匹配历史模型"""
    __tablename__ = "resource_match_history"
    __table_args__ = {"schema": "resource_discovery"}
    
    id: Optional[int] = Field(default=None, primary_key=True, description="匹配记录ID")
    
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


class ResourceMatchHistoryCreate(ResourceMatchHistoryBase):
    """创建资源匹配历史请求模型"""
    pass


class ResourceMatchHistoryUpdate(SQLModel):
    """更新资源匹配历史请求模型"""
    final_selected_resource: Optional[str] = Field(default=None, description="用户最终选择的资源ID")
    execution_success: Optional[bool] = Field(default=None, description="是否执行成功")
    execution_result: Optional[Dict[str, Any]] = Field(default=None, description="执行结果")
    response_time: Optional[float] = Field(default=None, description="响应时间(毫秒)")
    user_feedback: Optional[UserFeedback] = Field(default=None, description="用户反馈")
    feedback_note: Optional[str] = Field(default=None, description="反馈备注")


class ResourceMatchHistoryResponse(ResourceMatchHistoryBase):
    """资源匹配历史响应模型"""
    id: int = Field(description="匹配记录ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class MatchHistoryQuery(SQLModel):
    """匹配历史查询模型"""
    user_id: Optional[str] = Field(default=None, description="用户ID")
    session_id: Optional[str] = Field(default=None, description="会话ID")
    user_feedback: Optional[UserFeedback] = Field(default=None, description="用户反馈")
    start_date: Optional[datetime] = Field(default=None, description="开始日期")
    end_date: Optional[datetime] = Field(default=None, description="结束日期")
    limit: int = Field(default=50, ge=1, le=1000, description="返回数量限制")
    offset: int = Field(default=0, ge=0, description="偏移量")


class MatchHistoryStats(SQLModel):
    """匹配历史统计模型"""
    total_queries: int = Field(description="总查询数")
    successful_matches: int = Field(description="成功匹配数")
    user_selections: int = Field(description="用户选择数")
    positive_feedback: int = Field(description="正面反馈数")
    negative_feedback: int = Field(description="负面反馈数")
    avg_response_time: float = Field(description="平均响应时间(毫秒)")
    avg_similarity_score: float = Field(description="平均相似度分数")
    most_queried_resources: List[Dict[str, Any]] = Field(description="最常查询的资源")
    query_trends: List[Dict[str, Any]] = Field(description="查询趋势")


class FeedbackSubmission(SQLModel):
    """反馈提交模型"""
    match_history_id: int = Field(description="匹配历史ID")
    user_feedback: UserFeedback = Field(description="用户反馈")
    feedback_note: Optional[str] = Field(default=None, description="反馈备注")
    selected_resource: Optional[str] = Field(default=None, description="用户选择的资源")


class QueryAnalytics(SQLModel):
    """查询分析模型"""
    query_text: str = Field(description="查询文本")
    frequency: int = Field(description="查询频率")
    avg_similarity: float = Field(description="平均相似度")
    success_rate: float = Field(description="成功率")
    most_matched_resources: List[str] = Field(description="最常匹配的资源")
    last_queried: datetime = Field(description="最后查询时间")
