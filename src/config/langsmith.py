# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
LangSmith tracing configuration for Olight Manufacturing Intelligence System.

This module handles the initialization and configuration of LangSmith tracing
for monitoring and debugging AI agent workflows.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def setup_langsmith_tracing() -> bool:
    """
    Setup LangSmith tracing based on environment variables.
    
    Returns:
        bool: True if LangSmith tracing is enabled and configured, False otherwise
    """
    try:
        # Check if LangSmith tracing is enabled
        langsmith_tracing = os.getenv("LANGSMITH_TRACING", "false").lower()
        if langsmith_tracing not in ["true", "1", "yes", "on"]:
            logger.info("🔍 LangSmith tracing is disabled")
            return False
        
        # Get LangSmith configuration
        langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        langsmith_project = os.getenv("LANGSMITH_PROJECT")
        langsmith_endpoint = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        
        if not langsmith_api_key:
            logger.warning("⚠️ LANGSMITH_API_KEY not found, tracing disabled")
            return False
        
        if not langsmith_project:
            logger.warning("⚠️ LANGSMITH_PROJECT not found, tracing disabled")
            return False
        
        # Set environment variables for LangSmith
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = langsmith_endpoint
        os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
        os.environ["LANGCHAIN_PROJECT"] = langsmith_project
        
        logger.info(f"✅ LangSmith tracing enabled")
        logger.info(f"   📊 Project: {langsmith_project}")
        logger.info(f"   🌐 Endpoint: {langsmith_endpoint}")
        logger.info(f"   🔑 API Key: {langsmith_api_key[:8]}...{langsmith_api_key[-4:]}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to setup LangSmith tracing: {e}")
        return False


def get_langsmith_config() -> dict:
    """
    Get current LangSmith configuration.
    
    Returns:
        dict: LangSmith configuration details
    """
    return {
        "enabled": os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true",
        "endpoint": os.getenv("LANGCHAIN_ENDPOINT"),
        "project": os.getenv("LANGCHAIN_PROJECT"),
        "api_key_set": bool(os.getenv("LANGCHAIN_API_KEY")),
    }


def create_langsmith_run_name(agent_type: str, user_query: str) -> str:
    """
    Create a descriptive run name for LangSmith tracing.
    
    Args:
        agent_type: Type of agent (coordinator, data_analyst, planner, etc.)
        user_query: User's query or request
        
    Returns:
        str: Formatted run name for LangSmith
    """
    # Truncate query if too long
    max_query_length = 50
    if len(user_query) > max_query_length:
        query_preview = user_query[:max_query_length] + "..."
    else:
        query_preview = user_query
    
    return f"[{agent_type.upper()}] {query_preview}"


def add_langsmith_metadata(metadata: dict) -> dict:
    """
    Add standard metadata for LangSmith runs.
    
    Args:
        metadata: Existing metadata dictionary
        
    Returns:
        dict: Enhanced metadata with LangSmith-specific fields
    """
    enhanced_metadata = metadata.copy()
    
    # Add system information
    enhanced_metadata.update({
        "system": "olight-manufacturing-intelligence",
        "version": "1.0.0",
        "environment": os.getenv("PYTHON_ENV", "development"),
        "langsmith_enabled": get_langsmith_config()["enabled"],
    })
    
    return enhanced_metadata


# Initialize LangSmith on module import
_langsmith_initialized = setup_langsmith_tracing()


def is_langsmith_enabled() -> bool:
    """
    Check if LangSmith tracing is currently enabled.
    
    Returns:
        bool: True if LangSmith is enabled and configured
    """
    return _langsmith_initialized and get_langsmith_config()["enabled"]


def log_langsmith_status():
    """Log current LangSmith status for debugging."""
    config = get_langsmith_config()
    
    if config["enabled"]:
        logger.info("🔍 LangSmith Status: ENABLED")
        logger.info(f"   📊 Project: {config['project']}")
        logger.info(f"   🌐 Endpoint: {config['endpoint']}")
        logger.info(f"   🔑 API Key: {'SET' if config['api_key_set'] else 'NOT SET'}")
    else:
        logger.info("🔍 LangSmith Status: DISABLED")
        
    logger.info(f"   🏭 System: Olight Manufacturing Intelligence")
    logger.info(f"   🌍 Environment: {os.getenv('PYTHON_ENV', 'development')}")
