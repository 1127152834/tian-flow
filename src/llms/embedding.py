# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
嵌入模型管理模块

提供统一的嵌入模型接口，支持多种嵌入模型提供商
"""

import logging
from typing import List, Dict, Any, Optional
from functools import lru_cache

from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from src.config.settings import get_settings

logger = logging.getLogger(__name__)

# 嵌入模型缓存
_embedding_models: Dict[str, Any] = {}


def get_embedding_model(model_type: str = "BASE_EMBEDDING") -> Any:
    """
    获取嵌入模型实例
    
    Args:
        model_type: 模型类型，支持 BASE_EMBEDDING, BASE_RERANK 等
        
    Returns:
        嵌入模型实例
    """
    global _embedding_models
    
    if model_type in _embedding_models:
        return _embedding_models[model_type]
    
    try:
        settings = get_settings()
        
        # 根据模型类型获取配置
        if model_type == "BASE_EMBEDDING":
            config = settings.base_embedding_model
        elif model_type == "BASE_RERANK":
            config = settings.base_rerank_model
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        # 创建嵌入模型
        model = _create_embedding_model(config)
        
        # 缓存模型
        _embedding_models[model_type] = model
        
        logger.info(f"Successfully loaded embedding model: {config.model}")
        return model
        
    except Exception as e:
        logger.error(f"Failed to load embedding model {model_type}: {e}")
        # 返回默认模型作为回退
        return _get_fallback_model()


def _create_embedding_model(config) -> Any:
    """
    根据配置创建嵌入模型
    
    Args:
        config: 模型配置
        
    Returns:
        嵌入模型实例
    """
    try:
        model_name = config.model
        base_url = config.base_url
        api_key = config.api_key
        
        logger.info(f"Creating embedding model: {model_name}")
        logger.info(f"Base URL: {base_url}")
        logger.info(f"API Key present: {bool(api_key)}")
        
        # 判断是否为远程 API 服务
        is_remote_api = (
            api_key and base_url and (
                'openai.com' in base_url.lower() or
                'api.openai.com' in base_url or
                'siliconflow.cn' in base_url.lower() or
                'api.' in base_url.lower() or
                '/v1' in base_url or
                base_url.startswith(('http://', 'https://'))
            )
        )
        
        if is_remote_api:
            logger.info(f"Using remote API service: {base_url}")
            return OpenAIEmbeddings(
                model=model_name,
                openai_api_key=api_key,
                openai_api_base=base_url
            )
        
        # 本地 HuggingFace 模型
        else:
            logger.info(f"Using local HuggingFace model: {model_name}")
            return HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
    except Exception as e:
        logger.error(f"Failed to create embedding model: {e}")
        return _get_fallback_model()


def _get_fallback_model() -> Any:
    """
    获取回退嵌入模型
    
    Returns:
        默认的嵌入模型实例
    """
    logger.info("Using fallback embedding model")
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )


def embed_query(text: str, model_type: str = "BASE_EMBEDDING") -> List[float]:
    """
    为单个查询文本生成嵌入向量
    
    Args:
        text: 查询文本
        model_type: 模型类型
        
    Returns:
        嵌入向量
    """
    try:
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * get_embedding_dimension(model_type)
        
        model = get_embedding_model(model_type)
        
        # 预处理文本
        cleaned_text = _preprocess_text(text.strip())
        
        # 生成嵌入
        embedding = model.embed_query(cleaned_text)
        
        logger.debug(f"Generated embedding for query (length={len(text)})")
        return embedding
        
    except Exception as e:
        logger.error(f"Failed to embed query: {e}")
        # 返回零向量作为回退
        return [0.0] * get_embedding_dimension(model_type)


def embed_texts(texts: List[str], model_type: str = "BASE_EMBEDDING") -> List[List[float]]:
    """
    为多个文本生成嵌入向量
    
    Args:
        texts: 文本列表
        model_type: 模型类型
        
    Returns:
        嵌入向量列表
    """
    try:
        if not texts:
            return []
        
        model = get_embedding_model(model_type)
        
        # 预处理文本
        cleaned_texts = [_preprocess_text(text) for text in texts if text and text.strip()]
        
        if not cleaned_texts:
            logger.warning("No valid texts provided for embedding")
            return []
        
        # 批量生成嵌入
        embeddings = model.embed_documents(cleaned_texts)
        
        logger.debug(f"Generated embeddings for {len(texts)} texts")
        return embeddings
        
    except Exception as e:
        logger.error(f"Failed to embed texts: {e}")
        # 返回零向量作为回退
        dimension = get_embedding_dimension(model_type)
        return [[0.0] * dimension for _ in texts]


def get_embedding_dimension(model_type: str = "BASE_EMBEDDING") -> int:
    """
    获取嵌入向量的维度
    
    Args:
        model_type: 模型类型
        
    Returns:
        向量维度
    """
    try:
        settings = get_settings()
        
        if model_type == "BASE_EMBEDDING":
            return settings.base_embedding_model.vector_dimension
        elif model_type == "BASE_RERANK":
            # 重排序模型通常返回分数，不是向量
            return 1
        else:
            logger.warning(f"Unknown model type: {model_type}, using default dimension")
            return 1024
            
    except Exception as e:
        logger.error(f"Failed to get embedding dimension: {e}")
        return 1024


def _preprocess_text(text: str) -> str:
    """
    预处理文本
    
    Args:
        text: 原始文本
        
    Returns:
        预处理后的文本
    """
    if not text:
        return ""
    
    # 基础清理
    cleaned = text.strip()
    
    # 移除多余的空白字符
    import re
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # 限制长度（避免超过模型的最大输入长度）
    max_length = 8000  # 大多数模型的安全长度
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
        logger.warning(f"Text truncated to {max_length} characters")
    
    return cleaned


@lru_cache(maxsize=128)
def get_cached_embedding(text: str, model_type: str = "BASE_EMBEDDING") -> tuple:
    """
    获取缓存的嵌入向量（用于频繁查询的文本）
    
    Args:
        text: 文本
        model_type: 模型类型
        
    Returns:
        嵌入向量的元组（用于缓存）
    """
    embedding = embed_query(text, model_type)
    return tuple(embedding)


def clear_embedding_cache():
    """清除嵌入向量缓存"""
    global _embedding_models
    _embedding_models.clear()
    get_cached_embedding.cache_clear()
    logger.info("Embedding cache cleared")
