-- =====================================================
-- 资源发现模块数据库迁移脚本
-- 基于 Ti-Flow 意图识别模块设计
-- =====================================================

-- 创建资源发现模式
CREATE SCHEMA IF NOT EXISTS resource_discovery;

-- 1. 资源注册表 - 记录系统中发现的各种资源
CREATE TABLE IF NOT EXISTS resource_discovery.resource_registry (
    id BIGSERIAL PRIMARY KEY,
    resource_id VARCHAR(255) NOT NULL UNIQUE, -- 资源唯一标识 (如: database_1, api_2, tool_search)
    resource_name VARCHAR(255) NOT NULL, -- 资源名称
    resource_type VARCHAR(50) NOT NULL, -- 'database', 'api', 'tool', 'knowledge_base', 'text2sql'
    description TEXT, -- 资源描述
    capabilities JSONB, -- 资源能力列表 (如: ["数据查询", "统计分析"])
    tags JSONB, -- 资源标签 (如: ["数据库", "SQL", "分析"])
    metadata JSONB, -- 资源元数据 (包含连接信息、配置等)
    
    -- 资源可用性
    is_active BOOLEAN DEFAULT TRUE, -- 是否激活
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'inactive', 'maintenance', 'error'
    
    -- 引用关系 (指向原始数据来源)
    source_table VARCHAR(100), -- 原始数据表名 (如: database_datasources)
    source_id INTEGER, -- 原始数据ID
    
    -- 向量化状态
    vector_updated_at TIMESTAMP WITH TIME ZONE, -- 向量最后更新时间
    vectorization_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    
    -- 性能指标
    usage_count INTEGER DEFAULT 0, -- 使用次数
    success_rate FLOAT DEFAULT 1.0, -- 成功率
    avg_response_time INTEGER DEFAULT 0, -- 平均响应时间(毫秒)
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_resource_registry_type ON resource_discovery.resource_registry (resource_type);
CREATE INDEX IF NOT EXISTS idx_resource_registry_status ON resource_discovery.resource_registry (status);
CREATE INDEX IF NOT EXISTS idx_resource_registry_source ON resource_discovery.resource_registry (source_table, source_id);
CREATE INDEX IF NOT EXISTS idx_resource_registry_vector_status ON resource_discovery.resource_registry (vectorization_status);
CREATE INDEX IF NOT EXISTS idx_resource_registry_updated_at ON resource_discovery.resource_registry (updated_at);
CREATE INDEX IF NOT EXISTS idx_resource_registry_name ON resource_discovery.resource_registry (resource_name);

-- 2. 资源向量存储表 - 存储资源的各种向量表示
CREATE TABLE IF NOT EXISTS resource_discovery.resource_vectors (
    id BIGSERIAL PRIMARY KEY,
    resource_id VARCHAR(255) NOT NULL, -- 资源ID (关联resource_registry.resource_id)
    vector_type VARCHAR(20) NOT NULL, -- 'name', 'description', 'capabilities', 'composite'
    content TEXT NOT NULL, -- 原始文本内容
    
    -- 向量数据 (使用 pgvector)
    embedding vector(1536), -- 向量数据 (默认1536维)
    embedding_dimension INTEGER NOT NULL DEFAULT 1536, -- 向量维度
    
    -- 模型信息
    embedding_model_name VARCHAR(100), -- 使用的Embedding模型名称
    
    -- 向量质量
    vector_norm FLOAT, -- 向量范数 (用于质量评估)
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (resource_id) REFERENCES resource_discovery.resource_registry(resource_id) ON DELETE CASCADE,
    
    -- 唯一约束 (每个资源的每种向量类型只能有一条记录)
    UNIQUE (resource_id, vector_type)
);

-- 创建向量索引
CREATE INDEX IF NOT EXISTS idx_resource_vectors_embedding ON resource_discovery.resource_vectors 
USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_resource_vectors_resource_type ON resource_discovery.resource_vectors (resource_id, vector_type);
CREATE INDEX IF NOT EXISTS idx_resource_vectors_dimension ON resource_discovery.resource_vectors (embedding_dimension);

-- 3. 资源匹配历史表 - 记录用户查询和匹配结果
CREATE TABLE IF NOT EXISTS resource_discovery.resource_match_history (
    id BIGSERIAL PRIMARY KEY,
    
    -- 查询信息
    user_query TEXT NOT NULL, -- 用户原始查询
    query_hash VARCHAR(64), -- 查询hash (用于去重和缓存)
    user_context JSONB, -- 用户上下文信息
    
    -- 匹配结果
    matched_resource_ids JSONB, -- 匹配到的资源ID列表
    similarity_scores JSONB, -- 相似度得分列表
    confidence_scores JSONB, -- 置信度得分列表
    reasoning JSONB, -- 匹配推理信息
    
    -- 最终选择
    final_selected_resource VARCHAR(255), -- 用户最终选择的资源ID
    
    -- 执行结果
    execution_success BOOLEAN, -- 是否执行成功
    execution_result JSONB, -- 执行结果
    response_time FLOAT, -- 响应时间 (毫秒)
    
    -- 用户反馈
    user_feedback VARCHAR(20), -- 'positive', 'negative', 'neutral'
    feedback_note TEXT, -- 反馈备注
    
    -- 会话信息
    session_id VARCHAR(128), -- 会话ID
    user_id VARCHAR(128), -- 用户ID
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_resource_match_history_query_hash ON resource_discovery.resource_match_history (query_hash);
CREATE INDEX IF NOT EXISTS idx_resource_match_history_user_feedback ON resource_discovery.resource_match_history (user_feedback);
CREATE INDEX IF NOT EXISTS idx_resource_match_history_session_user ON resource_discovery.resource_match_history (session_id, user_id);
CREATE INDEX IF NOT EXISTS idx_resource_match_history_created_at ON resource_discovery.resource_match_history (created_at);
CREATE INDEX IF NOT EXISTS idx_resource_match_history_response_time ON resource_discovery.resource_match_history (response_time);

-- 4. 资源使用统计表 - 统计资源的使用情况
CREATE TABLE IF NOT EXISTS resource_discovery.resource_usage_stats (
    id BIGSERIAL PRIMARY KEY,
    resource_id VARCHAR(255) NOT NULL, -- 资源ID
    
    -- 统计数据
    total_matches INTEGER DEFAULT 0, -- 总匹配次数
    successful_matches INTEGER DEFAULT 0, -- 成功匹配次数
    user_selections INTEGER DEFAULT 0, -- 用户选择次数
    positive_feedback INTEGER DEFAULT 0, -- 正面反馈次数
    negative_feedback INTEGER DEFAULT 0, -- 负面反馈次数
    
    -- 性能指标
    avg_similarity_score FLOAT, -- 平均相似度得分
    avg_response_time FLOAT, -- 平均响应时间
    
    -- 统计周期
    stats_date DATE NOT NULL, -- 统计日期
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (resource_id) REFERENCES resource_discovery.resource_registry(resource_id) ON DELETE CASCADE,
    
    -- 唯一约束
    UNIQUE (resource_id, stats_date)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_resource_usage_stats_resource_date ON resource_discovery.resource_usage_stats (resource_id, stats_date);
CREATE INDEX IF NOT EXISTS idx_resource_usage_stats_date ON resource_discovery.resource_usage_stats (stats_date);

-- 5. 系统状态管理表 - 记录系统操作状态
CREATE TABLE IF NOT EXISTS resource_discovery.system_status (
    id BIGSERIAL PRIMARY KEY,
    operation_type VARCHAR(50) NOT NULL, -- 'discovery', 'vectorization', 'sync'
    status VARCHAR(20) NOT NULL, -- 'pending', 'running', 'completed', 'failed'
    
    -- 操作详情
    total_items INTEGER DEFAULT 0, -- 总项目数
    successful_items INTEGER DEFAULT 0, -- 成功项目数
    failed_items INTEGER DEFAULT 0, -- 失败项目数
    error_message TEXT, -- 错误信息
    
    -- 结果数据
    result_data JSONB, -- 操作结果数据
    
    -- 时间信息
    started_at TIMESTAMP WITH TIME ZONE, -- 开始时间
    completed_at TIMESTAMP WITH TIME ZONE, -- 完成时间
    duration_seconds INTEGER, -- 持续时间(秒)
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_system_status_operation_type ON resource_discovery.system_status (operation_type);
CREATE INDEX IF NOT EXISTS idx_system_status_status ON resource_discovery.system_status (status);
CREATE INDEX IF NOT EXISTS idx_system_status_created_at ON resource_discovery.system_status (created_at);

-- 创建更新时间戳的触发器函数
CREATE OR REPLACE FUNCTION resource_discovery.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有表添加更新时间戳触发器
CREATE TRIGGER update_resource_registry_updated_at 
    BEFORE UPDATE ON resource_discovery.resource_registry 
    FOR EACH ROW EXECUTE FUNCTION resource_discovery.update_updated_at_column();

CREATE TRIGGER update_resource_vectors_updated_at 
    BEFORE UPDATE ON resource_discovery.resource_vectors 
    FOR EACH ROW EXECUTE FUNCTION resource_discovery.update_updated_at_column();

CREATE TRIGGER update_resource_match_history_updated_at 
    BEFORE UPDATE ON resource_discovery.resource_match_history 
    FOR EACH ROW EXECUTE FUNCTION resource_discovery.update_updated_at_column();

CREATE TRIGGER update_resource_usage_stats_updated_at 
    BEFORE UPDATE ON resource_discovery.resource_usage_stats 
    FOR EACH ROW EXECUTE FUNCTION resource_discovery.update_updated_at_column();

CREATE TRIGGER update_system_status_updated_at 
    BEFORE UPDATE ON resource_discovery.system_status 
    FOR EACH ROW EXECUTE FUNCTION resource_discovery.update_updated_at_column();

-- =====================================================
-- 资源发现模块数据库迁移完成
-- =====================================================
