# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
API Tools Pydantic Schemas
API工具相关的Pydantic模式定义，用于FastAPI响应模型
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from .auth_config import AuthConfig, AuthType
from .parameter import Parameter, ParameterType, DataType
from .rate_limit import RateLimit
from .response_config import ResponseConfig, ResponseField, ResponseType, FieldRole


class APIDefinitionResponse(BaseModel):
    """API定义响应模型"""
    
    id: int
    name: str
    description: str
    category: str
    method: int  # HTTPMethod enum value
    url: str
    headers: Dict[str, str]
    timeout_seconds: int
    auth_config: Dict[str, Any]  # AuthConfig as dict
    parameters: List[Dict[str, Any]]  # List of Parameter as dict
    response_schema: Optional[Dict[str, Any]] = None
    response_config: Dict[str, Any]  # ResponseConfig as dict
    rate_limit: Dict[str, Any]  # RateLimit as dict
    enabled: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class APICallLogResponse(BaseModel):
    """API调用日志响应模型"""
    
    id: int
    api_definition_id: int
    session_id: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    status_code: Optional[int] = None
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class APIExecutionRequest(BaseModel):
    """API执行请求模型"""
    parameters: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = None


class APIExecutionResponse(BaseModel):
    """API执行响应模型"""
    success: bool
    api_definition_id: int
    execution_time_ms: int
    session_id: Optional[str] = None
    result: Dict[str, Any]


class APITestRequest(BaseModel):
    """API测试请求模型"""
    test_parameters: Optional[Dict[str, Any]] = None


class BulkUpdateRequest(BaseModel):
    """批量更新请求模型"""
    api_ids: List[int]
    category: Optional[str] = None
    enabled: Optional[bool] = None


class CurlParseRequest(BaseModel):
    """curl解析请求模型"""
    curl_command: str


class CurlImportRequest(BaseModel):
    """curl导入请求模型"""
    curl_command: str


class APIStatisticsResponse(BaseModel):
    """API统计响应模型"""
    total_apis: int
    enabled_apis: int
    disabled_apis: int
    category_distribution: Dict[str, int]
    method_distribution: Dict[str, int]


class CallStatisticsResponse(BaseModel):
    """调用统计响应模型"""
    total_calls: int
    success_calls: int
    failed_calls: int
    average_response_time: float
    success_rate: float
    period_days: int
    start_date: datetime
    end_date: datetime


class CountResponse(BaseModel):
    """计数响应模型"""
    count: int


class MessageResponse(BaseModel):
    """消息响应模型"""
    message: str


class CategoriesResponse(BaseModel):
    """分类响应模型"""
    categories: List[str]


class SearchResponse(BaseModel):
    """搜索响应模型"""
    results: List[APIDefinitionResponse]


class RecentResponse(BaseModel):
    """最近项目响应模型"""
    results: List[APIDefinitionResponse]


class BulkUpdateResponse(BaseModel):
    """批量更新响应模型"""
    message: str
    updated_count: int


class LogsByAPIResponse(BaseModel):
    """按API获取日志响应模型"""
    logs: List[APICallLogResponse]


class LogsBySessionResponse(BaseModel):
    """按会话获取日志响应模型"""
    logs: List[APICallLogResponse]


class DailyStatsResponse(BaseModel):
    """每日统计响应模型"""
    daily_stats: List[Dict[str, Any]]


class ErrorStatsResponse(BaseModel):
    """错误统计响应模型"""
    error_stats: List[Dict[str, Any]]


class RecentErrorsResponse(BaseModel):
    """最近错误响应模型"""
    recent_errors: List[APICallLogResponse]


class CleanupResponse(BaseModel):
    """清理响应模型"""
    message: str
    deleted_count: int


class CurlParseResponse(BaseModel):
    """curl解析响应模型"""
    success: bool
    api_definition: Optional[Dict[str, Any]] = None
    message: str
    error_message: Optional[str] = None


class CurlValidateResponse(BaseModel):
    """curl验证响应模型"""
    valid: bool
    error_message: Optional[str] = None
    extracted_info: Optional[Dict[str, Any]] = None
