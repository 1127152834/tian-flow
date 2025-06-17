"""
资源发现服务

基于 Ti-Flow 的 ResourceDiscoveryService 设计，自动发现系统中的各种资源
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.models.resource_discovery import (
    ResourceRegistry,
    ResourceRegistryCreate,
    ResourceType,
    ResourceStatus,
    VectorizationStatus
)

logger = logging.getLogger(__name__)


class ResourceDiscoveryService:
    """资源发现服务 - 自动发现系统中的各种资源"""
    
    def __init__(self):
        self.discovered_resources = []
    
    async def discover_all_resources(self, session: Session) -> List[Dict[str, Any]]:
        """发现所有可用资源"""
        resources = []
        
        try:
            # 发现数据库资源
            db_resources = await self._discover_database_resources(session)
            resources.extend(db_resources)
            
            # 发现 API 资源
            api_resources = await self._discover_api_resources(session)
            resources.extend(api_resources)
            
            # 发现系统工具
            tool_resources = await self._discover_system_tools()
            resources.extend(tool_resources)
            
            # 发现知识库资源 (预留)
            # kb_resources = await self._discover_knowledge_base_resources(session)
            # resources.extend(kb_resources)
            
            # 发现 Text2SQL 资源
            text2sql_resources = await self._discover_text2sql_resources(session)
            resources.extend(text2sql_resources)
            
            logger.info(f"✅ 发现了 {len(resources)} 个资源")
            return resources
            
        except Exception as e:
            logger.error(f"资源发现失败: {e}")
            return []
    
    async def _discover_database_resources(self, session: Session) -> List[Dict[str, Any]]:
        """发现数据库连接资源"""
        resources = []
        
        try:
            # 查询数据库数据源表
            query = text("""
                SELECT id, name, database_type, host, port, database_name, description, created_at
                FROM database_management.database_datasources
                WHERE deleted_at IS NULL
                ORDER BY created_at DESC
            """)
            
            result = session.execute(query)
            datasources = result.fetchall()
            
            for ds in datasources:
                resource = {
                    "resource_id": f"database_{ds.id}",
                    "resource_name": ds.name,
                    "resource_type": ResourceType.DATABASE,
                    "description": ds.description or f"数据库连接: {ds.name} ({ds.database_type})",
                    "capabilities": [
                        "数据查询", "SQL执行", "表结构获取",
                        "数据分析", "统计计算", "数据导出"
                    ],
                    "tags": [
                        "database", "sql", "data", ds.database_type.lower(),
                        ds.name.lower().replace(" ", "_")
                    ],
                    "metadata": {
                        "datasource_id": ds.id,
                        "database_type": ds.database_type,
                        "host": ds.host,
                        "port": ds.port,
                        "database_name": ds.database_name,
                        "created_at": ds.created_at.isoformat() if ds.created_at else None
                    },
                    "source_table": "database_datasources",
                    "source_id": ds.id,
                    "is_active": True,
                    "status": ResourceStatus.ACTIVE
                }
                resources.append(resource)
            
            logger.info(f"发现了 {len(resources)} 个数据库资源")
            return resources
            
        except Exception as e:
            logger.error(f"发现数据库资源失败: {e}")
            return []
    
    async def _discover_api_resources(self, session: Session) -> List[Dict[str, Any]]:
        """发现 API 定义资源"""
        resources = []
        
        try:
            # 查询 API 定义表
            query = text("""
                SELECT id, name, description, method, url, category, enabled, created_at
                FROM api_tools.api_definitions
                ORDER BY created_at DESC
            """)
            
            result = session.execute(query)
            api_defs = result.fetchall()
            
            for api in api_defs:
                # 将 HTTP 方法数字转换为字符串
                method_map = {0: "GET", 1: "POST", 2: "PUT", 3: "DELETE", 4: "PATCH"}
                method_str = method_map.get(api.method, "GET")
                
                resource = {
                    "resource_id": f"api_{api.id}",
                    "resource_name": api.name,
                    "resource_type": ResourceType.API,
                    "description": api.description or f"API接口: {api.name}",
                    "capabilities": [
                        "HTTP请求", "数据获取", "外部服务调用",
                        "实时数据", "第三方集成", "API调用"
                    ],
                    "tags": [
                        "api", "http", method_str.lower(), 
                        api.category or "general",
                        api.name.lower().replace(" ", "_")
                    ],
                    "metadata": {
                        "api_id": api.id,
                        "method": method_str,
                        "url": api.url,
                        "category": api.category,
                        "enabled": api.enabled,
                        "created_at": api.created_at.isoformat() if api.created_at else None
                    },
                    "source_table": "api_definitions",
                    "source_id": api.id,
                    "is_active": api.enabled,
                    "status": ResourceStatus.ACTIVE if api.enabled else ResourceStatus.INACTIVE
                }
                resources.append(resource)
            
            logger.info(f"发现了 {len(resources)} 个 API 资源")
            return resources
            
        except Exception as e:
            logger.error(f"发现 API 资源失败: {e}")
            return []
    
    async def _discover_system_tools(self) -> List[Dict[str, Any]]:
        """发现系统工具资源"""
        resources = []
        
        try:
            # 通过反射发现所有 @tool 装饰的函数
            tools = await self._scan_tool_functions()
            
            for tool_func in tools:
                function_name = tool_func.__name__
                module_name = tool_func.__module__
                
                # 提取工具描述
                description = tool_func.__doc__ or f"系统工具: {function_name}"
                if description:
                    description = description.strip().split('\n')[0]  # 取第一行作为描述
                
                resource = {
                    "resource_id": f"tool_{function_name}",
                    "resource_name": function_name,
                    "resource_type": ResourceType.TOOL,
                    "description": description,
                    "capabilities": self._extract_tool_capabilities(tool_func),
                    "tags": [
                        "tool", "system", "function",
                        function_name.lower(),
                        module_name.split('.')[-1] if '.' in module_name else module_name
                    ],
                    "metadata": {
                        "function_name": function_name,
                        "module": module_name,
                        "is_async": asyncio.iscoroutinefunction(tool_func),
                        "signature": str(tool_func.__annotations__) if hasattr(tool_func, '__annotations__') else None
                    },
                    "source_table": "system_tools",
                    "source_id": hash(f"{module_name}.{function_name}"),
                    "is_active": True,
                    "status": ResourceStatus.ACTIVE
                }
                resources.append(resource)
            
            logger.info(f"发现了 {len(resources)} 个系统工具资源")
            return resources
            
        except Exception as e:
            logger.error(f"发现系统工具失败: {e}")
            return []
    
    async def _discover_text2sql_resources(self, session: Session) -> List[Dict[str, Any]]:
        """发现 Text2SQL 相关资源"""
        resources = []
        
        try:
            # 查询 vanna_embeddings 表中的训练数据
            query = text("""
                SELECT DISTINCT datasource_id, content_type, COUNT(*) as count
                FROM text2sql.vanna_embeddings
                GROUP BY datasource_id, content_type
                ORDER BY datasource_id, content_type
            """)
            
            result = session.execute(query)
            embeddings = result.fetchall()
            
            for emb in embeddings:
                content_type = emb.content_type
                datasource_id = emb.datasource_id
                count = emb.count
                
                if content_type == "DDL":
                    resource_type_suffix = "tables"
                    description = f"数据库表结构信息 (数据源 {datasource_id})"
                    capabilities = ["表结构查询", "字段信息", "DDL生成", "模式分析"]
                elif content_type == "SQL":
                    resource_type_suffix = "sql_examples"
                    description = f"SQL查询示例 (数据源 {datasource_id})"
                    capabilities = ["SQL示例", "查询模板", "语法参考", "最佳实践"]
                else:
                    resource_type_suffix = "documentation"
                    description = f"数据库文档 (数据源 {datasource_id})"
                    capabilities = ["文档查询", "说明信息", "使用指南"]
                
                resource = {
                    "resource_id": f"text2sql_{datasource_id}_{content_type.lower()}",
                    "resource_name": f"Text2SQL {resource_type_suffix} (数据源 {datasource_id})",
                    "resource_type": ResourceType.TEXT2SQL,
                    "description": description,
                    "capabilities": capabilities,
                    "tags": [
                        "text2sql", "vanna", content_type.lower(),
                        f"datasource_{datasource_id}", "training_data"
                    ],
                    "metadata": {
                        "datasource_id": datasource_id,
                        "content_type": content_type,
                        "embedding_count": count,
                        "source": "vanna_embeddings"
                    },
                    "source_table": "vanna_embeddings",
                    "source_id": datasource_id,
                    "is_active": True,
                    "status": ResourceStatus.ACTIVE
                }
                resources.append(resource)
            
            logger.info(f"发现了 {len(resources)} 个 Text2SQL 资源")
            return resources
            
        except Exception as e:
            logger.error(f"发现 Text2SQL 资源失败: {e}")
            return []
    
    async def _scan_tool_functions(self) -> List:
        """扫描系统中所有的工具函数"""
        tools = []
        
        try:
            # 导入工具模块并扫描 @tool 装饰的函数
            import importlib
            import pkgutil
            import inspect
            
            # 扫描 src.tools 模块
            try:
                import src.tools as tools_module
                for importer, modname, ispkg in pkgutil.iter_modules(tools_module.__path__, tools_module.__name__ + "."):
                    try:
                        module = importlib.import_module(modname)
                        for name, obj in inspect.getmembers(module, inspect.isfunction):
                            # 检查是否有 tool 装饰器的标记
                            if hasattr(obj, '__tool__') or hasattr(obj, '_tool_name'):
                                tools.append(obj)
                    except Exception as e:
                        logger.warning(f"扫描模块 {modname} 失败: {e}")
            except ImportError:
                logger.warning("未找到 src.tools 模块")
            
            # 也可以扫描其他可能包含工具的模块
            # 这里可以根据实际项目结构添加更多模块
            
        except Exception as e:
            logger.error(f"扫描工具函数失败: {e}")
        
        return tools
    
    def _extract_tool_capabilities(self, tool_func) -> List[str]:
        """从工具函数中提取能力描述"""
        capabilities = ["工具调用", "系统功能"]
        
        # 根据函数名推断能力
        func_name = tool_func.__name__.lower()
        
        if "search" in func_name:
            capabilities.extend(["搜索", "查询", "检索"])
        if "get" in func_name or "fetch" in func_name:
            capabilities.extend(["数据获取", "信息检索"])
        if "create" in func_name or "generate" in func_name:
            capabilities.extend(["创建", "生成"])
        if "update" in func_name or "modify" in func_name:
            capabilities.extend(["更新", "修改"])
        if "delete" in func_name or "remove" in func_name:
            capabilities.extend(["删除", "移除"])
        if "analyze" in func_name or "process" in func_name:
            capabilities.extend(["分析", "处理"])
        
        return list(set(capabilities))  # 去重
