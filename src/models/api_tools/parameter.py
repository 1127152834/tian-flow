# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Parameter Models
参数定义相关的数据模型
"""

from enum import IntEnum
from typing import Optional, Any, Union, List
from pydantic import BaseModel, Field, field_validator


class ParameterType(IntEnum):
    """参数类型枚举"""
    QUERY = 0       # 查询参数
    HEADER = 1      # 请求头参数
    PATH = 2        # 路径参数
    BODY = 3        # 请求体参数
    FORM = 4        # 表单参数


class DataType(IntEnum):
    """数据类型枚举"""
    STRING = 0      # 字符串
    INTEGER = 1     # 整数
    FLOAT = 2       # 浮点数
    BOOLEAN = 3     # 布尔值
    ARRAY = 4       # 数组
    OBJECT = 5      # 对象
    FILE = 6        # 文件


class Parameter(BaseModel):
    """参数定义模型"""
    
    name: str = Field(description="参数名称")
    description: Optional[str] = Field(default="", description="参数描述")
    parameter_type: ParameterType = Field(description="参数类型")
    data_type: DataType = Field(default=DataType.STRING, description="数据类型")
    
    # 验证规则
    required: bool = Field(default=False, description="是否必需")
    default_value: Optional[Any] = Field(default=None, description="默认值")
    
    # 字符串类型验证
    min_length: Optional[int] = Field(default=None, ge=0, description="最小长度")
    max_length: Optional[int] = Field(default=None, ge=0, description="最大长度")
    pattern: Optional[str] = Field(default=None, description="正则表达式模式")
    
    # 数值类型验证
    minimum: Optional[Union[int, float]] = Field(default=None, description="最小值")
    maximum: Optional[Union[int, float]] = Field(default=None, description="最大值")
    
    # 数组类型验证
    min_items: Optional[int] = Field(default=None, ge=0, description="数组最小元素数")
    max_items: Optional[int] = Field(default=None, ge=0, description="数组最大元素数")
    item_type: Optional[DataType] = Field(default=None, description="数组元素类型")
    
    # 枚举值
    enum_values: Optional[List[Any]] = Field(default=None, description="枚举值列表")
    
    # 示例值
    example: Optional[Any] = Field(default=None, description="示例值")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """验证参数名称"""
        if not v or not v.strip():
            raise ValueError('参数名称不能为空')
        
        # 移除首尾空格
        v = v.strip()
        
        # 检查长度
        if len(v) > 100:
            raise ValueError('参数名称不能超过100个字符')
        
        return v
    
    @field_validator('min_length', 'max_length')
    @classmethod
    def validate_length_constraints(cls, v):
        """验证长度约束"""
        if v is not None and v < 0:
            raise ValueError('长度约束不能为负数')
        return v
    
    @field_validator('min_items', 'max_items')
    @classmethod
    def validate_items_constraints(cls, v):
        """验证数组元素数量约束"""
        if v is not None and v < 0:
            raise ValueError('数组元素数量约束不能为负数')
        return v
    
    def validate_value(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        验证参数值
        
        Returns:
            tuple: (是否有效, 错误信息)
        """
        # 检查必需参数
        if self.required and (value is None or value == ""):
            return False, f"参数 '{self.name}' 是必需的"
        
        # 如果值为空且不是必需的，使用默认值
        if value is None or value == "":
            if self.default_value is not None:
                value = self.default_value
            else:
                return True, None
        
        # 数据类型验证
        try:
            if self.data_type == DataType.STRING:
                value = str(value)
                
                # 长度验证
                if self.min_length is not None and len(value) < self.min_length:
                    return False, f"参数 '{self.name}' 长度不能少于 {self.min_length} 个字符"
                if self.max_length is not None and len(value) > self.max_length:
                    return False, f"参数 '{self.name}' 长度不能超过 {self.max_length} 个字符"
                
                # 正则表达式验证
                if self.pattern:
                    import re
                    if not re.match(self.pattern, value):
                        return False, f"参数 '{self.name}' 格式不正确"
            
            elif self.data_type == DataType.INTEGER:
                value = int(value)
                
                # 数值范围验证
                if self.minimum is not None and value < self.minimum:
                    return False, f"参数 '{self.name}' 不能小于 {self.minimum}"
                if self.maximum is not None and value > self.maximum:
                    return False, f"参数 '{self.name}' 不能大于 {self.maximum}"
            
            elif self.data_type == DataType.FLOAT:
                value = float(value)
                
                # 数值范围验证
                if self.minimum is not None and value < self.minimum:
                    return False, f"参数 '{self.name}' 不能小于 {self.minimum}"
                if self.maximum is not None and value > self.maximum:
                    return False, f"参数 '{self.name}' 不能大于 {self.maximum}"
            
            elif self.data_type == DataType.BOOLEAN:
                if isinstance(value, str):
                    value = value.lower() in ('true', '1', 'yes', 'on')
                else:
                    value = bool(value)
            
            elif self.data_type == DataType.ARRAY:
                if not isinstance(value, list):
                    return False, f"参数 '{self.name}' 必须是数组类型"
                
                # 数组长度验证
                if self.min_items is not None and len(value) < self.min_items:
                    return False, f"参数 '{self.name}' 数组元素不能少于 {self.min_items} 个"
                if self.max_items is not None and len(value) > self.max_items:
                    return False, f"参数 '{self.name}' 数组元素不能超过 {self.max_items} 个"
        
        except (ValueError, TypeError) as e:
            return False, f"参数 '{self.name}' 数据类型转换失败: {str(e)}"
        
        # 枚举值验证
        if self.enum_values and value not in self.enum_values:
            return False, f"参数 '{self.name}' 值必须是以下之一: {', '.join(map(str, self.enum_values))}"
        
        return True, None
    
    def get_converted_value(self, value: Any) -> Any:
        """获取转换后的参数值"""
        if value is None or value == "":
            return self.default_value
        
        try:
            if self.data_type == DataType.STRING:
                return str(value)
            elif self.data_type == DataType.INTEGER:
                return int(value)
            elif self.data_type == DataType.FLOAT:
                return float(value)
            elif self.data_type == DataType.BOOLEAN:
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                return bool(value)
            elif self.data_type == DataType.ARRAY:
                return list(value) if not isinstance(value, list) else value
            else:
                return value
        except (ValueError, TypeError):
            return value
