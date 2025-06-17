// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// Neo4j Schema Initialization for DeerFlow Knowledge Graph
// Provides graph structure for complex graph operations and community detection

// ============================================================================
// 1. Node Labels and Constraints
// ============================================================================

// Entity nodes - represent entities from PostgreSQL
CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
FOR (e:Entity) REQUIRE e.entity_id IS UNIQUE;

CREATE CONSTRAINT entity_pg_id_unique IF NOT EXISTS
FOR (e:Entity) REQUIRE e.pg_id IS UNIQUE;

// Community nodes - represent detected communities
CREATE CONSTRAINT community_id_unique IF NOT EXISTS
FOR (c:Community) REQUIRE c.community_id IS UNIQUE;

CREATE CONSTRAINT community_pg_id_unique IF NOT EXISTS
FOR (c:Community) REQUIRE c.pg_id IS UNIQUE;

// Chunk nodes - represent text chunks for detailed analysis
CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS
FOR (ch:Chunk) REQUIRE ch.chunk_id IS UNIQUE;

// ============================================================================
// 2. Relationship Types and Constraints
// ============================================================================

// No unique constraints on relationships as they can have duplicates
// But we'll create indexes for performance

// ============================================================================
// 3. Indexes for Performance
// ============================================================================

// Entity indexes
CREATE INDEX entity_type_index IF NOT EXISTS
FOR (e:Entity) ON (e.entity_type);

CREATE INDEX entity_name_index IF NOT EXISTS
FOR (e:Entity) ON (e.entity_name);

CREATE INDEX entity_datasource_index IF NOT EXISTS
FOR (e:Entity) ON (e.datasource_id);

CREATE INDEX entity_confidence_index IF NOT EXISTS
FOR (e:Entity) ON (e.confidence_score);

CREATE INDEX entity_active_index IF NOT EXISTS
FOR (e:Entity) ON (e.is_active);

// Community indexes
CREATE INDEX community_type_index IF NOT EXISTS
FOR (c:Community) ON (c.community_type);

CREATE INDEX community_datasource_index IF NOT EXISTS
FOR (c:Community) ON (c.datasource_id);

CREATE INDEX community_centrality_index IF NOT EXISTS
FOR (c:Community) ON (c.centrality_score);

// Chunk indexes
CREATE INDEX chunk_datasource_index IF NOT EXISTS
FOR (ch:Chunk) ON (ch.datasource_id);

// Relationship indexes
CREATE INDEX rel_type_index IF NOT EXISTS
FOR ()-[r]-() ON (r.relation_type);

CREATE INDEX rel_weight_index IF NOT EXISTS
FOR ()-[r]-() ON (r.weight);

CREATE INDEX rel_confidence_index IF NOT EXISTS
FOR ()-[r]-() ON (r.confidence_score);

// ============================================================================
// 4. Graph Data Science (GDS) Configuration
// ============================================================================

// Create graph projections for community detection and analysis
// Note: These will be created dynamically in the application code
// but we document the structure here

/*
// Example graph projection for community detection
CALL gds.graph.project(
    'knowledge-graph',
    'Entity',
    {
        RELATES_TO: {
            orientation: 'UNDIRECTED',
            properties: ['weight', 'confidence_score']
        }
    }
);

// Example Leiden community detection
CALL gds.leiden.write(
    'knowledge-graph',
    {
        writeProperty: 'community_id',
        relationshipWeightProperty: 'weight'
    }
);
*/

// ============================================================================
// 5. Sample Data Structure Documentation
// ============================================================================

/*
// Entity Node Structure:
(:Entity {
    entity_id: "unique_entity_identifier",
    pg_id: 123,  // PostgreSQL ID for synchronization
    entity_type: "person|product|organization|concept",
    entity_name: "Display Name",
    entity_label: "Alternative Label",
    description: "Human readable description",
    datasource_id: 1,
    source_table: "table_name",
    source_column: "column_name",
    confidence_score: 0.95,
    is_active: true,
    is_verified: false,
    created_at: datetime(),
    updated_at: datetime(),
    properties: {
        // Additional entity-specific properties
        custom_field1: "value1",
        custom_field2: "value2"
    }
})

// Relationship Structure:
(:Entity)-[:RELATES_TO {
    relation_id: "unique_relation_identifier",
    pg_id: 456,  // PostgreSQL ID for synchronization
    relation_type: "works_for|located_in|part_of|similar_to",
    relation_name: "Display Name",
    description: "Human readable description",
    weight: 1.0,
    datasource_id: 1,
    source_table: "table_name",
    confidence_score: 0.85,
    is_active: true,
    is_verified: false,
    created_at: datetime(),
    updated_at: datetime(),
    properties: {
        // Additional relation-specific properties
        strength: "strong|medium|weak",
        direction: "bidirectional|unidirectional"
    }
}]->(:Entity)

// Community Node Structure:
(:Community {
    community_id: "unique_community_identifier",
    pg_id: 789,  // PostgreSQL ID for synchronization
    community_name: "Community Display Name",
    community_type: "functional|topical|structural",
    summary: "Generated community summary",
    keywords: ["keyword1", "keyword2", "keyword3"],
    entity_count: 25,
    relation_count: 45,
    centrality_score: 0.75,
    datasource_id: 1,
    algorithm_used: "leiden|sllpa|louvain",
    detection_parameters: {
        resolution: 1.0,
        iterations: 10
    },
    is_active: true,
    created_at: datetime(),
    updated_at: datetime()
})

// Entity-Community Relationship:
(:Entity)-[:BELONGS_TO {
    membership_strength: 0.8,
    role: "core|peripheral|bridge"
}]->(:Community)

// Chunk Node Structure (for detailed text analysis):
(:Chunk {
    chunk_id: "unique_chunk_identifier",
    text: "Original text content",
    chunk_index: 0,
    datasource_id: 1,
    source_table: "table_name",
    source_row_id: 123,
    created_at: datetime()
})

// Entity-Chunk Relationship:
(:Entity)-[:MENTIONED_IN {
    mention_count: 3,
    relevance_score: 0.9
}]->(:Chunk)
*/

// ============================================================================
// 6. Utility Procedures and Functions
// ============================================================================

// Note: Custom procedures would be implemented in Java/Python plugins
// Here we document the intended functionality

/*
// Custom procedure for entity similarity calculation
CALL kg.similarity.entities(entity1_id, entity2_id) YIELD similarity_score

// Custom procedure for path finding with semantic constraints
CALL kg.path.semantic(start_entity, end_entity, max_hops, relation_types) 
YIELD path, relevance_score

// Custom procedure for community summary generation
CALL kg.community.summarize(community_id) YIELD summary, keywords

// Custom procedure for graph statistics
CALL kg.stats.overview(datasource_id) 
YIELD entity_count, relation_count, community_count, avg_clustering_coefficient
*/

// ============================================================================
// 7. Data Synchronization Helpers
// ============================================================================

// Procedures for synchronizing with PostgreSQL
// These will be implemented in the application layer

/*
// Sync entity from PostgreSQL
MERGE (e:Entity {pg_id: $pg_id})
SET e += $properties
SET e.updated_at = datetime()

// Sync relationship from PostgreSQL
MATCH (source:Entity {pg_id: $source_pg_id})
MATCH (target:Entity {pg_id: $target_pg_id})
MERGE (source)-[r:RELATES_TO {pg_id: $relation_pg_id}]->(target)
SET r += $properties
SET r.updated_at = datetime()

// Clean up orphaned nodes
MATCH (e:Entity)
WHERE NOT EXISTS((e)-[]-())
AND e.is_active = false
DELETE e
*/

// ============================================================================
// 8. Performance Optimization Settings
// ============================================================================

/*
// Recommended Neo4j configuration for knowledge graphs:

// Memory settings (adjust based on available RAM)
dbms.memory.heap.initial_size=2G
dbms.memory.heap.max_size=4G
dbms.memory.pagecache.size=2G

// Query performance
cypher.default_language_version=5
cypher.hints.error=true
cypher.lenient_create_relationship=false

// GDS settings
gds.enterprise.license_file=/path/to/license
gds.graph.store.arrow.enabled=true

// Logging
dbms.logs.query.enabled=true
dbms.logs.query.threshold=1s
*/

// ============================================================================
// Schema initialization complete
// ============================================================================
