"""
Olight 统一路由管理

简单地将所有路由集中在一个地方管理，不改变原有的业务逻辑
"""

from fastapi import APIRouter

# 导入现有的路由
from .text2sql import router as text2sql_router
from .resource_discovery import router as resource_discovery_router
from .api_tools import (
    api_definition_router,
    api_call_log_router,
    curl_parser_router
)

# 导入从 app.py 迁移过来的路由
from .chat import router as chat_router
from .content_generation import router as content_generation_router
from .system import router as system_router
from .database_datasources import router as database_datasources_router

# WebSocket路由直接在主应用中注册，不在这里包含

# 创建主路由器
api_router = APIRouter()

# 注册所有子路由
api_router.include_router(text2sql_router)
api_router.include_router(resource_discovery_router)
api_router.include_router(api_definition_router)
api_router.include_router(api_call_log_router)
api_router.include_router(curl_parser_router)

# 注册从 app.py 迁移过来的路由
api_router.include_router(chat_router)
api_router.include_router(content_generation_router)
api_router.include_router(system_router)
api_router.include_router(database_datasources_router)

# WebSocket路由已在主应用中直接注册

__all__ = ["api_router"]
