#!/usr/bin/env python3

"""
测试图结构是否正确
"""

import asyncio
import logging
from src.graph.builder import build_graph_with_memory
from langchain_core.messages import HumanMessage

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_graph_structure():
    """测试图结构"""
    
    # 构建图
    graph = build_graph_with_memory()
    
    logger.info("=== 图结构信息 ===")
    logger.info(f"节点: {list(graph.nodes.keys())}")
    
    # 检查是否包含数据分析师节点
    if "data_analyst" in graph.nodes:
        logger.info("✅ 数据分析师节点已添加到图中")
    else:
        logger.error("❌ 数据分析师节点未找到")
    
    # 测试简单的流程
    input_data = {
        "messages": [
            HumanMessage(content="请帮我生成一个图表，显示以下销售数据：1月1000，2月1200，3月1100。请用柱状图显示。")
        ],
        "plan_iterations": 0,
        "final_report": "",
        "current_plan": None,
        "observations": [],
        "auto_accepted_plan": True,
        "enable_background_investigation": False,
        "research_topic": "请帮我生成一个图表，显示以下销售数据：1月1000，2月1200，3月1100。请用柱状图显示。",
    }
    
    config = {
        "thread_id": "test_thread_456",
        "resources": [],
        "max_plan_iterations": 1,
        "max_step_num": 1,
        "max_search_results": 3,
        "mcp_settings": None,
        "report_style": "academic",
        "enable_deep_thinking": False,
    }
    
    logger.info("\n=== 测试图执行 ===")
    
    try:
        step_count = 0
        found_data_analyst = False
        
        async for agent, _, event_data in graph.astream(
            input_data,
            config=config,
            stream_mode=["messages", "updates"],
            subgraphs=True,
        ):
            step_count += 1
            logger.info(f"步骤 {step_count}: {agent}")
            
            if isinstance(agent, tuple) and len(agent) > 0:
                agent_name = agent[0].split(":")[0] if ":" in agent[0] else agent[0]
                
                if agent_name == "data_analyst":
                    found_data_analyst = True
                    logger.info("✅ 成功路由到数据分析师！")
                    
                    # 检查内容
                    if hasattr(event_data, 'content'):
                        content = str(event_data.content)
                        if any(keyword in content.lower() for keyword in ['chart', '图表', 'recharts', 'barchart']):
                            logger.info("✅ 数据分析师生成了图表内容")
                        logger.info(f"内容长度: {len(content)}")
                    break
            
            # 限制步骤数
            if step_count > 5:
                break
        
        if found_data_analyst:
            logger.info("✅ 图结构和路由工作正常")
        else:
            logger.error("❌ 未能路由到数据分析师")
            
    except Exception as e:
        logger.error(f"❌ 图执行失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """运行测试"""
    logger.info("开始测试图结构...")
    await test_graph_structure()
    logger.info("测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
