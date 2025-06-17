-- Text2SQL Module Database Schema for deer-flow
-- Migrated from ti-flow with adaptations for deer-flow architecture
-- Uses pgvector for vector storage and PostgreSQL features

-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema for text2sql module
CREATE SCHEMA IF NOT EXISTS text2sql;

-- Create function to update updated_at column
CREATE OR REPLACE FUNCTION text2sql.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 1. SQL Query History Table
-- Stores all generated SQL queries and their execution results
CREATE TABLE IF NOT EXISTS text2sql.query_history (
    id SERIAL PRIMARY KEY,
    user_question TEXT NOT NULL,
    generated_sql TEXT NOT NULL,
    datasource_id INTEGER NOT NULL,
    
    -- Execution details
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING' 
        CHECK (status IN ('PENDING', 'SUCCESS', 'FAILED', 'TIMEOUT')),
    execution_time_ms INTEGER,
    result_rows INTEGER,
    result_data JSONB, -- Store query results (limited for performance)
    error_message TEXT,
    
    -- AI/ML details
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    model_used VARCHAR(100),
    explanation TEXT,
    similar_examples JSONB, -- Store similar training examples used
    
    -- User feedback
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    user_feedback TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint (will be added after database_management schema exists)
    CONSTRAINT fk_query_history_datasource 
        FOREIGN KEY (datasource_id) 
        REFERENCES database_management.database_datasources(id) 
        ON DELETE CASCADE
);

-- 2. Training Data Table
-- Stores training examples for improving SQL generation
CREATE TABLE IF NOT EXISTS text2sql.training_data (
    id SERIAL PRIMARY KEY,
    datasource_id INTEGER NOT NULL,
    
    -- Training content
    content_type VARCHAR(50) NOT NULL DEFAULT 'SQL'
        CHECK (content_type IN ('DDL', 'DOCUMENTATION', 'SQL', 'SCHEMA')),
    question TEXT, -- Natural language question (for SQL type)
    sql_query TEXT, -- Corresponding SQL query (for SQL type)
    content TEXT NOT NULL, -- Raw content for embedding
    
    -- Schema information
    table_names TEXT[], -- Tables involved in this training data
    database_schema JSONB, -- Relevant schema information
    
    -- Vector embedding
    embedding vector(1024), -- Using 1024 dimensions for BGE-M3 model
    embedding_model VARCHAR(100), -- Model used for embedding
    
    -- Metadata
    metadata JSONB, -- Additional metadata
    content_hash VARCHAR(64) NOT NULL, -- Hash for deduplication
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_validated BOOLEAN NOT NULL DEFAULT FALSE,
    validation_score FLOAT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_training_data_datasource 
        FOREIGN KEY (datasource_id) 
        REFERENCES database_management.database_datasources(id) 
        ON DELETE CASCADE,
        
    -- Unique constraint for content deduplication
    CONSTRAINT unique_training_content 
        UNIQUE (datasource_id, content_hash)
);

-- 3. SQL Queries Cache Table
-- Stores frequently used queries and their embeddings for fast retrieval
CREATE TABLE IF NOT EXISTS text2sql.sql_queries (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL, -- Natural language query
    sql_text TEXT NOT NULL, -- Generated SQL
    datasource_id INTEGER NOT NULL,
    
    -- Query metadata
    table_names TEXT[], -- Tables used in the query
    query_complexity VARCHAR(20) DEFAULT 'SIMPLE'
        CHECK (query_complexity IN ('SIMPLE', 'MEDIUM', 'COMPLEX')),
    
    -- Vector embedding for similarity search
    embedding vector(1024),
    embedding_model VARCHAR(100),
    
    -- Usage statistics
    usage_count INTEGER NOT NULL DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    average_execution_time_ms INTEGER,
    success_rate FLOAT DEFAULT 1.0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_sql_queries_datasource 
        FOREIGN KEY (datasource_id) 
        REFERENCES database_management.database_datasources(id) 
        ON DELETE CASCADE
);

-- 4. Model Training Sessions Table
-- Tracks training sessions and model improvements
CREATE TABLE IF NOT EXISTS text2sql.training_sessions (
    id SERIAL PRIMARY KEY,
    datasource_id INTEGER NOT NULL,
    
    -- Training details
    session_name VARCHAR(255),
    training_data_count INTEGER NOT NULL DEFAULT 0,
    model_version VARCHAR(50),
    training_parameters JSONB,
    
    -- Results
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED')),
    accuracy_score FLOAT,
    validation_score FLOAT,
    training_time_seconds INTEGER,
    
    -- Metadata
    notes TEXT,
    error_message TEXT,
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Foreign key constraint
    CONSTRAINT fk_training_sessions_datasource 
        FOREIGN KEY (datasource_id) 
        REFERENCES database_management.database_datasources(id) 
        ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_query_history_datasource_id ON text2sql.query_history(datasource_id);
CREATE INDEX IF NOT EXISTS idx_query_history_created_at ON text2sql.query_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_query_history_status ON text2sql.query_history(status);

CREATE INDEX IF NOT EXISTS idx_training_data_datasource_id ON text2sql.training_data(datasource_id);
CREATE INDEX IF NOT EXISTS idx_training_data_content_type ON text2sql.training_data(content_type);
CREATE INDEX IF NOT EXISTS idx_training_data_is_active ON text2sql.training_data(is_active);
CREATE INDEX IF NOT EXISTS idx_training_data_content_hash ON text2sql.training_data(content_hash);

CREATE INDEX IF NOT EXISTS idx_sql_queries_datasource_id ON text2sql.sql_queries(datasource_id);
CREATE INDEX IF NOT EXISTS idx_sql_queries_usage_count ON text2sql.sql_queries(usage_count DESC);
CREATE INDEX IF NOT EXISTS idx_sql_queries_last_used ON text2sql.sql_queries(last_used_at DESC);

CREATE INDEX IF NOT EXISTS idx_training_sessions_datasource_id ON text2sql.training_sessions(datasource_id);
CREATE INDEX IF NOT EXISTS idx_training_sessions_status ON text2sql.training_sessions(status);

-- Create vector indexes for similarity search (using HNSW)
CREATE INDEX IF NOT EXISTS idx_training_data_embedding ON text2sql.training_data
    USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_sql_queries_embedding ON text2sql.sql_queries
    USING hnsw (embedding vector_cosine_ops);

-- Create triggers to automatically update updated_at
DROP TRIGGER IF EXISTS update_training_data_updated_at ON text2sql.training_data;
CREATE TRIGGER update_training_data_updated_at
    BEFORE UPDATE ON text2sql.training_data
    FOR EACH ROW EXECUTE FUNCTION text2sql.update_updated_at_column();

DROP TRIGGER IF EXISTS update_sql_queries_updated_at ON text2sql.sql_queries;
CREATE TRIGGER update_sql_queries_updated_at
    BEFORE UPDATE ON text2sql.sql_queries
    FOR EACH ROW EXECUTE FUNCTION text2sql.update_updated_at_column();

-- 4. Vanna Embeddings Table
-- Stores vector embeddings for training data using Vanna AI - matches ti-flow design
CREATE TABLE IF NOT EXISTS text2sql.vanna_embeddings (
    id SERIAL PRIMARY KEY,
    datasource_id INTEGER NOT NULL,

    -- Content information
    content_type VARCHAR(50) NOT NULL DEFAULT 'SQL'
        CHECK (content_type IN ('DDL', 'DOCUMENTATION', 'SQL')),
    content TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL,

    -- Database information
    database_name VARCHAR(256),

    -- Vector embedding (using 1024 dimensions for compatibility)
    embedding_vector vector(1024),
    embedding_dimension INTEGER,

    -- Metadata
    meta_data JSONB,

    -- DDL related fields
    table_name VARCHAR(256),
    column_name VARCHAR(256),

    -- SQL related fields
    question TEXT,
    sql_query TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraint
    CONSTRAINT fk_vanna_embeddings_datasource
        FOREIGN KEY (datasource_id)
        REFERENCES database_management.database_datasources(id)
        ON DELETE CASCADE,

    -- Unique constraint for content deduplication
    CONSTRAINT unique_vanna_content
        UNIQUE (datasource_id, content_hash)
);

-- Create indexes for vanna_embeddings
CREATE INDEX IF NOT EXISTS idx_vanna_embeddings_datasource_id ON text2sql.vanna_embeddings(datasource_id);
CREATE INDEX IF NOT EXISTS idx_vanna_embeddings_content_type ON text2sql.vanna_embeddings(content_type);
CREATE INDEX IF NOT EXISTS idx_vanna_embeddings_content_hash ON text2sql.vanna_embeddings(content_hash);
CREATE INDEX IF NOT EXISTS idx_vanna_embeddings_table_name ON text2sql.vanna_embeddings(table_name);
CREATE INDEX IF NOT EXISTS idx_vanna_embeddings_database_name ON text2sql.vanna_embeddings(database_name);

-- Create vector index for similarity search (using HNSW)
CREATE INDEX IF NOT EXISTS idx_vanna_embeddings_embedding_vector ON text2sql.vanna_embeddings
    USING hnsw (embedding_vector vector_cosine_ops);

-- Create trigger for updated_at
CREATE TRIGGER update_vanna_embeddings_updated_at
    BEFORE UPDATE ON text2sql.vanna_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION text2sql.update_updated_at_column();

-- Add comments for documentation
COMMENT ON SCHEMA text2sql IS 'Text2SQL module for natural language to SQL conversion';
COMMENT ON TABLE text2sql.query_history IS 'Stores all SQL queries generated from natural language';
COMMENT ON TABLE text2sql.training_data IS 'Training examples for improving SQL generation accuracy';
COMMENT ON TABLE text2sql.sql_queries IS 'Cache of frequently used queries with embeddings';
COMMENT ON TABLE text2sql.training_sessions IS 'Tracks model training sessions and results';
COMMENT ON TABLE text2sql.vanna_embeddings IS 'Vector embeddings for training data using Vanna AI - matches ti-flow design';
