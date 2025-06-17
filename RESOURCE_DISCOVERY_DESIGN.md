# 🔍 DeerFlow 资源发现模块设计方案

## 🎯 设计目标

基于 Ti-Flow 意图识别模块的成功实践，为 DeerFlow 设计一个更强大的**智能资源发现和匹配系统**：

- **统一资源管理** - 将所有系统资源抽象为统一的可发现资源
- **智能语义匹配** - 基于向量相似度的智能资源推荐
- **动态实时更新** - 监控资源变化，支持增量向量化
- **深度 Agent 集成** - 作为 DeerFlow Agent 的核心工具

## 🏗️ 核心架构

### 1. 资源抽象层
```python
class UniversalResource:
    """统一资源抽象"""
    resource_id: str          # 全局唯一标识
    resource_type: str        # 资源类型
    name: str                 # 资源名称
    description: str          # 资源描述
    capabilities: List[str]   # 资源能力
    usage_info: Dict         # 使用说明
    metadata: Dict           # 元数据
    vector_embeddings: Dict  # 多维度向量
```

### 2. 资源发现服务
```python
class ResourceDiscoveryService:
    """资源发现服务 - 自动发现所有系统资源"""
    
    async def discover_all_resources(self) -> List[UniversalResource]:
        """发现所有可用资源"""
        resources = []
        
        # 发现数据库连接
        resources.extend(await self._discover_database_resources())
        
        # 发现 API 定义
        resources.extend(await self._discover_api_resources())
        
        # 发现系统工具
        resources.extend(await self._discover_system_tools())
        
        # 发现知识库
        resources.extend(await self._discover_knowledge_bases())
        
        # 发现 Text2SQL 资源
        resources.extend(await self._discover_text2sql_resources())
        
        return resources
```

### 3. 智能向量化器
```python
class IntelligentVectorizer:
    """智能向量化器 - 多维度向量化策略"""
    
    async def vectorize_resource(self, resource: UniversalResource) -> Dict[str, Any]:
        """多维度向量化资源"""
        vectors = {}
        
        # 1. 名称向量 - 精确匹配
        vectors["name"] = await self._vectorize_text(resource.name)
        
        # 2. 描述向量 - 语义理解
        vectors["description"] = await self._vectorize_text(resource.description)
        
        # 3. 能力向量 - 功能匹配
        capability_text = " ".join(resource.capabilities)
        vectors["capabilities"] = await self._vectorize_text(capability_text)
        
        # 4. 复合向量 - 综合匹配
        composite_text = self._build_composite_text(resource)
        vectors["composite"] = await self._vectorize_text(composite_text)
        
        return vectors
```

### 4. 智能匹配器
```python
class IntelligentMatcher:
    """智能匹配器 - 基于用户意图的资源推荐"""
    
    async def match_resources(
        self, 
        user_query: str, 
        top_k: int = 5
    ) -> List[ResourceMatch]:
        """匹配最相关的资源"""
        
        # 1. 查询向量化
        query_vector = await self._vectorize_query(user_query)
        
        # 2. 多维度相似度搜索
        matches = await self._search_similar_resources(query_vector, top_k * 2)
        
        # 3. 智能重排序
        ranked_matches = await self._intelligent_rerank(user_query, matches)
        
        # 4. 返回最佳匹配
        return ranked_matches[:top_k]
```

## 📊 数据模型设计

### 1. 资源注册表
```sql
CREATE TABLE resource_registry (
    id BIGSERIAL PRIMARY KEY,
    resource_id VARCHAR(255) UNIQUE NOT NULL,
    resource_type VARCHAR(50) NOT NULL,  -- 'database', 'api', 'tool', 'knowledge_base', 'text2sql'
    name VARCHAR(255) NOT NULL,
    description TEXT,
    capabilities JSONB,
    usage_info JSONB,
    metadata JSONB,
    
    -- 状态管理
    is_active BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'active',
    
    -- 性能指标
    usage_count INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 1.0,
    avg_response_time INTEGER DEFAULT 0,
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_vectorized_at TIMESTAMP WITH TIME ZONE
);
```

### 2. 向量存储表
```sql
CREATE TABLE resource_vectors (
    id BIGSERIAL PRIMARY KEY,
    resource_id VARCHAR(255) NOT NULL,
    vector_type VARCHAR(20) NOT NULL,  -- 'name', 'description', 'capabilities', 'composite'
    content TEXT NOT NULL,
    embedding VECTOR(1536),  -- 支持不同维度
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    FOREIGN KEY (resource_id) REFERENCES resource_registry(resource_id) ON DELETE CASCADE
);

-- 向量索引
CREATE INDEX idx_resource_vectors_embedding ON resource_vectors 
USING hnsw (embedding vector_cosine_ops);
```

### 3. 匹配历史表
```sql
CREATE TABLE resource_match_history (
    id BIGSERIAL PRIMARY KEY,
    user_query TEXT NOT NULL,
    query_hash VARCHAR(64),
    matched_resources JSONB,
    selected_resource VARCHAR(255),
    execution_success BOOLEAN,
    user_feedback VARCHAR(20),  -- 'positive', 'negative', 'neutral'
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔄 资源发现策略

### 1. 数据库资源发现
```python
async def _discover_database_resources(self) -> List[UniversalResource]:
    """发现数据库连接资源"""
    resources = []
    
    # 从 database_datasource 表获取所有数据库连接
    datasources = await self._get_database_datasources()
    
    for ds in datasources:
        resource = UniversalResource(
            resource_id=f"database_{ds.id}",
            resource_type="database",
            name=ds.name,
            description=f"数据库连接: {ds.name}",
            capabilities=[
                "数据查询", "SQL执行", "表结构获取", 
                "数据分析", "统计计算"
            ],
            usage_info={
                "connection_type": ds.db_type,
                "host": ds.host,
                "database": ds.database,
                "available_tables": await self._get_table_list(ds)
            },
            metadata={
                "datasource_id": ds.id,
                "created_at": ds.created_at.isoformat()
            }
        )
        resources.append(resource)
    
    return resources
```

### 2. API 资源发现
```python
async def _discover_api_resources(self) -> List[UniversalResource]:
    """发现 API 定义资源"""
    resources = []
    
    # 从 api_definitions 表获取所有 API
    api_defs = await self._get_api_definitions()
    
    for api in api_defs:
        resource = UniversalResource(
            resource_id=f"api_{api.id}",
            resource_type="api",
            name=api.name,
            description=api.description,
            capabilities=[
                "HTTP请求", "数据获取", "外部服务调用",
                "实时数据", "第三方集成"
            ],
            usage_info={
                "method": api.method,
                "url": api.url,
                "parameters": api.parameters,
                "auth_required": api.auth_config.auth_type != "NONE"
            },
            metadata={
                "api_id": api.id,
                "category": api.category,
                "enabled": api.enabled
            }
        )
        resources.append(resource)
    
    return resources
```

### 3. 系统工具发现
```python
async def _discover_system_tools(self) -> List[UniversalResource]:
    """发现系统工具资源"""
    resources = []
    
    # 通过反射发现所有 @tool 装饰的函数
    tools = await self._scan_tool_functions()
    
    for tool_func in tools:
        resource = UniversalResource(
            resource_id=f"tool_{tool_func.__name__}",
            resource_type="tool",
            name=tool_func.__name__,
            description=tool_func.__doc__ or f"系统工具: {tool_func.__name__}",
            capabilities=self._extract_tool_capabilities(tool_func),
            usage_info={
                "function_name": tool_func.__name__,
                "parameters": self._get_function_signature(tool_func),
                "module": tool_func.__module__
            },
            metadata={
                "tool_type": "system",
                "is_async": asyncio.iscoroutinefunction(tool_func)
            }
        )
        resources.append(resource)
    
    return resources
```

## 🎯 智能匹配算法

### 1. 多维度相似度计算
```python
async def _calculate_similarity_score(
    self, 
    query_vector: List[float], 
    resource: UniversalResource
) -> float:
    """计算多维度相似度分数"""
    
    scores = []
    weights = {
        "name": 0.3,        # 名称匹配权重
        "description": 0.4,  # 描述匹配权重
        "capabilities": 0.2, # 能力匹配权重
        "composite": 0.1     # 复合匹配权重
    }
    
    for vector_type, weight in weights.items():
        if vector_type in resource.vector_embeddings:
            similarity = cosine_similarity(
                query_vector, 
                resource.vector_embeddings[vector_type]
            )
            scores.append(similarity * weight)
    
    return sum(scores)
```

### 2. 智能重排序
```python
async def _intelligent_rerank(
    self, 
    user_query: str, 
    initial_matches: List[ResourceMatch]
) -> List[ResourceMatch]:
    """基于多种因素的智能重排序"""
    
    for match in initial_matches:
        # 1. 基础相似度分数
        base_score = match.similarity_score
        
        # 2. 历史使用偏好
        usage_boost = await self._calculate_usage_preference(match.resource)
        
        # 3. 性能指标加权
        performance_boost = self._calculate_performance_score(match.resource)
        
        # 4. 上下文相关性
        context_boost = await self._calculate_context_relevance(
            user_query, match.resource
        )
        
        # 综合评分
        match.final_score = (
            base_score * 0.6 +
            usage_boost * 0.2 +
            performance_boost * 0.1 +
            context_boost * 0.1
        )
    
    # 按最终分数排序
    return sorted(initial_matches, key=lambda x: x.final_score, reverse=True)
```

## 🔄 增量更新机制

### 1. 资源变更监控
```python
class ResourceChangeMonitor:
    """资源变更监控器"""
    
    async def monitor_resource_changes(self):
        """监控资源变更"""
        
        # 监控数据库连接变更
        await self._monitor_database_changes()
        
        # 监控 API 定义变更
        await self._monitor_api_changes()
        
        # 监控工具变更
        await self._monitor_tool_changes()
        
        # 监控知识库变更
        await self._monitor_knowledge_base_changes()
```

### 2. 增量向量化
```python
async def incremental_vectorization(self, changed_resources: List[str]):
    """增量向量化变更的资源"""
    
    for resource_id in changed_resources:
        # 1. 重新发现资源
        resource = await self._rediscover_resource(resource_id)
        
        # 2. 删除旧向量
        await self._delete_old_vectors(resource_id)
        
        # 3. 重新向量化
        vectors = await self.vectorizer.vectorize_resource(resource)
        
        # 4. 存储新向量
        await self._store_vectors(resource_id, vectors)
```

## 🛠️ Agent 工具集成

### 1. 资源路由工具
```python
@tool
async def resource_discovery_tool(
    user_query: str,
    max_resources: int = 3
) -> List[Dict[str, Any]]:
    """
    智能资源发现工具
    
    根据用户查询找到最匹配的系统资源
    """
    matcher = IntelligentMatcher()
    matches = await matcher.match_resources(user_query, max_resources)
    
    return [
        {
            "resource_id": match.resource.resource_id,
            "name": match.resource.name,
            "type": match.resource.resource_type,
            "description": match.resource.description,
            "capabilities": match.resource.capabilities,
            "usage_info": match.resource.usage_info,
            "confidence": match.final_score
        }
        for match in matches
    ]
```

## 📈 性能优化策略

1. **向量缓存** - 缓存常用查询的向量结果
2. **批量处理** - 批量向量化和存储
3. **异步处理** - 非阻塞的资源发现和向量化
4. **增量更新** - 只处理变更的资源
5. **智能预加载** - 预测性资源加载

## 🎯 下一步实施计划

1. **Phase 1**: 核心架构和数据模型
2. **Phase 2**: 资源发现服务实现
3. **Phase 3**: 向量化和匹配算法
4. **Phase 4**: Agent 工具集成
5. **Phase 5**: 增量更新和性能优化
