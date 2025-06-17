"""
API 请求模型

避免循环导入，将路由需要的请求模型集中在这里
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from src.rag.retriever import Resource


class ChatMessage(BaseModel):
    role: str = Field(..., description="The role of the message sender")
    content: str | List[Dict[str, Any]] = Field(
        ...,
        description="The content of the message, either a string or a list of content items",
    )


class ChatRequest(BaseModel):
    messages: Optional[List[ChatMessage]] = Field(
        [], description="History of messages between the user and the assistant"
    )
    resources: Optional[List[Resource]] = Field(
        [], description="Resources to be used for the research"
    )
    thread_id: Optional[str] = Field(
        "__default__", description="The thread ID for the conversation"
    )
    max_plan_iterations: Optional[int] = Field(
        3, description="Maximum number of plan iterations"
    )
    max_step_iterations: Optional[int] = Field(
        25, description="Maximum number of step iterations"
    )
    max_search_results: Optional[int] = Field(
        10, description="Maximum number of search results"
    )
    auto_accepted_plan: Optional[bool] = Field(
        False, description="Whether to auto accept the plan"
    )
    interrupt_feedback: Optional[str] = Field(
        None, description="Interrupt feedback from the user on the plan"
    )
    mcp_settings: Optional[Dict[str, Any]] = Field(
        {}, description="MCP settings for the conversation"
    )
    enable_background_investigation: Optional[bool] = Field(
        False, description="Whether to enable background investigation"
    )
    report_style: Optional[str] = Field(
        "default", description="The style of the report"
    )
    enable_deep_thinking: Optional[bool] = Field(
        False, description="Whether to enable deep thinking"
    )


# 内容生成相关请求模型
class GeneratePodcastRequest(BaseModel):
    content: str = Field(..., description="The content of the podcast")


class GeneratePPTRequest(BaseModel):
    content: str = Field(..., description="The content of the ppt")


class GenerateProseRequest(BaseModel):
    prompt: str = Field(..., description="The content of the prose")
    option: str = Field(..., description="The option of the prose writer")
    command: Optional[str] = Field(
        "", description="The user custom command of the prose writer"
    )


class EnhancePromptRequest(BaseModel):
    prompt: str = Field(..., description="The original prompt to enhance")
    context: Optional[str] = Field(
        "", description="Additional context about the intended use"
    )
    report_style: Optional[str] = Field(
        "default", description="The style of the enhanced prompt"
    )


# TTS 请求模型
class TTSRequest(BaseModel):
    text: str = Field(..., description="The text to convert to speech")
    voice_type: Optional[str] = Field(
        "BV700_V2_streaming", description="The voice type to use"
    )
    encoding: Optional[str] = Field("mp3", description="The audio encoding format")
    speed_ratio: Optional[float] = Field(1.0, description="The speed ratio")
    volume_ratio: Optional[float] = Field(1.0, description="The volume ratio")
    pitch_ratio: Optional[float] = Field(1.0, description="The pitch ratio")
    use_frontend: Optional[int] = Field(
        1, description="Whether to use frontend processing"
    )
    frontend_type: Optional[str] = Field("unitTson", description="Frontend type")


# MCP 请求模型
class MCPServerMetadataRequest(BaseModel):
    server_name: str = Field(..., description="The name of the MCP server")
    timeout: Optional[int] = Field(None, description="Optional timeout in seconds")


class MCPServerMetadataResponse(BaseModel):
    server_name: str = Field(..., description="The name of the MCP server")
    server_info: Dict[str, Any] = Field(default_factory=dict, description="Server information")
    tools: List[Dict[str, Any]] = Field(default_factory=list, description="Available tools")
    resources: List[Dict[str, Any]] = Field(default_factory=list, description="Available resources")
    status: str = Field(..., description="Connection status")
    error: Optional[str] = Field(None, description="Error message if any")


# RAG 请求模型
class RAGConfigResponse(BaseModel):
    provider: str | None = Field(
        None, description="The provider of the RAG, default is ragflow"
    )


class RAGResourceRequest(BaseModel):
    query: str | None = Field(
        None, description="The query of the resource need to be searched"
    )


class RAGResourcesResponse(BaseModel):
    resources: List[Resource] = Field(..., description="The resources of the RAG")


# 配置响应模型
class ConfigResponse(BaseModel):
    rag: RAGConfigResponse = Field(..., description="The config of the RAG")
    models: Dict[str, List[str]] = Field(..., description="The configured models")
