-- Drop training_data table and related objects
-- This table is no longer needed as we store training data directly in vanna_embeddings

-- Drop triggers first
DROP TRIGGER IF EXISTS update_training_data_updated_at ON text2sql.training_data;

-- Drop indexes
DROP INDEX IF EXISTS text2sql.idx_training_data_datasource_id;
DROP INDEX IF EXISTS text2sql.idx_training_data_content_type;
DROP INDEX IF EXISTS text2sql.idx_training_data_is_active;
DROP INDEX IF EXISTS text2sql.idx_training_data_content_hash;
DROP INDEX IF EXISTS text2sql.idx_training_data_embedding;

-- Drop the table
DROP TABLE IF EXISTS text2sql.training_data;

-- Add comment
COMMENT ON SCHEMA text2sql IS 'Text2SQL module - training_data table removed, using vanna_embeddings instead';
