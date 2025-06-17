"""
资源发现服务

基于 Ti-Flow 的 ResourceDiscoveryService 设计，自动发现系统中的各种资源
"""

import logging
import asyncio
import json
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
from src.tools.api_tools import execute_api, list_available_apis, get_api_details
from src.tools.text2sql_tools import text2sql_query, generate_sql_only, get_training_examples
from src.tools.database_tools import database_query, list_databases, test_database_connection

logger = logging.getLogger(__name__)


class ResourceDiscoveryService:
    """资源发现服务 - 自动发现系统中的各种资源"""

    def __init__(self):
        self.discovered_resources = []
        self.tool_registry = {
            'api': {
                'execute_api': execute_api,
                'list_available_apis': list_available_apis,
                'get_api_details': get_api_details
            },
            'text2sql': {
                'text2sql_query': text2sql_query,
                'generate_sql_only': generate_sql_only,
                'get_training_examples': get_training_examples
            },
            'database': {
                'database_query': database_query,
                'list_databases': list_databases,
                'test_database_connection': test_database_connection
            }
        }
    
    async def discover_all_resources(self, session: Session) -> List[Dict[str, Any]]:
        """发现所有可用资源"""
        resources = []

        try:
            # 使用真实工具发现数据库资源
            db_resources = await self._discover_database_resources_with_tools()
            resources.extend(db_resources)

            # 使用真实工具发现 API 资源
            api_resources = await self._discover_api_resources_with_tools()
            resources.extend(api_resources)

            # 发现系统工具
            tool_resources = await self._discover_system_tools()
            resources.extend(tool_resources)

            # 使用真实工具发现 Text2SQL 资源
            text2sql_resources = await self._discover_text2sql_resources_with_tools()
            resources.extend(text2sql_resources)

            logger.info(f"✅ 发现了 {len(resources)} 个资源")
            return resources

        except Exception as e:
            logger.error(f"资源发现失败: {e}")
            return []

    async def discover_all_resources_legacy(self, session: Session) -> List[Dict[str, Any]]:
        """发现所有可用资源 (传统方法，保留作为备用)"""
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

            # 发现 Text2SQL 资源
            text2sql_resources = await self._discover_text2sql_resources(session)
            resources.extend(text2sql_resources)

            logger.info(f"✅ 发现了 {len(resources)} 个资源")
            return resources

        except Exception as e:
            logger.error(f"资源发现失败: {e}")
            return []

    async def _discover_database_resources_with_tools(self) -> List[Dict[str, Any]]:
        """使用真实工具发现数据库资源"""
        resources = []

        try:
            # 使用 list_databases 工具获取数据库列表
            result = list_databases.invoke({'enabled_only': True})
            result_data = json.loads(result)

            if result_data.get('success') and result_data.get('data'):
                databases = result_data['data']['databases']

                for db in databases:
                    resource = {
                        "resource_id": f"database_{db['id']}",
                        "resource_name": db['name'],
                        "resource_type": ResourceType.DATABASE,
                        "description": db.get('description') or f"数据库连接: {db['name']} ({db['type']})",
                        "capabilities": [
                            "数据查询", "表结构获取", "连接测试",
                            "数据分析", "统计计算", "元数据查询"
                        ],
                        "tags": [
                            "database", "data", db['type'].lower(),
                            db['name'].lower().replace(" ", "_")
                        ],
                        "metadata": {
                            "datasource_id": db['id'],
                            "database_type": db['type'],
                            "host": db.get('host'),
                            "port": db.get('port'),
                            "database": db.get('database'),
                            "enabled": db.get('enabled', True),
                            "created_at": db.get('created_at'),
                            "tool_methods": ["database_query", "test_database_connection"]
                        },
                        "source_table": "database_datasources",
                        "source_id": db['id'],
                        "is_active": db.get('enabled', True),
                        "status": ResourceStatus.ACTIVE if db.get('enabled', True) else ResourceStatus.INACTIVE
                    }
                    resources.append(resource)

            logger.info(f"使用工具发现了 {len(resources)} 个数据库资源")
            return resources

        except Exception as e:
            logger.error(f"使用工具发现数据库资源失败: {e}")
            return []

    async def _discover_api_resources_with_tools(self) -> List[Dict[str, Any]]:
        """使用真实工具发现API资源"""
        resources = []

        try:
            # 使用 list_available_apis 工具获取API列表
            result = list_available_apis.invoke({'enabled_only': True})
            result_data = json.loads(result)

            if result_data.get('success') and result_data.get('data'):
                apis = result_data['data']['apis']

                for api in apis:
                    resource = {
                        "resource_id": f"api_{api['id']}",
                        "resource_name": api['name'],
                        "resource_type": ResourceType.API,
                        "description": api.get('description') or f"API接口: {api['name']}",
                        "capabilities": [
                            "HTTP请求", "数据获取", "外部服务调用",
                            "实时数据", "第三方集成", "API调用"
                        ],
                        "tags": [
                            "api", "http", str(api['method']).lower(),
                            api.get('category', 'general'),
                            api['name'].lower().replace(" ", "_")
                        ],
                        "metadata": {
                            "api_id": api['id'],
                            "method": api['method'],
                            "url": api['url'],
                            "category": api.get('category'),
                            "enabled": api.get('enabled', True),
                            "tool_methods": ["execute_api", "get_api_details"]
                        },
                        "source_table": "api_definitions",
                        "source_id": api['id'],
                        "is_active": api.get('enabled', True),
                        "status": ResourceStatus.ACTIVE if api.get('enabled', True) else ResourceStatus.INACTIVE
                    }
                    resources.append(resource)

            logger.info(f"使用工具发现了 {len(resources)} 个API资源")
            return resources

        except Exception as e:
            logger.error(f"使用工具发现API资源失败: {e}")
            return []

    async def _discover_text2sql_resources_with_tools(self) -> List[Dict[str, Any]]:
        """使用真实工具发现Text2SQL资源"""
        resources = []

        try:
            # 使用 get_training_examples 工具获取训练示例
            result = get_training_examples.invoke({'limit': 100})
            result_data = json.loads(result)

            if result_data.get('success') and result_data.get('data'):
                examples = result_data['data']['examples']

                # 按数据源分组
                datasource_groups = {}
                for example in examples:
                    # 这里需要从example中提取datasource_id，如果没有则使用默认值
                    datasource_id = 1  # 默认数据源ID

                    if datasource_id not in datasource_groups:
                        datasource_groups[datasource_id] = []
                    datasource_groups[datasource_id].append(example)

                for datasource_id, group_examples in datasource_groups.items():
                    resource = {
                        "resource_id": f"text2sql_{datasource_id}",
                        "resource_name": f"Text2SQL训练数据 (数据源 {datasource_id})",
                        "resource_type": ResourceType.TEXT2SQL,
                        "description": f"Text2SQL训练示例和查询模板 (数据源 {datasource_id})",
                        "capabilities": [
                            "自然语言转SQL", "SQL生成", "查询示例",
                            "语法参考", "最佳实践", "SQL验证"
                        ],
                        "tags": [
                            "text2sql", "vanna", "training_data",
                            f"datasource_{datasource_id}", "sql_examples"
                        ],
                        "metadata": {
                            "datasource_id": datasource_id,
                            "example_count": len(group_examples),
                            "tool_methods": ["text2sql_query", "generate_sql_only", "get_training_examples"]
                        },
                        "source_table": "vanna_embeddings",
                        "source_id": datasource_id,
                        "is_active": True,
                        "status": ResourceStatus.ACTIVE
                    }
                    resources.append(resource)

            logger.info(f"使用工具发现了 {len(resources)} 个Text2SQL资源")
            return resources

        except Exception as e:
            logger.error(f"使用工具发现Text2SQL资源失败: {e}")
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

    def get_available_tools(self) -> Dict[str, Any]:
        """获取所有可用的工具"""
        return {
            "tool_registry": self.tool_registry,
            "tool_count": sum(len(tools) for tools in self.tool_registry.values()),
            "categories": list(self.tool_registry.keys())
        }

    async def execute_tool(self, category: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行指定的工具"""
        try:
            if category not in self.tool_registry:
                return {
                    "success": False,
                    "error": f"工具类别 '{category}' 不存在",
                    "available_categories": list(self.tool_registry.keys())
                }

            if tool_name not in self.tool_registry[category]:
                return {
                    "success": False,
                    "error": f"工具 '{tool_name}' 在类别 '{category}' 中不存在",
                    "available_tools": list(self.tool_registry[category].keys())
                }

            tool = self.tool_registry[category][tool_name]
            result = tool.invoke(parameters)

            return {
                "success": True,
                "category": category,
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result
            }

        except Exception as e:
            logger.error(f"执行工具失败: {category}.{tool_name} - {e}")
            return {
                "success": False,
                "error": str(e),
                "category": category,
                "tool_name": tool_name,
                "parameters": parameters
            }

    async def discover_resources_for_query(self, query: str) -> List[Dict[str, Any]]:
        """根据查询发现相关资源"""
        try:
            # 使用所有工具发现资源
            all_resources = await self.discover_all_resources(None)

            # 简单的关键词匹配来过滤相关资源
            query_lower = query.lower()
            relevant_resources = []

            for resource in all_resources:
                # 检查资源名称、描述、标签和能力
                if (query_lower in resource.get('resource_name', '').lower() or
                    query_lower in resource.get('description', '').lower() or
                    any(query_lower in tag.lower() for tag in resource.get('tags', [])) or
                    any(query_lower in cap.lower() for cap in resource.get('capabilities', []))):
                    relevant_resources.append(resource)

            logger.info(f"为查询 '{query}' 找到 {len(relevant_resources)} 个相关资源")
            return relevant_resources

        except Exception as e:
            logger.error(f"为查询发现资源失败: {e}")
            return []
