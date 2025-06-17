# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Knowledge Graph PostgreSQL repository for DeerFlow.

Provides data access layer for knowledge graph entities, relations, queries, and statistics
with pgvector integration for semantic search.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple

# Note: asyncpg imports will be added when database connection is implemented
# import asyncpg
# from asyncpg import Connection, Pool

from src.models.knowledge_graph import (
    KnowledgeGraphEntity,
    KnowledgeGraphRelation,
    KnowledgeGraphQuery,
    KnowledgeGraphCommunity,
    KnowledgeGraphStatistics,
    QueryStatus,
    QueryType
)

# Note: Database connection will be implemented later
# from src.database.connection import get_database_pool

logger = logging.getLogger(__name__)


class KnowledgeGraphRepository:
    """
    PostgreSQL repository for knowledge graph data with pgvector support.

    Provides CRUD operations, vector similarity search, and batch processing
    for all knowledge graph entities.

    Note: This is a placeholder implementation. Database connection logic
    will be implemented when the database layer is ready.
    """

    def __init__(self):
        """Initialize the repository"""
        self.pool: Optional[Any] = None  # Will be asyncpg.Pool when implemented

    async def get_connection(self) -> Any:
        """Get database connection from pool"""
        # Placeholder implementation
        raise NotImplementedError("Database connection not yet implemented")

    async def release_connection(self, conn: Any):
        """Release database connection back to pool"""
        # Placeholder implementation
        pass
    
    # ============================================================================
    # Entity Operations
    # ============================================================================
    
    async def create_entity(self, entity: KnowledgeGraphEntity) -> int:
        """Create a new entity and return its ID"""
        conn = await self.get_connection()
        try:
            query = """
                INSERT INTO knowledge_graph.entities (
                    datasource_id, entity_id, entity_type, entity_name, entity_label,
                    properties, description, embedding, embedding_model,
                    source_table, source_column, confidence_score, neo4j_node_id,
                    is_active, is_verified
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                RETURNING id
            """
            
            result = await conn.fetchrow(
                query,
                entity.datasource_id,
                entity.entity_id,
                entity.entity_type,
                entity.entity_name,
                entity.entity_label,
                entity.properties,
                entity.description,
                entity.embedding,
                entity.embedding_model,
                entity.source_table,
                entity.source_column,
                entity.confidence_score,
                entity.neo4j_node_id,
                entity.is_active,
                entity.is_verified
            )
            
            return result['id']
            
        except Exception as e:
            logger.error(f"Failed to create entity: {e}")
            raise
        finally:
            await self.release_connection(conn)
    
    async def get_entity(self, entity_id: int) -> Optional[KnowledgeGraphEntity]:
        """Get entity by ID"""
        conn = await self.get_connection()
        try:
            query = """
                SELECT * FROM knowledge_graph.entities WHERE id = $1
            """
            
            result = await conn.fetchrow(query, entity_id)
            if result:
                return KnowledgeGraphEntity(**dict(result))
            return None
            
        except Exception as e:
            logger.error(f"Failed to get entity {entity_id}: {e}")
            raise
        finally:
            await self.release_connection(conn)
    
    async def update_entity(self, entity: KnowledgeGraphEntity) -> bool:
        """Update an existing entity"""
        conn = await self.get_connection()
        try:
            query = """
                UPDATE knowledge_graph.entities SET
                    entity_type = $2, entity_name = $3, entity_label = $4,
                    properties = $5, description = $6, embedding = $7, embedding_model = $8,
                    source_table = $9, source_column = $10, confidence_score = $11,
                    neo4j_node_id = $12, is_active = $13, is_verified = $14,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = $1
            """
            
            result = await conn.execute(
                query,
                entity.id,
                entity.entity_type,
                entity.entity_name,
                entity.entity_label,
                entity.properties,
                entity.description,
                entity.embedding,
                entity.embedding_model,
                entity.source_table,
                entity.source_column,
                entity.confidence_score,
                entity.neo4j_node_id,
                entity.is_active,
                entity.is_verified
            )
            
            return result.split()[-1] == '1'  # Check if one row was updated
            
        except Exception as e:
            logger.error(f"Failed to update entity {entity.id}: {e}")
            raise
        finally:
            await self.release_connection(conn)
    
    async def delete_entity(self, entity_id: int) -> bool:
        """Delete an entity"""
        conn = await self.get_connection()
        try:
            query = """
                DELETE FROM knowledge_graph.entities WHERE id = $1
            """
            
            result = await conn.execute(query, entity_id)
            return result.split()[-1] == '1'  # Check if one row was deleted
            
        except Exception as e:
            logger.error(f"Failed to delete entity {entity_id}: {e}")
            raise
        finally:
            await self.release_connection(conn)
    
    async def find_entities_by_datasource(
        self, 
        datasource_id: int, 
        entity_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[KnowledgeGraphEntity]:
        """Find entities by datasource with optional filtering"""
        conn = await self.get_connection()
        try:
            if entity_type:
                query = """
                    SELECT * FROM knowledge_graph.entities 
                    WHERE datasource_id = $1 AND entity_type = $2 AND is_active = true
                    ORDER BY created_at DESC
                    LIMIT $3 OFFSET $4
                """
                results = await conn.fetch(query, datasource_id, entity_type, limit, offset)
            else:
                query = """
                    SELECT * FROM knowledge_graph.entities 
                    WHERE datasource_id = $1 AND is_active = true
                    ORDER BY created_at DESC
                    LIMIT $2 OFFSET $3
                """
                results = await conn.fetch(query, datasource_id, limit, offset)
            
            return [KnowledgeGraphEntity(**dict(row)) for row in results]
            
        except Exception as e:
            logger.error(f"Failed to find entities for datasource {datasource_id}: {e}")
            raise
        finally:
            await self.release_connection(conn)
    
    async def search_entities_by_embedding(
        self,
        datasource_id: int,
        query_embedding: List[float],
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Tuple[KnowledgeGraphEntity, float]]:
        """Search entities by vector similarity using pgvector"""
        conn = await self.get_connection()
        try:
            query = """
                SELECT *, (embedding <=> $2::vector) as distance
                FROM knowledge_graph.entities 
                WHERE datasource_id = $1 
                    AND embedding IS NOT NULL 
                    AND is_active = true
                    AND (1 - (embedding <=> $2::vector)) >= $4
                ORDER BY embedding <=> $2::vector
                LIMIT $3
            """
            
            results = await conn.fetch(
                query, 
                datasource_id, 
                query_embedding, 
                limit, 
                similarity_threshold
            )
            
            entities_with_scores = []
            for row in results:
                entity_data = dict(row)
                distance = entity_data.pop('distance')
                similarity = 1 - distance  # Convert distance to similarity
                entity = KnowledgeGraphEntity(**entity_data)
                entities_with_scores.append((entity, similarity))
            
            return entities_with_scores
            
        except Exception as e:
            logger.error(f"Failed to search entities by embedding: {e}")
            raise
        finally:
            await self.release_connection(conn)
    
    async def count_entities(self, datasource_id: int) -> int:
        """Count total entities for a datasource"""
        conn = await self.get_connection()
        try:
            query = """
                SELECT COUNT(*) FROM knowledge_graph.entities 
                WHERE datasource_id = $1 AND is_active = true
            """
            
            result = await conn.fetchval(query, datasource_id)
            return result or 0
            
        except Exception as e:
            logger.error(f"Failed to count entities for datasource {datasource_id}: {e}")
            raise
        finally:
            await self.release_connection(conn)
    
    # ============================================================================
    # Relation Operations
    # ============================================================================
    
    async def create_relation(self, relation: KnowledgeGraphRelation) -> int:
        """Create a new relation and return its ID"""
        conn = await self.get_connection()
        try:
            query = """
                INSERT INTO knowledge_graph.relations (
                    datasource_id, relation_id, relation_type, relation_name,
                    source_entity_id, target_entity_id, properties, description, weight,
                    embedding, embedding_model, source_table, source_columns,
                    confidence_score, neo4j_relationship_id, is_active, is_verified
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                RETURNING id
            """
            
            result = await conn.fetchrow(
                query,
                relation.datasource_id,
                relation.relation_id,
                relation.relation_type,
                relation.relation_name,
                relation.source_entity_id,
                relation.target_entity_id,
                relation.properties,
                relation.description,
                relation.weight,
                relation.embedding,
                relation.embedding_model,
                relation.source_table,
                relation.source_columns,
                relation.confidence_score,
                relation.neo4j_relationship_id,
                relation.is_active,
                relation.is_verified
            )
            
            return result['id']
            
        except Exception as e:
            logger.error(f"Failed to create relation: {e}")
            raise
        finally:
            await self.release_connection(conn)
    
    async def get_relation(self, relation_id: int) -> Optional[KnowledgeGraphRelation]:
        """Get relation by ID"""
        conn = await self.get_connection()
        try:
            query = """
                SELECT * FROM knowledge_graph.relations WHERE id = $1
            """
            
            result = await conn.fetchrow(query, relation_id)
            if result:
                return KnowledgeGraphRelation(**dict(result))
            return None
            
        except Exception as e:
            logger.error(f"Failed to get relation {relation_id}: {e}")
            raise
        finally:
            await self.release_connection(conn)

    async def find_relations_by_entity(
        self,
        entity_id: int,
        direction: str = "both"  # "incoming", "outgoing", "both"
    ) -> List[KnowledgeGraphRelation]:
        """Find relations connected to an entity"""
        conn = await self.get_connection()
        try:
            if direction == "incoming":
                query = """
                    SELECT * FROM knowledge_graph.relations
                    WHERE target_entity_id = $1 AND is_active = true
                    ORDER BY weight DESC
                """
            elif direction == "outgoing":
                query = """
                    SELECT * FROM knowledge_graph.relations
                    WHERE source_entity_id = $1 AND is_active = true
                    ORDER BY weight DESC
                """
            else:  # both
                query = """
                    SELECT * FROM knowledge_graph.relations
                    WHERE (source_entity_id = $1 OR target_entity_id = $1) AND is_active = true
                    ORDER BY weight DESC
                """

            results = await conn.fetch(query, entity_id)
            return [KnowledgeGraphRelation(**dict(row)) for row in results]

        except Exception as e:
            logger.error(f"Failed to find relations for entity {entity_id}: {e}")
            raise
        finally:
            await self.release_connection(conn)

    async def count_relations(self, datasource_id: int) -> int:
        """Count total relations for a datasource"""
        conn = await self.get_connection()
        try:
            query = """
                SELECT COUNT(*) FROM knowledge_graph.relations
                WHERE datasource_id = $1 AND is_active = true
            """

            result = await conn.fetchval(query, datasource_id)
            return result or 0

        except Exception as e:
            logger.error(f"Failed to count relations for datasource {datasource_id}: {e}")
            raise
        finally:
            await self.release_connection(conn)

    # ============================================================================
    # Query Operations
    # ============================================================================

    async def create_query(self, query: KnowledgeGraphQuery) -> int:
        """Create a new query record and return its ID"""
        conn = await self.get_connection()
        try:
            sql = """
                INSERT INTO knowledge_graph.query_history (
                    datasource_id, user_question, processed_question, query_type,
                    graph_query, entities_involved, relations_involved,
                    answer, result_entities, result_relations, result_paths, reasoning_chain,
                    status, execution_time_ms, confidence_score,
                    model_used, explanation, evidence_sources,
                    question_embedding, embedding_model, metadata, error_message
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22)
                RETURNING id
            """

            result = await conn.fetchrow(
                sql,
                query.datasource_id,
                query.user_question,
                query.processed_question,
                query.query_type.value,
                query.graph_query,
                query.entities_involved,
                query.relations_involved,
                query.answer,
                query.result_entities,
                query.result_relations,
                query.result_paths,
                query.reasoning_chain,
                query.status.value,
                query.execution_time_ms,
                query.confidence_score,
                query.model_used,
                query.explanation,
                query.evidence_sources,
                query.question_embedding,
                query.embedding_model,
                query.metadata,
                query.error_message
            )

            return result['id']

        except Exception as e:
            logger.error(f"Failed to create query: {e}")
            raise
        finally:
            await self.release_connection(conn)

    async def update_query(self, query: KnowledgeGraphQuery) -> bool:
        """Update an existing query"""
        conn = await self.get_connection()
        try:
            sql = """
                UPDATE knowledge_graph.query_history SET
                    processed_question = $2, graph_query = $3, entities_involved = $4,
                    relations_involved = $5, answer = $6, result_entities = $7,
                    result_relations = $8, result_paths = $9, reasoning_chain = $10,
                    status = $11, execution_time_ms = $12, confidence_score = $13,
                    model_used = $14, explanation = $15, evidence_sources = $16,
                    question_embedding = $17, embedding_model = $18, metadata = $19,
                    error_message = $20, updated_at = CURRENT_TIMESTAMP
                WHERE id = $1
            """

            result = await conn.execute(
                sql,
                query.id,
                query.processed_question,
                query.graph_query,
                query.entities_involved,
                query.relations_involved,
                query.answer,
                query.result_entities,
                query.result_relations,
                query.result_paths,
                query.reasoning_chain,
                query.status.value,
                query.execution_time_ms,
                query.confidence_score,
                query.model_used,
                query.explanation,
                query.evidence_sources,
                query.question_embedding,
                query.embedding_model,
                query.metadata,
                query.error_message
            )

            return result.split()[-1] == '1'

        except Exception as e:
            logger.error(f"Failed to update query {query.id}: {e}")
            raise
        finally:
            await self.release_connection(conn)

    async def get_query_history(
        self,
        datasource_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[KnowledgeGraphQuery]:
        """Get query history for a datasource"""
        conn = await self.get_connection()
        try:
            query = """
                SELECT * FROM knowledge_graph.query_history
                WHERE datasource_id = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
            """

            results = await conn.fetch(query, datasource_id, limit, offset)

            queries = []
            for row in results:
                query_data = dict(row)
                # Convert enum strings back to enums
                query_data['status'] = QueryStatus(query_data['status'])
                query_data['query_type'] = QueryType(query_data['query_type'])
                queries.append(KnowledgeGraphQuery(**query_data))

            return queries

        except Exception as e:
            logger.error(f"Failed to get query history for datasource {datasource_id}: {e}")
            raise
        finally:
            await self.release_connection(conn)

    # ============================================================================
    # Community Operations
    # ============================================================================

    async def create_community(self, community: KnowledgeGraphCommunity) -> int:
        """Create a new community and return its ID"""
        conn = await self.get_connection()
        try:
            query = """
                INSERT INTO knowledge_graph.communities (
                    datasource_id, community_id, community_name, community_type,
                    entity_ids, summary, keywords, entity_count, relation_count,
                    centrality_score, embedding, embedding_model, neo4j_community_id,
                    algorithm_used, detection_parameters, is_active
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                RETURNING id
            """

            result = await conn.fetchrow(
                query,
                community.datasource_id,
                community.community_id,
                community.community_name,
                community.community_type,
                community.entity_ids,
                community.summary,
                community.keywords,
                community.entity_count,
                community.relation_count,
                community.centrality_score,
                community.embedding,
                community.embedding_model,
                community.neo4j_community_id,
                community.algorithm_used,
                community.detection_parameters,
                community.is_active
            )

            return result['id']

        except Exception as e:
            logger.error(f"Failed to create community: {e}")
            raise
        finally:
            await self.release_connection(conn)

    async def find_communities_by_datasource(
        self,
        datasource_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[KnowledgeGraphCommunity]:
        """Find communities by datasource"""
        conn = await self.get_connection()
        try:
            query = """
                SELECT * FROM knowledge_graph.communities
                WHERE datasource_id = $1 AND is_active = true
                ORDER BY centrality_score DESC NULLS LAST, entity_count DESC
                LIMIT $2 OFFSET $3
            """

            results = await conn.fetch(query, datasource_id, limit, offset)
            return [KnowledgeGraphCommunity(**dict(row)) for row in results]

        except Exception as e:
            logger.error(f"Failed to find communities for datasource {datasource_id}: {e}")
            raise
        finally:
            await self.release_connection(conn)

    # ============================================================================
    # Statistics Operations
    # ============================================================================

    async def upsert_statistics(self, stats: KnowledgeGraphStatistics) -> int:
        """Create or update statistics for a datasource"""
        conn = await self.get_connection()
        try:
            query = """
                INSERT INTO knowledge_graph.statistics (
                    datasource_id, total_entities, total_relations, total_communities,
                    entity_types, relation_types, verified_entities, verified_relations,
                    avg_confidence_score, total_queries, successful_queries, avg_query_time_ms,
                    query_types_distribution, avg_local_search_time_ms, avg_global_search_time_ms,
                    avg_hybrid_search_time_ms, avg_deep_research_time_ms, calculated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
                ON CONFLICT (datasource_id) DO UPDATE SET
                    total_entities = EXCLUDED.total_entities,
                    total_relations = EXCLUDED.total_relations,
                    total_communities = EXCLUDED.total_communities,
                    entity_types = EXCLUDED.entity_types,
                    relation_types = EXCLUDED.relation_types,
                    verified_entities = EXCLUDED.verified_entities,
                    verified_relations = EXCLUDED.verified_relations,
                    avg_confidence_score = EXCLUDED.avg_confidence_score,
                    total_queries = EXCLUDED.total_queries,
                    successful_queries = EXCLUDED.successful_queries,
                    avg_query_time_ms = EXCLUDED.avg_query_time_ms,
                    query_types_distribution = EXCLUDED.query_types_distribution,
                    avg_local_search_time_ms = EXCLUDED.avg_local_search_time_ms,
                    avg_global_search_time_ms = EXCLUDED.avg_global_search_time_ms,
                    avg_hybrid_search_time_ms = EXCLUDED.avg_hybrid_search_time_ms,
                    avg_deep_research_time_ms = EXCLUDED.avg_deep_research_time_ms,
                    calculated_at = EXCLUDED.calculated_at
                RETURNING id
            """

            result = await conn.fetchrow(
                query,
                stats.datasource_id,
                stats.total_entities,
                stats.total_relations,
                stats.total_communities,
                stats.entity_types,
                stats.relation_types,
                stats.verified_entities,
                stats.verified_relations,
                stats.avg_confidence_score,
                stats.total_queries,
                stats.successful_queries,
                stats.avg_query_time_ms,
                stats.query_types_distribution,
                stats.avg_local_search_time_ms,
                stats.avg_global_search_time_ms,
                stats.avg_hybrid_search_time_ms,
                stats.avg_deep_research_time_ms,
                stats.calculated_at or datetime.now(timezone.utc)
            )

            return result['id']

        except Exception as e:
            logger.error(f"Failed to upsert statistics: {e}")
            raise
        finally:
            await self.release_connection(conn)

    async def get_statistics(self, datasource_id: int) -> Optional[KnowledgeGraphStatistics]:
        """Get statistics for a datasource"""
        conn = await self.get_connection()
        try:
            query = """
                SELECT * FROM knowledge_graph.statistics WHERE datasource_id = $1
            """

            result = await conn.fetchrow(query, datasource_id)
            if result:
                return KnowledgeGraphStatistics(**dict(result))
            return None

        except Exception as e:
            logger.error(f"Failed to get statistics for datasource {datasource_id}: {e}")
            raise
        finally:
            await self.release_connection(conn)

    # ============================================================================
    # Batch Operations
    # ============================================================================

    async def batch_create_entities(self, entities: List[KnowledgeGraphEntity]) -> List[int]:
        """Batch create entities for better performance"""
        if not entities:
            return []

        conn = await self.get_connection()
        try:
            # Prepare data for batch insert
            values = []
            for entity in entities:
                values.append((
                    entity.datasource_id, entity.entity_id, entity.entity_type,
                    entity.entity_name, entity.entity_label, entity.properties,
                    entity.description, entity.embedding, entity.embedding_model,
                    entity.source_table, entity.source_column, entity.confidence_score,
                    entity.neo4j_node_id, entity.is_active, entity.is_verified
                ))

            query = """
                INSERT INTO knowledge_graph.entities (
                    datasource_id, entity_id, entity_type, entity_name, entity_label,
                    properties, description, embedding, embedding_model,
                    source_table, source_column, confidence_score, neo4j_node_id,
                    is_active, is_verified
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                RETURNING id
            """

            results = await conn.fetch(query, *values)
            return [row['id'] for row in results]

        except Exception as e:
            logger.error(f"Failed to batch create entities: {e}")
            raise
        finally:
            await self.release_connection(conn)

    async def batch_create_relations(self, relations: List[KnowledgeGraphRelation]) -> List[int]:
        """Batch create relations for better performance"""
        if not relations:
            return []

        conn = await self.get_connection()
        try:
            # Use executemany for batch insert
            query = """
                INSERT INTO knowledge_graph.relations (
                    datasource_id, relation_id, relation_type, relation_name,
                    source_entity_id, target_entity_id, properties, description, weight,
                    embedding, embedding_model, source_table, source_columns,
                    confidence_score, neo4j_relationship_id, is_active, is_verified
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                RETURNING id
            """

            values = []
            for relation in relations:
                values.append((
                    relation.datasource_id, relation.relation_id, relation.relation_type,
                    relation.relation_name, relation.source_entity_id, relation.target_entity_id,
                    relation.properties, relation.description, relation.weight,
                    relation.embedding, relation.embedding_model, relation.source_table,
                    relation.source_columns, relation.confidence_score,
                    relation.neo4j_relationship_id, relation.is_active, relation.is_verified
                ))

            results = await conn.fetch(query, *values)
            return [row['id'] for row in results]

        except Exception as e:
            logger.error(f"Failed to batch create relations: {e}")
            raise
        finally:
            await self.release_connection(conn)
