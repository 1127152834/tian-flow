"""
聊天相关 API 路由
"""

import json
import logging
from uuid import uuid4
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.schemas.api_requests import ChatRequest
from src.graph.builder import build_graph_with_memory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["聊天"])

# 构建工作流图
graph = build_graph_with_memory()


async def _astream_workflow_generator(
    messages,
    thread_id: str,
    resources,
    max_plan_iterations: int,
    max_step_iterations: int,
    max_search_results: int,
    auto_accepted_plan: bool,
    interrupt_feedback: Optional[str],
    mcp_settings,
    enable_background_investigation: bool,
    report_style: str,
    enable_deep_thinking: bool,
) -> AsyncGenerator[str, None]:
    """流式生成工作流响应"""
    try:
        from langchain_core.messages import AIMessageChunk, ToolMessage, BaseMessage
        from langgraph.types import Command
        from typing import cast

        input_ = {
            "messages": messages,
            "plan_iterations": 0,
            "final_report": "",
            "current_plan": None,
            "observations": [],
            "auto_accepted_plan": auto_accepted_plan,
            "enable_background_investigation": enable_background_investigation,
            "research_topic": messages[-1]["content"] if messages else "",
        }

        if not auto_accepted_plan and interrupt_feedback:
            resume_msg = f"[{interrupt_feedback}]"
            # add the last message to the resume message
            if messages:
                resume_msg += f" {messages[-1]['content']}"
            input_ = Command(resume=resume_msg)

        # 构建用户设置字典
        user_settings = {
            "enableBackgroundInvestigation": enable_background_investigation,
            "enableDeepThinking": enable_deep_thinking,
            "reportStyle": report_style,
            "maxPlanIterations": max_plan_iterations,
            "maxStepNum": max_step_iterations,
            "maxSearchResults": max_search_results,
        }

        async for agent, _, event_data in graph.astream(
            input_,
            config={
                "configurable": {
                    "thread_id": thread_id,
                    "resources": resources,
                    "max_plan_iterations": max_plan_iterations,
                    "max_step_num": max_step_iterations,
                    "max_search_results": max_search_results,
                    "mcp_settings": mcp_settings,
                    "report_style": report_style,
                    "enable_deep_thinking": enable_deep_thinking,
                    "user_settings": user_settings,
                }
            },
            stream_mode=["messages", "updates"],
            subgraphs=True,
        ):
            if isinstance(event_data, dict):
                if "__interrupt__" in event_data:
                    yield _format_sse_event(
                        "interrupt",
                        {
                            "thread_id": thread_id,
                            "id": event_data["__interrupt__"][0].ns[0],
                            "role": "assistant",
                            "content": event_data["__interrupt__"][0].value,
                            "finish_reason": "interrupt",
                            "options": [
                                {"text": "Edit plan", "value": "edit_plan"},
                                {"text": "Start research", "value": "accepted"},
                            ],
                        },
                    )
                continue

            message_chunk, message_metadata = cast(
                tuple[BaseMessage, dict[str, any]], event_data
            )
            event_stream_message: dict[str, any] = {
                "thread_id": thread_id,
                "agent": agent[0].split(":")[0],
                "id": message_chunk.id,
                "role": "assistant",
                "content": message_chunk.content,
            }
            if message_chunk.additional_kwargs.get("reasoning_content"):
                event_stream_message["reasoning_content"] = message_chunk.additional_kwargs[
                    "reasoning_content"
                ]
            if message_chunk.response_metadata.get("finish_reason"):
                event_stream_message["finish_reason"] = message_chunk.response_metadata.get(
                    "finish_reason"
                )
            if isinstance(message_chunk, ToolMessage):
                # Tool Message - Return the result of the tool call
                event_stream_message["tool_call_id"] = message_chunk.tool_call_id
                yield _format_sse_event("tool_call_result", event_stream_message)
            elif isinstance(message_chunk, AIMessageChunk):
                # AI Message - Raw message tokens
                if message_chunk.tool_calls:
                    # AI Message - Tool Call
                    event_stream_message["tool_calls"] = message_chunk.tool_calls
                    event_stream_message["tool_call_chunks"] = (
                        message_chunk.tool_call_chunks
                    )
                    yield _format_sse_event("tool_calls", event_stream_message)
                elif message_chunk.tool_call_chunks:
                    # AI Message - Tool Call Chunks
                    event_stream_message["tool_call_chunks"] = (
                        message_chunk.tool_call_chunks
                    )
                    yield _format_sse_event("tool_call_chunks", event_stream_message)
                else:
                    # AI Message - Raw message tokens
                    yield _format_sse_event("message_chunk", event_stream_message)

    except Exception as e:
        logger.exception(f"Error in workflow stream: {str(e)}")
        yield _format_sse_event("error", {"error": str(e)})


def _format_sse_event(event_type: str, data: dict) -> str:
    """格式化 SSE 事件"""
    if data.get("content") == "":
        data.pop("content")
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """聊天流式接口"""
    thread_id = request.thread_id
    if thread_id == "__default__":
        thread_id = str(uuid4())
        
    return StreamingResponse(
        _astream_workflow_generator(
            request.model_dump()["messages"],
            thread_id,
            request.resources,
            request.max_plan_iterations,
            request.max_step_iterations,
            request.max_search_results,
            request.auto_accepted_plan,
            request.interrupt_feedback,
            request.mcp_settings,
            request.enable_background_investigation,
            request.report_style,
            request.enable_deep_thinking,
        ),
        media_type="text/event-stream",
    )
