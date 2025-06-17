# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
API Call Log Routes
API调用日志路由 - 严格按照ti-flow实现
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends

from src.repositories.api_tools import APICallLogRepository
from src.database import get_db_session

router = APIRouter(prefix="/api/api-call-logs", tags=["API调用日志"])


@router.get("")
def list_api_call_logs(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    api_definition_id: Optional[int] = Query(None, description="按API定义ID过滤"),
    session_id: Optional[str] = Query(None, description="按会话ID过滤"),
    status_code: Optional[int] = Query(None, description="按状态码过滤"),
    has_error: Optional[bool] = Query(None, description="按是否有错误过滤"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db_session=Depends(get_db_session)
):
    """获取API调用日志列表"""
    repo = APICallLogRepository()
    return repo.paginate(
        db_session=db_session,
        skip=skip,
        limit=limit,
        api_definition_id=api_definition_id,
        session_id=session_id,
        status_code=status_code,
        start_date=start_date,
        end_date=end_date,
        has_error=has_error
    )


@router.get("/count")
def count_api_call_logs(
    api_definition_id: Optional[int] = Query(None, description="按API定义ID过滤"),
    session_id: Optional[str] = Query(None, description="按会话ID过滤"),
    status_code: Optional[int] = Query(None, description="按状态码过滤"),
    has_error: Optional[bool] = Query(None, description="按是否有错误过滤"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db_session=Depends(get_db_session)
):
    """获取API调用日志总数"""
    repo = APICallLogRepository()
    return {
        "count": repo.count(
            db_session=db_session,
            api_definition_id=api_definition_id,
            session_id=session_id,
            status_code=status_code,
            start_date=start_date,
            end_date=end_date,
            has_error=has_error
        )
    }


@router.get("/{log_id}")
def get_api_call_log(
    log_id: int,
    db_session=Depends(get_db_session)
):
    """获取API调用日志详情"""
    repo = APICallLogRepository()
    log = repo.get(db_session, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="调用日志未找到")
    return log


@router.get("/by-api/{api_definition_id}")
def get_logs_by_api_definition(
    api_definition_id: int,
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db_session=Depends(get_db_session)
):
    """获取指定API的调用日志"""
    repo = APICallLogRepository()
    logs = repo.get_by_api_definition(db_session, api_definition_id, limit)
    return {"logs": logs}


@router.get("/by-session/{session_id}")
def get_logs_by_session(
    session_id: str,
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db_session=Depends(get_db_session)
):
    """获取指定会话的调用日志"""
    repo = APICallLogRepository()
    logs = repo.get_by_session(db_session, session_id, limit)
    return {"logs": logs}


@router.get("/statistics/summary")
def get_call_statistics(
    api_definition_id: Optional[int] = Query(None, description="按API定义ID过滤"),
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db_session=Depends(get_db_session)
):
    """获取API调用统计摘要"""
    repo = APICallLogRepository()
    return repo.get_statistics(
        db_session=db_session,
        api_definition_id=api_definition_id,
        days=days
    )


@router.get("/statistics/daily")
def get_daily_statistics(
    api_definition_id: Optional[int] = Query(None, description="按API定义ID过滤"),
    days: int = Query(7, ge=1, le=30, description="统计天数"),
    db_session=Depends(get_db_session)
):
    """获取每日API调用统计"""
    repo = APICallLogRepository()
    return {
        "daily_stats": repo.get_daily_statistics(
            db_session=db_session,
            api_definition_id=api_definition_id,
            days=days
        )
    }


@router.get("/statistics/errors")
def get_error_statistics(
    api_definition_id: Optional[int] = Query(None, description="按API定义ID过滤"),
    days: int = Query(7, ge=1, le=30, description="统计天数"),
    db_session=Depends(get_db_session)
):
    """获取错误统计"""
    repo = APICallLogRepository()
    return {
        "error_stats": repo.get_error_statistics(
            db_session=db_session,
            api_definition_id=api_definition_id,
            days=days
        )
    }


@router.get("/recent/errors")
def get_recent_errors(
    api_definition_id: Optional[int] = Query(None, description="按API定义ID过滤"),
    limit: int = Query(10, ge=1, le=50, description="返回记录数"),
    db_session=Depends(get_db_session)
):
    """获取最近的错误日志"""
    repo = APICallLogRepository()
    errors = repo.get_recent_errors(
        db_session=db_session,
        api_definition_id=api_definition_id,
        limit=limit
    )
    return {"recent_errors": errors}


@router.delete("/cleanup")
def cleanup_old_logs(
    days: int = Query(90, ge=30, le=365, description="保留天数"),
    db_session=Depends(get_db_session)
):
    """清理旧日志"""
    repo = APICallLogRepository()
    deleted_count = repo.cleanup_old_logs(db_session, days)
    return {
        "message": f"已清理 {deleted_count} 条旧日志",
        "deleted_count": deleted_count
    }


# 内部API（用于记录调用日志）
@router.post("/internal/create")
def create_api_call_log(
    api_definition_id: int,
    session_id: Optional[str] = None,
    request_data: Optional[dict] = None,
    response_data: Optional[dict] = None,
    status_code: Optional[int] = None,
    execution_time_ms: Optional[int] = None,
    error_message: Optional[str] = None,
    db_session=Depends(get_db_session)
):
    """创建API调用日志（内部接口，供API执行引擎使用）"""
    repo = APICallLogRepository()
    log = repo.create_log(
        db_session=db_session,
        api_definition_id=api_definition_id,
        session_id=session_id,
        request_data=request_data,
        response_data=response_data,
        status_code=status_code,
        execution_time_ms=execution_time_ms,
        error_message=error_message,
    )
    return log
