# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
API Call Log Models
API调用日志相关的数据模型
"""

from datetime import datetime
from typing import Optional, Dict, TYPE_CHECKING
from sqlalchemy import Column, JSON, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from src.config.database import Base

if TYPE_CHECKING:
    from .api_definition import APIDefinition


class APICallLog(Base):
    """API调用日志表模型"""

    __tablename__ = "api_call_logs"
    __table_args__ = {"schema": "api_tools"}

    id = Column(Integer, primary_key=True)
    api_definition_id = Column(Integer, ForeignKey("api_tools.api_definitions.id"), nullable=False, index=True)
    session_id = Column(String(100), nullable=True, index=True)

    # 请求和响应数据
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)

    # 执行信息
    status_code = Column(Integer, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default="now()")
    updated_at = Column(DateTime(timezone=True), server_default="now()")

    # 关联关系
    api_definition = relationship(
        "APIDefinition",
        back_populates="call_logs"
    )

    def is_successful(self) -> bool:
        """判断调用是否成功"""
        return (
            self.status_code is not None 
            and 200 <= self.status_code < 300 
            and self.error_message is None
        )
    
    def get_execution_time_seconds(self) -> Optional[float]:
        """获取执行时间（秒）"""
        if self.execution_time_ms is not None:
            return self.execution_time_ms / 1000.0
        return None
    
    def get_response_size(self) -> Optional[int]:
        """获取响应数据大小（字节）"""
        if self.response_data:
            import json
            try:
                return len(json.dumps(self.response_data).encode('utf-8'))
            except (TypeError, ValueError):
                return None
        return None
    
    def get_request_size(self) -> Optional[int]:
        """获取请求数据大小（字节）"""
        if self.request_data:
            import json
            try:
                return len(json.dumps(self.request_data).encode('utf-8'))
            except (TypeError, ValueError):
                return None
        return None
    
    def get_status_category(self) -> str:
        """获取状态分类"""
        if self.status_code is None:
            return "unknown"
        elif 200 <= self.status_code < 300:
            return "success"
        elif 300 <= self.status_code < 400:
            return "redirect"
        elif 400 <= self.status_code < 500:
            return "client_error"
        elif 500 <= self.status_code < 600:
            return "server_error"
        else:
            return "unknown"
    
    def get_summary(self) -> Dict[str, any]:
        """获取调用摘要信息"""
        return {
            "id": self.id,
            "api_definition_id": self.api_definition_id,
            "session_id": self.session_id,
            "status_code": self.status_code,
            "status_category": self.get_status_category(),
            "execution_time_ms": self.execution_time_ms,
            "execution_time_seconds": self.get_execution_time_seconds(),
            "is_successful": self.is_successful(),
            "has_error": bool(self.error_message),
            "error_message": self.error_message,
            "request_size": self.get_request_size(),
            "response_size": self.get_response_size(),
            "created_at": self.created_at,
        }
