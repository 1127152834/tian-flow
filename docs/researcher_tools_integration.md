# Researcher智能体工具集成文档

## 📋 概述

本文档记录了为DeerFlow系统的Researcher智能体新增的查询工具集成过程。这些工具大大增强了Researcher的数据查询和API调用能力。

## 🛠️ 新增工具列表

### 1. API工具 (API Tools)
- **execute_api**: 执行API调用，支持动态参数传递
- **list_available_apis**: 列出系统中所有可用的API
- **get_api_details**: 获取指定API的详细配置信息

### 2. Text2SQL工具 (Text2SQL Tools)
- **text2sql_query**: 将自然语言转换为SQL并执行查询
- **generate_sql_only**: 仅生成SQL语句，不执行查询
- **get_training_examples**: 获取Text2SQL训练示例
- **validate_sql**: 验证SQL语句的语法和安全性

### 3. 数据库工具 (Database Tools)
- **database_query**: 执行数据库查询，支持多种查询类型
- **list_databases**: 列出所有可用的数据库连接
- **test_database_connection**: 测试数据库连接状态

## 🔧 集成步骤

### 1. 工具模块导入
在 `src/tools/__init__.py` 中添加了新工具的导入：

```python
# 新增的工具模块
from .api_tools import execute_api, list_available_apis, get_api_details
from .text2sql_tools import text2sql_query, generate_sql_only, get_training_examples, validate_sql
from .database_tools import database_query, list_databases, test_database_connection
```

### 2. 智能体节点更新
在 `src/graph/nodes.py` 中：

#### 导入新工具
```python
from src.tools import (
    # 原有工具
    crawl_tool,
    get_web_search_tool,
    get_retriever_tool,
    python_repl_tool,
    # 新增的查询工具
    execute_api,
    list_available_apis,
    get_api_details,
    text2sql_query,
    generate_sql_only,
    get_training_examples,
    validate_sql,
    database_query,
    list_databases,
    test_database_connection,
)
```

#### 更新Researcher节点
```python
async def researcher_node(state: State, config: RunnableConfig):
    # 基础搜索和爬虫工具
    tools = [get_web_search_tool(configurable.max_search_results), crawl_tool]
    
    # 检索工具（条件性添加）
    retriever_tool = get_retriever_tool(state.get("resources", []))
    if retriever_tool:
        tools.insert(0, retriever_tool)
    
    # 新增的查询工具 - 为Researcher提供更强的数据查询能力
    query_tools = [
        # API工具
        execute_api, list_available_apis, get_api_details,
        # Text2SQL工具
        text2sql_query, generate_sql_only, get_training_examples, validate_sql,
        # 数据库工具
        database_query, list_databases, test_database_connection,
    ]
    tools.extend(query_tools)
```

### 3. 提示模板更新
在 `src/prompts/researcher.md` 中添加了新工具的说明：

#### 工具描述
```markdown
**Data Query Tools**: For accessing structured data and APIs:
- **execute_api**: Execute API calls by name or ID with parameters
- **list_available_apis**: List all available APIs in the system
- **get_api_details**: Get detailed information about a specific API
- **text2sql_query**: Convert natural language questions to SQL and execute them
- **generate_sql_only**: Generate SQL from natural language without execution
- **get_training_examples**: Get Text2SQL training examples for reference
- **validate_sql**: Validate SQL syntax and safety before execution
- **database_query**: Query database information, tables, schema, or execute custom SQL
- **list_databases**: List all available database connections
- **test_database_connection**: Test database connectivity
```

#### 使用指导
```markdown
- **For data-related queries**: Use the data query tools when the task involves:
  - Accessing structured data from databases
  - Converting natural language to SQL queries
  - Executing API calls to retrieve specific information
  - Validating data queries before execution
```

## 🎯 工具分配策略

### 为什么选择Researcher智能体？
1. **职责匹配**: Researcher负责信息收集和研究，这些查询工具完美契合其职责
2. **工具协同**: 与现有的搜索、爬虫工具形成完整的信息获取工具链
3. **使用场景**: 当用户需要结构化数据时，Researcher可以无缝切换到数据查询模式

### 工具使用场景
- **网络搜索** → 获取公开信息
- **网页爬虫** → 深度内容提取
- **API调用** → 获取实时数据
- **数据库查询** → 访问结构化数据
- **Text2SQL** → 自然语言数据查询

## ✅ 验证结果

通过集成测试验证：
- ✅ 所有10个新工具成功导入
- ✅ 工具在Researcher智能体中可用
- ✅ 工具描述和参数正确解析
- ✅ 提示模板更新生效

## 🚀 使用效果

Researcher智能体现在具备了：
1. **全面的信息获取能力**: 从网络搜索到数据库查询
2. **智能的工具选择**: 根据任务类型自动选择合适的工具
3. **结构化数据处理**: 支持SQL查询和API调用
4. **安全的数据访问**: 内置SQL验证和连接测试

## 📈 后续优化建议

1. **工具使用统计**: 监控各工具的使用频率和效果
2. **错误处理优化**: 完善工具调用的异常处理机制
3. **性能优化**: 对频繁使用的工具进行缓存优化
4. **权限控制**: 为敏感数据访问添加权限验证

---

**集成完成时间**: 2025-06-17  
**集成工具数量**: 10个  
**目标智能体**: Researcher  
**状态**: ✅ 完成并验证
