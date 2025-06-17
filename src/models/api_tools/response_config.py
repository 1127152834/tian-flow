# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Response Config Models
响应配置相关的数据模型
"""

from enum import IntEnum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class ResponseType(IntEnum):
    """响应类型枚举"""
    JSON = 1        # JSON响应
    XML = 2         # XML响应
    TEXT = 3        # 纯文本响应
    HTML = 4        # HTML响应
    BINARY = 5      # 二进制响应


class FieldRole(IntEnum):
    """字段角色枚举"""
    DATA = 1        # 数据字段
    STATUS = 2      # 状态字段
    MESSAGE = 3     # 消息字段
    ERROR = 4       # 错误字段
    PAGINATION = 5  # 分页字段


class ResponseField(BaseModel):
    """响应字段定义模型"""
    
    name: str = Field(description="字段名称")
    path: str = Field(description="字段路径（JSONPath或XPath）")
    role: FieldRole = Field(default=FieldRole.DATA, description="字段角色")
    data_type: str = Field(default="string", description="数据类型")
    description: Optional[str] = Field(default="", description="字段描述")
    required: bool = Field(default=False, description="是否必需")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """验证字段名称"""
        if not v or not v.strip():
            raise ValueError('字段名称不能为空')
        return v.strip()
    
    @field_validator('path')
    @classmethod
    def validate_path(cls, v):
        """验证字段路径"""
        if not v or not v.strip():
            raise ValueError('字段路径不能为空')
        return v.strip()


class ResponseConfig(BaseModel):
    """响应配置模型"""
    
    response_type: ResponseType = Field(default=ResponseType.JSON, description="响应类型")
    content_type: str = Field(default="application/json", description="内容类型")
    encoding: str = Field(default="utf-8", description="编码格式")
    
    # 字段定义
    fields: List[ResponseField] = Field(default_factory=list, description="响应字段定义")
    
    # 特殊字段路径
    primary_data_field: Optional[str] = Field(default=None, description="主数据字段路径")
    status_field: Optional[str] = Field(default=None, description="状态字段路径")
    message_field: Optional[str] = Field(default=None, description="消息字段路径")
    
    # 成功条件
    success_conditions: Dict[str, Any] = Field(default_factory=dict, description="成功条件")
    
    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v):
        """验证内容类型"""
        if not v or not v.strip():
            return "application/json"
        return v.strip()
    
    @field_validator('encoding')
    @classmethod
    def validate_encoding(cls, v):
        """验证编码格式"""
        if not v or not v.strip():
            return "utf-8"
        return v.strip()
    
    def get_field_by_role(self, role: FieldRole) -> Optional[ResponseField]:
        """根据角色获取字段"""
        for field in self.fields:
            if field.role == role:
                return field
        return None
    
    def get_data_fields(self) -> List[ResponseField]:
        """获取数据字段列表"""
        return [field for field in self.fields if field.role == FieldRole.DATA]
    
    def get_status_field(self) -> Optional[ResponseField]:
        """获取状态字段"""
        return self.get_field_by_role(FieldRole.STATUS)
    
    def get_message_field(self) -> Optional[ResponseField]:
        """获取消息字段"""
        return self.get_field_by_role(FieldRole.MESSAGE)
    
    def get_error_field(self) -> Optional[ResponseField]:
        """获取错误字段"""
        return self.get_field_by_role(FieldRole.ERROR)
    
    def extract_field_value(self, response_data: Any, field_path: str) -> Any:
        """从响应数据中提取字段值"""
        if not field_path or not response_data:
            return None
        
        try:
            # 简单的JSONPath实现
            if isinstance(response_data, dict):
                # 支持点号分隔的路径，如 "data.items.0.name"
                keys = field_path.split('.')
                value = response_data
                
                for key in keys:
                    if isinstance(value, dict):
                        value = value.get(key)
                    elif isinstance(value, list) and key.isdigit():
                        index = int(key)
                        if 0 <= index < len(value):
                            value = value[index]
                        else:
                            return None
                    else:
                        return None
                
                return value
            
        except (KeyError, IndexError, ValueError, TypeError):
            pass
        
        return None
    
    def extract_primary_data(self, response_data: Any) -> Any:
        """提取主要数据"""
        if self.primary_data_field:
            return self.extract_field_value(response_data, self.primary_data_field)
        return response_data
    
    def extract_status(self, response_data: Any) -> Optional[Any]:
        """提取状态信息"""
        if self.status_field:
            return self.extract_field_value(response_data, self.status_field)
        return None
    
    def extract_message(self, response_data: Any) -> Optional[str]:
        """提取消息信息"""
        if self.message_field:
            value = self.extract_field_value(response_data, self.message_field)
            return str(value) if value is not None else None
        return None
    
    def is_success_response(self, response_data: Any, status_code: int = 200) -> bool:
        """判断响应是否成功"""
        # 首先检查HTTP状态码
        if status_code < 200 or status_code >= 300:
            return False
        
        # 检查自定义成功条件
        if self.success_conditions:
            for field_path, expected_value in self.success_conditions.items():
                actual_value = self.extract_field_value(response_data, field_path)
                if actual_value != expected_value:
                    return False
        
        # 检查状态字段
        status_value = self.extract_status(response_data)
        if status_value is not None:
            # 常见的成功状态值
            success_values = [True, "success", "ok", "SUCCESS", "OK", 200, 0]
            return status_value in success_values
        
        # 默认认为是成功的
        return True
    
    @classmethod
    def create_default_json(cls) -> "ResponseConfig":
        """创建默认JSON响应配置"""
        return cls(
            response_type=ResponseType.JSON,
            content_type="application/json",
            encoding="utf-8",
            fields=[],
            success_conditions={}
        )
    
    @classmethod
    def create_rest_api_config(cls) -> "ResponseConfig":
        """创建REST API响应配置"""
        return cls(
            response_type=ResponseType.JSON,
            content_type="application/json",
            encoding="utf-8",
            fields=[
                ResponseField(
                    name="data",
                    path="data",
                    role=FieldRole.DATA,
                    description="响应数据"
                ),
                ResponseField(
                    name="status",
                    path="status",
                    role=FieldRole.STATUS,
                    description="响应状态"
                ),
                ResponseField(
                    name="message",
                    path="message",
                    role=FieldRole.MESSAGE,
                    description="响应消息"
                )
            ],
            primary_data_field="data",
            status_field="status",
            message_field="message",
            success_conditions={"status": "success"}
        )
