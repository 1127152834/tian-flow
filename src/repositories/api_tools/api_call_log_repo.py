# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
API Call Log Repository
API调用日志仓库 - 严格按照ti-flow实现
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func

from src.models.api_tools import APICallLog


class APICallLogRepository:
    """API调用日志仓库"""
    
    def create_log(
        self,
        db_session: Session,
        api_definition_id: int,
        session_id: Optional[str] = None,
        request_data: Optional[Dict] = None,
        response_data: Optional[Dict] = None,
        status_code: Optional[int] = None,
        execution_time_ms: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> APICallLog:
        """创建API调用日志"""
        log = APICallLog(
            api_definition_id=api_definition_id,
            session_id=session_id,
            request_data=request_data,
            response_data=response_data,
            status_code=status_code,
            execution_time_ms=execution_time_ms,
            error_message=error_message,
        )
        
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)
        return log
    
    def get(self, db_session: Session, log_id: int) -> Optional[APICallLog]:
        """根据ID获取调用日志"""
        return db_session.query(APICallLog).filter(APICallLog.id == log_id).first()
    
    def get_by_api_definition(
        self,
        db_session: Session,
        api_definition_id: int,
        limit: int = 100
    ) -> List[APICallLog]:
        """获取指定API的调用日志"""
        return db_session.query(APICallLog).filter(
            APICallLog.api_definition_id == api_definition_id
        ).order_by(desc(APICallLog.created_at)).limit(limit).all()
    
    def get_by_session(
        self,
        db_session: Session,
        session_id: str,
        limit: int = 100
    ) -> List[APICallLog]:
        """获取指定会话的调用日志"""
        return db_session.query(APICallLog).filter(
            APICallLog.session_id == session_id
        ).order_by(desc(APICallLog.created_at)).limit(limit).all()
    
    def paginate(
        self,
        db_session: Session,
        skip: int = 0,
        limit: int = 100,
        api_definition_id: Optional[int] = None,
        session_id: Optional[str] = None,
        status_code: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        has_error: Optional[bool] = None,
    ) -> List[APICallLog]:
        """分页获取调用日志"""
        query = db_session.query(APICallLog)
        
        # 过滤条件
        if api_definition_id:
            query = query.filter(APICallLog.api_definition_id == api_definition_id)
        
        if session_id:
            query = query.filter(APICallLog.session_id == session_id)
        
        if status_code:
            query = query.filter(APICallLog.status_code == status_code)
        
        if start_date:
            query = query.filter(APICallLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(APICallLog.created_at <= end_date)
        
        if has_error is not None:
            if has_error:
                query = query.filter(APICallLog.error_message.isnot(None))
            else:
                query = query.filter(APICallLog.error_message.is_(None))
        
        # 排序和分页
        return query.order_by(desc(APICallLog.created_at)).offset(skip).limit(limit).all()
    
    def count(
        self,
        db_session: Session,
        api_definition_id: Optional[int] = None,
        session_id: Optional[str] = None,
        status_code: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        has_error: Optional[bool] = None,
    ) -> int:
        """获取调用日志总数"""
        query = db_session.query(func.count(APICallLog.id))
        
        # 过滤条件
        if api_definition_id:
            query = query.filter(APICallLog.api_definition_id == api_definition_id)
        
        if session_id:
            query = query.filter(APICallLog.session_id == session_id)
        
        if status_code:
            query = query.filter(APICallLog.status_code == status_code)
        
        if start_date:
            query = query.filter(APICallLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(APICallLog.created_at <= end_date)
        
        if has_error is not None:
            if has_error:
                query = query.filter(APICallLog.error_message.isnot(None))
            else:
                query = query.filter(APICallLog.error_message.is_(None))
        
        return query.scalar()
    
    def get_statistics(
        self,
        db_session: Session,
        api_definition_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """获取API调用统计摘要"""
        # 计算时间范围
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 基础查询
        base_query = db_session.query(APICallLog).filter(
            APICallLog.created_at >= start_date
        )
        
        if api_definition_id:
            base_query = base_query.filter(APICallLog.api_definition_id == api_definition_id)
        
        # 总调用次数
        total_calls = base_query.count()
        
        # 成功调用次数
        success_calls = base_query.filter(
            and_(
                APICallLog.status_code >= 200,
                APICallLog.status_code < 300,
                APICallLog.error_message.is_(None)
            )
        ).count()
        
        # 失败调用次数
        failed_calls = total_calls - success_calls
        
        # 平均响应时间
        avg_response_time = base_query.filter(
            APICallLog.execution_time_ms.isnot(None)
        ).with_entities(func.avg(APICallLog.execution_time_ms)).scalar() or 0
        
        # 成功率
        success_rate = (success_calls / total_calls * 100) if total_calls > 0 else 0
        
        return {
            "total_calls": total_calls,
            "success_calls": success_calls,
            "failed_calls": failed_calls,
            "average_response_time": round(avg_response_time, 2),
            "success_rate": round(success_rate, 2),
            "period_days": days,
            "start_date": start_date,
            "end_date": end_date
        }
    
    def get_daily_statistics(
        self,
        db_session: Session,
        api_definition_id: Optional[int] = None,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """获取每日API调用统计"""
        # 计算时间范围
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days-1)
        
        # 基础查询
        base_query = db_session.query(APICallLog).filter(
            func.date(APICallLog.created_at) >= start_date
        )
        
        if api_definition_id:
            base_query = base_query.filter(APICallLog.api_definition_id == api_definition_id)
        
        # 按日期分组统计
        daily_stats = base_query.with_entities(
            func.date(APICallLog.created_at).label('date'),
            func.count(APICallLog.id).label('total_calls'),
            func.sum(
                func.case(
                    (and_(
                        APICallLog.status_code >= 200,
                        APICallLog.status_code < 300,
                        APICallLog.error_message.is_(None)
                    ), 1),
                    else_=0
                )
            ).label('success_calls'),
            func.avg(APICallLog.execution_time_ms).label('avg_response_time')
        ).group_by(func.date(APICallLog.created_at)).all()
        
        # 转换为字典列表
        result = []
        for stat in daily_stats:
            success_calls = stat.success_calls or 0
            total_calls = stat.total_calls or 0
            success_rate = (success_calls / total_calls * 100) if total_calls > 0 else 0
            
            result.append({
                "date": stat.date.isoformat(),
                "total_calls": total_calls,
                "success_calls": success_calls,
                "failed_calls": total_calls - success_calls,
                "success_rate": round(success_rate, 2),
                "average_response_time": round(stat.avg_response_time or 0, 2)
            })
        
        return result
    
    def get_error_statistics(
        self,
        db_session: Session,
        api_definition_id: Optional[int] = None,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """获取错误统计"""
        # 计算时间范围
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 基础查询
        base_query = db_session.query(APICallLog).filter(
            and_(
                APICallLog.created_at >= start_date,
                APICallLog.error_message.isnot(None)
            )
        )
        
        if api_definition_id:
            base_query = base_query.filter(APICallLog.api_definition_id == api_definition_id)
        
        # 按错误信息分组统计
        error_stats = base_query.with_entities(
            APICallLog.error_message,
            func.count(APICallLog.id).label('count')
        ).group_by(APICallLog.error_message).order_by(desc('count')).limit(10).all()
        
        return [
            {
                "error_message": stat.error_message,
                "count": stat.count
            }
            for stat in error_stats
        ]
    
    def cleanup_old_logs(self, db_session: Session, days: int = 90) -> int:
        """清理旧日志"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted_count = db_session.query(APICallLog).filter(
            APICallLog.created_at < cutoff_date
        ).delete(synchronize_session=False)
        
        db_session.commit()
        return deleted_count
    
    def get_recent_errors(
        self,
        db_session: Session,
        api_definition_id: Optional[int] = None,
        limit: int = 10
    ) -> List[APICallLog]:
        """获取最近的错误日志"""
        query = db_session.query(APICallLog).filter(
            APICallLog.error_message.isnot(None)
        )
        
        if api_definition_id:
            query = query.filter(APICallLog.api_definition_id == api_definition_id)
        
        return query.order_by(desc(APICallLog.created_at)).limit(limit).all()


# 全局仓库实例
api_call_log_repo = APICallLogRepository()
