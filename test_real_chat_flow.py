#!/usr/bin/env python3

"""
测试真实聊天流程，模拟聊天界面的完整工作流
"""

import asyncio
import logging
from src.graph.builder import build_graph_with_memory
from langchain_core.messages import HumanMessage

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_real_chat_flow():
    """测试真实的聊天流程"""
    
    # 构建带内存的图（与聊天界面相同）
    graph = build_graph_with_memory()
    
    # 模拟聊天请求的输入格式
    input_data = {
        "messages": [
            HumanMessage(content="请帮我生成一个图表，显示以下销售数据：1月1000，2月1200，3月1100。请用柱状图显示。")
        ],
        "plan_iterations": 0,
        "final_report": "",
        "current_plan": None,
        "observations": [],
        "auto_accepted_plan": True,  # 自动接受计划，避免中断
        "enable_background_investigation": False,
        "research_topic": "请帮我生成一个图表，显示以下销售数据：1月1000，2月1200，3月1100。请用柱状图显示。",
    }
    
    # 模拟聊天配置
    config = {
        "thread_id": "test_thread_123",
        "resources": [],
        "max_plan_iterations": 3,
        "max_step_num": 3,
        "max_search_results": 5,
        "mcp_settings": None,
        "report_style": "academic",
        "enable_deep_thinking": False,
    }
    
    logger.info("=== 开始测试真实聊天流程 ===")
    logger.info(f"输入消息: {input_data['messages'][0].content}")
    
    try:
        # 使用与聊天界面相同的流式处理方式
        step_count = 0
        async for agent, _, event_data in graph.astream(
            input_data,
            config=config,
            stream_mode=["messages", "updates"],
            subgraphs=True,
        ):
            step_count += 1
            logger.info(f"\n--- 步骤 {step_count} ---")
            logger.info(f"当前智能体: {agent}")
            
            # 检查是否是数据分析师
            if isinstance(agent, tuple) and len(agent) > 0:
                agent_name = agent[0].split(":")[0] if ":" in agent[0] else agent[0]
                logger.info(f"智能体名称: {agent_name}")
                
                if agent_name == "data_analyst":
                    logger.info("✅ 成功！流程路由到了数据分析师")
                    
                    # 检查事件数据
                    if hasattr(event_data, 'content'):
                        content = event_data.content
                        if any(keyword in str(content).lower() for keyword in ['chart', '图表', 'recharts', 'barchart']):
                            logger.info("✅ 数据分析师生成了图表相关内容")
                            logger.info(f"内容预览: {str(content)[:200]}...")
                        else:
                            logger.info(f"数据分析师内容: {content}")
                elif agent_name == "coordinator":
                    logger.info("📍 Coordinator 正在处理...")
                elif agent_name == "planner":
                    logger.warning("⚠️  流程被路由到了 Planner")
                else:
                    logger.info(f"📍 其他智能体: {agent_name}")
            
            # 限制步骤数，避免无限循环
            if step_count > 10:
                logger.warning("达到最大步骤数，停止测试")
                break
                
    except Exception as e:
        logger.error(f"❌ 测试失败，出现异常: {e}")
        import traceback
        traceback.print_exc()

async def test_coordinator_only():
    """单独测试 Coordinator 的路由决策"""
    
    from src.graph.nodes import coordinator_node
    from src.config.configuration import Configuration
    from langchain_core.runnables import RunnableConfig
    
    # 创建测试状态
    test_state = {
        "messages": [
            HumanMessage(content="请帮我生成一个图表，显示以下销售数据：1月1000，2月1200，3月1100。请用柱状图显示。")
        ],
        "locale": "zh-CN",
        "research_topic": "",
        "enable_background_investigation": False,
        "resources": [],
        "observations": [],
        "current_plan": None,
        "final_report": None
    }
    
    # 创建配置
    config = RunnableConfig(
        configurable={
            "max_search_results": 5,
            "max_plan_iterations": 1,
            "max_step_num": 3,
            "enable_background_investigation": False,
            "resources": []
        }
    )
    
    logger.info("\n=== 单独测试 Coordinator ===")
    
    try:
        result = coordinator_node(test_state, config)
        logger.info(f"Coordinator 路由结果: {result.goto}")
        logger.info(f"更新数据: {result.update}")
        
        if result.goto == "data_analyst":
            logger.info("✅ Coordinator 正确路由到数据分析师")
        else:
            logger.error(f"❌ Coordinator 路由到了: {result.goto}")
            
    except Exception as e:
        logger.error(f"❌ Coordinator 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """运行所有测试"""
    logger.info("开始测试真实聊天流程...")
    
    # 先测试 Coordinator
    await test_coordinator_only()
    
    logger.info("\n" + "="*60 + "\n")
    
    # 再测试完整流程
    await test_real_chat_flow()
    
    logger.info("\n测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
