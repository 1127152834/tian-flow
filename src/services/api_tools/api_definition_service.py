# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
API Definition Service
API定义服务 - 严格按照ti-flow实现
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.models.api_tools import APIDefinition, APIDefinitionCreate, APIDefinitionUpdate
from src.repositories.api_tools import APIDefinitionRepository, APICallLogRepository
from .api_executor import APIExecutor
from .curl_parser import CurlParser


class APIDefinitionService:
    """API定义服务"""
    
    def __init__(self):
        self.api_def_repo = APIDefinitionRepository()
        self.api_log_repo = APICallLogRepository()
        self.api_executor = APIExecutor()
        self.curl_parser = CurlParser()
    
    def create_api_definition(
        self,
        db_session: Session,
        api_def_create: APIDefinitionCreate
    ) -> APIDefinition:
        """创建API定义"""
        # 检查名称是否已存在
        if self.api_def_repo.exists_by_name(db_session, api_def_create.name):
            raise ValueError(f"API名称 '{api_def_create.name}' 已存在")
        
        # 验证认证配置
        is_valid, error_msg = self.api_executor.auth_manager.validate_auth_config(
            api_def_create.auth_config
        )
        if not is_valid:
            raise ValueError(f"认证配置无效: {error_msg}")
        
        return self.api_def_repo.create(db_session, api_def_create)
    
    def get_api_definition(self, db_session: Session, api_id: int) -> Optional[APIDefinition]:
        """获取API定义"""
        return self.api_def_repo.get(db_session, api_id)
    
    def get_api_definitions(
        self,
        db_session: Session,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        enabled: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[APIDefinition]:
        """获取API定义列表"""
        return self.api_def_repo.get_all(
            db_session=db_session,
            skip=skip,
            limit=limit,
            category=category,
            enabled=enabled,
            search=search
        )
    
    def count_api_definitions(
        self,
        db_session: Session,
        category: Optional[str] = None,
        enabled: Optional[bool] = None,
        search: Optional[str] = None
    ) -> int:
        """获取API定义总数"""
        return self.api_def_repo.count(
            db_session=db_session,
            category=category,
            enabled=enabled,
            search=search
        )
    
    def update_api_definition(
        self,
        db_session: Session,
        api_id: int,
        api_def_update: APIDefinitionUpdate
    ) -> Optional[APIDefinition]:
        """更新API定义"""
        # 检查API是否存在
        existing_api = self.api_def_repo.get(db_session, api_id)
        if not existing_api:
            return None
        
        # 检查名称冲突（如果更新了名称）
        if api_def_update.name and api_def_update.name != existing_api.name:
            if self.api_def_repo.exists_by_name(db_session, api_def_update.name, exclude_id=api_id):
                raise ValueError(f"API名称 '{api_def_update.name}' 已存在")
        
        # 验证认证配置（如果更新了认证配置）
        if api_def_update.auth_config:
            is_valid, error_msg = self.api_executor.auth_manager.validate_auth_config(
                api_def_update.auth_config
            )
            if not is_valid:
                raise ValueError(f"认证配置无效: {error_msg}")
        
        return self.api_def_repo.update(db_session, api_id, api_def_update)
    
    def delete_api_definition(self, db_session: Session, api_id: int) -> bool:
        """删除API定义"""
        return self.api_def_repo.delete(db_session, api_id)
    
    def toggle_api_enabled(self, db_session: Session, api_id: int) -> Optional[APIDefinition]:
        """切换API启用状态"""
        return self.api_def_repo.toggle_enabled(db_session, api_id)
    
    async def execute_api(
        self,
        db_session: Session,
        api_id: int,
        parameters: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """执行API调用"""
        # 获取API定义
        api_def = self.api_def_repo.get(db_session, api_id)
        if not api_def:
            raise ValueError(f"API定义 {api_id} 不存在")
        
        if not api_def.enabled:
            raise ValueError(f"API '{api_def.name}' 已禁用")
        
        # 执行API调用
        exec_result = await self.api_executor.execute_api(
            api_def=api_def,
            parameters=parameters,
            session_id=session_id
        )
        
        # 记录调用日志
        try:
            self.api_log_repo.create_log(
                db_session=db_session,
                api_definition_id=exec_result.api_definition_id,
                session_id=exec_result.session_id,
                request_data=exec_result.request_data,
                response_data=exec_result.result.parsed_data,
                status_code=exec_result.result.status_code,
                execution_time_ms=exec_result.execution_time_ms,
                error_message=exec_result.result.error_message
            )
        except Exception as e:
            # 日志记录失败不应该影响API执行结果
            print(f"警告: API调用日志记录失败: {str(e)}")
        
        # 格式化返回结果
        return {
            "success": exec_result.success,
            "api_definition_id": exec_result.api_definition_id,
            "execution_time_ms": exec_result.execution_time_ms,
            "session_id": exec_result.session_id,
            "result": self.api_executor.result_processor.format_result_for_display(exec_result.result)
        }
    
    async def test_api_connection(
        self,
        db_session: Session,
        api_id: int,
        test_parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """测试API连接"""
        # 获取API定义
        api_def = self.api_def_repo.get(db_session, api_id)
        if not api_def:
            raise ValueError(f"API定义 {api_id} 不存在")
        
        # 执行连接测试
        return await self.api_executor.test_api_connection(api_def, test_parameters)
    
    def parse_curl_command(self, curl_command: str) -> Dict[str, Any]:
        """解析curl命令"""
        parse_result = self.curl_parser.parse_curl_command(curl_command)
        
        if not parse_result.success:
            raise ValueError(parse_result.error_message)
        
        return self.curl_parser.generate_api_definition_data(parse_result)
    
    def create_api_from_curl(
        self,
        db_session: Session,
        curl_command: str
    ) -> APIDefinition:
        """从curl命令创建API定义"""
        # 解析curl命令
        api_data = self.parse_curl_command(curl_command)
        
        # 确保名称唯一
        base_name = api_data["name"]
        counter = 1
        while self.api_def_repo.exists_by_name(db_session, api_data["name"]):
            api_data["name"] = f"{base_name} ({counter})"
            counter += 1
        
        # 创建API定义
        api_def_create = APIDefinitionCreate(**api_data)
        return self.create_api_definition(db_session, api_def_create)
    
    def get_api_statistics(self, db_session: Session) -> Dict[str, Any]:
        """获取API统计信息"""
        return self.api_def_repo.get_statistics(db_session)
    
    def get_categories(self, db_session: Session) -> List[str]:
        """获取所有分类"""
        return self.api_def_repo.get_categories(db_session)
    
    def search_apis(
        self,
        db_session: Session,
        query: str,
        limit: int = 10
    ) -> List[APIDefinition]:
        """搜索API定义"""
        return self.api_def_repo.search_apis(db_session, query, limit)
    
    def get_recent_apis(self, db_session: Session, limit: int = 5) -> List[APIDefinition]:
        """获取最近创建的API定义"""
        return self.api_def_repo.get_recent_apis(db_session, limit)
    
    def bulk_update_category(
        self,
        db_session: Session,
        api_ids: List[int],
        new_category: str
    ) -> int:
        """批量更新分类"""
        return self.api_def_repo.bulk_update_category(db_session, api_ids, new_category)
    
    def bulk_toggle_enabled(
        self,
        db_session: Session,
        api_ids: List[int],
        enabled: bool
    ) -> int:
        """批量切换启用状态"""
        return self.api_def_repo.bulk_toggle_enabled(db_session, api_ids, enabled)
    
    def get_parameter_schema(self, db_session: Session, api_id: int) -> Dict[str, Any]:
        """获取API参数模式"""
        api_def = self.api_def_repo.get(db_session, api_id)
        if not api_def:
            raise ValueError(f"API定义 {api_id} 不存在")
        
        return self.api_executor.parameter_mapper.get_parameter_schema(api_def)
    
    def validate_parameters(
        self,
        db_session: Session,
        api_id: int,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证API参数"""
        api_def = self.api_def_repo.get(db_session, api_id)
        if not api_def:
            raise ValueError(f"API定义 {api_id} 不存在")
        
        try:
            # 尝试映射参数（这会触发验证）
            mapped_params = self.api_executor.parameter_mapper.map_parameters(api_def, parameters)
            return {
                "valid": True,
                "mapped_parameters": {
                    "query_params": mapped_params.query_params,
                    "headers": mapped_params.headers,
                    "path_params": mapped_params.path_params,
                    "body_data": mapped_params.body_data,
                    "form_data": mapped_params.form_data
                }
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }




# 全局服务实例
api_definition_service = APIDefinitionService()
