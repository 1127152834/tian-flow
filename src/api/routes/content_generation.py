"""
内容生成相关 API 路由
"""

import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.schemas.api_requests import (
    GeneratePodcastRequest,
    GeneratePPTRequest,
    GenerateProseRequest,
    EnhancePromptRequest
)
from src.podcast.graph.builder import build_graph as build_podcast_graph
from src.ppt.graph.builder import build_graph as build_ppt_graph
from src.prose.graph.builder import build_graph as build_prose_graph
from src.llms.llm import get_llm_by_type

logger = logging.getLogger(__name__)
router = APIRouter(tags=["内容生成"])

INTERNAL_SERVER_ERROR_DETAIL = "Internal Server Error"


@router.post("/api/podcast/generate")
async def generate_podcast(request: GeneratePodcastRequest):
    """生成播客内容"""
    try:
        report_content = request.content
        print(report_content)
        workflow = build_podcast_graph()
        result = workflow.invoke({"content": report_content})
        return result
        
    except Exception as e:
        logger.exception(f"Error occurred during podcast generation: {str(e)}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)


@router.post("/api/ppt/generate")
async def generate_ppt(request: GeneratePPTRequest):
    """生成PPT内容"""
    try:
        report_content = request.content
        print(report_content)
        workflow = build_ppt_graph()
        result = workflow.invoke({"content": report_content})
        return result
        
    except Exception as e:
        logger.exception(f"Error occurred during ppt generation: {str(e)}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)


@router.post("/api/prose/generate")
async def generate_prose(request: GenerateProseRequest):
    """生成散文内容"""
    try:
        sanitized_prompt = request.prompt.replace("\r\n", "").replace("\n", "")
        logger.info(f"Generating prose for prompt: {sanitized_prompt}")
        workflow = build_prose_graph()
        events = workflow.astream(
            {
                "content": request.prompt,
                "option": request.option,
                "command": request.command,
            },
            stream_mode="messages",
            subgraphs=True,
        )
        
        return StreamingResponse(
            (f"data: {event[0].content}\n\n" async for _, event in events),
            media_type="text/event-stream",
        )
        
    except Exception as e:
        logger.exception(f"Error occurred during prose generation: {str(e)}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)


@router.post("/api/prompt/enhance")
async def enhance_prompt(request: EnhancePromptRequest):
    """增强提示词"""
    try:
        sanitized_prompt = request.prompt.replace("\r\n", "").replace("\n", "")
        logger.info(f"Enhancing prompt: {sanitized_prompt}")

        llm = get_llm_by_type("basic")
        
        # 构建增强提示词的系统消息
        system_message = """你是一个专业的提示词工程师。请帮助用户优化和增强他们的提示词，使其更加清晰、具体和有效。

请按照以下原则优化提示词：
1. 明确目标和期望输出
2. 提供必要的上下文信息
3. 使用清晰的指令和结构
4. 添加相关的约束条件
5. 包含示例（如果有帮助）

请直接返回优化后的提示词，不需要额外的解释。"""

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"请优化以下提示词：\n\n{request.prompt}"}
        ]
        
        response = await llm.ainvoke(messages)
        enhanced_prompt = response.content if hasattr(response, 'content') else str(response)
        
        return {
            "original_prompt": request.prompt,
            "enhanced_prompt": enhanced_prompt
        }
        
    except Exception as e:
        logger.exception(f"Error occurred during prompt enhancement: {str(e)}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)
