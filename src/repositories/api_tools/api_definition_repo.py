# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
API Definition Repository
API定义仓库 - 严格按照ti-flow实现
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func

from src.models.api_tools import APIDefinition, APIDefinitionCreate, APIDefinitionUpdate


class APIDefinitionRepository:
    """API定义仓库"""
    
    def create(self, db_session: Session, api_def_create: APIDefinitionCreate) -> APIDefinition:
        """创建API定义"""
        # 手动序列化 Pydantic 模型字段为字典
        data = api_def_create.model_dump()

        # 序列化嵌套的 Pydantic 模型
        if hasattr(api_def_create.auth_config, 'model_dump'):
            data['auth_config'] = api_def_create.auth_config.model_dump()

        if hasattr(api_def_create.response_config, 'model_dump'):
            data['response_config'] = api_def_create.response_config.model_dump()

        if hasattr(api_def_create.rate_limit, 'model_dump'):
            data['rate_limit'] = api_def_create.rate_limit.model_dump()

        # 序列化参数列表
        if api_def_create.parameters:
            data['parameters'] = [
                param.model_dump() if hasattr(param, 'model_dump') else param
                for param in api_def_create.parameters
            ]

        api_def = APIDefinition(**data)
        db_session.add(api_def)
        db_session.commit()
        db_session.refresh(api_def)
        return api_def
    
    def get(self, db_session: Session, api_id: int) -> Optional[APIDefinition]:
        """根据ID获取API定义"""
        return db_session.query(APIDefinition).filter(APIDefinition.id == api_id).first()
    
    def get_by_name(self, db_session: Session, name: str) -> Optional[APIDefinition]:
        """根据名称获取API定义"""
        return db_session.query(APIDefinition).filter(APIDefinition.name == name).first()
    
    def get_all(
        self, 
        db_session: Session,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        enabled: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[APIDefinition]:
        """获取API定义列表"""
        query = db_session.query(APIDefinition)
        
        # 分类过滤
        if category:
            query = query.filter(APIDefinition.category == category)
        
        # 启用状态过滤
        if enabled is not None:
            query = query.filter(APIDefinition.enabled == enabled)
        
        # 搜索过滤
        if search:
            search_filter = or_(
                APIDefinition.name.ilike(f"%{search}%"),
                APIDefinition.description.ilike(f"%{search}%"),
                APIDefinition.url.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # 排序和分页
        query = query.order_by(desc(APIDefinition.created_at))
        return query.offset(skip).limit(limit).all()
    
    def count(
        self,
        db_session: Session,
        category: Optional[str] = None,
        enabled: Optional[bool] = None,
        search: Optional[str] = None
    ) -> int:
        """获取API定义总数"""
        query = db_session.query(func.count(APIDefinition.id))
        
        # 分类过滤
        if category:
            query = query.filter(APIDefinition.category == category)
        
        # 启用状态过滤
        if enabled is not None:
            query = query.filter(APIDefinition.enabled == enabled)
        
        # 搜索过滤
        if search:
            search_filter = or_(
                APIDefinition.name.ilike(f"%{search}%"),
                APIDefinition.description.ilike(f"%{search}%"),
                APIDefinition.url.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        return query.scalar()
    
    def update(
        self, 
        db_session: Session, 
        api_id: int, 
        api_def_update: APIDefinitionUpdate
    ) -> Optional[APIDefinition]:
        """更新API定义"""
        api_def = self.get(db_session, api_id)
        if not api_def:
            return None
        
        # 更新字段
        update_data = api_def_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(api_def, field, value)
        
        db_session.commit()
        db_session.refresh(api_def)
        return api_def
    
    def delete(self, db_session: Session, api_id: int) -> bool:
        """删除API定义"""
        api_def = self.get(db_session, api_id)
        if not api_def:
            return False
        
        db_session.delete(api_def)
        db_session.commit()
        return True
    
    def toggle_enabled(self, db_session: Session, api_id: int) -> Optional[APIDefinition]:
        """切换API启用状态"""
        api_def = self.get(db_session, api_id)
        if not api_def:
            return None
        
        api_def.enabled = not api_def.enabled
        db_session.commit()
        db_session.refresh(api_def)
        return api_def
    
    def get_by_category(self, db_session: Session, category: str) -> List[APIDefinition]:
        """根据分类获取API定义列表"""
        return db_session.query(APIDefinition).filter(
            APIDefinition.category == category
        ).order_by(APIDefinition.name).all()
    
    def get_enabled_apis(self, db_session: Session) -> List[APIDefinition]:
        """获取所有启用的API定义"""
        return db_session.query(APIDefinition).filter(
            APIDefinition.enabled == True
        ).order_by(APIDefinition.name).all()
    
    def get_categories(self, db_session: Session) -> List[str]:
        """获取所有分类"""
        result = db_session.query(APIDefinition.category).distinct().all()
        return [row[0] for row in result if row[0]]
    
    def exists_by_name(self, db_session: Session, name: str, exclude_id: Optional[int] = None) -> bool:
        """检查名称是否已存在"""
        query = db_session.query(APIDefinition).filter(APIDefinition.name == name)
        
        if exclude_id:
            query = query.filter(APIDefinition.id != exclude_id)
        
        return query.first() is not None
    
    def get_statistics(self, db_session: Session) -> Dict[str, Any]:
        """获取API定义统计信息"""
        total_count = db_session.query(func.count(APIDefinition.id)).scalar()
        enabled_count = db_session.query(func.count(APIDefinition.id)).filter(
            APIDefinition.enabled == True
        ).scalar()
        disabled_count = total_count - enabled_count
        
        # 按分类统计
        category_stats = db_session.query(
            APIDefinition.category,
            func.count(APIDefinition.id).label('count')
        ).group_by(APIDefinition.category).all()
        
        category_distribution = {row[0]: row[1] for row in category_stats}
        
        # 按HTTP方法统计
        method_stats = db_session.query(
            APIDefinition.method,
            func.count(APIDefinition.id).label('count')
        ).group_by(APIDefinition.method).all()
        
        method_distribution = {row[0]: row[1] for row in method_stats}
        
        return {
            "total_apis": total_count,
            "enabled_apis": enabled_count,
            "disabled_apis": disabled_count,
            "category_distribution": category_distribution,
            "method_distribution": method_distribution
        }
    
    def search_apis(
        self,
        db_session: Session,
        query: str,
        limit: int = 10
    ) -> List[APIDefinition]:
        """搜索API定义"""
        search_filter = or_(
            APIDefinition.name.ilike(f"%{query}%"),
            APIDefinition.description.ilike(f"%{query}%"),
            APIDefinition.url.ilike(f"%{query}%"),
            APIDefinition.category.ilike(f"%{query}%")
        )
        
        return db_session.query(APIDefinition).filter(
            and_(APIDefinition.enabled == True, search_filter)
        ).order_by(APIDefinition.name).limit(limit).all()
    
    def get_recent_apis(self, db_session: Session, limit: int = 5) -> List[APIDefinition]:
        """获取最近创建的API定义"""
        return db_session.query(APIDefinition).order_by(
            desc(APIDefinition.created_at)
        ).limit(limit).all()
    
    def bulk_update_category(
        self,
        db_session: Session,
        api_ids: List[int],
        new_category: str
    ) -> int:
        """批量更新分类"""
        updated_count = db_session.query(APIDefinition).filter(
            APIDefinition.id.in_(api_ids)
        ).update(
            {"category": new_category},
            synchronize_session=False
        )
        
        db_session.commit()
        return updated_count
    
    def bulk_toggle_enabled(
        self,
        db_session: Session,
        api_ids: List[int],
        enabled: bool
    ) -> int:
        """批量切换启用状态"""
        updated_count = db_session.query(APIDefinition).filter(
            APIDefinition.id.in_(api_ids)
        ).update(
            {"enabled": enabled},
            synchronize_session=False
        )
        
        db_session.commit()
        return updated_count


# 全局仓库实例
api_definition_repo = APIDefinitionRepository()
