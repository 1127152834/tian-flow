# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.graph.builder import build_graph_with_memory
from src.config import BRANDING

# 导入统一的路由管理
from src.api.routes import api_router

logger = logging.getLogger(__name__)

INTERNAL_SERVER_ERROR_DETAIL = "Internal Server Error"

app = FastAPI(
    title=f"{BRANDING.display_name} API",
    description=f"API for {BRANDING.name}",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

graph = build_graph_with_memory()
app.include_router(api_router)

# 直接注册WebSocket路由
from src.api.routes.websocket_routes import router as websocket_router
app.include_router(websocket_router, prefix="/api")