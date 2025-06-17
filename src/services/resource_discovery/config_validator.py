# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
资源发现配置验证器

验证配置中的数据库、表、字段和工具的存在性和有效性
"""

import logging
import importlib
import inspect
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy import text, inspect as sqlalchemy_inspect
from sqlalchemy.orm import Session

from src.config.resource_discovery import ResourceDiscoveryConfig, ResourceConfig
from src.database import get_db_session

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """配置验证错误"""
    pass


class ConfigValidator:
    """配置验证器"""
    
    def __init__(self, config: ResourceDiscoveryConfig):
        self.config = config
        self.validation_results: Dict[str, Any] = {}
    
    async def validate_all(self) -> Dict[str, Any]:
        """验证所有配置项"""
        logger.info("🔍 开始验证资源发现配置...")
        
        results = {
            "overall_valid": True,
            "validation_time": None,
            "database_validation": {},
            "tool_validation": {},
            "permission_validation": {},
            "summary": {
                "total_resources": len(self.config.resources),
                "valid_resources": 0,
                "invalid_resources": 0,
                "warnings": []
            }
        }
        
        try:
            # 1. 验证基础配置格式
            basic_validation = self.config.validate_config()
            if not basic_validation["valid"]:
                results["overall_valid"] = False
                results["basic_validation"] = basic_validation
                return results
            
            # 2. 验证数据库相关
            db_results = await self._validate_database_resources()
            results["database_validation"] = db_results
            
            # 3. 验证工具相关
            tool_results = await self._validate_tools()
            results["tool_validation"] = tool_results
            
            # 4. 验证权限
            permission_results = await self._validate_permissions()
            results["permission_validation"] = permission_results
            
            # 5. 汇总结果
            valid_count = 0
            for resource in self.config.get_enabled_resources():
                table_name = resource.table
                if (db_results.get(table_name, {}).get("valid", False) and
                    tool_results.get(resource.tool, {}).get("valid", False)):
                    valid_count += 1
            
            results["summary"]["valid_resources"] = valid_count
            results["summary"]["invalid_resources"] = len(self.config.get_enabled_resources()) - valid_count
            
            # 整体验证结果
            results["overall_valid"] = (
                results["summary"]["invalid_resources"] == 0 and
                permission_results.get("valid", False)
            )
            
            logger.info(f"✅ 配置验证完成: {valid_count}/{len(self.config.get_enabled_resources())} 个资源有效")
            
        except Exception as e:
            logger.error(f"❌ 配置验证失败: {e}")
            results["overall_valid"] = False
            results["error"] = str(e)
        
        return results
    
    async def _validate_database_resources(self) -> Dict[str, Any]:
        """验证数据库资源"""
        logger.info("🔍 验证数据库资源...")
        
        results = {}
        session = next(get_db_session())
        
        try:
            # 获取数据库检查器
            inspector = sqlalchemy_inspect(session.bind)
            
            for resource in self.config.get_enabled_resources():
                table_name = resource.table
                logger.info(f"验证表: {table_name}")
                
                table_result = {
                    "valid": True,
                    "exists": False,
                    "schema_exists": False,
                    "fields_validation": {},
                    "errors": [],
                    "warnings": []
                }
                
                try:
                    # 解析表名（可能包含schema）
                    if '.' in table_name:
                        schema_name, table_name_only = table_name.split('.', 1)
                    else:
                        schema_name = 'public'
                        table_name_only = table_name
                    
                    # 验证schema是否存在
                    schemas = inspector.get_schema_names()
                    if schema_name not in schemas:
                        table_result["valid"] = False
                        table_result["errors"].append(f"Schema '{schema_name}' 不存在")
                    else:
                        table_result["schema_exists"] = True
                    
                    # 验证表是否存在
                    tables = inspector.get_table_names(schema=schema_name)
                    if table_name_only not in tables:
                        table_result["valid"] = False
                        table_result["errors"].append(f"表 '{table_name}' 不存在")
                    else:
                        table_result["exists"] = True
                        
                        # 验证字段是否存在
                        columns = inspector.get_columns(table_name_only, schema=schema_name)
                        column_names = [col['name'] for col in columns]
                        
                        for field in resource.fields:
                            if field in column_names:
                                table_result["fields_validation"][field] = {
                                    "exists": True,
                                    "type": next((col['type'] for col in columns if col['name'] == field), None)
                                }
                            else:
                                table_result["valid"] = False
                                table_result["fields_validation"][field] = {"exists": False}
                                table_result["errors"].append(f"字段 '{field}' 不存在")
                
                except Exception as e:
                    table_result["valid"] = False
                    table_result["errors"].append(f"验证失败: {str(e)}")
                
                results[resource.table] = table_result
        
        finally:
            session.close()
        
        return results
    
    async def _validate_tools(self) -> Dict[str, Any]:
        """验证工具是否存在"""
        logger.info("🔍 验证工具...")
        
        results = {}
        tool_names = self.config.get_all_tools()
        
        for tool_name in tool_names:
            tool_result = {
                "valid": False,
                "exists": False,
                "callable": False,
                "module_path": None,
                "function_signature": None,
                "errors": []
            }
            
            try:
                # 尝试在tools模块中查找工具
                tool_found = False
                
                # 检查 src.tools 模块
                try:
                    tools_module = importlib.import_module('src.tools')
                    if hasattr(tools_module, tool_name):
                        tool_func = getattr(tools_module, tool_name)
                        tool_result["exists"] = True
                        tool_result["callable"] = callable(tool_func)
                        tool_result["module_path"] = "src.tools"
                        if callable(tool_func):
                            tool_result["function_signature"] = str(inspect.signature(tool_func))
                        tool_found = True
                except ImportError:
                    pass
                
                # 检查其他可能的工具位置
                if not tool_found:
                    possible_modules = [
                        'src.tools.api_tools',
                        'src.tools.database_tools',
                        'src.tools.text2sql_tools',
                        'src.services.api_tools',
                        'src.api.routes'
                    ]
                    
                    for module_name in possible_modules:
                        try:
                            module = importlib.import_module(module_name)
                            if hasattr(module, tool_name):
                                tool_func = getattr(module, tool_name)
                                tool_result["exists"] = True
                                tool_result["callable"] = callable(tool_func)
                                tool_result["module_path"] = module_name
                                if callable(tool_func):
                                    tool_result["function_signature"] = str(inspect.signature(tool_func))
                                tool_found = True
                                break
                        except ImportError:
                            continue
                
                if not tool_found:
                    tool_result["errors"].append(f"工具 '{tool_name}' 未找到")
                elif not tool_result["callable"]:
                    tool_result["errors"].append(f"'{tool_name}' 不是可调用对象")
                else:
                    tool_result["valid"] = True
            
            except Exception as e:
                tool_result["errors"].append(f"验证工具 '{tool_name}' 时出错: {str(e)}")
            
            results[tool_name] = tool_result
        
        return results
    
    async def _validate_permissions(self) -> Dict[str, Any]:
        """验证数据库权限"""
        logger.info("🔍 验证数据库权限...")
        
        result = {
            "valid": True,
            "permissions": {},
            "errors": [],
            "warnings": []
        }
        
        session = next(get_db_session())
        
        try:
            # 测试基本查询权限
            try:
                session.execute(text("SELECT 1"))
                result["permissions"]["select"] = True
            except Exception as e:
                result["valid"] = False
                result["permissions"]["select"] = False
                result["errors"].append(f"缺少SELECT权限: {e}")
            
            # 测试创建触发器权限（如果启用了实时监听）
            if self.config.trigger_config.enable_realtime:
                try:
                    # 尝试创建一个测试触发器函数
                    test_function_sql = """
                    CREATE OR REPLACE FUNCTION test_trigger_permission() 
                    RETURNS trigger AS $$ 
                    BEGIN 
                        RETURN NULL; 
                    END; 
                    $$ LANGUAGE plpgsql;
                    """
                    session.execute(text(test_function_sql))
                    
                    # 删除测试函数
                    session.execute(text("DROP FUNCTION IF EXISTS test_trigger_permission()"))
                    session.commit()
                    
                    result["permissions"]["create_trigger"] = True
                except Exception as e:
                    result["permissions"]["create_trigger"] = False
                    result["warnings"].append(f"可能缺少创建触发器权限: {e}")
            
            # 测试通知权限
            try:
                session.execute(text("SELECT pg_notify('test_channel', 'test_message')"))
                result["permissions"]["notify"] = True
            except Exception as e:
                result["permissions"]["notify"] = False
                result["warnings"].append(f"可能缺少NOTIFY权限: {e}")
        
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"权限验证失败: {e}")
        
        finally:
            session.close()
        
        return result
    
    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """生成验证报告"""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("资源发现配置验证报告")
        report_lines.append("=" * 60)
        
        # 总体状态
        status = "✅ 通过" if validation_results["overall_valid"] else "❌ 失败"
        report_lines.append(f"总体状态: {status}")
        report_lines.append("")
        
        # 资源统计
        summary = validation_results.get("summary", {})
        report_lines.append(f"资源统计:")
        report_lines.append(f"  总计: {summary.get('total_resources', 0)}")
        report_lines.append(f"  有效: {summary.get('valid_resources', 0)}")
        report_lines.append(f"  无效: {summary.get('invalid_resources', 0)}")
        report_lines.append("")
        
        # 数据库验证结果
        db_validation = validation_results.get("database_validation", {})
        if db_validation:
            report_lines.append("数据库验证:")
            for table_name, table_result in db_validation.items():
                status = "✅" if table_result["valid"] else "❌"
                report_lines.append(f"  {status} {table_name}")
                if table_result.get("errors"):
                    for error in table_result["errors"]:
                        report_lines.append(f"    - {error}")
            report_lines.append("")
        
        # 工具验证结果
        tool_validation = validation_results.get("tool_validation", {})
        if tool_validation:
            report_lines.append("工具验证:")
            for tool_name, tool_result in tool_validation.items():
                status = "✅" if tool_result["valid"] else "❌"
                report_lines.append(f"  {status} {tool_name}")
                if tool_result.get("module_path"):
                    report_lines.append(f"    位置: {tool_result['module_path']}")
                if tool_result.get("errors"):
                    for error in tool_result["errors"]:
                        report_lines.append(f"    - {error}")
            report_lines.append("")
        
        # 权限验证结果
        permission_validation = validation_results.get("permission_validation", {})
        if permission_validation:
            report_lines.append("权限验证:")
            permissions = permission_validation.get("permissions", {})
            for perm_name, perm_status in permissions.items():
                status = "✅" if perm_status else "❌"
                report_lines.append(f"  {status} {perm_name}")
            
            if permission_validation.get("warnings"):
                report_lines.append("  警告:")
                for warning in permission_validation["warnings"]:
                    report_lines.append(f"    - {warning}")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
