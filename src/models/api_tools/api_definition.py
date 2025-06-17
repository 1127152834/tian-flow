# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
API Definition Models
API定义相关的数据模型
"""

from datetime import datetime
from enum import IntEnum
from typing import Optional, Dict, List, Any, TYPE_CHECKING
from sqlalchemy import Column, JSON, DateTime, TypeDecorator, Text, Integer, String, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, field_validator, model_serializer, ConfigDict
import json

from src.config.database import Base

from .auth_config import AuthConfig, AuthType
from .parameter import Parameter, ParameterType, DataType
from .rate_limit import RateLimit
from .response_config import ResponseConfig, ResponseField, ResponseType, FieldRole

if TYPE_CHECKING:
    from .api_call_log import APICallLog


class HTTPMethod(IntEnum):
    """HTTP方法枚举"""
    GET = 0
    POST = 1
    PUT = 2
    DELETE = 3
    PATCH = 4
    HEAD = 5
    OPTIONS = 6


class PydanticJSON(TypeDecorator):
    """Pydantic模型的JSON类型转换器"""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if hasattr(value, 'model_dump'):
                return json.dumps(value.model_dump())
            elif hasattr(value, 'dict'):
                return json.dumps(value.dict())
            else:
                return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            # PostgreSQL JSONB 字段已经返回字典，不需要再次解析
            if isinstance(value, str):
                return json.loads(value)
            else:
                return value
        return value


class APIDefinition(Base):
    """API定义主表模型"""

    __tablename__ = "api_definitions"
    __table_args__ = {"schema": "api_tools"}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True, unique=True)
    description = Column(String(500), nullable=False)
    category = Column(String(50), nullable=False, default="general", index=True)

    # HTTP配置
    method = Column(Integer, nullable=False)  # HTTPMethod enum
    url = Column(Text, nullable=False)
    headers = Column(JSON, nullable=False, default={})
    timeout_seconds = Column(Integer, nullable=False, default=30)

    # 认证和参数配置（存储为JSON）
    auth_config = Column(PydanticJSON, nullable=False)
    parameters = Column(PydanticJSON, nullable=False, default=[])
    response_schema = Column(JSON, nullable=True)
    response_config = Column(PydanticJSON, nullable=False, default={})
    rate_limit = Column(PydanticJSON, nullable=False)

    # 状态和元数据
    enabled = Column(Boolean, nullable=False, default=True, index=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default="now()")
    updated_at = Column(DateTime(timezone=True), server_default="now()")

    # 关联关系
    call_logs = relationship(
        "APICallLog",
        back_populates="api_definition",
        cascade="all, delete-orphan"
    )

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        """验证URL格式"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL必须以http://或https://开头')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """验证API名称"""
        if not v or len(v.strip()) == 0:
            raise ValueError('API名称不能为空')
        
        # 移除过严格的字符限制，支持中文字符
        # 只检查长度和基本的非法字符
        stripped_name = v.strip()
        
        # 检查是否包含不合适的控制字符
        if any(ord(c) < 32 for c in stripped_name if c not in ['\t']):
            raise ValueError('API名称不能包含控制字符')
        
        # 检查长度限制
        if len(stripped_name) > 100:
            raise ValueError('API名称不能超过100个字符')
        
        return stripped_name

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        """自定义序列化方法，确保前端兼容的格式"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'method': self.method.value if hasattr(self.method, 'value') else self.method,
            'url': self.url,
            'headers': self.headers,
            'timeout_seconds': self.timeout_seconds,
            'auth_config': self._serialize_auth_config(),
            'parameters': self._serialize_parameters(),
            'response_schema': self.response_schema,
            'response_config': self._serialize_response_config(),
            'rate_limit': self._serialize_rate_limit(),
            'enabled': self.enabled,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
        return data

    def _serialize_auth_config(self) -> Dict[str, Any]:
        """序列化认证配置"""
        if isinstance(self.auth_config, AuthConfig):
            return self.auth_config.model_dump()
        elif isinstance(self.auth_config, dict):
            return self.auth_config
        else:
            return AuthConfig().model_dump()

    def _serialize_parameters(self) -> List[Dict[str, Any]]:
        """序列化参数列表"""
        if isinstance(self.parameters, list):
            result = []
            for param in self.parameters:
                if isinstance(param, Parameter):
                    result.append(param.model_dump())
                elif isinstance(param, dict):
                    result.append(param)
            return result
        return []

    def _serialize_response_config(self) -> Dict[str, Any]:
        """序列化响应配置"""
        if isinstance(self.response_config, ResponseConfig):
            return self.response_config.model_dump()
        elif isinstance(self.response_config, dict):
            return self.response_config
        else:
            return ResponseConfig().model_dump()

    def _serialize_rate_limit(self) -> Dict[str, Any]:
        """序列化限流配置"""
        if isinstance(self.rate_limit, RateLimit):
            return self.rate_limit.model_dump()
        elif isinstance(self.rate_limit, dict):
            return self.rate_limit
        else:
            return RateLimit().model_dump()

    def get_parameter_by_name(self, name: str) -> Optional[Parameter]:
        """根据名称获取参数"""
        for param in self.parameters:
            if isinstance(param, Parameter) and param.name == name:
                return param
            elif isinstance(param, dict) and param.get('name') == name:
                return Parameter(**param)
        return None

    def get_parameters_by_type(self, param_type: ParameterType) -> List[Parameter]:
        """根据类型获取参数列表"""
        result = []
        for param in self.parameters:
            if isinstance(param, Parameter):
                if param.parameter_type == param_type:
                    result.append(param)
            elif isinstance(param, dict):
                param_obj = Parameter(**param)
                if param_obj.parameter_type == param_type:
                    result.append(param_obj)
        return result

    def is_enabled(self) -> bool:
        """检查API是否启用"""
        return self.enabled

    def get_method_name(self) -> str:
        """获取HTTP方法名称"""
        method_names = {
            HTTPMethod.GET: "GET",
            HTTPMethod.POST: "POST",
            HTTPMethod.PUT: "PUT",
            HTTPMethod.DELETE: "DELETE",
            HTTPMethod.PATCH: "PATCH",
            HTTPMethod.HEAD: "HEAD",
            HTTPMethod.OPTIONS: "OPTIONS"
        }
        return method_names.get(self.method, "GET")


class APIDefinitionCreate(BaseModel):
    """创建API定义的请求模型"""
    model_config = ConfigDict(use_enum_values=True)

    name: str = Field(min_length=1, max_length=100, description="API名称")
    description: str = Field(max_length=500, description="API描述")
    category: str = Field(default="general", max_length=50, description="API分类")
    method: HTTPMethod = Field(description="HTTP方法")
    url: str = Field(description="API地址")
    headers: Dict[str, str] = Field(default_factory=dict, description="默认请求头")
    timeout_seconds: int = Field(default=30, ge=5, le=300, description="超时时间")
    auth_config: AuthConfig = Field(description="认证配置")
    parameters: List[Parameter] = Field(default_factory=list, description="参数定义")
    response_schema: Optional[Dict] = Field(default=None, description="响应格式定义")
    response_config: ResponseConfig = Field(default_factory=lambda: ResponseConfig(), description="响应配置")
    rate_limit: RateLimit = Field(description="限流配置")
    enabled: bool = Field(default=True, description="是否启用")


class APIDefinitionUpdate(BaseModel):
    """更新API定义的请求模型"""
    model_config = ConfigDict(use_enum_values=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    category: Optional[str] = Field(default=None, max_length=50)
    method: Optional[HTTPMethod] = Field(default=None)
    url: Optional[str] = Field(default=None)
    headers: Optional[Dict[str, str]] = Field(default=None)
    timeout_seconds: Optional[int] = Field(default=None, ge=5, le=300)
    auth_config: Optional[AuthConfig] = Field(default=None)
    parameters: Optional[List[Parameter]] = Field(default=None)
    response_schema: Optional[Dict] = Field(default=None)
    response_config: Optional[ResponseConfig] = Field(default=None)
    rate_limit: Optional[RateLimit] = Field(default=None)
    enabled: Optional[bool] = Field(default=None)
