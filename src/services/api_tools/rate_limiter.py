# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Rate Limiter
限流器 - 严格按照ti-flow实现
"""

import time
import asyncio
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque

from src.models.api_tools import RateLimit


class RateLimitExceeded(Exception):
    """限流超出异常"""
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class RateLimiter:
    """限流器"""
    
    def __init__(self):
        # 存储每个API的请求记录
        self._request_records: Dict[str, deque] = defaultdict(deque)
        # 存储突发请求计数
        self._burst_counts: Dict[str, int] = defaultdict(int)
        # 存储最后重置时间
        self._last_reset: Dict[str, float] = defaultdict(float)
        # 锁，用于并发控制
        self._locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
    
    async def check_rate_limit(
        self,
        api_id: int,
        rate_limit: RateLimit,
        identifier: Optional[str] = None
    ) -> None:
        """
        检查限流
        
        Args:
            api_id: API ID
            rate_limit: 限流配置
            identifier: 标识符（如会话ID）
            
        Raises:
            RateLimitExceeded: 当超出限流时抛出
        """
        if not rate_limit.is_enabled():
            return
        
        # 生成限流键
        rate_limit_key = f"api_{api_id}"
        if identifier:
            rate_limit_key += f"_{identifier}"
        
        # 获取锁
        async with self._locks[rate_limit_key]:
            await self._check_rate_limit_internal(rate_limit_key, rate_limit)
    
    async def _check_rate_limit_internal(
        self,
        rate_limit_key: str,
        rate_limit: RateLimit
    ) -> None:
        """内部限流检查"""
        current_time = time.time()
        time_window = rate_limit.get_time_window_seconds()
        
        # 获取请求记录
        request_times = self._request_records[rate_limit_key]
        
        # 清理过期记录
        cutoff_time = current_time - time_window
        while request_times and request_times[0] <= cutoff_time:
            request_times.popleft()
        
        # 检查是否超出限制
        current_requests = len(request_times)
        
        if current_requests >= rate_limit.max_requests:
            if rate_limit.block_on_limit:
                # 计算重试等待时间
                retry_after = rate_limit.retry_after_seconds
                if retry_after is None and request_times:
                    # 计算到最早请求过期的时间
                    oldest_request = request_times[0]
                    retry_after = int(oldest_request + time_window - current_time) + 1
                
                raise RateLimitExceeded(
                    f"API调用频率超出限制: {rate_limit.max_requests}次/{time_window}秒",
                    retry_after=retry_after
                )
            else:
                # 不阻塞，但记录警告
                pass
        
        # 检查突发限制
        burst_size = rate_limit.get_effective_burst_size()
        burst_count = self._burst_counts[rate_limit_key]
        
        # 重置突发计数（每分钟重置一次）
        last_reset = self._last_reset[rate_limit_key]
        if current_time - last_reset >= 60:  # 1分钟
            self._burst_counts[rate_limit_key] = 0
            self._last_reset[rate_limit_key] = current_time
            burst_count = 0
        
        # 检查突发限制
        if burst_count >= burst_size:
            if rate_limit.block_on_limit:
                raise RateLimitExceeded(
                    f"突发请求超出限制: {burst_size}次/分钟",
                    retry_after=60
                )
        
        # 记录本次请求
        request_times.append(current_time)
        self._burst_counts[rate_limit_key] += 1
    
    def get_rate_limit_status(
        self,
        api_id: int,
        rate_limit: RateLimit,
        identifier: Optional[str] = None
    ) -> Dict[str, any]:
        """
        获取限流状态
        
        Args:
            api_id: API ID
            rate_limit: 限流配置
            identifier: 标识符
            
        Returns:
            Dict: 限流状态信息
        """
        if not rate_limit.is_enabled():
            return {
                "enabled": False,
                "current_requests": 0,
                "max_requests": rate_limit.max_requests,
                "time_window_seconds": rate_limit.get_time_window_seconds(),
                "remaining_requests": rate_limit.max_requests,
                "reset_time": None
            }
        
        # 生成限流键
        rate_limit_key = f"api_{api_id}"
        if identifier:
            rate_limit_key += f"_{identifier}"
        
        current_time = time.time()
        time_window = rate_limit.get_time_window_seconds()
        
        # 获取请求记录
        request_times = self._request_records[rate_limit_key]
        
        # 清理过期记录
        cutoff_time = current_time - time_window
        while request_times and request_times[0] <= cutoff_time:
            request_times.popleft()
        
        current_requests = len(request_times)
        remaining_requests = max(0, rate_limit.max_requests - current_requests)
        
        # 计算重置时间
        reset_time = None
        if request_times:
            oldest_request = request_times[0]
            reset_time = oldest_request + time_window
        
        return {
            "enabled": True,
            "current_requests": current_requests,
            "max_requests": rate_limit.max_requests,
            "time_window_seconds": time_window,
            "remaining_requests": remaining_requests,
            "reset_time": reset_time,
            "burst_count": self._burst_counts[rate_limit_key],
            "burst_limit": rate_limit.get_effective_burst_size()
        }
    
    def reset_rate_limit(
        self,
        api_id: int,
        identifier: Optional[str] = None
    ) -> None:
        """
        重置限流计数
        
        Args:
            api_id: API ID
            identifier: 标识符
        """
        rate_limit_key = f"api_{api_id}"
        if identifier:
            rate_limit_key += f"_{identifier}"
        
        # 清空记录
        if rate_limit_key in self._request_records:
            self._request_records[rate_limit_key].clear()
        
        if rate_limit_key in self._burst_counts:
            self._burst_counts[rate_limit_key] = 0
        
        if rate_limit_key in self._last_reset:
            self._last_reset[rate_limit_key] = time.time()
    
    def cleanup_expired_records(self) -> None:
        """清理过期记录"""
        current_time = time.time()
        
        # 清理请求记录（保留最近1小时的记录）
        cutoff_time = current_time - 3600  # 1小时
        
        for key, request_times in list(self._request_records.items()):
            while request_times and request_times[0] <= cutoff_time:
                request_times.popleft()
            
            # 如果队列为空，删除键
            if not request_times:
                del self._request_records[key]
        
        # 清理突发计数（超过1小时的重置）
        for key, last_reset in list(self._last_reset.items()):
            if current_time - last_reset > 3600:
                if key in self._burst_counts:
                    del self._burst_counts[key]
                del self._last_reset[key]
    
    async def wait_for_rate_limit_reset(
        self,
        api_id: int,
        rate_limit: RateLimit,
        identifier: Optional[str] = None
    ) -> None:
        """
        等待限流重置
        
        Args:
            api_id: API ID
            rate_limit: 限流配置
            identifier: 标识符
        """
        if not rate_limit.is_enabled():
            return
        
        status = self.get_rate_limit_status(api_id, rate_limit, identifier)
        
        if status["remaining_requests"] > 0:
            return
        
        # 计算等待时间
        if status["reset_time"]:
            wait_time = max(0, status["reset_time"] - time.time())
            if wait_time > 0:
                await asyncio.sleep(wait_time)


# 全局限流器实例
rate_limiter = RateLimiter()
