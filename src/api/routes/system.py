"""
系统配置相关 API 路由
"""

import os
import logging
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query

from src.schemas.api_requests import (
    ConfigResponse, RAGConfigResponse, RAGResourcesResponse, RAGResourceRequest,
    TTSRequest, MCPServerMetadataRequest, MCPServerMetadataResponse
)
from src.llms.llm import get_configured_llm_models
from src.config.tools import SELECTED_RAG_PROVIDER
from src.rag.builder import build_retriever
from src.tools import VolcengineTTS
from src.utils.mcp_utils import load_mcp_tools

logger = logging.getLogger(__name__)
router = APIRouter(tags=["系统配置"])

INTERNAL_SERVER_ERROR_DETAIL = "Internal Server Error"


@router.get("/api/config", response_model=ConfigResponse)
async def config():
    """Get the config of the server."""
    return ConfigResponse(
        rag=RAGConfigResponse(provider=SELECTED_RAG_PROVIDER),
        models=get_configured_llm_models(),
    )


@router.get("/api/rag/config", response_model=RAGConfigResponse)
async def rag_config():
    """Get the config of the RAG."""
    return RAGConfigResponse(provider=SELECTED_RAG_PROVIDER)


@router.get("/api/rag/resources", response_model=RAGResourcesResponse)
async def rag_resources(request: Annotated[RAGResourceRequest, Query()]):
    """Get the resources of the RAG."""
    retriever = build_retriever()
    if retriever:
        return RAGResourcesResponse(resources=retriever.list_resources(request.query))
    return RAGResourcesResponse(resources=[])


@router.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using volcengine TTS API."""
    try:
        app_id = os.getenv("VOLCENGINE_TTS_APPID", "")
        if not app_id:
            raise HTTPException(
                status_code=400, 
                detail="VOLCENGINE_TTS_APPID environment variable is not set"
            )

        access_token = os.getenv("VOLCENGINE_TTS_ACCESS_TOKEN", "")
        if not access_token:
            raise HTTPException(
                status_code=400, 
                detail="VOLCENGINE_TTS_ACCESS_TOKEN environment variable is not set"
            )

        cluster_id = os.getenv("VOLCENGINE_TTS_CLUSTER_ID", "")
        if not cluster_id:
            raise HTTPException(
                status_code=400, 
                detail="VOLCENGINE_TTS_CLUSTER_ID environment variable is not set"
            )

        voice_type = os.getenv("VOLCENGINE_TTS_VOICE_TYPE", "BV700_streaming")
        encoding = os.getenv("VOLCENGINE_TTS_ENCODING", "mp3")

        # Initialize TTS tool
        tts_tool = VolcengineTTS(
            app_id=app_id,
            access_token=access_token,
            cluster_id=cluster_id,
            voice_type=voice_type,
            encoding=encoding
        )

        # Convert text to speech
        result = await tts_tool.ainvoke({
            "text": request.text,
            "voice_type": request.voice_type or voice_type,
            "encoding": request.encoding or encoding,
            "speed_ratio": request.speed_ratio or 1.0,
            "volume_ratio": request.volume_ratio or 1.0,
            "pitch_ratio": request.pitch_ratio or 1.0
        })

        return {
            "success": True,
            "audio_data": result.get("audio_data"),
            "format": result.get("format", encoding),
            "duration": result.get("duration"),
            "message": "Text converted to speech successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in TTS endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)


@router.post("/api/mcp/server/metadata", response_model=MCPServerMetadataResponse)
async def mcp_server_metadata(request: MCPServerMetadataRequest):
    """Get information about an MCP server."""
    try:
        # Set default timeout with a longer value for this endpoint
        timeout = 300  # Default to 300 seconds for this endpoint
        
        if request.timeout and request.timeout > 0:
            timeout = request.timeout

        logger.info(f"Getting MCP server metadata for: {request.server_name} with timeout: {timeout}s")
        
        try:
            mcp_tools = load_mcp_tools()
            if request.server_name not in mcp_tools:
                raise HTTPException(
                    status_code=404,
                    detail=f"MCP server '{request.server_name}' not found or not configured"
                )

            # Get server information from loaded tools
            server_tools = mcp_tools[request.server_name]

            return MCPServerMetadataResponse(
                server_name=request.server_name,
                server_info={"status": "connected", "tools_count": len(server_tools)},
                tools=[{"name": tool.name, "description": tool.description} for tool in server_tools],
                resources=[],
                status="connected"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error connecting to MCP server '{request.server_name}': {str(e)}")
            return MCPServerMetadataResponse(
                server_name=request.server_name,
                server_info={},
                tools=[],
                resources=[],
                status="error",
                error=str(e)
            )
            
    except HTTPException:
        raise
    except Exception as e:
        if "timeout" in str(e).lower():
            logger.warning(f"MCP server metadata request timed out: {str(e)}")
            raise HTTPException(status_code=408, detail="Request timeout")
        else:
            logger.exception(f"Error in MCP server metadata endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)
