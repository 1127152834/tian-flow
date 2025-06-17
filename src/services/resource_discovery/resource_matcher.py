"""
资源匹配器

基于 Ti-Flow 的 IntentMatcher 设计，实现智能资源匹配
"""

import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.models.resource_discovery import (
    ResourceMatch,
    ResourceRegistryResponse,
    ResourceMatchHistory,
    ResourceMatchHistoryCreate,
    UserFeedback
)
from src.llms.embedding import embed_query

logger = logging.getLogger(__name__)


class ResourceMatcher:
    """资源匹配器 - 基于向量相似度的智能匹配"""
    
    def __init__(self, embedding_service=None):
        """
        初始化匹配器

        Args:
            embedding_service: 嵌入服务（已弃用，使用统一的嵌入服务）
        """
        self.similarity_threshold = 0.3
        self.confidence_weights = {
            "similarity": 0.6,
            "usage_history": 0.2,
            "performance": 0.1,
            "context": 0.1
        }

        logger.info(f"初始化资源匹配器:")
        logger.info(f"  相似度阈值: {self.similarity_threshold}")
        logger.info(f"  置信度权重: {self.confidence_weights}")
        logger.info(f"  使用统一嵌入服务: BASE_EMBEDDING")
    
    async def match_resources(
        self, 
        session: Session,
        user_query: str, 
        top_k: int = 5,
        resource_types: Optional[List[str]] = None,
        min_confidence: float = 0.3
    ) -> List[ResourceMatch]:
        """匹配用户查询到最相关的资源"""
        
        try:
            start_time = datetime.utcnow()
            
            # 1. 向量化查询
            query_vector = await self._get_query_embedding(user_query)
            if not query_vector:
                logger.warning("查询向量化失败")
                return []
            
            # 2. 向量相似度搜索
            similar_resources = await self._search_similar_resources(
                session, query_vector, top_k * 2, resource_types
            )
            
            if not similar_resources:
                logger.info("未找到相似资源")
                return []
            
            # 3. 智能重排序和置信度计算
            ranked_matches = await self._intelligent_rerank(
                session, user_query, similar_resources
            )
            
            # 4. 过滤低置信度结果
            filtered_matches = [
                match for match in ranked_matches 
                if match.confidence_score >= min_confidence
            ]
            
            # 5. 返回前 top_k 个结果
            final_matches = filtered_matches[:top_k]
            
            # 6. 记录匹配历史
            await self._record_match_history(
                session, user_query, final_matches, 
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )
            
            logger.info(f"匹配完成: 查询='{user_query}', 结果数={len(final_matches)}")
            return final_matches
            
        except Exception as e:
            logger.error(f"资源匹配失败: {e}")
            return []
    
    async def _get_query_embedding(self, query: str) -> Optional[List[float]]:
        """获取查询的向量嵌入"""
        try:
            if not query or not query.strip():
                logger.warning("空查询，返回零向量")
                return [0.0] * 1536

            # 使用统一的嵌入服务
            vector = embed_query(query.strip(), "BASE_EMBEDDING")

            if not vector:
                logger.error("嵌入服务返回空向量")
                return [0.0] * 1536

            return vector

        except Exception as e:
            logger.error(f"查询向量化失败: {e}")
            return [0.0] * 1536
    
    async def _search_similar_resources(
        self, 
        session: Session,
        query_vector: List[float], 
        limit: int,
        resource_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """向量相似度搜索"""
        try:
            # 构建查询条件
            type_condition = ""
            if resource_types:
                type_placeholders = ", ".join([f"'{t}'" for t in resource_types])
                type_condition = f"AND rr.resource_type IN ({type_placeholders})"
            
            # 向量相似度搜索查询 - 使用 CAST 确保类型匹配
            query_sql = text(f"""
                SELECT
                    rr.resource_id,
                    rr.resource_name,
                    rr.resource_type,
                    rr.description,
                    rr.capabilities,
                    rr.tags,
                    rr.metadata,
                    rr.usage_count,
                    rr.success_rate,
                    rr.avg_response_time,
                    rv.vector_type,
                    rv.content,
                    1 - (rv.embedding <=> CAST(:query_vector AS vector)) as similarity_score
                FROM resource_discovery.resource_registry rr
                JOIN resource_discovery.resource_vectors rv ON rr.resource_id = rv.resource_id
                WHERE rr.is_active = true
                AND rr.status = 'active'
                AND rv.vector_type = 'composite'
                {type_condition}
                ORDER BY rv.embedding <=> CAST(:query_vector AS vector)
                LIMIT :limit_num
            """)
            
            result = session.execute(query_sql, {
                "query_vector": query_vector,
                "limit_num": limit
            })
            
            resources = []
            for row in result.fetchall():
                resource = {
                    "resource_id": row.resource_id,
                    "resource_name": row.resource_name,
                    "resource_type": row.resource_type,
                    "description": row.description,
                    "capabilities": row.capabilities,
                    "tags": row.tags,
                    "metadata": row.metadata,
                    "usage_count": row.usage_count,
                    "success_rate": row.success_rate,
                    "avg_response_time": row.avg_response_time,
                    "vector_type": row.vector_type,
                    "vector_content": row.content,
                    "similarity_score": float(row.similarity_score)
                }
                resources.append(resource)
            
            logger.info(f"向量搜索找到 {len(resources)} 个相似资源")
            return resources
            
        except Exception as e:
            logger.error(f"向量相似度搜索失败: {e}")
            return []
    
    async def _intelligent_rerank(
        self, 
        session: Session,
        user_query: str, 
        resources: List[Dict[str, Any]]
    ) -> List[ResourceMatch]:
        """智能重排序和置信度计算"""
        matches = []
        
        for resource in resources:
            try:
                # 1. 基础相似度分数
                similarity_score = resource.get("similarity_score", 0.0)
                
                # 2. 使用历史偏好
                usage_boost = await self._calculate_usage_preference(session, resource)
                
                # 3. 性能指标加权
                performance_boost = self._calculate_performance_score(resource)
                
                # 4. 上下文相关性
                context_boost = await self._calculate_context_relevance(user_query, resource)
                
                # 5. 综合置信度计算
                confidence_score = (
                    similarity_score * self.confidence_weights["similarity"] +
                    usage_boost * self.confidence_weights["usage_history"] +
                    performance_boost * self.confidence_weights["performance"] +
                    context_boost * self.confidence_weights["context"]
                )
                
                # 6. 生成匹配推理
                reasoning = self._generate_match_reasoning(
                    user_query, resource, similarity_score, confidence_score
                )
                
                # 7. 创建匹配结果
                match = ResourceMatch(
                    resource=ResourceRegistryResponse(**{
                        k: v for k, v in resource.items() 
                        if k in ResourceRegistryResponse.__fields__
                    }),
                    similarity_score=similarity_score,
                    confidence_score=confidence_score,
                    reasoning=reasoning,
                    final_score=confidence_score
                )
                
                matches.append(match)
                
            except Exception as e:
                logger.error(f"重排序失败 {resource.get('resource_id')}: {e}")
        
        # 按置信度分数排序
        matches.sort(key=lambda x: x.confidence_score, reverse=True)
        return matches
    
    async def _calculate_usage_preference(self, session: Session, resource: Dict[str, Any]) -> float:
        """计算使用历史偏好分数"""
        try:
            resource_id = resource.get("resource_id")
            
            # 查询最近的使用统计
            query = text("""
                SELECT AVG(user_selections::float / GREATEST(total_matches, 1)) as selection_rate
                FROM resource_discovery.resource_usage_stats
                WHERE resource_id = :resource_id
                AND stats_date >= CURRENT_DATE - INTERVAL '30 days'
            """)
            
            result = session.execute(query, {"resource_id": resource_id})
            row = result.fetchone()
            
            if row and row.selection_rate is not None:
                return min(float(row.selection_rate), 1.0)
            
            return 0.5  # 默认中等偏好
            
        except Exception as e:
            logger.error(f"计算使用偏好失败: {e}")
            return 0.5
    
    def _calculate_performance_score(self, resource: Dict[str, Any]) -> float:
        """计算性能分数"""
        try:
            success_rate = resource.get("success_rate", 1.0)
            avg_response_time = resource.get("avg_response_time", 0)
            
            # 成功率权重 0.7，响应时间权重 0.3
            success_score = success_rate
            
            # 响应时间分数 (越快越好，超过5秒开始扣分)
            if avg_response_time <= 1000:  # 1秒以内
                time_score = 1.0
            elif avg_response_time <= 5000:  # 5秒以内
                time_score = 1.0 - (avg_response_time - 1000) / 4000 * 0.3
            else:  # 超过5秒
                time_score = 0.7 - min((avg_response_time - 5000) / 10000, 0.5)
            
            return success_score * 0.7 + time_score * 0.3
            
        except Exception as e:
            logger.error(f"计算性能分数失败: {e}")
            return 0.8
    
    async def _calculate_context_relevance(self, user_query: str, resource: Dict[str, Any]) -> float:
        """计算上下文相关性分数"""
        try:
            query_lower = user_query.lower()
            
            # 检查查询中的关键词是否在资源信息中出现
            relevance_score = 0.0
            
            # 检查资源名称
            resource_name = resource.get("resource_name", "").lower()
            if any(word in resource_name for word in query_lower.split()):
                relevance_score += 0.3
            
            # 检查描述
            description = resource.get("description", "").lower()
            if any(word in description for word in query_lower.split()):
                relevance_score += 0.2
            
            # 检查能力
            capabilities = resource.get("capabilities", [])
            capability_text = " ".join(capabilities).lower()
            if any(word in capability_text for word in query_lower.split()):
                relevance_score += 0.3
            
            # 检查标签
            tags = resource.get("tags", [])
            tag_text = " ".join(tags).lower()
            if any(word in tag_text for word in query_lower.split()):
                relevance_score += 0.2
            
            return min(relevance_score, 1.0)
            
        except Exception as e:
            logger.error(f"计算上下文相关性失败: {e}")
            return 0.5
    
    def _generate_match_reasoning(
        self, 
        user_query: str, 
        resource: Dict[str, Any], 
        similarity_score: float,
        confidence_score: float
    ) -> str:
        """生成匹配推理说明"""
        try:
            resource_name = resource.get("resource_name", "")
            resource_type = resource.get("resource_type", "")
            
            reasoning_parts = []
            
            # 相似度说明
            if similarity_score > 0.8:
                reasoning_parts.append(f"与查询高度相似 (相似度: {similarity_score:.2f})")
            elif similarity_score > 0.6:
                reasoning_parts.append(f"与查询较为相似 (相似度: {similarity_score:.2f})")
            else:
                reasoning_parts.append(f"与查询部分相似 (相似度: {similarity_score:.2f})")
            
            # 资源类型说明
            reasoning_parts.append(f"资源类型: {resource_type}")
            
            # 能力匹配说明
            capabilities = resource.get("capabilities", [])
            if capabilities:
                reasoning_parts.append(f"支持功能: {', '.join(capabilities[:3])}")
            
            # 置信度说明
            if confidence_score > 0.8:
                reasoning_parts.append("高置信度推荐")
            elif confidence_score > 0.6:
                reasoning_parts.append("中等置信度推荐")
            else:
                reasoning_parts.append("低置信度推荐")
            
            return " | ".join(reasoning_parts)
            
        except Exception as e:
            logger.error(f"生成匹配推理失败: {e}")
            return f"匹配资源: {resource.get('resource_name', 'Unknown')}"
    
    async def _record_match_history(
        self, 
        session: Session,
        user_query: str, 
        matches: List[ResourceMatch],
        response_time: float
    ):
        """记录匹配历史"""
        try:
            # 生成查询哈希
            query_hash = hashlib.md5(user_query.encode()).hexdigest()
            
            # 提取匹配结果信息
            matched_resource_ids = [match.resource.resource_id for match in matches]
            similarity_scores = [match.similarity_score for match in matches]
            confidence_scores = [match.confidence_score for match in matches]
            
            # 创建匹配历史记录
            history_data = ResourceMatchHistoryCreate(
                user_query=user_query,
                query_hash=query_hash,
                matched_resource_ids=matched_resource_ids,
                similarity_scores=similarity_scores,
                confidence_scores=confidence_scores,
                response_time=response_time,
                reasoning={
                    "total_matches": len(matches),
                    "avg_similarity": sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0,
                    "avg_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
                }
            )
            
            # 保存到数据库
            insert_query = text("""
                INSERT INTO resource_discovery.resource_match_history 
                (user_query, query_hash, matched_resource_ids, similarity_scores, 
                 confidence_scores, reasoning, response_time)
                VALUES (:user_query, :query_hash, :matched_resource_ids, :similarity_scores,
                        :confidence_scores, :reasoning, :response_time)
            """)
            
            session.execute(insert_query, {
                "user_query": user_query,
                "query_hash": query_hash,
                "matched_resource_ids": matched_resource_ids,
                "similarity_scores": similarity_scores,
                "confidence_scores": confidence_scores,
                "reasoning": history_data.reasoning,
                "response_time": response_time
            })
            session.commit()
            
            logger.debug(f"记录匹配历史成功: {query_hash}")
            
        except Exception as e:
            session.rollback()
            logger.error(f"记录匹配历史失败: {e}")
