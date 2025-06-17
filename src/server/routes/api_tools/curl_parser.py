# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Curl Parser Routes
curl解析路由 - 严格按照ti-flow实现
"""

from fastapi import APIRouter, HTTPException, Depends

from src.models.api_tools import (
    APIDefinitionResponse,
    CurlParseRequest, CurlImportRequest
)
from src.services.api_tools import APIDefinitionService
from src.database import get_db_session

router = APIRouter(prefix="/api/admin/curl-parse", tags=["curl解析"])


@router.post("/parse")
def parse_curl_command(
    request: CurlParseRequest
):
    """解析curl命令"""
    service = APIDefinitionService()

    if not request.curl_command.strip():
        raise HTTPException(status_code=400, detail="curl命令不能为空")

    try:
        api_data = service.parse_curl_command(request.curl_command)
        return {
            "success": True,
            "api_definition": api_data,
            "message": "curl命令解析成功"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"curl解析失败: {str(e)}")


@router.post("/import", response_model=APIDefinitionResponse)
def import_from_curl(
    request: CurlImportRequest,
    db_session=Depends(get_db_session)
):
    """从curl命令导入API定义"""
    from .api_definition import convert_api_definition_to_response

    service = APIDefinitionService()

    if not request.curl_command.strip():
        raise HTTPException(status_code=400, detail="curl命令不能为空")

    try:
        api_def = service.create_api_from_curl(db_session, request.curl_command)
        return convert_api_definition_to_response(api_def)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"curl导入失败: {str(e)}")


@router.post("/validate")
def validate_curl_command(
    request: CurlParseRequest
):
    """验证curl命令格式"""
    if not request.curl_command.strip():
        raise HTTPException(status_code=400, detail="curl命令不能为空")
    
    try:
        from src.services.api_tools import CurlParser
        parser = CurlParser()
        parse_result = parser.parse_curl_command(request.curl_command)
        
        return {
            "valid": parse_result.success,
            "error_message": parse_result.error_message if not parse_result.success else None,
            "extracted_info": {
                "method": parse_result.method.name if parse_result.method else None,
                "url": parse_result.url,
                "headers_count": len(parse_result.headers) if parse_result.headers else 0,
                "parameters_count": len(parse_result.parameters) if parse_result.parameters else 0,
                "has_auth": parse_result.auth_config is not None,
                "has_body": parse_result.body_data is not None
            } if parse_result.success else None
        }
    except Exception as e:
        return {
            "valid": False,
            "error_message": f"curl验证失败: {str(e)}"
        }
