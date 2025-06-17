#!/usr/bin/env python3
"""
测试智能路由功能
"""

import asyncio
import json
from src.graph.builder import build_graph_with_memory
from langchain_core.messages import HumanMessage

async def test_smart_routing():
    """测试智能路由功能"""
    graph = build_graph_with_memory()
    
    # 测试场景
    test_cases = [
        {
            "name": "问候测试",
            "message": "你好",
            "user_settings": {"enableBackgroundInvestigation": False},
            "expected_route": "__end__"
        },
        {
            "name": "图表请求测试",
            "message": "请帮我生成一个图表，显示销售数据",
            "user_settings": {"enableBackgroundInvestigation": False},
            "expected_route": "data_analyst"
        },
        {
            "name": "研究模式开启测试",
            "message": "请研究一下人工智能的发展历史",
            "user_settings": {"enableBackgroundInvestigation": True},
            "expected_route": "planner"
        },
        {
            "name": "研究模式关闭测试",
            "message": "分析一下当前的经济形势",
            "user_settings": {"enableBackgroundInvestigation": False},
            "expected_route": "data_analyst"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 测试: {test_case['name']}")
        print(f"📝 消息: {test_case['message']}")
        print(f"⚙️ 设置: {test_case['user_settings']}")
        
        # 构建输入
        input_data = {
            "messages": [HumanMessage(content=test_case["message"])],
            "plan_iterations": 0,
            "final_report": "",
            "current_plan": None,
            "observations": [],
            "auto_accepted_plan": False,
            "enable_background_investigation": test_case["user_settings"]["enableBackgroundInvestigation"],
            "research_topic": test_case["message"],
        }
        
        # 配置
        config = {
            "configurable": {
                "thread_id": f"test_{test_case['name'].replace(' ', '_')}",
                "resources": [],
                "max_plan_iterations": 1,
                "max_step_num": 3,
                "max_search_results": 3,
                "mcp_settings": {},
                "report_style": "academic",
                "enable_deep_thinking": False,
                "user_settings": test_case["user_settings"],
            }
        }
        
        try:
            # 执行单步
            result = await graph.ainvoke(input_data, config=config)
            
            # 检查结果
            print(f"✅ 执行成功")
            if "final_report" in result:
                print(f"📊 最终报告: {result['final_report'][:100]}...")
            
        except Exception as e:
            print(f"❌ 执行失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_smart_routing())
