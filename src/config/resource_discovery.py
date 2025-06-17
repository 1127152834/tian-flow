# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
资源发现配置管理

提供YAML配置文件的解析、验证和管理功能
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class VectorConfig:
    """向量配置"""
    similarity_threshold: float = 0.3
    max_results: int = 10
    batch_size: int = 100
    timeout_seconds: int = 30


@dataclass
class ResourceConfig:
    """资源配置"""
    table: str
    fields: List[str]
    tool: str
    description: str = ""
    enabled: bool = True


@dataclass
class TriggerConfig:
    """触发器配置"""
    trigger_prefix: str = "rd_trigger_"
    notify_channel_prefix: str = "rd_notify_"
    enable_realtime: bool = True
    batch_delay_ms: int = 1000


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    log_matching_details: bool = False
    log_vectorization: bool = True


@dataclass
class MatcherConfig:
    """匹配器配置"""
    # 置信度权重配置
    confidence_weights: Dict[str, float] = None
    # 多向量类型权重配置
    vector_type_weights: Dict[str, float] = None
    # 针对不同资源类型的特殊权重配置
    resource_type_weights: Dict[str, Dict[str, float]] = None

    def __post_init__(self):
        if self.confidence_weights is None:
            self.confidence_weights = {
                "similarity": 0.6,
                "usage_history": 0.2,
                "performance": 0.1,
                "context": 0.1
            }

        if self.vector_type_weights is None:
            self.vector_type_weights = {
                "name": 0.3,
                "description": 0.4,
                "capabilities": 0.2,
                "composite": 0.1
            }

        if self.resource_type_weights is None:
            self.resource_type_weights = {
                "TEXT2SQL": {
                    "name": 0.4,
                    "description": 0.3,
                    "capabilities": 0.2,
                    "composite": 0.1
                },
                "DATABASE": {
                    "name": 0.2,
                    "description": 0.3,
                    "capabilities": 0.3,
                    "composite": 0.2
                },
                "API": {
                    "name": 0.3,
                    "description": 0.3,
                    "capabilities": 0.2,
                    "composite": 0.2
                },
                "TOOL": {
                    "name": 0.3,
                    "description": 0.4,
                    "capabilities": 0.2,
                    "composite": 0.1
                }
            }


class ResourceDiscoveryConfig:
    """资源发现配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径，如果为None则从环境变量读取
        """
        if config_path is None:
            config_path = os.getenv('RESOURCE_DISCOVERY_CONFIG_PATH', 'config/resource-discovery.yaml')

        self.config_path = Path(config_path)
        self.config_data: Dict[str, Any] = {}
        self.last_modified: Optional[datetime] = None

        # 环境变量配置
        self.enable_triggers = os.getenv('RESOURCE_DISCOVERY_ENABLE_TRIGGERS', 'true').lower() == 'true'
        self.auto_sync = os.getenv('RESOURCE_DISCOVERY_AUTO_SYNC', 'true').lower() == 'true'
        self.log_level = os.getenv('RESOURCE_DISCOVERY_LOG_LEVEL', 'INFO')

        # 配置对象
        self.vector_config: VectorConfig = VectorConfig()
        self.matcher_config: MatcherConfig = MatcherConfig()
        self.resources: List[ResourceConfig] = []
        self.trigger_config: TriggerConfig = TriggerConfig()
        self.logging_config: LoggingConfig = LoggingConfig()

        # 加载配置
        self.load_config()
    
    def load_config(self) -> None:
        """加载配置文件"""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
            
            # 检查文件修改时间
            current_modified = datetime.fromtimestamp(self.config_path.stat().st_mtime)
            if self.last_modified and current_modified <= self.last_modified:
                return  # 文件未修改，无需重新加载
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f)
            
            self.last_modified = current_modified
            self._parse_config()
            
            logger.info(f"✅ 配置文件加载成功: {self.config_path}")
            
        except Exception as e:
            logger.error(f"❌ 配置文件加载失败: {e}")
            raise
    
    def _parse_config(self) -> None:
        """解析配置数据"""
        rd_config = self.config_data.get('resource_discovery', {})
        
        # 解析向量配置
        vector_config_data = rd_config.get('vector_config', {})
        self.vector_config = VectorConfig(
            similarity_threshold=vector_config_data.get('similarity_threshold', 0.3),
            max_results=vector_config_data.get('max_results', 10),
            batch_size=vector_config_data.get('batch_size', 100),
            timeout_seconds=vector_config_data.get('timeout_seconds', 30)
        )

        # 解析匹配器配置
        matcher_config_data = rd_config.get('matcher_config', {})
        self.matcher_config = MatcherConfig(
            confidence_weights=matcher_config_data.get('confidence_weights'),
            vector_type_weights=matcher_config_data.get('vector_type_weights'),
            resource_type_weights=matcher_config_data.get('resource_type_weights')
        )
        
        # 解析资源配置
        resources_data = rd_config.get('resources', [])
        self.resources = []
        for resource_data in resources_data:
            resource = ResourceConfig(
                table=resource_data['table'],
                fields=resource_data['fields'],
                tool=resource_data['tool'],
                description=resource_data.get('description', ''),
                enabled=resource_data.get('enabled', True)
            )
            self.resources.append(resource)
        
        # 解析触发器配置
        trigger_config_data = rd_config.get('trigger_config', {})
        self.trigger_config = TriggerConfig(
            trigger_prefix=trigger_config_data.get('trigger_prefix', 'rd_trigger_'),
            notify_channel_prefix=trigger_config_data.get('notify_channel_prefix', 'rd_notify_'),
            enable_realtime=trigger_config_data.get('enable_realtime', True),
            batch_delay_ms=trigger_config_data.get('batch_delay_ms', 1000)
        )
        
        # 解析日志配置
        logging_config_data = rd_config.get('logging', {})
        self.logging_config = LoggingConfig(
            level=logging_config_data.get('level', 'INFO'),
            log_matching_details=logging_config_data.get('log_matching_details', False),
            log_vectorization=logging_config_data.get('log_vectorization', True)
        )
    
    def reload_config(self) -> None:
        """重新加载配置文件"""
        logger.info("🔄 重新加载配置文件...")
        self.load_config()
    
    def get_enabled_resources(self) -> List[ResourceConfig]:
        """获取启用的资源配置"""
        return [resource for resource in self.resources if resource.enabled]
    
    def get_resource_by_table(self, table_name: str) -> Optional[ResourceConfig]:
        """根据表名获取资源配置"""
        for resource in self.resources:
            if resource.table == table_name:
                return resource
        return None
    
    def get_all_tables(self) -> List[str]:
        """获取所有配置的表名"""
        return [resource.table for resource in self.get_enabled_resources()]
    
    def get_all_tools(self) -> List[str]:
        """获取所有配置的工具名"""
        return list(set(resource.tool for resource in self.get_enabled_resources()))
    
    def validate_config(self) -> Dict[str, Any]:
        """验证配置的基本格式"""
        errors = []
        warnings = []
        
        # 验证必要字段
        if not self.resources:
            errors.append("未配置任何资源")
        
        # 验证每个资源配置
        for i, resource in enumerate(self.resources):
            if not resource.table:
                errors.append(f"资源 {i}: 缺少表名")
            if not resource.fields:
                errors.append(f"资源 {i}: 缺少字段列表")
            if not resource.tool:
                errors.append(f"资源 {i}: 缺少工具名")
        
        # 验证向量配置
        if not (0.0 <= self.vector_config.similarity_threshold <= 1.0):
            errors.append("相似度阈值必须在 0.0-1.0 之间")
        
        if self.vector_config.max_results <= 0:
            errors.append("最大结果数必须大于 0")
        
        # 检查重复的表名
        table_names = [resource.table for resource in self.resources]
        duplicates = set([name for name in table_names if table_names.count(name) > 1])
        if duplicates:
            warnings.append(f"发现重复的表名: {list(duplicates)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "resource_count": len(self.resources),
            "enabled_resource_count": len(self.get_enabled_resources())
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "config_path": str(self.config_path),
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
            "environment_variables": {
                "enable_triggers": self.enable_triggers,
                "auto_sync": self.auto_sync,
                "log_level": self.log_level
            },
            "vector_config": {
                "similarity_threshold": self.vector_config.similarity_threshold,
                "max_results": self.vector_config.max_results,
                "batch_size": self.vector_config.batch_size,
                "timeout_seconds": self.vector_config.timeout_seconds
            },
            "matcher_config": {
                "confidence_weights": self.matcher_config.confidence_weights,
                "vector_type_weights": self.matcher_config.vector_type_weights,
                "resource_type_weights": self.matcher_config.resource_type_weights
            },
            "resources": [
                {
                    "table": resource.table,
                    "fields": resource.fields,
                    "tool": resource.tool,
                    "description": resource.description,
                    "enabled": resource.enabled
                }
                for resource in self.resources
            ],
            "trigger_config": {
                "trigger_prefix": self.trigger_config.trigger_prefix,
                "notify_channel_prefix": self.trigger_config.notify_channel_prefix,
                "enable_realtime": self.trigger_config.enable_realtime,
                "batch_delay_ms": self.trigger_config.batch_delay_ms
            },
            "logging_config": {
                "level": self.logging_config.level,
                "log_matching_details": self.logging_config.log_matching_details,
                "log_vectorization": self.logging_config.log_vectorization
            }
        }


# 全局配置实例
_config_instance: Optional[ResourceDiscoveryConfig] = None


def get_resource_discovery_config() -> ResourceDiscoveryConfig:
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ResourceDiscoveryConfig()
    return _config_instance


def reload_resource_discovery_config() -> ResourceDiscoveryConfig:
    """重新加载全局配置实例"""
    global _config_instance
    _config_instance = ResourceDiscoveryConfig()
    return _config_instance
