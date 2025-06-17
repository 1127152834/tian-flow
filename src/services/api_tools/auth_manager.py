# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Auth Manager
认证管理器 - 严格按照ti-flow实现
"""

import base64
from typing import Dict, Optional, Tuple

from src.models.api_tools import AuthConfig, AuthType


class AuthManager:
    """认证管理器"""
    
    def __init__(self):
        pass
    
    def add_authentication(
        self,
        headers: Dict[str, str],
        auth_config: AuthConfig
    ) -> None:
        """
        添加认证信息到请求头
        
        Args:
            headers: 请求头字典（会被修改）
            auth_config: 认证配置
        """
        if not auth_config or not auth_config.is_valid():
            return
        
        if auth_config.auth_type == AuthType.NONE:
            return
        elif auth_config.auth_type == AuthType.API_KEY:
            self._add_api_key_auth(headers, auth_config)
        elif auth_config.auth_type == AuthType.BEARER:
            self._add_bearer_auth(headers, auth_config)
        elif auth_config.auth_type == AuthType.BASIC:
            self._add_basic_auth(headers, auth_config)
        elif auth_config.auth_type == AuthType.OAUTH2:
            self._add_oauth2_auth(headers, auth_config)
        elif auth_config.auth_type == AuthType.CUSTOM:
            self._add_custom_auth(headers, auth_config)
    
    def _add_api_key_auth(self, headers: Dict[str, str], auth_config: AuthConfig) -> None:
        """添加API Key认证"""
        if auth_config.api_key and auth_config.api_key_header:
            headers[auth_config.api_key_header] = auth_config.api_key
    
    def _add_bearer_auth(self, headers: Dict[str, str], auth_config: AuthConfig) -> None:
        """添加Bearer Token认证"""
        if auth_config.bearer_token:
            headers["Authorization"] = f"Bearer {auth_config.bearer_token}"
    
    def _add_basic_auth(self, headers: Dict[str, str], auth_config: AuthConfig) -> None:
        """添加Basic认证"""
        if auth_config.username and auth_config.password:
            credentials = f"{auth_config.username}:{auth_config.password}"
            encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('ascii')
            headers["Authorization"] = f"Basic {encoded_credentials}"
    
    def _add_oauth2_auth(self, headers: Dict[str, str], auth_config: AuthConfig) -> None:
        """添加OAuth2认证"""
        if auth_config.oauth2_token:
            headers["Authorization"] = f"Bearer {auth_config.oauth2_token}"
    
    def _add_custom_auth(self, headers: Dict[str, str], auth_config: AuthConfig) -> None:
        """添加自定义认证"""
        if auth_config.custom_headers:
            headers.update(auth_config.custom_headers)
    
    def get_basic_auth_tuple(self, auth_config: AuthConfig) -> Optional[Tuple[str, str]]:
        """
        获取Basic认证元组（用于httpx的auth参数）
        
        Args:
            auth_config: 认证配置
            
        Returns:
            Optional[Tuple[str, str]]: (username, password) 或 None
        """
        if (auth_config.auth_type == AuthType.BASIC 
            and auth_config.username 
            and auth_config.password):
            return (auth_config.username, auth_config.password)
        return None
    
    def get_auth_params(self, auth_config: AuthConfig) -> Dict[str, str]:
        """
        获取认证参数（用于查询参数）
        
        Args:
            auth_config: 认证配置
            
        Returns:
            Dict[str, str]: 认证参数
        """
        if auth_config.auth_type == AuthType.CUSTOM and auth_config.custom_params:
            return auth_config.custom_params.copy()
        return {}
    
    def validate_auth_config(self, auth_config: AuthConfig) -> Tuple[bool, Optional[str]]:
        """
        验证认证配置
        
        Args:
            auth_config: 认证配置
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        if not auth_config:
            return True, None
        
        if auth_config.auth_type == AuthType.NONE:
            return True, None
        elif auth_config.auth_type == AuthType.API_KEY:
            if not auth_config.api_key:
                return False, "API Key不能为空"
            if not auth_config.api_key_header:
                return False, "API Key请求头名称不能为空"
        elif auth_config.auth_type == AuthType.BEARER:
            if not auth_config.bearer_token:
                return False, "Bearer Token不能为空"
        elif auth_config.auth_type == AuthType.BASIC:
            if not auth_config.username:
                return False, "用户名不能为空"
            if not auth_config.password:
                return False, "密码不能为空"
        elif auth_config.auth_type == AuthType.OAUTH2:
            if not auth_config.oauth2_token:
                return False, "OAuth2 Token不能为空"
        elif auth_config.auth_type == AuthType.CUSTOM:
            if not auth_config.custom_headers and not auth_config.custom_params:
                return False, "自定义认证必须提供请求头或参数"
        
        return True, None
    
    def mask_sensitive_data(self, auth_config: AuthConfig) -> AuthConfig:
        """
        遮蔽敏感数据（用于日志记录）
        
        Args:
            auth_config: 认证配置
            
        Returns:
            AuthConfig: 遮蔽敏感数据后的配置
        """
        if not auth_config:
            return auth_config
        
        # 创建副本
        masked_config = auth_config.model_copy()
        
        # 遮蔽敏感字段
        if masked_config.api_key:
            masked_config.api_key = self._mask_string(masked_config.api_key)
        
        if masked_config.bearer_token:
            masked_config.bearer_token = self._mask_string(masked_config.bearer_token)
        
        if masked_config.password:
            masked_config.password = self._mask_string(masked_config.password)
        
        if masked_config.oauth2_token:
            masked_config.oauth2_token = self._mask_string(masked_config.oauth2_token)
        
        if masked_config.oauth2_client_secret:
            masked_config.oauth2_client_secret = self._mask_string(masked_config.oauth2_client_secret)
        
        if masked_config.custom_headers:
            masked_headers = {}
            for key, value in masked_config.custom_headers.items():
                # 遮蔽可能包含敏感信息的请求头
                if any(sensitive in key.lower() for sensitive in ['token', 'key', 'secret', 'auth', 'password']):
                    masked_headers[key] = self._mask_string(value)
                else:
                    masked_headers[key] = value
            masked_config.custom_headers = masked_headers
        
        if masked_config.custom_params:
            masked_params = {}
            for key, value in masked_config.custom_params.items():
                # 遮蔽可能包含敏感信息的参数
                if any(sensitive in key.lower() for sensitive in ['token', 'key', 'secret', 'auth', 'password']):
                    masked_params[key] = self._mask_string(value)
                else:
                    masked_params[key] = value
            masked_config.custom_params = masked_params
        
        return masked_config
    
    def _mask_string(self, value: str, show_chars: int = 4) -> str:
        """
        遮蔽字符串
        
        Args:
            value: 原始字符串
            show_chars: 显示的字符数
            
        Returns:
            str: 遮蔽后的字符串
        """
        if not value or len(value) <= show_chars:
            return "*" * len(value)
        
        return value[:show_chars] + "*" * (len(value) - show_chars)
    
    def get_auth_description(self, auth_config: AuthConfig) -> str:
        """
        获取认证配置描述
        
        Args:
            auth_config: 认证配置
            
        Returns:
            str: 认证描述
        """
        if not auth_config or auth_config.auth_type == AuthType.NONE:
            return "无认证"
        
        type_descriptions = {
            AuthType.API_KEY: f"API Key ({auth_config.api_key_header})",
            AuthType.BEARER: "Bearer Token",
            AuthType.BASIC: f"Basic ({auth_config.username})",
            AuthType.OAUTH2: "OAuth2",
            AuthType.CUSTOM: "自定义认证"
        }
        
        return type_descriptions.get(auth_config.auth_type, "未知认证类型")
