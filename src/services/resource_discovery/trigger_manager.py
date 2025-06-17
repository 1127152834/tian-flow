# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
数据库触发器管理器

管理资源发现系统的数据库触发器生命周期
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from src.config.resource_discovery import ResourceDiscoveryConfig, ResourceConfig
from src.database import get_db_session
from src.database.trigger_generator import TriggerSQLGenerator, TriggerConfig, create_trigger_config_from_resource

logger = logging.getLogger(__name__)


class TriggerManagerError(Exception):
    """触发器管理器错误"""
    pass


class TriggerManager:
    """触发器管理器"""
    
    def __init__(self, config: ResourceDiscoveryConfig):
        self.config = config
        self.generator = TriggerSQLGenerator()
        self.managed_triggers: Dict[str, TriggerConfig] = {}
    
    async def setup_all_triggers(self) -> Dict[str, Any]:
        """为所有启用的资源设置触发器"""
        logger.info("🔧 开始设置资源发现触发器...")
        
        results = {
            "success": True,
            "created_triggers": [],
            "failed_triggers": [],
            "skipped_triggers": [],
            "errors": []
        }
        
        if not self.config.enable_triggers:
            logger.info("⏭️ 触发器功能已禁用，跳过设置")
            results["skipped_triggers"].append("触发器功能已禁用")
            return results
        
        session = next(get_db_session())
        
        try:
            for resource in self.config.get_enabled_resources():
                try:
                    trigger_config = create_trigger_config_from_resource(
                        resource, self.config.trigger_config
                    )
                    
                    # 验证触发器配置
                    validation_errors = self.generator.validate_trigger_setup(trigger_config)
                    if validation_errors:
                        results["failed_triggers"].append({
                            "table": resource.table,
                            "errors": validation_errors
                        })
                        continue
                    
                    # 创建触发器
                    success = await self._create_trigger(session, trigger_config)
                    if success:
                        results["created_triggers"].append(resource.table)
                        self.managed_triggers[resource.table] = trigger_config
                        logger.info(f"✅ 触发器创建成功: {resource.table}")
                    else:
                        results["failed_triggers"].append({
                            "table": resource.table,
                            "errors": ["触发器创建失败"]
                        })
                
                except Exception as e:
                    logger.error(f"❌ 为表 {resource.table} 创建触发器失败: {e}")
                    results["failed_triggers"].append({
                        "table": resource.table,
                        "errors": [str(e)]
                    })
            
            # 提交所有更改
            session.commit()
            
            if results["failed_triggers"]:
                results["success"] = False
            
            logger.info(f"🎉 触发器设置完成: {len(results['created_triggers'])} 成功, {len(results['failed_triggers'])} 失败")
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ 触发器设置过程失败: {e}")
            results["success"] = False
            results["errors"].append(str(e))
        
        finally:
            session.close()
        
        return results
    
    async def remove_all_triggers(self) -> Dict[str, Any]:
        """移除所有管理的触发器"""
        logger.info("🗑️ 开始移除资源发现触发器...")
        
        results = {
            "success": True,
            "removed_triggers": [],
            "failed_removals": [],
            "errors": []
        }
        
        session = next(get_db_session())
        
        try:
            # 获取所有现有的触发器
            existing_triggers = await self._get_existing_triggers(session)
            
            for trigger_info in existing_triggers:
                try:
                    table_name = trigger_info["full_table_name"]
                    trigger_name = trigger_info["trigger_name"]
                    
                    # 创建临时配置用于生成删除SQL
                    temp_config = TriggerConfig(
                        table_name=table_name,
                        fields=[],  # 删除时不需要字段信息
                        trigger_prefix=self.config.trigger_config.trigger_prefix,
                        notify_channel_prefix=self.config.trigger_config.notify_channel_prefix
                    )
                    
                    # 生成并执行删除SQL
                    removal_sql = self.generator.generate_trigger_removal(temp_config)
                    session.execute(text(removal_sql))
                    
                    results["removed_triggers"].append(table_name)
                    logger.info(f"✅ 触发器删除成功: {table_name}")
                
                except Exception as e:
                    logger.error(f"❌ 删除触发器失败 {trigger_info}: {e}")
                    results["failed_removals"].append({
                        "trigger": trigger_info,
                        "error": str(e)
                    })
            
            # 提交更改
            session.commit()
            
            # 清空管理的触发器记录
            self.managed_triggers.clear()
            
            if results["failed_removals"]:
                results["success"] = False
            
            logger.info(f"🎉 触发器移除完成: {len(results['removed_triggers'])} 成功, {len(results['failed_removals'])} 失败")
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ 触发器移除过程失败: {e}")
            results["success"] = False
            results["errors"].append(str(e))
        
        finally:
            session.close()
        
        return results
    
    async def get_trigger_status(self) -> Dict[str, Any]:
        """获取所有触发器状态"""
        logger.info("📊 获取触发器状态...")
        
        session = next(get_db_session())
        
        try:
            # 获取现有触发器
            existing_triggers = await self._get_existing_triggers(session)
            
            # 获取配置中的资源
            configured_resources = self.config.get_enabled_resources()
            
            status = {
                "total_configured": len(configured_resources),
                "total_existing": len(existing_triggers),
                "triggers_enabled": self.config.enable_triggers,
                "configured_resources": [],
                "existing_triggers": existing_triggers,
                "missing_triggers": [],
                "extra_triggers": []
            }
            
            # 分析配置的资源
            configured_tables = set()
            for resource in configured_resources:
                configured_tables.add(resource.table)
                status["configured_resources"].append({
                    "table": resource.table,
                    "fields": resource.fields,
                    "tool": resource.tool,
                    "enabled": resource.enabled
                })
            
            # 分析现有触发器
            existing_tables = set()
            for trigger in existing_triggers:
                existing_tables.add(trigger["full_table_name"])
            
            # 找出缺失和多余的触发器
            status["missing_triggers"] = list(configured_tables - existing_tables)
            status["extra_triggers"] = list(existing_tables - configured_tables)
            
            return status
            
        except Exception as e:
            logger.error(f"❌ 获取触发器状态失败: {e}")
            return {
                "error": str(e),
                "triggers_enabled": self.config.enable_triggers
            }
        
        finally:
            session.close()
    
    async def _create_trigger(self, session: Session, trigger_config: TriggerConfig) -> bool:
        """创建单个触发器"""
        try:
            # 生成完整的触发器设置SQL
            setup_sql = self.generator.generate_complete_trigger_setup(trigger_config)
            
            # 执行SQL
            session.execute(text(setup_sql))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 创建触发器失败 {trigger_config.table_name}: {e}")
            return False
    
    async def _get_existing_triggers(self, session: Session) -> List[Dict[str, Any]]:
        """获取现有的资源发现触发器"""
        try:
            query_sql = self.generator.get_all_triggers_query(
                self.config.trigger_config.trigger_prefix
            )
            
            result = session.execute(text(query_sql))
            triggers = []
            
            for row in result.fetchall():
                trigger_info = {
                    "trigger_name": row.trigger_name,
                    "event_manipulation": row.event_manipulation,
                    "full_table_name": row.full_table_name,
                    "action_timing": row.action_timing,
                    "action_statement": row.action_statement,
                    "status": row.status
                }
                triggers.append(trigger_info)
            
            return triggers
            
        except Exception as e:
            logger.error(f"❌ 获取现有触发器失败: {e}")
            return []
    
    async def sync_triggers(self) -> Dict[str, Any]:
        """同步触发器：确保配置和实际状态一致"""
        logger.info("🔄 开始同步触发器...")
        
        # 获取当前状态
        status = await self.get_trigger_status()
        
        results = {
            "success": True,
            "actions_taken": [],
            "errors": []
        }
        
        try:
            # 如果触发器被禁用，移除所有触发器
            if not self.config.enable_triggers:
                if status.get("total_existing", 0) > 0:
                    removal_result = await self.remove_all_triggers()
                    results["actions_taken"].append({
                        "action": "remove_all",
                        "result": removal_result
                    })
                return results
            
            # 创建缺失的触发器
            if status.get("missing_triggers"):
                logger.info(f"📝 创建缺失的触发器: {status['missing_triggers']}")
                creation_result = await self.setup_all_triggers()
                results["actions_taken"].append({
                    "action": "create_missing",
                    "result": creation_result
                })
            
            # 移除多余的触发器
            if status.get("extra_triggers"):
                logger.info(f"🗑️ 移除多余的触发器: {status['extra_triggers']}")
                # 这里可以实现选择性移除逻辑
                results["actions_taken"].append({
                    "action": "identified_extra",
                    "extra_triggers": status["extra_triggers"]
                })
            
            logger.info("✅ 触发器同步完成")
            
        except Exception as e:
            logger.error(f"❌ 触发器同步失败: {e}")
            results["success"] = False
            results["errors"].append(str(e))
        
        return results
