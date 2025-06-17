-- =====================================================
-- 修复向量维度问题
-- 将向量维度从1536改为1024以匹配真实嵌入服务
-- =====================================================

-- 1. 删除现有的向量数据（因为维度不匹配）
DELETE FROM resource_discovery.resource_vectors;

-- 2. 删除现有的向量索引
DROP INDEX IF EXISTS resource_discovery.idx_resource_vectors_embedding;

-- 3. 修改向量列的维度
ALTER TABLE resource_discovery.resource_vectors 
ALTER COLUMN embedding TYPE vector(1024);

-- 4. 更新默认维度
ALTER TABLE resource_discovery.resource_vectors 
ALTER COLUMN embedding_dimension SET DEFAULT 1024;

-- 5. 重新创建向量索引
CREATE INDEX idx_resource_vectors_embedding ON resource_discovery.resource_vectors 
USING hnsw (embedding vector_cosine_ops);

-- 6. 更新现有记录的维度（如果有的话）
UPDATE resource_discovery.resource_vectors 
SET embedding_dimension = 1024 
WHERE embedding_dimension = 1536;

-- 7. 同时修复 source_id 字段的范围问题
-- 将 source_id 改为 BIGINT 以支持更大的哈希值
ALTER TABLE resource_discovery.resource_registry 
ALTER COLUMN source_id TYPE BIGINT;

-- 8. 显示修改结果
SELECT 'Vector dimension updated to 1024' as info;

-- =====================================================
-- 向量维度修复完成
-- =====================================================
