"""
资源向量化器

基于 Ti-Flow 的 SmartResourceVectorizer 设计，实现智能资源向量化
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.models.resource_discovery import (
    ResourceVector,
    ResourceVectorCreate,
    VectorType,
    VectorizationStatus
)
from src.llms.embedding import embed_query, get_embedding_dimension

logger = logging.getLogger(__name__)


class ResourceVectorizer:
    """资源向量化器 - 智能向量化资源"""

    def __init__(self, embedding_service=None):
        """
        初始化向量化器

        Args:
            embedding_service: 嵌入服务，用于生成向量（已弃用，使用统一的嵌入服务）
        """
        # 使用统一的嵌入服务
        self.embedding_dimension = get_embedding_dimension("BASE_EMBEDDING")
        self.max_concurrent_tasks = 5
        self.request_timeout = 30.0
        self.batch_delay = 0.1

        logger.info(f"初始化资源向量化器:")
        logger.info(f"  向量维度: {self.embedding_dimension}")
        logger.info(f"  最大并发数: {self.max_concurrent_tasks}")
        logger.info(f"  请求超时: {self.request_timeout}s")
        logger.info(f"  使用统一嵌入服务: BASE_EMBEDDING")
    
    async def vectorize_resource(self, session: Session, resource: Dict[str, Any]) -> Dict[str, Any]:
        """向量化单个资源"""
        try:
            resource_id = resource.get("resource_id")
            resource_type = resource.get("resource_type")
            
            logger.info(f"开始向量化资源: {resource_id} (类型: {resource_type})")
            
            # 根据资源类型选择不同的向量化策略
            if resource_type == "text2sql":
                vectors = await self._vectorize_text2sql_resource(resource)
            else:
                vectors = await self._vectorize_normal_resource(resource)
            
            # 保存向量到数据库
            saved_vectors = []
            for vector_type, vector_data in vectors.items():
                try:
                    vector_record = await self._save_vector_to_db(
                        session, resource_id, vector_type, vector_data
                    )
                    if vector_record:
                        saved_vectors.append(vector_type)
                except Exception as e:
                    logger.error(f"保存向量失败 {resource_id}:{vector_type} - {e}")
            
            # 更新资源的向量化状态
            await self._update_vectorization_status(
                session, resource_id, 
                VectorizationStatus.COMPLETED if saved_vectors else VectorizationStatus.FAILED
            )
            
            result = {
                **resource,
                "vectors": vectors,
                "vectorized_types": saved_vectors,
                "vectorization_status": "completed" if saved_vectors else "failed"
            }
            
            logger.info(f"资源向量化完成: {resource_id}, 生成向量类型: {saved_vectors}")
            return result
            
        except Exception as e:
            logger.error(f"资源向量化失败 {resource.get('resource_id')}: {e}")
            await self._update_vectorization_status(
                session, resource.get("resource_id"), VectorizationStatus.FAILED
            )
            return {**resource, "vectors": {}, "vectorization_status": "failed", "error": str(e)}
    
    async def _vectorize_normal_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """向量化普通资源"""
        vectors = {}
        
        try:
            # 1. 名称向量
            name = resource.get("resource_name", "")
            if name:
                name_vector = await self._get_embedding(name)
                if name_vector:
                    vectors[VectorType.NAME] = {
                        "content": name,
                        "embedding": name_vector
                    }
            
            # 2. 描述向量
            description = resource.get("description", "")
            if description:
                desc_vector = await self._get_embedding(description)
                if desc_vector:
                    vectors[VectorType.DESCRIPTION] = {
                        "content": description,
                        "embedding": desc_vector
                    }
            
            # 3. 能力向量
            capabilities = resource.get("capabilities", [])
            if capabilities:
                capability_text = ", ".join(capabilities)
                cap_vector = await self._get_embedding(capability_text)
                if cap_vector:
                    vectors[VectorType.CAPABILITIES] = {
                        "content": capability_text,
                        "embedding": cap_vector
                    }
            
            # 4. 复合向量 - 综合所有信息
            composite_text = self._build_composite_text(resource)
            if composite_text:
                composite_vector = await self._get_embedding(composite_text)
                if composite_vector:
                    vectors[VectorType.COMPOSITE] = {
                        "content": composite_text,
                        "embedding": composite_vector
                    }
            
            return vectors
            
        except Exception as e:
            logger.error(f"普通资源向量化失败: {e}")
            return {}
    
    async def _vectorize_text2sql_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """向量化 Text2SQL 资源 - 特殊处理"""
        vectors = {}
        
        try:
            metadata = resource.get("metadata", {})
            content_type = metadata.get("content_type", "")
            
            # 根据内容类型生成特殊的复合文本
            if content_type == "DDL":
                composite_text = self._build_ddl_composite_text(resource, metadata)
            elif content_type == "SQL":
                composite_text = self._build_sql_composite_text(resource, metadata)
            else:
                composite_text = self._build_composite_text(resource)
            
            # 生成复合向量
            if composite_text:
                composite_vector = await self._get_embedding(composite_text)
                if composite_vector:
                    vectors[VectorType.COMPOSITE] = {
                        "content": composite_text,
                        "embedding": composite_vector
                    }
            
            # 也生成描述向量
            description = resource.get("description", "")
            if description:
                desc_vector = await self._get_embedding(description)
                if desc_vector:
                    vectors[VectorType.DESCRIPTION] = {
                        "content": description,
                        "embedding": desc_vector
                    }
            
            return vectors
            
        except Exception as e:
            logger.error(f"Text2SQL 资源向量化失败: {e}")
            return {}
    
    def _build_composite_text(self, resource: Dict[str, Any]) -> str:
        """构建复合文本"""
        parts = []
        
        # 添加名称
        name = resource.get("resource_name", "")
        if name:
            parts.append(f"名称: {name}")
        
        # 添加类型
        resource_type = resource.get("resource_type", "")
        if resource_type:
            parts.append(f"类型: {resource_type}")
        
        # 添加描述
        description = resource.get("description", "")
        if description:
            parts.append(f"描述: {description}")
        
        # 添加能力
        capabilities = resource.get("capabilities", [])
        if capabilities:
            parts.append(f"能力: {', '.join(capabilities)}")
        
        # 添加标签
        tags = resource.get("tags", [])
        if tags:
            parts.append(f"标签: {', '.join(tags)}")
        
        return " | ".join(parts)
    
    def _build_ddl_composite_text(self, resource: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """构建 DDL 类型的复合文本"""
        parts = []
        
        parts.append(f"数据库表结构信息")
        parts.append(f"数据源ID: {metadata.get('datasource_id', '')}")
        parts.append(f"内容类型: 表结构定义")
        
        description = resource.get("description", "")
        if description:
            parts.append(description)
        
        capabilities = resource.get("capabilities", [])
        if capabilities:
            parts.append(f"支持功能: {', '.join(capabilities)}")
        
        return " | ".join(parts)
    
    def _build_sql_composite_text(self, resource: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """构建 SQL 类型的复合文本"""
        parts = []
        
        parts.append(f"SQL查询示例")
        parts.append(f"数据源ID: {metadata.get('datasource_id', '')}")
        parts.append(f"内容类型: SQL查询模板")
        
        description = resource.get("description", "")
        if description:
            parts.append(description)
        
        capabilities = resource.get("capabilities", [])
        if capabilities:
            parts.append(f"支持功能: {', '.join(capabilities)}")
        
        return " | ".join(parts)
    
    async def _get_embedding(self, text: str) -> Optional[List[float]]:
        """获取文本的向量嵌入"""
        try:
            if not text or not text.strip():
                logger.warning("空文本，返回零向量")
                return [0.0] * self.embedding_dimension

            # 使用统一的嵌入服务
            vector = embed_query(text.strip(), "BASE_EMBEDDING")

            if not vector or len(vector) != self.embedding_dimension:
                logger.warning(f"向量维度不匹配: 期望 {self.embedding_dimension}, 实际 {len(vector) if vector else 0}")
                return [0.0] * self.embedding_dimension

            return vector

        except Exception as e:
            logger.error(f"获取向量嵌入失败: {e}")
            return [0.0] * self.embedding_dimension
    
    async def _save_vector_to_db(
        self, 
        session: Session, 
        resource_id: str, 
        vector_type: str, 
        vector_data: Dict[str, Any]
    ) -> Optional[ResourceVector]:
        """保存向量到数据库"""
        try:
            # 删除已存在的向量
            delete_query = text("""
                DELETE FROM resource_discovery.resource_vectors 
                WHERE resource_id = :resource_id AND vector_type = :vector_type
            """)
            session.execute(delete_query, {
                "resource_id": resource_id,
                "vector_type": vector_type
            })
            
            # 插入新向量
            insert_query = text("""
                INSERT INTO resource_discovery.resource_vectors 
                (resource_id, vector_type, content, embedding, embedding_dimension, embedding_model_name)
                VALUES (:resource_id, :vector_type, :content, :embedding, :dimension, :model_name)
                RETURNING id
            """)
            
            embedding = vector_data.get("embedding", [])
            result = session.execute(insert_query, {
                "resource_id": resource_id,
                "vector_type": vector_type,
                "content": vector_data.get("content", ""),
                "embedding": embedding,
                "dimension": len(embedding) if embedding else self.embedding_dimension,
                "model_name": "default"
            })
            
            session.commit()
            vector_id = result.fetchone()[0]
            
            logger.debug(f"保存向量成功: {resource_id}:{vector_type} (ID: {vector_id})")
            return vector_id
            
        except Exception as e:
            session.rollback()
            logger.error(f"保存向量失败: {e}")
            return None
    
    async def _update_vectorization_status(
        self, 
        session: Session, 
        resource_id: str, 
        status: VectorizationStatus
    ):
        """更新资源的向量化状态"""
        try:
            update_query = text("""
                UPDATE resource_discovery.resource_registry 
                SET vectorization_status = :status, vector_updated_at = :updated_at
                WHERE resource_id = :resource_id
            """)
            
            session.execute(update_query, {
                "resource_id": resource_id,
                "status": status.value,
                "updated_at": datetime.utcnow()
            })
            session.commit()
            
        except Exception as e:
            session.rollback()
            logger.error(f"更新向量化状态失败: {e}")
    
    async def batch_vectorize_resources(
        self, 
        session: Session, 
        resources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """批量向量化资源"""
        total_resources = len(resources)
        logger.info(f"🚀 开始批量向量化 {total_resources} 个资源")
        
        # 使用信号量限制并发数
        semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        success_count = 0
        error_count = 0
        results = []
        
        async def vectorize_with_semaphore(resource: Dict[str, Any], index: int) -> Dict[str, Any]:
            nonlocal success_count, error_count
            
            async with semaphore:
                try:
                    result = await self.vectorize_resource(session, resource)
                    if result.get("vectorization_status") == "completed":
                        success_count += 1
                    else:
                        error_count += 1
                    
                    # 显示进度
                    if (index + 1) % 5 == 0 or (index + 1) == total_resources:
                        progress = (index + 1) / total_resources * 100
                        logger.info(f"⏳ 进度: {progress:.0f}% ({index + 1}/{total_resources})")
                    
                    return result
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"向量化失败 {resource.get('resource_id')}: {e}")
                    return {**resource, "vectorization_status": "failed", "error": str(e)}
        
        # 并发执行向量化任务
        tasks = [
            vectorize_with_semaphore(resource, i) 
            for i, resource in enumerate(resources)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        final_results = []
        for result in results:
            if isinstance(result, Exception):
                error_count += 1
                logger.error(f"向量化任务异常: {result}")
            else:
                final_results.append(result)
        
        logger.info(f"✅ 批量向量化完成: 成功 {success_count}, 失败 {error_count}")
        return final_results
