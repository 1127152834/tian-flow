"""
资源发现工具

为 Olight Agent 提供智能资源发现和匹配功能
"""

import logging
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.database import get_database_config
from src.services.resource_discovery import (
    ResourceDiscoveryService,
    ResourceMatcher,
    ResourceSynchronizer
)
from src.tools.decorators import tool

logger = logging.getLogger(__name__)


def get_database_session():
    """获取数据库会话"""
    db_config = get_database_config()
    engine = create_engine(
        f"postgresql://{db_config['user']}:{db_config['password']}@"
        f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


@tool
async def discover_resources(
    user_query: str,
    max_results: int = 5,
    resource_types: Optional[List[str]] = None,
    min_confidence: float = 0.3
) -> Dict[str, Any]:
    """
    智能资源发现工具
    
    根据用户查询找到最匹配的系统资源，包括数据库、API、工具等。
    
    Args:
        user_query: 用户查询描述，例如 "查询用户数据" 或 "获取天气信息"
        max_results: 最大返回结果数，默认5个
        resource_types: 限制的资源类型列表，可选值: ["database", "api", "tool", "text2sql"]
        min_confidence: 最小置信度阈值，默认0.3
    
    Returns:
        包含匹配资源列表和相关信息的字典
    """
    try:
        logger.info(f"🔍 开始资源发现: '{user_query}'")
        
        # 获取数据库会话
        session = get_database_session()
        
        try:
            # 初始化服务（现在使用统一的嵌入服务）
            matcher = ResourceMatcher()
            
            # 执行资源匹配
            matches = await matcher.match_resources(
                session=session,
                user_query=user_query,
                top_k=max_results,
                resource_types=resource_types,
                min_confidence=min_confidence
            )
            
            # 转换结果为简化格式
            simplified_matches = []
            for match in matches:
                simplified_match = {
                    "resource_id": match.resource.resource_id,
                    "resource_name": match.resource.resource_name,
                    "resource_type": match.resource.resource_type,
                    "description": match.resource.description,
                    "capabilities": match.resource.capabilities,
                    "similarity_score": round(match.similarity_score, 3),
                    "confidence_score": round(match.confidence_score, 3),
                    "reasoning": match.reasoning
                }
                simplified_matches.append(simplified_match)
            
            result = {
                "success": True,
                "query": user_query,
                "matches": simplified_matches,
                "total_matches": len(simplified_matches),
                "search_parameters": {
                    "max_results": max_results,
                    "resource_types": resource_types,
                    "min_confidence": min_confidence
                }
            }
            
            logger.info(f"✅ 资源发现完成: 找到 {len(simplified_matches)} 个匹配资源")
            return result
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"❌ 资源发现失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": user_query,
            "matches": []
        }


@tool
async def sync_system_resources(force_full_sync: bool = False) -> Dict[str, Any]:
    """
    同步系统资源
    
    扫描系统中的所有资源（数据库、API、工具等）并更新资源注册表。
    
    Args:
        force_full_sync: 是否强制全量同步，默认False（增量同步）
    
    Returns:
        同步结果信息
    """
    try:
        logger.info(f"🔄 开始资源同步: force_full={force_full_sync}")
        
        # 获取数据库会话
        session = get_database_session()
        
        try:
            # 初始化服务（现在使用统一的嵌入服务）
            synchronizer = ResourceSynchronizer()
            
            # 执行同步
            result = await synchronizer.sync_and_vectorize_incremental(
                session=session,
                force_full_sync=force_full_sync
            )
            
            logger.info(f"✅ 资源同步完成: {result.get('message', 'Success')}")
            return result
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"❌ 资源同步失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"资源同步失败: {str(e)}"
        }


@tool
async def get_resource_statistics() -> Dict[str, Any]:
    """
    获取资源统计信息
    
    返回系统中各类资源的统计数据，包括总数、状态分布等。
    
    Returns:
        资源统计信息
    """
    try:
        logger.info("📊 获取资源统计信息")
        
        # 获取数据库会话
        session = get_database_session()
        
        try:
            from sqlalchemy import text
            
            # 资源统计
            resource_stats_query = text("""
                SELECT 
                    resource_type,
                    COUNT(*) as total_count,
                    COUNT(*) FILTER (WHERE is_active = true) as active_count,
                    COUNT(*) FILTER (WHERE vectorization_status = 'completed') as vectorized_count
                FROM resource_discovery.resource_registry
                GROUP BY resource_type
                ORDER BY resource_type
            """)
            
            result = session.execute(resource_stats_query)
            resource_stats = {}
            total_resources = 0
            total_active = 0
            total_vectorized = 0
            
            for row in result.fetchall():
                resource_stats[row.resource_type] = {
                    "total": row.total_count,
                    "active": row.active_count,
                    "vectorized": row.vectorized_count
                }
                total_resources += row.total_count
                total_active += row.active_count
                total_vectorized += row.vectorized_count
            
            # 最近操作统计
            recent_operations_query = text("""
                SELECT 
                    operation_type,
                    status,
                    COUNT(*) as count
                FROM resource_discovery.system_status
                WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY operation_type, status
                ORDER BY operation_type, status
            """)
            
            result = session.execute(recent_operations_query)
            recent_operations = {}
            
            for row in result.fetchall():
                if row.operation_type not in recent_operations:
                    recent_operations[row.operation_type] = {}
                recent_operations[row.operation_type][row.status] = row.count
            
            statistics = {
                "success": True,
                "summary": {
                    "total_resources": total_resources,
                    "active_resources": total_active,
                    "vectorized_resources": total_vectorized,
                    "vectorization_rate": round(total_vectorized / total_resources * 100, 1) if total_resources > 0 else 0
                },
                "by_type": resource_stats,
                "recent_operations": recent_operations,
                "generated_at": "now"
            }
            
            logger.info(f"✅ 统计信息获取完成: {total_resources} 个资源")
            return statistics
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"❌ 获取统计信息失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "summary": {
                "total_resources": 0,
                "active_resources": 0,
                "vectorized_resources": 0,
                "vectorization_rate": 0
            }
        }


@tool
async def search_resources_by_type(
    resource_type: str,
    limit: int = 10
) -> Dict[str, Any]:
    """
    按类型搜索资源
    
    获取指定类型的所有资源列表。
    
    Args:
        resource_type: 资源类型，可选值: "database", "api", "tool", "text2sql"
        limit: 返回数量限制，默认10个
    
    Returns:
        指定类型的资源列表
    """
    try:
        logger.info(f"🔍 按类型搜索资源: {resource_type}")
        
        # 获取数据库会话
        session = get_database_session()
        
        try:
            from sqlalchemy import text
            
            query = text("""
                SELECT resource_id, resource_name, description, capabilities, 
                       tags, is_active, status, vectorization_status
                FROM resource_discovery.resource_registry
                WHERE resource_type = :resource_type
                AND is_active = true
                ORDER BY created_at DESC
                LIMIT :limit
            """)
            
            result = session.execute(query, {
                "resource_type": resource_type,
                "limit": limit
            })
            
            resources = []
            for row in result.fetchall():
                resource = {
                    "resource_id": row.resource_id,
                    "resource_name": row.resource_name,
                    "description": row.description,
                    "capabilities": row.capabilities,
                    "tags": row.tags,
                    "is_active": row.is_active,
                    "status": row.status,
                    "vectorization_status": row.vectorization_status
                }
                resources.append(resource)
            
            result_data = {
                "success": True,
                "resource_type": resource_type,
                "resources": resources,
                "total_found": len(resources),
                "limit": limit
            }
            
            logger.info(f"✅ 类型搜索完成: 找到 {len(resources)} 个 {resource_type} 资源")
            return result_data
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"❌ 类型搜索失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "resource_type": resource_type,
            "resources": []
        }
