# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Auth Config Models
认证配置相关的数据模型
"""

from enum import IntEnum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class AuthType(IntEnum):
    """认证类型枚举"""
    NONE = 0        # 无认证
    API_KEY = 1     # API Key认证
    BEARER = 2      # Bearer Token认证
    BASIC = 3       # Basic认证
    OAUTH2 = 4      # OAuth2认证
    CUSTOM = 5      # 自定义认证


class AuthConfig(BaseModel):
    """认证配置模型"""
    
    auth_type: AuthType = Field(default=AuthType.NONE, description="认证类型")
    
    # API Key认证配置
    api_key: Optional[str] = Field(default=None, description="API密钥")
    api_key_header: Optional[str] = Field(default="X-API-Key", description="API密钥请求头名称")
    
    # Bearer Token认证配置
    bearer_token: Optional[str] = Field(default=None, description="Bearer令牌")
    
    # Basic认证配置
    username: Optional[str] = Field(default=None, description="用户名")
    password: Optional[str] = Field(default=None, description="密码")
    
    # OAuth2认证配置
    oauth2_token: Optional[str] = Field(default=None, description="OAuth2访问令牌")
    oauth2_token_url: Optional[str] = Field(default=None, description="OAuth2令牌获取URL")
    oauth2_client_id: Optional[str] = Field(default=None, description="OAuth2客户端ID")
    oauth2_client_secret: Optional[str] = Field(default=None, description="OAuth2客户端密钥")
    oauth2_scope: Optional[str] = Field(default=None, description="OAuth2权限范围")
    
    # 自定义认证配置
    custom_headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="自定义请求头")
    custom_params: Optional[Dict[str, str]] = Field(default_factory=dict, description="自定义参数")
    
    @field_validator('api_key_header')
    @classmethod
    def validate_api_key_header(cls, v):
        """验证API密钥请求头名称"""
        if v and not v.strip():
            return "X-API-Key"
        return v
    
    @field_validator('custom_headers', 'custom_params')
    @classmethod
    def validate_custom_fields(cls, v):
        """验证自定义字段"""
        if v is None:
            return {}
        return v
    
    def get_auth_headers(self) -> Dict[str, str]:
        """获取认证请求头"""
        headers = {}
        
        if self.auth_type == AuthType.API_KEY and self.api_key:
            headers[self.api_key_header or "X-API-Key"] = self.api_key
        elif self.auth_type == AuthType.BEARER and self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        elif self.auth_type == AuthType.OAUTH2 and self.oauth2_token:
            headers["Authorization"] = f"Bearer {self.oauth2_token}"
        elif self.auth_type == AuthType.CUSTOM and self.custom_headers:
            headers.update(self.custom_headers)
        
        return headers
    
    def get_auth_params(self) -> Dict[str, str]:
        """获取认证参数"""
        params = {}
        
        if self.auth_type == AuthType.CUSTOM and self.custom_params:
            params.update(self.custom_params)
        
        return params
    
    def requires_basic_auth(self) -> bool:
        """是否需要Basic认证"""
        return (
            self.auth_type == AuthType.BASIC 
            and self.username is not None 
            and self.password is not None
        )
    
    def get_basic_auth(self) -> Optional[tuple]:
        """获取Basic认证信息"""
        if self.requires_basic_auth():
            return (self.username, self.password)
        return None
    
    def is_valid(self) -> bool:
        """验证认证配置是否有效"""
        if self.auth_type == AuthType.NONE:
            return True
        elif self.auth_type == AuthType.API_KEY:
            return bool(self.api_key and self.api_key_header)
        elif self.auth_type == AuthType.BEARER:
            return bool(self.bearer_token)
        elif self.auth_type == AuthType.BASIC:
            return bool(self.username and self.password)
        elif self.auth_type == AuthType.OAUTH2:
            return bool(self.oauth2_token)
        elif self.auth_type == AuthType.CUSTOM:
            return bool(self.custom_headers or self.custom_params)
        
        return False
