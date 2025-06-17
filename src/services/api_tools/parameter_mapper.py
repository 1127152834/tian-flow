# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Parameter Mapper
参数映射器 - 严格按照ti-flow实现
"""

import re
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode
from pydantic import BaseModel

from src.models.api_tools import APIDefinition, Parameter, ParameterType


class MappedParameters(BaseModel):
    """映射后的参数"""
    
    query_params: Dict[str, Any] = {}
    headers: Dict[str, str] = {}
    path_params: Dict[str, Any] = {}
    body_data: Optional[Any] = None
    form_data: Dict[str, Any] = {}
    processed_url: Optional[str] = None


class ParameterMapper:
    """参数映射器"""
    
    def __init__(self):
        self.path_param_pattern = re.compile(r'\{([^}]+)\}')
    
    def map_parameters(
        self, 
        api_def: APIDefinition, 
        input_params: Dict[str, Any]
    ) -> MappedParameters:
        """
        映射输入参数到API调用参数
        
        Args:
            api_def: API定义
            input_params: 输入参数
            
        Returns:
            MappedParameters: 映射后的参数
        """
        mapped = MappedParameters()
        
        # 验证和转换参数
        validated_params = self._validate_and_convert_parameters(api_def, input_params)
        
        # 分类映射参数
        for param in api_def.parameters:
            if isinstance(param, dict):
                param = Parameter(**param)
            
            param_name = param.name
            param_value = validated_params.get(param_name)
            
            # 跳过空值（除非有默认值）
            if param_value is None and param.default_value is None:
                if param.required:
                    raise ValueError(f"必需参数 '{param_name}' 缺失")
                continue
            
            # 使用默认值
            if param_value is None:
                param_value = param.default_value
            
            # 根据参数类型分类
            if param.parameter_type == ParameterType.QUERY:
                mapped.query_params[param_name] = param_value
            elif param.parameter_type == ParameterType.HEADER:
                mapped.headers[param_name] = str(param_value)
            elif param.parameter_type == ParameterType.PATH:
                mapped.path_params[param_name] = param_value
            elif param.parameter_type == ParameterType.BODY:
                mapped.body_data = param_value
            elif param.parameter_type == ParameterType.FORM:
                mapped.form_data[param_name] = param_value
        
        # 处理路径参数
        mapped.processed_url = self._process_path_parameters(api_def.url, mapped.path_params)
        
        # 合并默认请求头
        if api_def.headers:
            for key, value in api_def.headers.items():
                if key not in mapped.headers:
                    mapped.headers[key] = value
        
        return mapped
    
    def _validate_and_convert_parameters(
        self, 
        api_def: APIDefinition, 
        input_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证和转换参数"""
        validated_params = {}
        
        for param_data in api_def.parameters:
            # 确保参数是 Parameter 对象
            if isinstance(param_data, dict):
                param = Parameter(**param_data)
            else:
                param = param_data

            param_name = param.name
            param_value = input_params.get(param_name)

            # 验证参数
            is_valid, error_msg = param.validate_value(param_value)
            if not is_valid:
                raise ValueError(error_msg)

            # 转换参数值
            if param_value is not None:
                validated_params[param_name] = param.get_converted_value(param_value)
        
        return validated_params
    
    def _process_path_parameters(self, url: str, path_params: Dict[str, Any]) -> str:
        """处理路径参数"""
        if not path_params:
            return url
        
        processed_url = url
        
        # 查找所有路径参数占位符
        matches = self.path_param_pattern.findall(url)
        
        for param_name in matches:
            if param_name in path_params:
                placeholder = f"{{{param_name}}}"
                param_value = str(path_params[param_name])
                processed_url = processed_url.replace(placeholder, param_value)
            else:
                raise ValueError(f"路径参数 '{param_name}' 未提供")
        
        return processed_url
    
    def get_required_parameters(self, api_def: APIDefinition) -> List[str]:
        """获取必需参数列表"""
        required_params = []
        
        for param in api_def.parameters:
            if isinstance(param, dict):
                param = Parameter(**param)
            
            if param.required:
                required_params.append(param.name)
        
        return required_params
    
    def get_parameter_schema(self, api_def: APIDefinition) -> Dict[str, Any]:
        """获取参数模式定义"""
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param in api_def.parameters:
            if isinstance(param, dict):
                param = Parameter(**param)
            
            param_schema = self._get_parameter_json_schema(param)
            schema["properties"][param.name] = param_schema
            
            if param.required:
                schema["required"].append(param.name)
        
        return schema
    
    def _get_parameter_json_schema(self, param: Parameter) -> Dict[str, Any]:
        """获取单个参数的JSON Schema"""
        from src.models.api_tools import DataType
        
        # 基础类型映射
        type_mapping = {
            DataType.STRING: "string",
            DataType.INTEGER: "integer",
            DataType.FLOAT: "number",
            DataType.BOOLEAN: "boolean",
            DataType.ARRAY: "array",
            DataType.OBJECT: "object",
            DataType.FILE: "string"
        }
        
        schema = {
            "type": type_mapping.get(param.data_type, "string"),
            "description": param.description or param.name
        }
        
        # 添加验证规则
        if param.data_type == DataType.STRING:
            if param.min_length is not None:
                schema["minLength"] = param.min_length
            if param.max_length is not None:
                schema["maxLength"] = param.max_length
            if param.pattern:
                schema["pattern"] = param.pattern
        
        elif param.data_type in [DataType.INTEGER, DataType.FLOAT]:
            if param.minimum is not None:
                schema["minimum"] = param.minimum
            if param.maximum is not None:
                schema["maximum"] = param.maximum
        
        elif param.data_type == DataType.ARRAY:
            if param.min_items is not None:
                schema["minItems"] = param.min_items
            if param.max_items is not None:
                schema["maxItems"] = param.max_items
            if param.item_type is not None:
                item_type_mapping = {
                    DataType.STRING: "string",
                    DataType.INTEGER: "integer",
                    DataType.FLOAT: "number",
                    DataType.BOOLEAN: "boolean"
                }
                schema["items"] = {"type": item_type_mapping.get(param.item_type, "string")}
        
        # 添加枚举值
        if param.enum_values:
            schema["enum"] = param.enum_values
        
        # 添加默认值
        if param.default_value is not None:
            schema["default"] = param.default_value
        
        # 添加示例值
        if param.example is not None:
            schema["example"] = param.example
        
        return schema
