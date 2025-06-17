# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Curl Parser
curl命令解析器 - 严格按照ti-flow实现
"""

import re
import json
import shlex
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, parse_qs
from pydantic import BaseModel

from src.models.api_tools import (
    HTTPMethod, AuthConfig, AuthType, Parameter, ParameterType, 
    DataType, RateLimit, ResponseConfig
)


class CurlParseResult(BaseModel):
    """curl解析结果"""
    
    success: bool
    name: Optional[str] = None
    description: Optional[str] = None
    method: Optional[HTTPMethod] = None
    url: Optional[str] = None
    headers: Dict[str, str] = {}
    auth_config: Optional[AuthConfig] = None
    parameters: List[Parameter] = []
    body_data: Optional[Any] = None
    error_message: Optional[str] = None


class CurlParser:
    """curl命令解析器"""
    
    def __init__(self):
        # curl命令的基本模式
        self.curl_pattern = re.compile(r'^curl\s+', re.IGNORECASE)
        
        # 常见的认证头模式
        self.auth_patterns = {
            'bearer': re.compile(r'bearer\s+(.+)', re.IGNORECASE),
            'basic': re.compile(r'basic\s+(.+)', re.IGNORECASE),
            'api_key': re.compile(r'(x-api-key|api-key|apikey)', re.IGNORECASE)
        }
    
    def parse_curl_command(self, curl_command: str) -> CurlParseResult:
        """
        解析curl命令并提取API定义信息
        
        Args:
            curl_command: curl命令字符串
            
        Returns:
            CurlParseResult: 解析结果
        """
        try:
            # 1. 预处理curl命令
            cleaned_curl = self._preprocess_curl(curl_command)
            
            # 2. 基础解析（正则匹配）
            basic_info = self._basic_curl_parse(cleaned_curl)
            
            # 3. 构建结果
            result = self._build_parse_result(basic_info)
            
            return result
            
        except Exception as e:
            return CurlParseResult(
                success=False,
                error_message=f"解析curl命令失败: {str(e)}"
            )
    
    def _preprocess_curl(self, curl_command: str) -> str:
        """预处理curl命令"""
        # 移除多余的空白字符
        cleaned = re.sub(r'\s+', ' ', curl_command.strip())
        
        # 移除行继续符
        cleaned = cleaned.replace('\\\n', ' ').replace('\\', '')
        
        # 确保以curl开头
        if not self.curl_pattern.match(cleaned):
            cleaned = 'curl ' + cleaned
        
        return cleaned
    
    def _basic_curl_parse(self, curl_command: str) -> Dict[str, Any]:
        """基础curl解析"""
        try:
            # 使用shlex分割命令行参数
            args = shlex.split(curl_command)
        except ValueError:
            # 如果shlex失败，使用简单的空格分割
            args = curl_command.split()
        
        parsed_info = {
            'method': HTTPMethod.GET,
            'url': None,
            'headers': {},
            'data': None,
            'auth_config': None,
            'query_params': {}
        }
        
        i = 1  # 跳过'curl'
        while i < len(args):
            arg = args[i]
            
            # URL参数（通常是最后一个没有前缀的参数）
            if not arg.startswith('-') and parsed_info['url'] is None:
                parsed_info['url'] = arg
            
            # HTTP方法
            elif arg in ['-X', '--request']:
                if i + 1 < len(args):
                    method_str = args[i + 1].upper()
                    parsed_info['method'] = self._parse_http_method(method_str)
                    i += 1
            
            # 请求头
            elif arg in ['-H', '--header']:
                if i + 1 < len(args):
                    header = args[i + 1]
                    self._parse_header(header, parsed_info)
                    i += 1
            
            # 请求体数据
            elif arg in ['-d', '--data', '--data-raw']:
                if i + 1 < len(args):
                    parsed_info['data'] = args[i + 1]
                    if parsed_info['method'] == HTTPMethod.GET:
                        parsed_info['method'] = HTTPMethod.POST
                    i += 1
            
            # JSON数据
            elif arg in ['--data-json']:
                if i + 1 < len(args):
                    parsed_info['data'] = args[i + 1]
                    parsed_info['headers']['Content-Type'] = 'application/json'
                    if parsed_info['method'] == HTTPMethod.GET:
                        parsed_info['method'] = HTTPMethod.POST
                    i += 1
            
            # 表单数据
            elif arg in ['-F', '--form']:
                if i + 1 < len(args):
                    # 表单数据处理
                    if 'form_data' not in parsed_info:
                        parsed_info['form_data'] = []
                    parsed_info['form_data'].append(args[i + 1])
                    if parsed_info['method'] == HTTPMethod.GET:
                        parsed_info['method'] = HTTPMethod.POST
                    i += 1
            
            # 用户认证
            elif arg in ['-u', '--user']:
                if i + 1 < len(args):
                    self._parse_basic_auth(args[i + 1], parsed_info)
                    i += 1
            
            i += 1
        
        # 解析URL中的查询参数
        if parsed_info['url']:
            parsed_info = self._extract_query_params(parsed_info)
        
        return parsed_info
    
    def _parse_http_method(self, method_str: str) -> HTTPMethod:
        """解析HTTP方法"""
        method_mapping = {
            'GET': HTTPMethod.GET,
            'POST': HTTPMethod.POST,
            'PUT': HTTPMethod.PUT,
            'DELETE': HTTPMethod.DELETE,
            'PATCH': HTTPMethod.PATCH,
            'HEAD': HTTPMethod.HEAD,
            'OPTIONS': HTTPMethod.OPTIONS
        }
        return method_mapping.get(method_str.upper(), HTTPMethod.GET)
    
    def _parse_header(self, header: str, parsed_info: Dict[str, Any]) -> None:
        """解析请求头"""
        if ':' in header:
            key, value = header.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            parsed_info['headers'][key] = value
            
            # 检查认证头
            if key.lower() == 'authorization':
                self._parse_authorization_header(value, parsed_info)
            elif self.auth_patterns['api_key'].match(key):
                # API Key认证
                parsed_info['auth_config'] = AuthConfig(
                    auth_type=AuthType.API_KEY,
                    api_key=value,
                    api_key_header=key
                )
    
    def _parse_authorization_header(self, auth_value: str, parsed_info: Dict[str, Any]) -> None:
        """解析Authorization头"""
        auth_value = auth_value.strip()
        
        # Bearer Token
        bearer_match = self.auth_patterns['bearer'].match(auth_value)
        if bearer_match:
            parsed_info['auth_config'] = AuthConfig(
                auth_type=AuthType.BEARER,
                bearer_token=bearer_match.group(1)
            )
            return
        
        # Basic Auth
        basic_match = self.auth_patterns['basic'].match(auth_value)
        if basic_match:
            try:
                import base64
                decoded = base64.b64decode(basic_match.group(1)).decode('utf-8')
                if ':' in decoded:
                    username, password = decoded.split(':', 1)
                    parsed_info['auth_config'] = AuthConfig(
                        auth_type=AuthType.BASIC,
                        username=username,
                        password=password
                    )
            except Exception:
                pass
    
    def _parse_basic_auth(self, user_info: str, parsed_info: Dict[str, Any]) -> None:
        """解析Basic认证"""
        if ':' in user_info:
            username, password = user_info.split(':', 1)
            parsed_info['auth_config'] = AuthConfig(
                auth_type=AuthType.BASIC,
                username=username,
                password=password
            )
    
    def _extract_query_params(self, parsed_info: Dict[str, Any]) -> Dict[str, Any]:
        """从URL中提取查询参数"""
        url = parsed_info['url']
        if not url:
            return parsed_info
        
        try:
            parsed_url = urlparse(url)
            if parsed_url.query:
                query_params = parse_qs(parsed_url.query, keep_blank_values=True)
                # 转换为简单的字典（取第一个值）
                parsed_info['query_params'] = {
                    k: v[0] if v else '' for k, v in query_params.items()
                }
                
                # 移除URL中的查询参数
                parsed_info['url'] = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        except Exception:
            pass
        
        return parsed_info
    
    def _build_parse_result(self, parsed_info: Dict[str, Any]) -> CurlParseResult:
        """构建解析结果"""
        if not parsed_info.get('url'):
            return CurlParseResult(
                success=False,
                error_message="未找到有效的URL"
            )
        
        # 生成API名称
        url = parsed_info['url']
        parsed_url = urlparse(url)
        api_name = f"{parsed_info['method'].name} {parsed_url.path or '/'}"
        if len(api_name) > 100:
            api_name = api_name[:97] + "..."
        
        # 生成描述
        description = f"从curl命令导入的API: {url}"
        
        # 构建参数列表
        parameters = []
        
        # 添加查询参数
        for param_name, param_value in parsed_info.get('query_params', {}).items():
            parameters.append(Parameter(
                name=param_name,
                description=f"查询参数: {param_name}",
                parameter_type=ParameterType.QUERY,
                data_type=DataType.STRING,
                default_value=param_value,
                example=param_value
            ))
        
        # 处理请求体数据
        body_data = None
        if parsed_info.get('data'):
            data = parsed_info['data']
            try:
                # 尝试解析为JSON
                json_data = json.loads(data)
                body_data = json_data
                
                # 为JSON字段创建参数
                if isinstance(json_data, dict):
                    for key, value in json_data.items():
                        parameters.append(Parameter(
                            name=key,
                            description=f"请求体参数: {key}",
                            parameter_type=ParameterType.BODY,
                            data_type=self._infer_data_type(value),
                            default_value=value,
                            example=value
                        ))
            except json.JSONDecodeError:
                # 不是JSON，可能是表单数据
                if '=' in data:
                    # 解析表单数据
                    for pair in data.split('&'):
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            parameters.append(Parameter(
                                name=key,
                                description=f"表单参数: {key}",
                                parameter_type=ParameterType.FORM,
                                data_type=DataType.STRING,
                                default_value=value,
                                example=value
                            ))
                else:
                    # 原始数据
                    body_data = data
        
        # 处理表单数据
        if parsed_info.get('form_data'):
            for form_item in parsed_info['form_data']:
                if '=' in form_item:
                    key, value = form_item.split('=', 1)
                    parameters.append(Parameter(
                        name=key,
                        description=f"表单参数: {key}",
                        parameter_type=ParameterType.FORM,
                        data_type=DataType.STRING,
                        default_value=value,
                        example=value
                    ))
        
        return CurlParseResult(
            success=True,
            name=api_name,
            description=description,
            method=parsed_info['method'],
            url=parsed_info['url'],
            headers=parsed_info.get('headers', {}),
            auth_config=parsed_info.get('auth_config'),
            parameters=parameters,
            body_data=body_data
        )
    
    def _infer_data_type(self, value: Any) -> DataType:
        """推断数据类型"""
        if isinstance(value, bool):
            return DataType.BOOLEAN
        elif isinstance(value, int):
            return DataType.INTEGER
        elif isinstance(value, float):
            return DataType.FLOAT
        elif isinstance(value, list):
            return DataType.ARRAY
        elif isinstance(value, dict):
            return DataType.OBJECT
        else:
            return DataType.STRING
    
    def generate_api_definition_data(self, parse_result: CurlParseResult) -> Dict[str, Any]:
        """生成API定义数据"""
        if not parse_result.success:
            raise ValueError(parse_result.error_message)

        return {
            "name": parse_result.name,
            "description": parse_result.description,
            "category": "imported",
            "method": parse_result.method,
            "url": parse_result.url,
            "headers": parse_result.headers,
            "timeout_seconds": 30,
            "auth_config": parse_result.auth_config or AuthConfig(),
            "parameters": parse_result.parameters,
            "response_config": ResponseConfig.create_default_json(),
            "rate_limit": RateLimit.create_default(),
            "enabled": True
        }
