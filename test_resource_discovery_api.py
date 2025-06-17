#!/usr/bin/env python3
"""
测试资源发现 API 接口
"""

import asyncio
import json
from src.services.resource_discovery.resource_matcher import ResourceMatcher
from src.database import get_db_session

async def test_resource_matching():
    """测试资源匹配功能"""
    print("🧪 测试资源发现匹配功能")
    
    # 获取数据库会话
    session = next(get_db_session())
    
    try:
        # 初始化资源匹配器
        matcher = ResourceMatcher()
        
        # 测试查询
        test_queries = [
            "查询数据库中的用户信息",
            "调用API获取产品数据", 
            "执行SQL统计分析",
            "获取订单相关信息"
        ]
        
        for query in test_queries:
            print(f"\n🔍 测试查询: '{query}'")
            
            try:
                # 执行资源匹配
                matches = await matcher.match_resources(
                    session=session,
                    user_query=query,
                    top_k=5,
                    min_confidence=0.1
                )
                
                if matches:
                    print(f"✅ 找到 {len(matches)} 个匹配资源:")
                    for i, match in enumerate(matches, 1):
                        confidence_level = "low"
                        if match.confidence_score >= 0.8:
                            confidence_level = "high"
                        elif match.confidence_score >= 0.6:
                            confidence_level = "medium"
                        
                        print(f"  {i}. {match.resource.resource_name}")
                        print(f"     类型: {match.resource.resource_type}")
                        print(f"     相似度: {match.similarity_score:.3f}")
                        print(f"     置信度: {match.confidence_score:.3f} ({confidence_level})")
                        print(f"     描述: {match.resource.description}")
                        print()
                else:
                    print("❌ 未找到匹配的资源")
                    
            except Exception as e:
                print(f"❌ 查询失败: {e}")
                
    finally:
        session.close()

async def test_api_response_format():
    """测试 API 响应格式"""
    print("\n🔧 测试 API 响应格式")
    
    session = next(get_db_session())
    
    try:
        matcher = ResourceMatcher()
        
        # 模拟 API 请求
        request = {
            "query": "查询数据库中的用户信息",
            "top_k": 3,
            "min_confidence": 0.1,
            "resource_types": None
        }
        
        print(f"📤 请求参数: {json.dumps(request, ensure_ascii=False, indent=2)}")
        
        # 执行匹配
        matches = await matcher.match_resources(
            session=session,
            user_query=request["query"],
            top_k=request["top_k"],
            min_confidence=request["min_confidence"],
            resource_types=request["resource_types"]
        )
        
        # 格式化响应
        formatted_matches = []
        for match in matches:
            confidence_level = "low"
            if match.confidence_score >= 0.8:
                confidence_level = "high"
            elif match.confidence_score >= 0.6:
                confidence_level = "medium"
            
            formatted_match = {
                "resource_id": match.resource.resource_id,
                "resource_name": match.resource.resource_name,
                "resource_type": match.resource.resource_type,
                "description": match.resource.description or "",
                "capabilities": match.resource.capabilities or [],
                "similarity_score": round(match.similarity_score, 3),
                "confidence_score": round(match.confidence_score, 3),
                "confidence": confidence_level,
                "reasoning": f"基于向量相似度匹配，相似度: {match.similarity_score:.3f}",
                "detailed_scores": {
                    "similarity": round(match.similarity_score, 3),
                    "confidence": round(match.confidence_score, 3)
                }
            }
            formatted_matches.append(formatted_match)
        
        # 构建完整响应
        response_data = {
            "query": request["query"],
            "total_matches": len(formatted_matches),
            "matches": formatted_matches,
            "best_match": formatted_matches[0] if formatted_matches else None,
            "processing_time": 0.123,  # 模拟处理时间
            "parameters": {
                "top_k": request["top_k"],
                "min_confidence": request["min_confidence"],
                "resource_types": request["resource_types"]
            }
        }
        
        api_response = {
            "success": True,
            "data": response_data
        }
        
        print(f"📥 API 响应: {json.dumps(api_response, ensure_ascii=False, indent=2)}")
        
    finally:
        session.close()

async def main():
    """主函数"""
    print("=" * 60)
    print("🚀 DeerFlow 资源发现 API 测试")
    print("=" * 60)
    
    # 测试资源匹配
    await test_resource_matching()
    
    # 测试 API 响应格式
    await test_api_response_format()
    
    print("\n✅ 测试完成!")
    print("\n💡 提示:")
    print("1. 前端页面地址: http://localhost:3000/zh/resource-discovery")
    print("2. API 接口地址: http://localhost:8000/api/resource-discovery/test-match")
    print("3. 确保后端服务器正常运行")

if __name__ == "__main__":
    asyncio.run(main())
