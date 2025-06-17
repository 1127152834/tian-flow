# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
API Executor
API执行器 - 严格按照ti-flow实现
"""

import time
import asyncio
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlencode
import httpx
from pydantic import BaseModel

from src.models.api_tools import APIDefinition, HTTPMethod
from .parameter_mapper import ParameterMapper, MappedParameters
from .result_processor import ResultProcessor, ProcessedResult
from .rate_limiter import RateLimiter, RateLimitExceeded
from .auth_manager import AuthManager


class APIExecutionResult(BaseModel):
    """API执行结果"""
    
    success: bool
    result: ProcessedResult
    api_definition_id: int
    execution_time_ms: int
    session_id: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None


class APIExecutor:
    """API执行器"""
    
    def __init__(self):
        self.parameter_mapper = ParameterMapper()
        self.result_processor = ResultProcessor()
        self.rate_limiter = RateLimiter()
        self.auth_manager = AuthManager()
        
        # HTTP客户端配置
        self.client_config = {
            "timeout": httpx.Timeout(30.0),
            "follow_redirects": True,
            "verify": True
        }
    
    async def execute_api(
        self,
        api_def: APIDefinition,
        parameters: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> APIExecutionResult:
        """
        执行API调用的主方法
        
        Args:
            api_def: API定义
            parameters: 输入参数
            session_id: 会话ID
            
        Returns:
            APIExecutionResult: 执行结果
        """
        start_time = time.time()
        request_data = None
        
        try:
            # 1. 限流检查
            # 确保 rate_limit 是 RateLimit 对象
            from src.models.api_tools import RateLimit
            if isinstance(api_def.rate_limit, dict):
                rate_limit_obj = RateLimit(**api_def.rate_limit)
            else:
                rate_limit_obj = api_def.rate_limit

            await self.rate_limiter.check_rate_limit(
                api_def.id, rate_limit_obj, session_id
            )
            
            # 2. 参数映射和验证
            mapped_params = self.parameter_mapper.map_parameters(api_def, parameters)
            
            # 3. 执行HTTP请求，并获取最终使用的headers（包含认证头）
            result, final_headers = await self._execute_http_request(api_def, mapped_params)
            
            # 4. 构建包含最终headers的请求数据用于日志记录
            request_data = self._build_request_data(api_def, mapped_params, final_headers)
            
            # 5. 计算执行时间
            execution_time_ms = int((time.time() - start_time) * 1000)
            result.execution_time_ms = execution_time_ms
            
            # 6. 创建执行结果
            exec_result = APIExecutionResult(
                success=result.success,
                result=result,
                api_definition_id=api_def.id,
                execution_time_ms=execution_time_ms,
                session_id=session_id,
                request_data=request_data
            )
            
            return exec_result
            
        except RateLimitExceeded as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            result = self.result_processor.process_exception(e, execution_time_ms)
            
            exec_result = APIExecutionResult(
                success=False,
                result=result,
                api_definition_id=api_def.id,
                execution_time_ms=execution_time_ms,
                session_id=session_id,
                request_data=request_data
            )
            
            return exec_result
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            result = self.result_processor.process_exception(e, execution_time_ms)
            
            exec_result = APIExecutionResult(
                success=False,
                result=result,
                api_definition_id=api_def.id,
                execution_time_ms=execution_time_ms,
                session_id=session_id,
                request_data=request_data
            )
            
            return exec_result
    
    async def _execute_http_request(
        self,
        api_def: APIDefinition,
        mapped_params: MappedParameters
    ) -> Tuple[ProcessedResult, Dict[str, str]]:
        """执行HTTP请求"""
        
        # 创建HTTP客户端
        client_config = self.client_config.copy()
        client_config["timeout"] = httpx.Timeout(api_def.timeout_seconds)
        
        async with httpx.AsyncClient(**client_config) as client:
            
            # 构建请求参数
            url = mapped_params.processed_url or api_def.url
            method = self._get_method_name(api_def.method)
            headers = mapped_params.headers.copy()
            
            # 添加认证
            # 确保 auth_config 是 AuthConfig 对象
            from src.models.api_tools import AuthConfig
            if isinstance(api_def.auth_config, dict):
                auth_config_obj = AuthConfig(**api_def.auth_config)
            else:
                auth_config_obj = api_def.auth_config

            self.auth_manager.add_authentication(headers, auth_config_obj)
            
            # 准备请求参数
            request_kwargs = {
                "method": method,
                "url": url,
                "headers": headers,
            }
            
            # 添加查询参数
            if mapped_params.query_params:
                if "?" in url:
                    url += "&" + urlencode(mapped_params.query_params)
                else:
                    url += "?" + urlencode(mapped_params.query_params)
                request_kwargs["url"] = url
            
            # 添加请求体
            if mapped_params.body_data is not None:
                if isinstance(mapped_params.body_data, dict):
                    # JSON请求体
                    request_kwargs["json"] = mapped_params.body_data
                    if "content-type" not in {k.lower(): v for k, v in headers.items()}:
                        headers["Content-Type"] = "application/json"
                else:
                    # 原始请求体
                    request_kwargs["content"] = mapped_params.body_data
            
            # 添加表单数据
            if mapped_params.form_data:
                request_kwargs["data"] = mapped_params.form_data
                if "content-type" not in {k.lower(): v for k, v in headers.items()}:
                    headers["Content-Type"] = "application/x-www-form-urlencoded"
            
            # 添加Basic认证（如果需要）
            basic_auth = self.auth_manager.get_basic_auth_tuple(auth_config_obj)
            if basic_auth:
                request_kwargs["auth"] = basic_auth
            
            # 执行请求
            start_time = time.time()
            response = await client.request(**request_kwargs)
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # 处理响应
            result = self.result_processor.process_response(
                api_def=api_def,
                status_code=response.status_code,
                headers=dict(response.headers),
                content=response.content,
                execution_time_ms=execution_time_ms
            )
            
            return result, headers
    
    def _get_method_name(self, method: HTTPMethod) -> str:
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
        return method_names.get(method, "GET")
    
    def _build_request_data(
        self,
        api_def: APIDefinition,
        mapped_params: MappedParameters,
        final_headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """构建请求数据用于日志记录"""
        request_data = {
            "method": self._get_method_name(api_def.method),
            "url": mapped_params.processed_url or api_def.url,
            "headers": final_headers.copy(),
            "query_params": mapped_params.query_params.copy(),
        }
        
        if mapped_params.body_data is not None:
            request_data["body"] = mapped_params.body_data
        
        if mapped_params.form_data:
            request_data["form_data"] = mapped_params.form_data.copy()
        
        # 遮蔽敏感信息
        request_data["headers"] = self._mask_sensitive_headers(request_data["headers"])
        
        return request_data
    
    def _mask_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """遮蔽敏感请求头"""
        masked_headers = {}
        sensitive_headers = ['authorization', 'x-api-key', 'cookie', 'set-cookie']
        
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                masked_headers[key] = self._mask_string(value)
            else:
                masked_headers[key] = value
        
        return masked_headers
    
    def _mask_string(self, value: str, show_chars: int = 4) -> str:
        """遮蔽字符串"""
        if not value or len(value) <= show_chars:
            return "*" * len(value)
        
        return value[:show_chars] + "*" * (len(value) - show_chars)
    
    async def test_api_connection(
        self,
        api_def: APIDefinition,
        test_parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        测试API连接
        
        Args:
            api_def: API定义
            test_parameters: 测试参数
            
        Returns:
            Dict: 测试结果
        """
        start_time = time.time()
        
        try:
            # 使用测试参数或默认参数
            parameters = test_parameters or {}
            
            # 为必需参数提供默认值
            required_params = self.parameter_mapper.get_required_parameters(api_def)
            for param_name in required_params:
                if param_name not in parameters:
                    # 提供简单的默认值
                    parameters[param_name] = "test"
            
            # 映射参数
            mapped_params = self.parameter_mapper.map_parameters(api_def, parameters)
            
            # 执行轻量级连接测试
            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
                url = mapped_params.processed_url or api_def.url
                headers = mapped_params.headers.copy()
                
                # 添加认证信息
                # 确保 auth_config 是 AuthConfig 对象
                from src.models.api_tools import AuthConfig
                if isinstance(api_def.auth_config, dict):
                    auth_config_obj = AuthConfig(**api_def.auth_config)
                else:
                    auth_config_obj = api_def.auth_config

                self.auth_manager.add_authentication(headers, auth_config_obj)
                
                # 只发送HEAD请求或GET请求测试连接
                method_name = self._get_method_name(api_def.method)
                if method_name.upper() in ["GET", "HEAD"]:
                    response = await client.head(url, headers=headers)
                else:
                    response = await client.get(url, headers=headers)
                
                execution_time_ms = int((time.time() - start_time) * 1000)
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response_headers": dict(response.headers),
                    "execution_time_ms": execution_time_ms,
                    "message": "连接测试成功"
                }
        
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": execution_time_ms,
                "message": "连接测试失败"
            }
