-- Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
-- SPDX-License-Identifier: MIT

-- Knowledge Graph Schema for DeerFlow
-- Provides graph-based question answering capabilities with pgvector integration

-- Create knowledge graph schema
CREATE SCHEMA IF NOT EXISTS knowledge_graph;

-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Knowledge Graph Entities Table
-- Stores entities (nodes) in the knowledge graph
CREATE TABLE IF NOT EXISTS knowledge_graph.entities (
    id SERIAL PRIMARY KEY,
    datasource_id INTEGER NOT NULL,
    
    -- Entity information
    entity_id VARCHAR(255) NOT NULL, -- Unique identifier within datasource
    entity_type VARCHAR(100) NOT NULL, -- Type of entity (person, product, etc.)
    entity_name VARCHAR(500) NOT NULL, -- Display name
    entity_label VARCHAR(500), -- Alternative label
    
    -- Properties
    properties JSONB NOT NULL DEFAULT '{}', -- Entity properties as JSON
    description TEXT, -- Human-readable description
    
    -- Vector embedding for semantic search (pgvector)
    embedding vector(1024), -- Using 1024 dimensions for BGE-M3 model
    embedding_model VARCHAR(100), -- Model used for embedding
    
    -- Metadata
    source_table VARCHAR(255), -- Source database table
    source_column VARCHAR(255), -- Source database column
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    -- Neo4j integration
    neo4j_node_id BIGINT, -- Neo4j node ID for synchronization
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_entities_datasource 
        FOREIGN KEY (datasource_id) 
        REFERENCES database_management.database_datasources(id) 
        ON DELETE CASCADE,
    
    -- Unique constraint
    UNIQUE(datasource_id, entity_id)
);

-- 2. Knowledge Graph Relations Table
-- Stores relationships (edges) between entities
CREATE TABLE IF NOT EXISTS knowledge_graph.relations (
    id SERIAL PRIMARY KEY,
    datasource_id INTEGER NOT NULL,
    
    -- Relation information
    relation_id VARCHAR(255) NOT NULL, -- Unique identifier within datasource
    relation_type VARCHAR(100) NOT NULL, -- Type of relation (works_for, located_in, etc.)
    relation_name VARCHAR(500) NOT NULL, -- Display name
    
    -- Connected entities
    source_entity_id INTEGER NOT NULL, -- Source entity
    target_entity_id INTEGER NOT NULL, -- Target entity
    
    -- Properties
    properties JSONB NOT NULL DEFAULT '{}', -- Relation properties as JSON
    description TEXT, -- Human-readable description
    weight FLOAT DEFAULT 1.0, -- Relation strength/weight
    
    -- Vector embedding for semantic search (pgvector)
    embedding vector(1024), -- Using 1024 dimensions for BGE-M3 model
    embedding_model VARCHAR(100), -- Model used for embedding
    
    -- Metadata
    source_table VARCHAR(255), -- Source database table
    source_columns TEXT[], -- Source database columns involved
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    -- Neo4j integration
    neo4j_relationship_id BIGINT, -- Neo4j relationship ID for synchronization
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_relations_datasource 
        FOREIGN KEY (datasource_id) 
        REFERENCES database_management.database_datasources(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_relations_source_entity 
        FOREIGN KEY (source_entity_id) 
        REFERENCES knowledge_graph.entities(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_relations_target_entity 
        FOREIGN KEY (target_entity_id) 
        REFERENCES knowledge_graph.entities(id) 
        ON DELETE CASCADE,
    
    -- Unique constraint
    UNIQUE(datasource_id, relation_id)
);

-- 3. Knowledge Graph Query History Table
-- Stores question-answering queries and results
CREATE TABLE IF NOT EXISTS knowledge_graph.query_history (
    id SERIAL PRIMARY KEY,
    datasource_id INTEGER NOT NULL,
    
    -- Query information
    user_question TEXT NOT NULL,
    processed_question TEXT, -- Processed/normalized question
    query_type VARCHAR(50) NOT NULL DEFAULT 'GRAPH_QA' 
        CHECK (query_type IN ('GRAPH_QA', 'LOCAL_SEARCH', 'GLOBAL_SEARCH', 'HYBRID_SEARCH', 'DEEP_RESEARCH')),
    
    -- Graph query details
    graph_query JSONB, -- Graph traversal query (Cypher-like or custom format)
    entities_involved INTEGER[], -- Array of entity IDs involved
    relations_involved INTEGER[], -- Array of relation IDs involved
    
    -- Results
    answer TEXT, -- Generated answer
    result_entities JSONB, -- Entities in the result
    result_relations JSONB, -- Relations in the result
    result_paths JSONB, -- Graph paths found
    reasoning_chain JSONB, -- Step-by-step reasoning process
    
    -- Execution details
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING' 
        CHECK (status IN ('PENDING', 'SUCCESS', 'FAILED', 'TIMEOUT')),
    execution_time_ms INTEGER,
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    -- AI/ML details
    model_used VARCHAR(100),
    explanation TEXT, -- Explanation of how the answer was derived
    evidence_sources JSONB, -- Sources of evidence used
    
    -- Vector embedding for question (pgvector)
    question_embedding vector(1024),
    embedding_model VARCHAR(100),
    
    -- Metadata
    metadata JSONB,
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_kg_query_history_datasource 
        FOREIGN KEY (datasource_id) 
        REFERENCES database_management.database_datasources(id) 
        ON DELETE CASCADE
);

-- 4. Knowledge Graph Communities Table
-- Stores detected communities and their summaries
CREATE TABLE IF NOT EXISTS knowledge_graph.communities (
    id SERIAL PRIMARY KEY,
    datasource_id INTEGER NOT NULL,
    
    -- Community information
    community_id VARCHAR(255) NOT NULL, -- Unique community identifier
    community_name VARCHAR(500), -- Human-readable name
    community_type VARCHAR(100), -- Type of community
    
    -- Community content
    entity_ids INTEGER[], -- Array of entity IDs in this community
    summary TEXT, -- Community summary
    keywords TEXT[], -- Key terms representing this community
    
    -- Statistics
    entity_count INTEGER DEFAULT 0,
    relation_count INTEGER DEFAULT 0,
    centrality_score FLOAT, -- Community importance score
    
    -- Vector embedding for community (pgvector)
    embedding vector(1024),
    embedding_model VARCHAR(100),
    
    -- Neo4j integration
    neo4j_community_id BIGINT, -- Neo4j community ID
    
    -- Detection metadata
    algorithm_used VARCHAR(50), -- Algorithm used for detection (leiden, sllpa, etc.)
    detection_parameters JSONB, -- Parameters used in detection
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_communities_datasource 
        FOREIGN KEY (datasource_id) 
        REFERENCES database_management.database_datasources(id) 
        ON DELETE CASCADE,
    
    -- Unique constraint
    UNIQUE(datasource_id, community_id)
);

-- 5. Knowledge Graph Build Tasks Table
-- Tracks graph building tasks and their progress
CREATE TABLE IF NOT EXISTS knowledge_graph.build_tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL UNIQUE, -- UUID for task tracking
    datasource_id INTEGER NOT NULL,

    -- Task configuration
    entity_types TEXT[] NOT NULL, -- Entity types to extract
    relation_types TEXT[] NOT NULL, -- Relation types to extract
    chunk_size INTEGER DEFAULT 500,
    overlap INTEGER DEFAULT 100,
    similarity_threshold FLOAT DEFAULT 0.9,
    conflict_strategy VARCHAR(50) DEFAULT 'manual_first',

    -- Processing options
    enable_community_detection BOOLEAN DEFAULT TRUE,
    community_algorithm VARCHAR(50) DEFAULT 'leiden',
    incremental_update BOOLEAN DEFAULT FALSE,

    -- Progress tracking
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')),
    total_chunks INTEGER,
    processed_chunks INTEGER DEFAULT 0,
    entities_extracted INTEGER DEFAULT 0,
    relations_extracted INTEGER DEFAULT 0,
    communities_detected INTEGER DEFAULT 0,

    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    estimated_completion TIMESTAMP WITH TIME ZONE,

    -- Results
    build_summary JSONB, -- Summary of build results
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraint
    CONSTRAINT fk_build_tasks_datasource
        FOREIGN KEY (datasource_id)
        REFERENCES database_management.database_datasources(id)
        ON DELETE CASCADE
);

-- 6. Knowledge Graph Statistics Table
-- Stores statistics and metrics for knowledge graphs
CREATE TABLE IF NOT EXISTS knowledge_graph.statistics (
    id SERIAL PRIMARY KEY,
    datasource_id INTEGER NOT NULL,

    -- Graph statistics
    total_entities INTEGER NOT NULL DEFAULT 0,
    total_relations INTEGER NOT NULL DEFAULT 0,
    total_communities INTEGER DEFAULT 0,
    entity_types JSONB, -- Count by entity type
    relation_types JSONB, -- Count by relation type

    -- Quality metrics
    verified_entities INTEGER DEFAULT 0,
    verified_relations INTEGER DEFAULT 0,
    avg_confidence_score FLOAT,

    -- Query statistics
    total_queries INTEGER DEFAULT 0,
    successful_queries INTEGER DEFAULT 0,
    avg_query_time_ms FLOAT,
    query_types_distribution JSONB, -- Distribution of query types

    -- Performance metrics
    avg_local_search_time_ms FLOAT,
    avg_global_search_time_ms FLOAT,
    avg_hybrid_search_time_ms FLOAT,
    avg_deep_research_time_ms FLOAT,

    -- Timestamps
    calculated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraint
    CONSTRAINT fk_kg_statistics_datasource
        FOREIGN KEY (datasource_id)
        REFERENCES database_management.database_datasources(id)
        ON DELETE CASCADE,

    -- Unique constraint (one record per datasource)
    UNIQUE(datasource_id)
);

-- Create indexes for performance
-- Entity indexes
CREATE INDEX IF NOT EXISTS idx_entities_datasource_id ON knowledge_graph.entities(datasource_id);
CREATE INDEX IF NOT EXISTS idx_entities_type ON knowledge_graph.entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_entities_name ON knowledge_graph.entities(entity_name);
CREATE INDEX IF NOT EXISTS idx_entities_embedding ON knowledge_graph.entities USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_entities_active ON knowledge_graph.entities(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_entities_neo4j_id ON knowledge_graph.entities(neo4j_node_id) WHERE neo4j_node_id IS NOT NULL;

-- Relation indexes
CREATE INDEX IF NOT EXISTS idx_relations_datasource_id ON knowledge_graph.relations(datasource_id);
CREATE INDEX IF NOT EXISTS idx_relations_type ON knowledge_graph.relations(relation_type);
CREATE INDEX IF NOT EXISTS idx_relations_source_entity ON knowledge_graph.relations(source_entity_id);
CREATE INDEX IF NOT EXISTS idx_relations_target_entity ON knowledge_graph.relations(target_entity_id);
CREATE INDEX IF NOT EXISTS idx_relations_embedding ON knowledge_graph.relations USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_relations_active ON knowledge_graph.relations(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_relations_neo4j_id ON knowledge_graph.relations(neo4j_relationship_id) WHERE neo4j_relationship_id IS NOT NULL;

-- Query history indexes
CREATE INDEX IF NOT EXISTS idx_kg_query_history_datasource_id ON knowledge_graph.query_history(datasource_id);
CREATE INDEX IF NOT EXISTS idx_kg_query_history_status ON knowledge_graph.query_history(status);
CREATE INDEX IF NOT EXISTS idx_kg_query_history_type ON knowledge_graph.query_history(query_type);
CREATE INDEX IF NOT EXISTS idx_kg_query_history_created_at ON knowledge_graph.query_history(created_at);
CREATE INDEX IF NOT EXISTS idx_kg_query_history_question_embedding ON knowledge_graph.query_history USING ivfflat (question_embedding vector_cosine_ops) WITH (lists = 100);

-- Community indexes
CREATE INDEX IF NOT EXISTS idx_communities_datasource_id ON knowledge_graph.communities(datasource_id);
CREATE INDEX IF NOT EXISTS idx_communities_type ON knowledge_graph.communities(community_type);
CREATE INDEX IF NOT EXISTS idx_communities_embedding ON knowledge_graph.communities USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_communities_active ON knowledge_graph.communities(is_active) WHERE is_active = true;

-- Build task indexes
CREATE INDEX IF NOT EXISTS idx_build_tasks_datasource_id ON knowledge_graph.build_tasks(datasource_id);
CREATE INDEX IF NOT EXISTS idx_build_tasks_status ON knowledge_graph.build_tasks(status);
CREATE INDEX IF NOT EXISTS idx_build_tasks_created_at ON knowledge_graph.build_tasks(created_at);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION knowledge_graph.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_entities_updated_at BEFORE UPDATE ON knowledge_graph.entities
    FOR EACH ROW EXECUTE FUNCTION knowledge_graph.update_updated_at_column();

CREATE TRIGGER update_relations_updated_at BEFORE UPDATE ON knowledge_graph.relations
    FOR EACH ROW EXECUTE FUNCTION knowledge_graph.update_updated_at_column();

CREATE TRIGGER update_kg_query_history_updated_at BEFORE UPDATE ON knowledge_graph.query_history
    FOR EACH ROW EXECUTE FUNCTION knowledge_graph.update_updated_at_column();

CREATE TRIGGER update_communities_updated_at BEFORE UPDATE ON knowledge_graph.communities
    FOR EACH ROW EXECUTE FUNCTION knowledge_graph.update_updated_at_column();

CREATE TRIGGER update_build_tasks_updated_at BEFORE UPDATE ON knowledge_graph.build_tasks
    FOR EACH ROW EXECUTE FUNCTION knowledge_graph.update_updated_at_column();

-- Add comments for documentation
COMMENT ON SCHEMA knowledge_graph IS 'Knowledge Graph RAG module for graph-based question answering';
COMMENT ON TABLE knowledge_graph.entities IS 'Entities (nodes) in the knowledge graph with pgvector embeddings';
COMMENT ON TABLE knowledge_graph.relations IS 'Relations (edges) between entities in the knowledge graph';
COMMENT ON TABLE knowledge_graph.query_history IS 'History of knowledge graph queries and multi-strategy answers';
COMMENT ON TABLE knowledge_graph.communities IS 'Detected communities with summaries for global search';
COMMENT ON TABLE knowledge_graph.build_tasks IS 'Knowledge graph build tasks and progress tracking';
COMMENT ON TABLE knowledge_graph.statistics IS 'Statistics and metrics for knowledge graphs';
