-- PostgreSQL initialization script for deer-flow
-- This script sets up the database with pgvector extension and initial schema

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema for database management module
CREATE SCHEMA IF NOT EXISTS database_management;

-- Create table for database datasources (for reference, actual storage is in config file)
CREATE TABLE IF NOT EXISTS database_management.datasource_logs (
    id SERIAL PRIMARY KEY,
    datasource_id INTEGER NOT NULL,
    datasource_name VARCHAR(255) NOT NULL,
    operation VARCHAR(50) NOT NULL, -- 'create', 'update', 'delete', 'test_connection'
    operation_details JSONB,
    success BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create table for connection test history
CREATE TABLE IF NOT EXISTS database_management.connection_tests (
    id SERIAL PRIMARY KEY,
    datasource_id INTEGER NOT NULL,
    datasource_name VARCHAR(255) NOT NULL,
    database_type VARCHAR(20) NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    database_name VARCHAR(255) NOT NULL,
    success BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    response_time_ms INTEGER,
    tested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create schema for text2sql module
CREATE SCHEMA IF NOT EXISTS text2sql;

-- Create table for storing SQL queries and their embeddings
CREATE TABLE IF NOT EXISTS text2sql.sql_queries (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    sql_text TEXT NOT NULL,
    database_type VARCHAR(50) NOT NULL,
    table_names TEXT[], -- Array of table names used in the query
    embedding vector(1024), -- Using 1024 dimensions for BGE-M3 model
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create table for storing training data
CREATE TABLE IF NOT EXISTS text2sql.training_data (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    sql_query TEXT NOT NULL,
    database_schema JSONB, -- Store table schema information
    database_type VARCHAR(50) NOT NULL,
    datasource_id INTEGER, -- Reference to database datasource
    is_validated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create table for query history
CREATE TABLE IF NOT EXISTS text2sql.query_history (
    id SERIAL PRIMARY KEY,
    user_question TEXT NOT NULL,
    generated_sql TEXT NOT NULL,
    execution_result JSONB, -- Store query results or error messages
    execution_time_ms INTEGER,
    datasource_id INTEGER,
    is_successful BOOLEAN DEFAULT FALSE,
    feedback_rating INTEGER CHECK (feedback_rating >= 1 AND feedback_rating <= 5),
    feedback_comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create schema for API tools module
CREATE SCHEMA IF NOT EXISTS api_tools;

-- Create table for API definitions (严格按照ti-flow结构)
CREATE TABLE IF NOT EXISTS api_tools.api_definitions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(500) NOT NULL,
    category VARCHAR(50) NOT NULL DEFAULT 'general',
    method INTEGER NOT NULL, -- HTTPMethod enum (0=GET, 1=POST, 2=PUT, 3=DELETE, 4=PATCH)
    url TEXT NOT NULL,
    headers JSONB NOT NULL DEFAULT '{}',
    timeout_seconds INTEGER NOT NULL DEFAULT 30 CHECK (timeout_seconds >= 5 AND timeout_seconds <= 300),
    auth_config JSONB NOT NULL,
    parameters JSONB NOT NULL DEFAULT '[]',
    response_schema JSONB,
    response_config JSONB NOT NULL DEFAULT '{}',
    rate_limit JSONB NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for API definitions
CREATE INDEX IF NOT EXISTS ix_api_definitions_name ON api_tools.api_definitions(name);
CREATE INDEX IF NOT EXISTS ix_api_definitions_category ON api_tools.api_definitions(category);
CREATE INDEX IF NOT EXISTS ix_api_definitions_enabled ON api_tools.api_definitions(enabled);
CREATE INDEX IF NOT EXISTS ix_api_definitions_created_at ON api_tools.api_definitions(created_at);

-- Create table for API call logs (严格按照ti-flow结构)
CREATE TABLE IF NOT EXISTS api_tools.api_call_logs (
    id SERIAL PRIMARY KEY,
    api_definition_id INTEGER NOT NULL REFERENCES api_tools.api_definitions(id) ON DELETE CASCADE,
    session_id VARCHAR(100),
    request_data JSONB,
    response_data JSONB,
    status_code INTEGER,
    execution_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for API call logs
CREATE INDEX IF NOT EXISTS ix_api_call_logs_api_definition_id ON api_tools.api_call_logs(api_definition_id);
CREATE INDEX IF NOT EXISTS ix_api_call_logs_session_id ON api_tools.api_call_logs(session_id);
CREATE INDEX IF NOT EXISTS ix_api_call_logs_created_at ON api_tools.api_call_logs(created_at);

-- Create schema for intent recognition module
CREATE SCHEMA IF NOT EXISTS intent_recognition;

-- =====================================================
-- 资源发现模块数据库表 (基于 Ti-Flow 意图识别模块设计)
-- =====================================================

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

-- Create table for intent matching history
CREATE TABLE IF NOT EXISTS intent_recognition.intent_matches (
    id SERIAL PRIMARY KEY,
    user_intent TEXT NOT NULL,
    matched_resources JSONB, -- Array of matched resource IDs and scores
    selected_resource_id INTEGER REFERENCES intent_recognition.resource_nodes(id),
    confidence_score FLOAT,
    is_successful BOOLEAN DEFAULT FALSE,
    feedback_rating INTEGER CHECK (feedback_rating >= 1 AND feedback_rating <= 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create schema for chat management
CREATE SCHEMA IF NOT EXISTS chat;

-- Create table for chat conversations
CREATE TABLE IF NOT EXISTS chat.conversations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255), -- Session identifier instead of user_id
    title VARCHAR(255),
    description TEXT,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create table for chat messages
CREATE TABLE IF NOT EXISTS chat.messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES chat.conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    content_type VARCHAR(20) DEFAULT 'text' CHECK (content_type IN ('text', 'markdown', 'json')),
    metadata JSONB DEFAULT '{}', -- Store additional message metadata (model used, tokens, etc.)
    parent_message_id INTEGER REFERENCES chat.messages(id),
    is_edited BOOLEAN DEFAULT FALSE,
    edit_history JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create schema for user management (simple user system)
CREATE SCHEMA IF NOT EXISTS users;

-- Create table for users (simple user management)
CREATE TABLE IF NOT EXISTS users.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE,
    display_name VARCHAR(255),
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create schema for chat management
CREATE SCHEMA IF NOT EXISTS chat;

-- Create table for chat conversations
CREATE TABLE IF NOT EXISTS chat.conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users.users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    description TEXT,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create table for chat messages
CREATE TABLE IF NOT EXISTS chat.messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES chat.conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    content_type VARCHAR(20) DEFAULT 'text' CHECK (content_type IN ('text', 'markdown', 'json')),
    metadata JSONB DEFAULT '{}', -- Store additional message metadata (model used, tokens, etc.)
    parent_message_id INTEGER REFERENCES chat.messages(id),
    is_edited BOOLEAN DEFAULT FALSE,
    edit_history JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create schema for system management
CREATE SCHEMA IF NOT EXISTS system;

-- Create table for system configuration
CREATE TABLE IF NOT EXISTS system.configurations (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL UNIQUE,
    config_value JSONB NOT NULL,
    description TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create table for system logs
CREATE TABLE IF NOT EXISTS system.logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL, -- 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    module VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    details JSONB,
    user_id VARCHAR(255), -- Optional user identifier
    session_id VARCHAR(255), -- Optional session identifier
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create table for background tasks (Celery task tracking)
CREATE TABLE IF NOT EXISTS system.background_tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL UNIQUE,
    task_name VARCHAR(255) NOT NULL,
    task_args JSONB,
    task_kwargs JSONB,
    status VARCHAR(50) DEFAULT 'PENDING', -- 'PENDING', 'STARTED', 'SUCCESS', 'FAILURE', 'RETRY', 'REVOKED'
    result JSONB,
    error_message TEXT,
    traceback TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sql_queries_embedding ON text2sql.sql_queries USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_sql_queries_database_type ON text2sql.sql_queries(database_type);
CREATE INDEX IF NOT EXISTS idx_sql_queries_created_at ON text2sql.sql_queries(created_at);

CREATE INDEX IF NOT EXISTS idx_training_data_database_type ON text2sql.training_data(database_type);
CREATE INDEX IF NOT EXISTS idx_training_data_datasource_id ON text2sql.training_data(datasource_id);
CREATE INDEX IF NOT EXISTS idx_training_data_is_validated ON text2sql.training_data(is_validated);

CREATE INDEX IF NOT EXISTS idx_query_history_datasource_id ON text2sql.query_history(datasource_id);
CREATE INDEX IF NOT EXISTS idx_query_history_created_at ON text2sql.query_history(created_at);
CREATE INDEX IF NOT EXISTS idx_query_history_is_successful ON text2sql.query_history(is_successful);

CREATE INDEX IF NOT EXISTS idx_call_logs_api_definition_id ON api_tools.call_logs(api_definition_id);
CREATE INDEX IF NOT EXISTS idx_call_logs_created_at ON api_tools.call_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_call_logs_is_successful ON api_tools.call_logs(is_successful);

CREATE INDEX IF NOT EXISTS idx_resource_nodes_embedding ON intent_recognition.resource_nodes USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_resource_nodes_resource_type ON intent_recognition.resource_nodes(resource_type);
CREATE INDEX IF NOT EXISTS idx_resource_nodes_usage_count ON intent_recognition.resource_nodes(usage_count);

CREATE INDEX IF NOT EXISTS idx_intent_matches_created_at ON intent_recognition.intent_matches(created_at);
CREATE INDEX IF NOT EXISTS idx_intent_matches_confidence_score ON intent_recognition.intent_matches(confidence_score);

-- Database management indexes
CREATE INDEX IF NOT EXISTS idx_datasource_logs_datasource_id ON database_management.datasource_logs(datasource_id);
CREATE INDEX IF NOT EXISTS idx_datasource_logs_operation ON database_management.datasource_logs(operation);
CREATE INDEX IF NOT EXISTS idx_datasource_logs_created_at ON database_management.datasource_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_connection_tests_datasource_id ON database_management.connection_tests(datasource_id);
CREATE INDEX IF NOT EXISTS idx_connection_tests_success ON database_management.connection_tests(success);
CREATE INDEX IF NOT EXISTS idx_connection_tests_tested_at ON database_management.connection_tests(tested_at);

-- API tools indexes
CREATE INDEX IF NOT EXISTS idx_api_definitions_name ON api_tools.api_definitions(name);
CREATE INDEX IF NOT EXISTS idx_api_definitions_category ON api_tools.api_definitions(category);
CREATE INDEX IF NOT EXISTS idx_api_definitions_enabled ON api_tools.api_definitions(enabled);

-- System indexes
CREATE INDEX IF NOT EXISTS idx_configurations_config_key ON system.configurations(config_key);
CREATE INDEX IF NOT EXISTS idx_logs_level ON system.logs(level);
CREATE INDEX IF NOT EXISTS idx_logs_module ON system.logs(module);
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON system.logs(created_at);
CREATE INDEX IF NOT EXISTS idx_background_tasks_task_id ON system.background_tasks(task_id);
CREATE INDEX IF NOT EXISTS idx_background_tasks_status ON system.background_tasks(status);
CREATE INDEX IF NOT EXISTS idx_background_tasks_created_at ON system.background_tasks(created_at);

-- User management indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users.users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users.users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users.users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users.users(created_at);

-- Chat management indexes
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON chat.conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON chat.conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_conversations_is_archived ON chat.conversations(is_archived);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON chat.messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_role ON chat.messages(role);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON chat.messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_parent_message_id ON chat.messages(parent_message_id);

-- User management indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users.users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users.users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users.users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users.users(created_at);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON users.sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_session_token ON users.sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON users.sessions(expires_at);

CREATE INDEX IF NOT EXISTS idx_preferences_user_id ON users.preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_preferences_key ON users.preferences(preference_key);

-- Chat management indexes
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON chat.conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON chat.conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_conversations_is_archived ON chat.conversations(is_archived);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON chat.messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON chat.messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_role ON chat.messages(role);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON chat.messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_parent_message_id ON chat.messages(parent_message_id);

CREATE INDEX IF NOT EXISTS idx_message_attachments_message_id ON chat.message_attachments(message_id);
CREATE INDEX IF NOT EXISTS idx_message_reactions_message_id ON chat.message_reactions(message_id);
CREATE INDEX IF NOT EXISTS idx_message_reactions_user_id ON chat.message_reactions(user_id);

CREATE INDEX IF NOT EXISTS idx_templates_user_id ON chat.templates(user_id);
CREATE INDEX IF NOT EXISTS idx_templates_category ON chat.templates(category);
CREATE INDEX IF NOT EXISTS idx_templates_is_public ON chat.templates(is_public);

CREATE INDEX IF NOT EXISTS idx_conversation_shares_conversation_id ON chat.conversation_shares(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversation_shares_share_token ON chat.conversation_shares(share_token);
CREATE INDEX IF NOT EXISTS idx_conversation_shares_expires_at ON chat.conversation_shares(expires_at);

CREATE INDEX IF NOT EXISTS idx_conversation_tags_conversation_id ON chat.conversation_tags(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversation_tags_tag_name ON chat.conversation_tags(tag_name);

-- Create functions for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_sql_queries_updated_at BEFORE UPDATE ON text2sql.sql_queries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_training_data_updated_at BEFORE UPDATE ON text2sql.training_data FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_resource_nodes_updated_at BEFORE UPDATE ON intent_recognition.resource_nodes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_api_definitions_updated_at BEFORE UPDATE ON api_tools.api_definitions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_configurations_updated_at BEFORE UPDATE ON system.configurations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- User and chat management triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users.users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON chat.conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_messages_updated_at BEFORE UPDATE ON chat.messages FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- User management triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users.users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_preferences_updated_at BEFORE UPDATE ON users.preferences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Chat management triggers
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON chat.conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_messages_updated_at BEFORE UPDATE ON chat.messages FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON chat.templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data for testing

-- Insert sample users
INSERT INTO users.users (username, email, display_name) VALUES
('admin', 'admin@example.com', 'Administrator'),
('demo_user', 'demo@example.com', 'Demo User'),
('test_user', 'test@example.com', 'Test User')
ON CONFLICT (username) DO NOTHING;

-- Insert sample training data
INSERT INTO text2sql.training_data (question, sql_query, database_type, is_validated) VALUES
('Show me all users', 'SELECT * FROM users;', 'POSTGRESQL', true),
('Count total orders', 'SELECT COUNT(*) FROM orders;', 'POSTGRESQL', true),
('Find users created today', 'SELECT * FROM users WHERE DATE(created_at) = CURRENT_DATE;', 'POSTGRESQL', true),
('Get top 10 products by sales', 'SELECT product_name, SUM(quantity) as total_sales FROM order_items oi JOIN products p ON oi.product_id = p.id GROUP BY product_name ORDER BY total_sales DESC LIMIT 10;', 'POSTGRESQL', true)
ON CONFLICT DO NOTHING;

-- Insert sample API definitions for testing
INSERT INTO api_tools.api_definitions (name, description, category, method, url, headers, parameters) VALUES
('JSONPlaceholder Posts', 'Get posts from JSONPlaceholder API', 'testing', 'GET', 'https://jsonplaceholder.typicode.com/posts', '{"Content-Type": "application/json"}', '[]'),
('JSONPlaceholder Users', 'Get users from JSONPlaceholder API', 'testing', 'GET', 'https://jsonplaceholder.typicode.com/users', '{"Content-Type": "application/json"}', '[]'),
('HTTPBin GET', 'Test GET request with HTTPBin', 'testing', 'GET', 'https://httpbin.org/get', '{}', '[{"name": "param1", "type": "string", "required": false, "description": "Test parameter"}]')
ON CONFLICT (name) DO NOTHING;

-- Insert sample system configurations
INSERT INTO system.configurations (config_key, config_value, description) VALUES
('text2sql.enabled', 'true', 'Enable Text2SQL functionality'),
('text2sql.max_sql_examples', '10', 'Maximum number of SQL examples to use for training'),
('text2sql.similarity_threshold', '0.7', 'Minimum similarity threshold for vector search'),
('api_tools.enabled', 'true', 'Enable API tools functionality'),
('api_tools.default_timeout', '30', 'Default timeout for API calls in seconds'),
('intent_recognition.enabled', 'true', 'Enable intent recognition functionality'),
('intent_recognition.confidence_threshold', '0.8', 'Minimum confidence threshold for intent matching')
ON CONFLICT (config_key) DO NOTHING;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA database_management TO PUBLIC;
GRANT USAGE ON SCHEMA text2sql TO PUBLIC;
GRANT USAGE ON SCHEMA api_tools TO PUBLIC;
GRANT USAGE ON SCHEMA intent_recognition TO PUBLIC;
GRANT USAGE ON SCHEMA users TO PUBLIC;
GRANT USAGE ON SCHEMA chat TO PUBLIC;
GRANT USAGE ON SCHEMA system TO PUBLIC;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA database_management TO aolei;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA text2sql TO aolei;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA api_tools TO aolei;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA intent_recognition TO aolei;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA users TO aolei;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA chat TO aolei;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA system TO aolei;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA database_management TO aolei;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA text2sql TO aolei;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA api_tools TO aolei;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA intent_recognition TO aolei;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA users TO aolei;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA chat TO aolei;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA system TO aolei;

-- Print completion message
DO $$
BEGIN
    RAISE NOTICE 'PostgreSQL database initialized successfully with pgvector extension and deer-flow schemas!';
    RAISE NOTICE 'Created schemas: database_management, text2sql, api_tools, intent_recognition, users, chat, system';
    RAISE NOTICE 'Created tables for all deer-flow migration modules:';
    RAISE NOTICE '  - Database Management: datasource_logs, connection_tests';
    RAISE NOTICE '  - Text2SQL: sql_queries, training_data, query_history';
    RAISE NOTICE '  - API Tools: api_definitions, call_logs';
    RAISE NOTICE '  - Intent Recognition: resource_nodes, intent_matches';
    RAISE NOTICE '  - Users: users (simple user management)';
    RAISE NOTICE '  - Chat: conversations, messages (chat history)';
    RAISE NOTICE '  - System: configurations, logs, background_tasks';
    RAISE NOTICE 'Database is ready for deer-flow migration modules!';
END $$;
