# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Rate Limit Models
限流配置相关的数据模型
"""

from enum import IntEnum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class RateLimitType(IntEnum):
    """限流类型枚举"""
    NONE = 0        # 无限流
    PER_SECOND = 1  # 每秒限流
    PER_MINUTE = 2  # 每分钟限流
    PER_HOUR = 3    # 每小时限流
    PER_DAY = 4     # 每天限流


class RateLimit(BaseModel):
    """限流配置模型"""
    
    enabled: bool = Field(default=False, description="是否启用限流")
    rate_limit_type: RateLimitType = Field(default=RateLimitType.NONE, description="限流类型")
    max_requests: int = Field(default=100, ge=1, description="最大请求数")
    time_window_seconds: int = Field(default=60, ge=1, description="时间窗口（秒）")
    
    # 突发流量控制
    burst_size: Optional[int] = Field(default=None, ge=1, description="突发请求数量")
    
    # 限流策略
    block_on_limit: bool = Field(default=True, description="达到限制时是否阻塞请求")
    retry_after_seconds: Optional[int] = Field(default=None, ge=1, description="重试等待时间（秒）")
    
    @field_validator('max_requests')
    @classmethod
    def validate_max_requests(cls, v):
        """验证最大请求数"""
        if v <= 0:
            raise ValueError('最大请求数必须大于0')
        return v
    
    @field_validator('time_window_seconds')
    @classmethod
    def validate_time_window(cls, v):
        """验证时间窗口"""
        if v <= 0:
            raise ValueError('时间窗口必须大于0秒')
        return v
    
    @field_validator('burst_size')
    @classmethod
    def validate_burst_size(cls, v, info):
        """验证突发请求数量"""
        if v is not None:
            max_requests = info.data.get('max_requests', 100)
            if v <= 0:
                raise ValueError('突发请求数量必须大于0')
            if v > max_requests * 2:
                raise ValueError('突发请求数量不能超过最大请求数的2倍')
        return v
    
    def get_time_window_seconds(self) -> int:
        """根据限流类型获取时间窗口（秒）"""
        if self.rate_limit_type == RateLimitType.PER_SECOND:
            return 1
        elif self.rate_limit_type == RateLimitType.PER_MINUTE:
            return 60
        elif self.rate_limit_type == RateLimitType.PER_HOUR:
            return 3600
        elif self.rate_limit_type == RateLimitType.PER_DAY:
            return 86400
        else:
            return self.time_window_seconds
    
    def get_effective_burst_size(self) -> int:
        """获取有效的突发请求数量"""
        if self.burst_size is not None:
            return self.burst_size
        # 默认突发大小为最大请求数的20%，最少为1
        return max(1, int(self.max_requests * 0.2))
    
    def is_enabled(self) -> bool:
        """检查限流是否启用"""
        return self.enabled and self.rate_limit_type != RateLimitType.NONE
    
    def get_rate_limit_key(self, identifier: str) -> str:
        """获取限流键"""
        return f"rate_limit:{identifier}:{self.rate_limit_type.value}"
    
    def get_description(self) -> str:
        """获取限流配置描述"""
        if not self.is_enabled():
            return "无限流"
        
        type_names = {
            RateLimitType.PER_SECOND: "每秒",
            RateLimitType.PER_MINUTE: "每分钟", 
            RateLimitType.PER_HOUR: "每小时",
            RateLimitType.PER_DAY: "每天"
        }
        
        type_name = type_names.get(self.rate_limit_type, "自定义时间窗口")
        description = f"{type_name}最多 {self.max_requests} 次请求"
        
        if self.burst_size:
            description += f"，突发 {self.burst_size} 次"
        
        if not self.block_on_limit:
            description += "，超限不阻塞"
        
        if self.retry_after_seconds:
            description += f"，重试等待 {self.retry_after_seconds} 秒"
        
        return description
    
    @classmethod
    def create_default(cls) -> "RateLimit":
        """创建默认限流配置"""
        return cls(
            enabled=False,
            rate_limit_type=RateLimitType.NONE,
            max_requests=100,
            time_window_seconds=60,
            block_on_limit=True
        )
    
    @classmethod
    def create_per_minute(cls, max_requests: int = 60) -> "RateLimit":
        """创建每分钟限流配置"""
        return cls(
            enabled=True,
            rate_limit_type=RateLimitType.PER_MINUTE,
            max_requests=max_requests,
            time_window_seconds=60,
            block_on_limit=True
        )
    
    @classmethod
    def create_per_hour(cls, max_requests: int = 1000) -> "RateLimit":
        """创建每小时限流配置"""
        return cls(
            enabled=True,
            rate_limit_type=RateLimitType.PER_HOUR,
            max_requests=max_requests,
            time_window_seconds=3600,
            block_on_limit=True
        )
