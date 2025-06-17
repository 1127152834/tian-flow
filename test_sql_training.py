#!/usr/bin/env python3
"""
测试SQL问答对训练
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.text2sql import Text2SQLService


async def test_sql_training():
    """测试SQL问答对训练"""

    print("🧪 测试SQL问答对训练")
    print("=" * 50)

    # 创建服务实例（在异步上下文中）
    text2sql_service = Text2SQLService()

    # 假设数据源ID为1
    datasource_id = 1
    
    # 准备SQL问答对训练数据
    sql_pairs = [
        {
            "question": "查询所有数据源",
            "sql": "SELECT * FROM database_management.database_datasources;"
        },
        {
            "question": "统计数据源总数",
            "sql": "SELECT COUNT(*) FROM database_management.database_datasources;"
        },
        {
            "question": "查询活跃的数据源",
            "sql": "SELECT * FROM database_management.database_datasources WHERE connection_status = 'CONNECTED';"
        },
        {
            "question": "查询最近创建的数据源",
            "sql": "SELECT * FROM database_management.database_datasources ORDER BY created_at DESC LIMIT 10;"
        },
        {
            "question": "查询所有连接测试记录",
            "sql": "SELECT * FROM database_management.connection_tests ORDER BY tested_at DESC;"
        },
        {
            "question": "统计成功的连接测试",
            "sql": "SELECT COUNT(*) FROM database_management.connection_tests WHERE test_result = true;"
        },
        {
            "question": "查询查询历史",
            "sql": "SELECT * FROM text2sql.query_history ORDER BY created_at DESC LIMIT 20;"
        },
        {
            "question": "统计SQL查询总数",
            "sql": "SELECT COUNT(*) FROM text2sql.sql_queries;"
        },
        {
            "question": "查询训练数据",
            "sql": "SELECT * FROM text2sql.training_data WHERE is_active = true;"
        },
        {
            "question": "查看向量嵌入数据",
            "sql": "SELECT * FROM text2sql.vanna_embeddings ORDER BY created_at DESC LIMIT 10;"
        }
    ]
    
    try:
        # 1. 测试SQL问答对训练
        print("\n1️⃣ 测试SQL问答对训练...")
        result = await text2sql_service.train_sql_pairs(
            datasource_id=datasource_id,
            sql_pairs=sql_pairs
        )
        
        print(f"SQL训练结果:")
        print(f"   总计: {result.get('total', 0)}")
        print(f"   成功: {result.get('successful', 0)}")
        print(f"   失败: {result.get('failed', 0)}")
        
        if result.get('successful', 0) > 0:
            print("✅ SQL问答对训练成功！")
        else:
            print("❌ SQL问答对训练失败！")
            return False
        
        # 2. 测试SQL生成
        print("\n2️⃣ 测试SQL生成...")
        test_questions = [
            "查询所有数据源",
            "统计数据源总数",
            "查询活跃的数据源"
        ]
        
        for question in test_questions:
            try:
                sql_result = await text2sql_service.generate_sql(
                    datasource_id=datasource_id,
                    question=question,
                    include_explanation=True
                )
                
                if sql_result.get('success'):
                    print(f"✅ 问题: '{question}'")
                    print(f"   生成SQL: {sql_result.get('sql', 'N/A')}")
                    print(f"   置信度: {sql_result.get('confidence', 0.0)}")
                else:
                    print(f"❌ 问题: '{question}' - 生成失败: {sql_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ 问题: '{question}' - 异常: {e}")
        
        print("\n🎉 SQL训练和生成测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("🚀 启动SQL问答对训练测试...")
    
    success = await test_sql_training()
    
    if success:
        print("\n✅ SQL训练测试通过！现在应该可以正常生成SQL了。")
        print("\n📋 接下来您可以:")
        print("   1. 在前端测试SQL生成功能")
        print("   2. 验证问答对训练界面")
        print("   3. 测试更多复杂的SQL查询")
    else:
        print("\n❌ SQL训练测试失败！请检查错误信息。")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())
