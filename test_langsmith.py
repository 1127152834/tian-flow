#!/usr/bin/env python3
"""
LangSmith追踪测试脚本

测试LangSmith是否正确集成到DeerFlow系统中
"""

import asyncio
import logging
from src.config.langsmith import setup_langsmith_tracing, is_langsmith_enabled, log_langsmith_status
from src.graph.builder import build_graph_with_memory

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_langsmith_integration():
    """测试LangSmith集成"""
    
    print("🔍 LangSmith集成测试")
    print("=" * 50)
    
    # 1. 检查LangSmith状态
    print("1. 检查LangSmith状态...")
    setup_langsmith_tracing()
    log_langsmith_status()
    
    if not is_langsmith_enabled():
        print("❌ LangSmith未启用，测试终止")
        return
    
    print("✅ LangSmith已启用")
    print()
    
    # 2. 构建图
    print("2. 构建工作流图...")
    try:
        graph = build_graph_with_memory()
        print("✅ 图构建成功")
        print(f"   可用节点: {list(graph.nodes.keys())}")
    except Exception as e:
        print(f"❌ 图构建失败: {e}")
        return
    
    print()
    
    # 3. 测试简单的数据查询（会路由到数据分析师）
    print("3. 测试数据分析师路由...")
    test_query = "查询数据库列表"
    
    try:
        # 准备初始状态
        initial_state = {
            "messages": [{"role": "user", "content": test_query}],
            "locale": "zh-CN"
        }
        
        # 配置
        config = {
            "configurable": {
                "thread_id": "langsmith-test-001",
            },
            "recursion_limit": 10,
        }
        
        print(f"   查询: {test_query}")
        print("   执行中...")
        
        # 执行工作流
        result = await graph.ainvoke(initial_state, config)
        
        print("✅ 工作流执行成功")
        print(f"   最终消息数量: {len(result.get('messages', []))}")
        
        # 显示最后的响应
        if result.get('messages'):
            last_message = result['messages'][-1]
            if hasattr(last_message, 'content'):
                content = last_message.content
            else:
                content = str(last_message)
            
            print(f"   最后响应预览: {content[:100]}...")
        
    except Exception as e:
        print(f"❌ 工作流执行失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    print("🎉 LangSmith集成测试完成！")
    print()
    print("📊 查看追踪数据:")
    print("   1. 打开 LangSmith Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024")
    print("   2. 或访问 LangSmith 项目: https://smith.langchain.com/o/bb84a9af-2b70-4578-9510-7b9bcca06599/p/olight-manufacturing-intelligence")
    print("   3. 查找线程ID: langsmith-test-001")


if __name__ == "__main__":
    asyncio.run(test_langsmith_integration())
