# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Settings configuration for DeerFlow.

Provides configuration management for embedding and rerank models.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from functools import lru_cache

from src.config import load_yaml_config

@dataclass
class EmbeddingModelConfig:
    """Configuration for embedding models"""
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    vector_dimension: int = 1024
    provider: Optional[str] = None

@dataclass
class RerankModelConfig:
    """Configuration for rerank models"""
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    provider: Optional[str] = None

@dataclass
class Settings:
    """Main settings class"""
    base_embedding_model: EmbeddingModelConfig
    base_rerank_model: Optional[RerankModelConfig] = None

def _get_config_file_path() -> str:
    """Get the path to the configuration file."""
    return str((Path(__file__).parent.parent.parent / "conf.yaml").resolve())

def _get_env_config(prefix: str) -> Dict[str, Any]:
    """
    Get configuration from environment variables.
    Environment variables should follow the format: {PREFIX}__{KEY}
    e.g., BASE_EMBEDDING_MODEL__api_key, BASE_RERANK_MODEL__base_url
    """
    env_prefix = f"{prefix}__"
    conf = {}
    for key, value in os.environ.items():
        if key.startswith(env_prefix):
            conf_key = key[len(env_prefix):].lower()
            conf[conf_key] = value
    return conf

def _create_embedding_config(config_dict: Dict[str, Any]) -> EmbeddingModelConfig:
    """Create embedding model configuration from dictionary"""
    return EmbeddingModelConfig(
        model=config_dict.get("model", "BAAI/bge-m3"),
        api_key=config_dict.get("api_key"),
        base_url=config_dict.get("base_url"),
        vector_dimension=config_dict.get("vector_dimension", 1024),
        provider=config_dict.get("provider")
    )

def _create_rerank_config(config_dict: Dict[str, Any]) -> Optional[RerankModelConfig]:
    """Create rerank model configuration from dictionary"""
    if not config_dict or not config_dict.get("model"):
        return None
    
    return RerankModelConfig(
        model=config_dict.get("model"),
        api_key=config_dict.get("api_key"),
        base_url=config_dict.get("base_url"),
        provider=config_dict.get("provider")
    )

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get application settings.
    
    This function loads configuration from YAML file and environment variables,
    with environment variables taking precedence.
    
    Returns:
        Settings object with embedding and rerank model configurations
    """
    try:
        # Load YAML configuration
        yaml_config = load_yaml_config(_get_config_file_path())
        
        # Get embedding model configuration
        embedding_yaml = yaml_config.get("BASE_EMBEDDING_MODEL", {})
        embedding_env = _get_env_config("BASE_EMBEDDING_MODEL")
        embedding_config = {**embedding_yaml, **embedding_env}
        
        # Get rerank model configuration
        rerank_yaml = yaml_config.get("BASE_RERANK_MODEL", {})
        rerank_env = _get_env_config("BASE_RERANK_MODEL")
        rerank_config = {**rerank_yaml, **rerank_env}
        
        # Create settings
        settings = Settings(
            base_embedding_model=_create_embedding_config(embedding_config),
            base_rerank_model=_create_rerank_config(rerank_config)
        )
        
        return settings
        
    except Exception as e:
        # Fallback to default configuration
        print(f"Warning: Failed to load settings, using defaults: {e}")
        return Settings(
            base_embedding_model=EmbeddingModelConfig(
                model="sentence-transformers/all-MiniLM-L6-v2",
                vector_dimension=384
            )
        )

def clear_settings_cache():
    """Clear the settings cache"""
    get_settings.cache_clear()

# Convenience functions for backward compatibility
def get_embedding_config() -> EmbeddingModelConfig:
    """Get embedding model configuration"""
    return get_settings().base_embedding_model

def get_rerank_config() -> Optional[RerankModelConfig]:
    """Get rerank model configuration"""
    return get_settings().base_rerank_model
