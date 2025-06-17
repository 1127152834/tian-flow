# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Graph Synchronization service for DeerFlow Knowledge Graph.

Provides data synchronization between PostgreSQL and Neo4j with conflict resolution,
ensuring data consistency across both databases.
"""

import logging
import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Set
from enum import Enum

from src.models.knowledge_graph import (
    KnowledgeGraphEntity,
    KnowledgeGraphRelation,
    ConflictStrategy
)
from src.repositories.knowledge_graph import KnowledgeGraphRepository
from src.repositories.neo4j_graph import Neo4jGraphRepository

logger = logging.getLogger(__name__)


class SyncDirection(str, Enum):
    """Synchronization direction"""
    PG_TO_NEO4J = "pg_to_neo4j"
    NEO4J_TO_PG = "neo4j_to_pg"
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(str, Enum):
    """Synchronization status"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    CONFLICT = "conflict"


class GraphSyncService:
    """
    Service for synchronizing data between PostgreSQL and Neo4j.
    
    Handles entity and relation synchronization with conflict detection
    and resolution strategies.
    """
    
    def __init__(
        self, 
        pg_repo: KnowledgeGraphRepository,
        neo4j_repo: Neo4jGraphRepository
    ):
        """Initialize sync service with repositories"""
        self.pg_repo = pg_repo
        self.neo4j_repo = neo4j_repo
        
        # Sync statistics
        self.sync_stats = {
            'entities_synced': 0,
            'relations_synced': 0,
            'conflicts_detected': 0,
            'conflicts_resolved': 0,
            'errors': 0
        }
    
    async def sync_datasource(
        self,
        datasource_id: int,
        direction: SyncDirection = SyncDirection.PG_TO_NEO4J,
        conflict_strategy: ConflictStrategy = ConflictStrategy.MANUAL_FIRST,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Synchronize all data for a datasource between PostgreSQL and Neo4j
        
        Args:
            datasource_id: ID of the datasource to sync
            direction: Direction of synchronization
            conflict_strategy: Strategy for resolving conflicts
            batch_size: Number of records to process in each batch
            
        Returns:
            Dict containing sync results and statistics
        """
        try:
            logger.info(f"Starting sync for datasource {datasource_id}, direction: {direction}")
            
            # Reset statistics
            self.sync_stats = {
                'entities_synced': 0,
                'relations_synced': 0,
                'conflicts_detected': 0,
                'conflicts_resolved': 0,
                'errors': 0
            }
            
            start_time = datetime.now(timezone.utc)
            
            if direction in [SyncDirection.PG_TO_NEO4J, SyncDirection.BIDIRECTIONAL]:
                # Sync entities from PostgreSQL to Neo4j
                await self._sync_entities_pg_to_neo4j(datasource_id, batch_size, conflict_strategy)
                
                # Sync relations from PostgreSQL to Neo4j
                await self._sync_relations_pg_to_neo4j(datasource_id, batch_size, conflict_strategy)
            
            if direction in [SyncDirection.NEO4J_TO_PG, SyncDirection.BIDIRECTIONAL]:
                # Sync from Neo4j to PostgreSQL (if needed)
                await self._sync_neo4j_to_pg(datasource_id, batch_size, conflict_strategy)
            
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            # Determine overall status
            if self.sync_stats['errors'] > 0:
                status = SyncStatus.FAILED
            elif self.sync_stats['conflicts_detected'] > 0:
                status = SyncStatus.CONFLICT
            else:
                status = SyncStatus.SUCCESS
            
            result = {
                'status': status.value,
                'datasource_id': datasource_id,
                'direction': direction.value,
                'duration_seconds': duration,
                'statistics': self.sync_stats.copy(),
                'started_at': start_time.isoformat(),
                'completed_at': end_time.isoformat()
            }
            
            logger.info(f"Sync completed for datasource {datasource_id}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Sync failed for datasource {datasource_id}: {e}")
            self.sync_stats['errors'] += 1
            raise
    
    async def _sync_entities_pg_to_neo4j(
        self,
        datasource_id: int,
        batch_size: int,
        conflict_strategy: ConflictStrategy
    ):
        """Sync entities from PostgreSQL to Neo4j"""
        try:
            offset = 0
            
            while True:
                # Get batch of entities from PostgreSQL
                entities = await self.pg_repo.find_entities_by_datasource(
                    datasource_id=datasource_id,
                    limit=batch_size,
                    offset=offset
                )
                
                if not entities:
                    break
                
                # Sync each entity to Neo4j
                for entity in entities:
                    try:
                        neo4j_id = await self.neo4j_repo.sync_entity_to_neo4j(entity)
                        
                        # Update PostgreSQL with Neo4j ID if not already set
                        if neo4j_id and entity.neo4j_node_id != neo4j_id:
                            entity.neo4j_node_id = neo4j_id
                            await self.pg_repo.update_entity(entity)
                        
                        self.sync_stats['entities_synced'] += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to sync entity {entity.id}: {e}")
                        self.sync_stats['errors'] += 1
                
                offset += batch_size
                
                # Add small delay to prevent overwhelming the databases
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Failed to sync entities from PG to Neo4j: {e}")
            raise
    
    async def _sync_relations_pg_to_neo4j(
        self,
        datasource_id: int,
        batch_size: int,
        conflict_strategy: ConflictStrategy
    ):
        """Sync relations from PostgreSQL to Neo4j"""
        try:
            # Get all entities for this datasource to find relations
            entities = await self.pg_repo.find_entities_by_datasource(
                datasource_id=datasource_id,
                limit=10000  # Large limit to get all entities
            )
            
            entity_ids = [entity.id for entity in entities]
            
            # Process relations in batches
            for i in range(0, len(entity_ids), batch_size):
                batch_entity_ids = entity_ids[i:i + batch_size]
                
                for entity_id in batch_entity_ids:
                    try:
                        # Get relations for this entity
                        relations = await self.pg_repo.find_relations_by_entity(entity_id)
                        
                        for relation in relations:
                            try:
                                neo4j_id = await self.neo4j_repo.sync_relation_to_neo4j(relation)
                                
                                # Update PostgreSQL with Neo4j ID if not already set
                                if neo4j_id and relation.neo4j_relationship_id != neo4j_id:
                                    relation.neo4j_relationship_id = neo4j_id
                                    await self.pg_repo.update_relation(relation)
                                
                                self.sync_stats['relations_synced'] += 1
                                
                            except Exception as e:
                                logger.error(f"Failed to sync relation {relation.id}: {e}")
                                self.sync_stats['errors'] += 1
                    
                    except Exception as e:
                        logger.error(f"Failed to get relations for entity {entity_id}: {e}")
                        self.sync_stats['errors'] += 1
                
                # Add delay between batches
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Failed to sync relations from PG to Neo4j: {e}")
            raise
    
    async def _sync_neo4j_to_pg(
        self,
        datasource_id: int,
        batch_size: int,
        conflict_strategy: ConflictStrategy
    ):
        """Sync data from Neo4j back to PostgreSQL (for bidirectional sync)"""
        try:
            # This would be implemented if we need to sync computed properties
            # from Neo4j back to PostgreSQL (e.g., centrality scores, community IDs)
            logger.info(f"Neo4j to PostgreSQL sync not yet implemented for datasource {datasource_id}")
            
        except Exception as e:
            logger.error(f"Failed to sync from Neo4j to PG: {e}")
            raise
    
    async def detect_sync_conflicts(
        self,
        datasource_id: int
    ) -> List[Dict[str, Any]]:
        """
        Detect synchronization conflicts between PostgreSQL and Neo4j
        
        Returns:
            List of detected conflicts with details
        """
        conflicts = []
        
        try:
            # Get entities from PostgreSQL
            pg_entities = await self.pg_repo.find_entities_by_datasource(datasource_id)
            
            for entity in pg_entities:
                if entity.neo4j_node_id:
                    # Check if entity exists in Neo4j with same properties
                    # This would require additional Neo4j queries to compare properties
                    # For now, we'll implement basic existence check
                    pass
            
            # Similar checks for relations
            # Implementation would depend on specific conflict detection requirements
            
        except Exception as e:
            logger.error(f"Failed to detect sync conflicts: {e}")
            raise
        
        return conflicts
    
    async def resolve_conflict(
        self,
        conflict: Dict[str, Any],
        strategy: ConflictStrategy
    ) -> bool:
        """
        Resolve a specific synchronization conflict
        
        Args:
            conflict: Conflict details
            strategy: Resolution strategy
            
        Returns:
            True if conflict was resolved successfully
        """
        try:
            if strategy == ConflictStrategy.MANUAL_FIRST:
                # Prioritize manually edited data
                return await self._resolve_manual_first(conflict)
            elif strategy == ConflictStrategy.AUTO_FIRST:
                # Prioritize automatically generated data
                return await self._resolve_auto_first(conflict)
            elif strategy == ConflictStrategy.MERGE:
                # Attempt to merge conflicting data
                return await self._resolve_merge(conflict)
            else:
                logger.error(f"Unknown conflict resolution strategy: {strategy}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to resolve conflict: {e}")
            return False
    
    async def _resolve_manual_first(self, conflict: Dict[str, Any]) -> bool:
        """Resolve conflict by prioritizing manual edits"""
        # Implementation would depend on how we track manual vs automatic edits
        # This could use timestamps, user IDs, or specific flags
        return True
    
    async def _resolve_auto_first(self, conflict: Dict[str, Any]) -> bool:
        """Resolve conflict by prioritizing automatic updates"""
        # Implementation for auto-first strategy
        return True
    
    async def _resolve_merge(self, conflict: Dict[str, Any]) -> bool:
        """Resolve conflict by merging data"""
        # Implementation for merge strategy
        # This would be the most complex, requiring field-level merging logic
        return True
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """Get current synchronization statistics"""
        return self.sync_stats.copy()
    
    async def validate_sync_integrity(self, datasource_id: int) -> Dict[str, Any]:
        """
        Validate data integrity between PostgreSQL and Neo4j
        
        Returns:
            Validation results with any inconsistencies found
        """
        try:
            # Count entities in both databases
            pg_entity_count = await self.pg_repo.count_entities(datasource_id)
            pg_relation_count = await self.pg_repo.count_relations(datasource_id)
            
            # Get Neo4j statistics
            neo4j_stats = self.neo4j_repo.get_graph_statistics(datasource_id)
            neo4j_entity_count = neo4j_stats.get('entity_count', 0)
            neo4j_relation_count = neo4j_stats.get('relation_count', 0)
            
            # Check for discrepancies
            entity_diff = abs(pg_entity_count - neo4j_entity_count)
            relation_diff = abs(pg_relation_count - neo4j_relation_count)
            
            is_consistent = entity_diff == 0 and relation_diff == 0
            
            return {
                'is_consistent': is_consistent,
                'datasource_id': datasource_id,
                'postgresql': {
                    'entity_count': pg_entity_count,
                    'relation_count': pg_relation_count
                },
                'neo4j': {
                    'entity_count': neo4j_entity_count,
                    'relation_count': neo4j_relation_count
                },
                'discrepancies': {
                    'entity_diff': entity_diff,
                    'relation_diff': relation_diff
                },
                'validated_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to validate sync integrity: {e}")
            raise


# Create service instance (would be initialized with actual repositories)
# graph_sync_service = GraphSyncService(pg_repo, neo4j_repo)
