#!/usr/bin/env python3
"""
模拟API调用测试修复后的Vanna集成
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.vanna.service_manager import VannaServiceManager

async def test_api_simulation():
    """模拟API调用测试"""
    print("🧪 模拟API调用测试...")
    
    try:
        # 1. 初始化服务管理器
        print("\n1️⃣ 初始化服务管理器...")
        service_manager = VannaServiceManager()
        
        # 2. 先训练一些数据（模拟训练API调用）
        print("\n2️⃣ 训练数据（模拟训练API调用）...")
        datasource_id = 1
        vanna_instance = service_manager._get_vanna_instance(datasource_id)
        
        # 训练SQL问答对
        training_pairs = [
            {"question": "查一下现在有多少数据库可以使用", "sql": "SELECT COUNT(*) as database_count FROM information_schema.schemata"},
            {"question": "获取所有用户", "sql": "SELECT * FROM users"},
            {"question": "有多少个用户", "sql": "SELECT COUNT(*) FROM users"},
            {"question": "获取活跃用户", "sql": "SELECT * FROM users WHERE active = true"},
            {"question": "今天的订单数量", "sql": "SELECT COUNT(*) FROM orders WHERE DATE(created_at) = CURRENT_DATE"},
            {"question": "数据库列表", "sql": "SHOW DATABASES"},
            {"question": "查看数据库", "sql": "SELECT schema_name FROM information_schema.schemata"}
        ]
        
        for pair in training_pairs:
            result_id = vanna_instance.add_question_sql(
                question=pair["question"],
                sql=pair["sql"]
            )
            print(f"✅ 训练成功: '{pair['question']}' -> ID: {result_id}")
        
        # 3. 测试API调用（模拟实际的API请求）
        print("\n3️⃣ 测试API调用...")
        
        test_questions = [
            "查一下现在有多少数据库可以使用",  # 这是用户实际的问题
            "获取所有用户",
            "有多少个用户",
            "数据库列表",
            "查看数据库"
        ]
        
        for question in test_questions:
            print(f"\n🤔 问题: {question}")
            
            # 模拟API调用
            result = await service_manager.generate_sql(datasource_id, question)
            
            if result["success"]:
                print(f"✅ SQL生成成功: {result['sql']}")
                print(f"   置信度: {result['confidence']}")
                print(f"   生成时间: {result['generation_time']:.3f}秒")
                print(f"   相似SQL数量: {len(result.get('similar_sqls', []))}")
            else:
                print(f"❌ SQL生成失败: {result['error']}")
                print(f"   消息: {result.get('message', 'N/A')}")
        
        # 4. 测试向量存储的内部状态
        print("\n4️⃣ 检查向量存储状态...")
        vector_store = vanna_instance.vector_store
        print(f"训练数据数量: {len(vector_store._vanna_embeddings)}")
        
        for i, record in enumerate(vector_store._vanna_embeddings):
            print(f"  {i+1}. 问题: {record['question']}")
            print(f"     SQL: {record['sql_query']}")
            print(f"     向量维度: {record['embedding_dimension']}")
            print(f"     内容哈希: {record['content_hash'][:16]}...")
        
        print("\n🎉 API模拟测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    success = await test_api_simulation()
    if success:
        print("\n✅ API模拟测试成功！")
    else:
        print("\n❌ API模拟测试失败！")
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
