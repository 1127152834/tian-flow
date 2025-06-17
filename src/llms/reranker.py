# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Reranker Model Management

统一管理重排序模型的加载和缓存。
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Tuple
import requests
import json

from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from src.config import load_yaml_config

# Cache for reranker model instances
_reranker_cache: Dict[str, Any] = {}


def _get_env_reranker_conf(model_type: str = "BASE_RERANK") -> Dict[str, Any]:
    """
    Get reranker model configuration from environment variables.
    Environment variables should follow the format: {MODEL_TYPE}_MODEL__{KEY}
    e.g., BASE_RERANK_MODEL__api_key, BASE_RERANK_MODEL__base_url
    """
    prefix = f"{model_type}_MODEL__"
    conf = {}
    for key, value in os.environ.items():
        if key.startswith(prefix):
            conf_key = key[len(prefix) :].lower()
            conf[conf_key] = value
    return conf


class APIReranker:
    """API-based reranker for OpenAI-compatible endpoints"""
    
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        
    def predict(self, query_doc_pairs: List[Tuple[str, str]]) -> List[float]:
        """
        Predict relevance scores for query-document pairs.
        
        Args:
            query_doc_pairs: List of (query, document) tuples
            
        Returns:
            List of relevance scores
        """
        try:
            # Format the request for reranking API
            documents = [doc for _, doc in query_doc_pairs]
            query = query_doc_pairs[0][0] if query_doc_pairs else ""
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "query": query,
                "documents": documents,
                "return_documents": False,
                "top_k": len(documents)
            }
            
            response = requests.post(
                f"{self.base_url}/rerank",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # Extract scores from the response
                if "results" in result:
                    scores = [item.get("relevance_score", 0.0) for item in result["results"]]
                    return scores
                else:
                    # Fallback: return uniform scores
                    return [0.5] * len(query_doc_pairs)
            else:
                # Fallback: return uniform scores
                return [0.5] * len(query_doc_pairs)
                
        except Exception as e:
            # Fallback: return uniform scores
            return [0.5] * len(query_doc_pairs)


def _create_reranker_model(conf: Dict[str, Any]) -> Any:
    """
    Create reranker model instance based on configuration.
    
    Args:
        conf: Model configuration
        
    Returns:
        Reranker model instance
    """
    model_name = conf.get("model", "")
    
    # Check if it's an API-based model
    if conf.get("base_url") and conf.get("api_key"):
        return APIReranker(
            base_url=conf["base_url"],
            api_key=conf["api_key"],
            model=model_name
        )
    
    # Use local HuggingFace model
    elif model_name.startswith("BAAI/bge-reranker") or "reranker" in model_name.lower():
        return HuggingFaceCrossEncoder(
            model_name=model_name,
            model_kwargs={'device': 'cpu'}  # Use GPU if available: 'cuda'
        )
    
    # Default fallback
    else:
        raise ValueError(f"Unsupported reranker model: {model_name}")


def get_reranker_model(model_type: str = "BASE_RERANK") -> Any:
    """
    Get reranker model instance by type. Returns cached instance if available.
    
    Args:
        model_type: Model type (BASE_RERANK, etc.)
        
    Returns:
        Reranker model instance
    """
    cache_key = f"{model_type}_reranker"
    
    if cache_key in _reranker_cache:
        return _reranker_cache[cache_key]

    # Load configuration
    conf = load_yaml_config(
        str((Path(__file__).parent.parent.parent / "conf.yaml").resolve())
    )
    
    # Get model configuration
    model_conf_key = f"{model_type}_MODEL"
    model_conf = conf.get(model_conf_key, {})
    
    if not isinstance(model_conf, dict):
        raise ValueError(f"Invalid reranker model configuration: {model_conf_key}")
    
    # Get configuration from environment variables
    env_conf = _get_env_reranker_conf(model_type)
    
    # Merge configurations, with environment variables taking precedence
    merged_conf = {**model_conf, **env_conf}
    
    if not merged_conf:
        raise ValueError(f"No configuration found for reranker model: {model_type}")
    
    # Create and cache the model
    reranker_model = _create_reranker_model(merged_conf)
    _reranker_cache[cache_key] = reranker_model
    
    return reranker_model


def rerank_documents(
    query: str, 
    documents: List[str], 
    model_type: str = "BASE_RERANK",
    top_k: int = None
) -> List[Tuple[int, float, str]]:
    """
    Rerank documents based on their relevance to the query.
    
    Args:
        query: Search query
        documents: List of documents to rerank
        model_type: Model type to use
        top_k: Number of top documents to return (None for all)
        
    Returns:
        List of tuples (original_index, score, document)
    """
    if not documents:
        return []
    
    reranker = get_reranker_model(model_type)
    
    # Prepare query-document pairs
    query_doc_pairs = [(query, doc) for doc in documents]
    
    # Get relevance scores
    if hasattr(reranker, 'predict'):
        scores = reranker.predict(query_doc_pairs)
    elif hasattr(reranker, 'score'):
        # For some HuggingFace models
        scores = [reranker.score([query, doc]) for doc in documents]
    else:
        # Fallback: return uniform scores
        scores = [0.5] * len(documents)
    
    # Create tuples with original indices
    scored_docs = [
        (i, float(score), doc) 
        for i, (score, doc) in enumerate(zip(scores, documents))
    ]
    
    # Sort by score in descending order
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    
    # Return top_k if specified
    if top_k is not None:
        scored_docs = scored_docs[:top_k]
    
    return scored_docs


def rerank_with_metadata(
    query: str,
    documents_with_metadata: List[Dict[str, Any]],
    text_field: str = "content",
    model_type: str = "BASE_RERANK",
    top_k: int = None
) -> List[Dict[str, Any]]:
    """
    Rerank documents with metadata based on their relevance to the query.
    
    Args:
        query: Search query
        documents_with_metadata: List of documents with metadata
        text_field: Field name containing the document text
        model_type: Model type to use
        top_k: Number of top documents to return (None for all)
        
    Returns:
        List of reranked documents with added rerank_score field
    """
    if not documents_with_metadata:
        return []
    
    # Extract text content
    documents = [doc.get(text_field, "") for doc in documents_with_metadata]
    
    # Rerank documents
    reranked = rerank_documents(query, documents, model_type, top_k)
    
    # Build result with metadata and scores
    result = []
    for original_idx, score, _ in reranked:
        doc_with_score = documents_with_metadata[original_idx].copy()
        doc_with_score["rerank_score"] = score
        result.append(doc_with_score)
    
    return result