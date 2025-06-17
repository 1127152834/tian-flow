-- =====================================================
-- 实时更新触发器
-- 为资源发现模块创建数据库触发器，实现实时更新
-- =====================================================

-- 1. 创建通知函数
CREATE OR REPLACE FUNCTION resource_discovery.notify_resource_change()
RETURNS TRIGGER AS $$
BEGIN
    -- 发送通知到资源发现模块
    PERFORM pg_notify(
        'resource_change',
        json_build_object(
            'operation', TG_OP,
            'table_name', TG_TABLE_NAME,
            'schema_name', TG_TABLE_SCHEMA,
            'record_id', CASE 
                WHEN TG_OP = 'DELETE' THEN OLD.id
                ELSE NEW.id
            END,
            'timestamp', EXTRACT(EPOCH FROM NOW())
        )::text
    );
    
    -- 返回适当的记录
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 2. 为数据库数据源表创建触发器
DROP TRIGGER IF EXISTS trigger_database_datasource_change ON database_management.database_datasources;
CREATE TRIGGER trigger_database_datasource_change
    AFTER INSERT OR UPDATE OR DELETE
    ON database_management.database_datasources
    FOR EACH ROW
    EXECUTE FUNCTION resource_discovery.notify_resource_change();

-- 3. 为 API 定义表创建触发器
DROP TRIGGER IF EXISTS trigger_api_definition_change ON api_tools.api_definitions;
CREATE TRIGGER trigger_api_definition_change
    AFTER INSERT OR UPDATE OR DELETE
    ON api_tools.api_definitions
    FOR EACH ROW
    EXECUTE FUNCTION resource_discovery.notify_resource_change();

-- 4. 为 vanna_embeddings 表创建触发器
DROP TRIGGER IF EXISTS trigger_vanna_embedding_change ON text2sql.vanna_embeddings;
CREATE TRIGGER trigger_vanna_embedding_change
    AFTER INSERT OR UPDATE OR DELETE
    ON text2sql.vanna_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION resource_discovery.notify_resource_change();

-- 5. 创建资源发现配置表
CREATE TABLE IF NOT EXISTS resource_discovery.discovery_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value JSONB NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 插入默认配置
INSERT INTO resource_discovery.discovery_config (config_key, config_value, description) VALUES
('auto_sync_enabled', 'true', '是否启用自动同步'),
('sync_interval_minutes', '30', '自动同步间隔（分钟）'),
('batch_size', '50', '批处理大小'),
('similarity_threshold', '0.3', '相似度阈值'),
('confidence_weights', '{"similarity": 0.6, "usage_history": 0.2, "performance": 0.1, "context": 0.1}', '置信度权重配置'),
('embedding_model', '"default"', '嵌入模型名称'),
('max_concurrent_tasks', '5', '最大并发任务数'),
('request_timeout_seconds', '30', '请求超时时间（秒）')
ON CONFLICT (config_key) DO NOTHING;

-- 6. 创建性能监控表
CREATE TABLE IF NOT EXISTS resource_discovery.performance_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_unit VARCHAR(20),
    resource_id VARCHAR(255),
    operation_type VARCHAR(50),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建性能监控表的索引
CREATE INDEX IF NOT EXISTS idx_performance_metrics_name_time ON resource_discovery.performance_metrics (metric_name, recorded_at);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_resource ON resource_discovery.performance_metrics (resource_id);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_operation ON resource_discovery.performance_metrics (operation_type);

-- 7. 创建查询缓存表
CREATE TABLE IF NOT EXISTS resource_discovery.query_cache (
    id BIGSERIAL PRIMARY KEY,
    query_hash VARCHAR(64) NOT NULL UNIQUE,
    user_query TEXT NOT NULL,
    cached_results JSONB NOT NULL,
    cache_metadata JSONB,
    hit_count INTEGER DEFAULT 0,
    last_hit_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建查询缓存表的索引
CREATE INDEX IF NOT EXISTS idx_query_cache_hash ON resource_discovery.query_cache (query_hash);
CREATE INDEX IF NOT EXISTS idx_query_cache_expires ON resource_discovery.query_cache (expires_at);
CREATE INDEX IF NOT EXISTS idx_query_cache_hit_count ON resource_discovery.query_cache (hit_count DESC);

-- 8. 创建资源健康检查表
CREATE TABLE IF NOT EXISTS resource_discovery.resource_health (
    id BIGSERIAL PRIMARY KEY,
    resource_id VARCHAR(255) NOT NULL,
    health_status VARCHAR(20) NOT NULL, -- 'healthy', 'warning', 'error', 'unknown'
    health_score FLOAT, -- 0.0 - 1.0
    last_check_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    check_details JSONB,

    -- 外键约束
    FOREIGN KEY (resource_id) REFERENCES resource_discovery.resource_registry(resource_id) ON DELETE CASCADE,

    -- 唯一约束
    UNIQUE (resource_id)
);

-- 创建资源健康检查表的索引
CREATE INDEX IF NOT EXISTS idx_resource_health_status ON resource_discovery.resource_health (health_status);
CREATE INDEX IF NOT EXISTS idx_resource_health_score ON resource_discovery.resource_health (health_score DESC);
CREATE INDEX IF NOT EXISTS idx_resource_health_check_time ON resource_discovery.resource_health (last_check_at);

-- 9. 创建用户偏好表
CREATE TABLE IF NOT EXISTS resource_discovery.user_preferences (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(128) NOT NULL,
    resource_type VARCHAR(50),
    preference_score FLOAT DEFAULT 1.0,
    usage_frequency INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    preference_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 唯一约束
    UNIQUE (user_id, resource_type)
);

-- 创建用户偏好表的索引
CREATE INDEX IF NOT EXISTS idx_user_preferences_user ON resource_discovery.user_preferences (user_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_type ON resource_discovery.user_preferences (resource_type);
CREATE INDEX IF NOT EXISTS idx_user_preferences_score ON resource_discovery.user_preferences (preference_score DESC);

-- 10. 创建自动清理函数
CREATE OR REPLACE FUNCTION resource_discovery.cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- 清理过期的查询缓存
    DELETE FROM resource_discovery.query_cache 
    WHERE expires_at < NOW();
    
    -- 清理旧的性能指标（保留30天）
    DELETE FROM resource_discovery.performance_metrics 
    WHERE recorded_at < NOW() - INTERVAL '30 days';
    
    -- 清理旧的匹配历史（保留90天）
    DELETE FROM resource_discovery.resource_match_history 
    WHERE created_at < NOW() - INTERVAL '90 days';
    
    -- 清理旧的系统状态记录（保留30天）
    DELETE FROM resource_discovery.system_status 
    WHERE created_at < NOW() - INTERVAL '30 days'
    AND status IN ('completed', 'failed');
    
    RAISE NOTICE 'Resource discovery cleanup completed';
END;
$$ LANGUAGE plpgsql;

-- 11. 创建定时清理任务（需要 pg_cron 扩展）
-- 注意：这需要 pg_cron 扩展，如果没有安装可以注释掉
-- SELECT cron.schedule('resource-discovery-cleanup', '0 2 * * *', 'SELECT resource_discovery.cleanup_old_data();');

-- 12. 创建资源发现统计视图
CREATE OR REPLACE VIEW resource_discovery.resource_statistics AS
SELECT 
    resource_type,
    COUNT(*) as total_count,
    COUNT(*) FILTER (WHERE is_active = true) as active_count,
    COUNT(*) FILTER (WHERE vectorization_status = 'completed') as vectorized_count,
    AVG(usage_count) as avg_usage_count,
    AVG(success_rate) as avg_success_rate,
    AVG(avg_response_time) as avg_response_time,
    MIN(created_at) as first_created,
    MAX(updated_at) as last_updated
FROM resource_discovery.resource_registry
GROUP BY resource_type;

-- 13. 创建热门查询视图
CREATE OR REPLACE VIEW resource_discovery.popular_queries AS
SELECT 
    user_query,
    COUNT(*) as query_count,
    AVG(response_time) as avg_response_time,
    COUNT(*) FILTER (WHERE user_feedback = 'positive') as positive_feedback,
    COUNT(*) FILTER (WHERE user_feedback = 'negative') as negative_feedback,
    MAX(created_at) as last_queried
FROM resource_discovery.resource_match_history
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY user_query
ORDER BY query_count DESC
LIMIT 100;

-- 14. 创建资源健康概览视图
CREATE OR REPLACE VIEW resource_discovery.health_overview AS
SELECT 
    rr.resource_type,
    COUNT(*) as total_resources,
    COUNT(*) FILTER (WHERE rh.health_status = 'healthy') as healthy_count,
    COUNT(*) FILTER (WHERE rh.health_status = 'warning') as warning_count,
    COUNT(*) FILTER (WHERE rh.health_status = 'error') as error_count,
    COUNT(*) FILTER (WHERE rh.health_status IS NULL) as unchecked_count,
    AVG(rh.health_score) as avg_health_score
FROM resource_discovery.resource_registry rr
LEFT JOIN resource_discovery.resource_health rh ON rr.resource_id = rh.resource_id
WHERE rr.is_active = true
GROUP BY rr.resource_type;

-- 15. 添加更新时间戳触发器
CREATE TRIGGER update_discovery_config_updated_at 
    BEFORE UPDATE ON resource_discovery.discovery_config 
    FOR EACH ROW EXECUTE FUNCTION resource_discovery.update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at 
    BEFORE UPDATE ON resource_discovery.user_preferences 
    FOR EACH ROW EXECUTE FUNCTION resource_discovery.update_updated_at_column();

-- =====================================================
-- 实时更新触发器创建完成
-- =====================================================

-- 显示创建的对象
SELECT 'Triggers created:' as info;
SELECT
    trigger_schema,
    event_object_table,
    trigger_name
FROM information_schema.triggers
WHERE trigger_schema IN ('database_management', 'api_tools', 'text2sql')
AND trigger_name LIKE '%resource%'
ORDER BY trigger_schema, event_object_table;

SELECT 'Tables created:' as info;
SELECT
    schemaname,
    tablename
FROM pg_tables
WHERE schemaname = 'resource_discovery'
ORDER BY tablename;
