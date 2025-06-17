#!/usr/bin/env python3
"""
测试修复后的Vanna集成
按照ti-flow的逻辑进行测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.vanna.service_manager import VannaServiceManager
from src.services.vanna.vector_store import PgVectorStore
from src.services.vanna.database_adapter import DatabaseAdapter

async def test_vanna_training_and_generation():
    """测试Vanna训练和SQL生成（按照ti-flow逻辑）"""
    print("🧪 测试修复后的Vanna集成...")
    
    try:
        # 1. 初始化Vanna服务管理器
        print("\n1️⃣ 初始化Vanna服务管理器...")
        service_manager = VannaServiceManager()
        
        # 2. 获取Vanna实例
        print("\n2️⃣ 获取Vanna实例...")
        datasource_id = 1
        vanna_instance = service_manager._get_vanna_instance(datasource_id)
        print(f"✅ Vanna实例创建成功: {type(vanna_instance)}")
        
        # 3. 测试DDL训练（按照ti-flow逻辑）
        print("\n3️⃣ 测试DDL训练...")
        ddl_statements = [
            "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100), active BOOLEAN DEFAULT true)",
            "CREATE TABLE orders (id INT PRIMARY KEY, user_id INT, amount DECIMAL(10,2), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
            "CREATE TABLE products (id INT PRIMARY KEY, name VARCHAR(100), price DECIMAL(10,2), category VARCHAR(50))"
        ]
        
        for ddl in ddl_statements:
            result_id = vanna_instance.add_ddl(ddl)
            print(f"✅ DDL训练成功: {ddl[:50]}... -> ID: {result_id}")
        
        # 4. 测试SQL问答对训练（按照ti-flow逻辑）
        print("\n4️⃣ 测试SQL问答对训练...")
        sql_pairs = [
            {"question": "获取所有用户", "sql": "SELECT * FROM users"},
            {"question": "有多少个用户", "sql": "SELECT COUNT(*) FROM users"},
            {"question": "获取活跃用户", "sql": "SELECT * FROM users WHERE active = true"},
            {"question": "今天的订单数量", "sql": "SELECT COUNT(*) FROM orders WHERE DATE(created_at) = CURRENT_DATE"},
            {"question": "获取所有产品", "sql": "SELECT * FROM products"},
            {"question": "价格超过100的产品", "sql": "SELECT * FROM products WHERE price > 100"}
        ]
        
        for pair in sql_pairs:
            result_id = vanna_instance.add_question_sql(
                question=pair["question"],
                sql=pair["sql"]
            )
            print(f"✅ SQL训练成功: '{pair['question']}' -> ID: {result_id}")
        
        # 5. 测试SQL生成（按照ti-flow逻辑）
        print("\n5️⃣ 测试SQL生成...")
        test_questions = [
            "获取所有用户",
            "有多少个用户",
            "获取活跃用户", 
            "今天的订单数量",
            "获取所有产品",
            "价格超过100的产品",
            "显示用户信息",  # 测试相似匹配
            "用户总数是多少"  # 测试相似匹配
        ]
        
        for question in test_questions:
            print(f"\n🤔 问题: {question}")
            
            # 使用get_similar_question_sql获取相似SQL（按照ti-flow逻辑）
            similar_sqls = vanna_instance.get_similar_question_sql(question, limit=3)
            
            if similar_sqls:
                print(f"✅ 找到 {len(similar_sqls)} 个相似SQL:")
                for i, sql in enumerate(similar_sqls, 1):
                    print(f"   {i}. {sql}")
                
                # 使用最相似的SQL作为结果（按照ti-flow逻辑）
                best_sql = similar_sqls[0]
                print(f"🎯 最佳SQL: {best_sql}")
            else:
                print("❌ 未找到相似的SQL")
        
        # 6. 测试服务管理器的generate_sql方法
        print("\n6️⃣ 测试服务管理器的generate_sql方法...")
        test_questions_for_service = [
            "获取所有用户",
            "有多少个用户", 
            "今天的订单数量",
            "没有训练过的问题"  # 测试未训练数据的情况
        ]
        
        for question in test_questions_for_service:
            print(f"\n🤔 问题: {question}")
            result = await service_manager.generate_sql(datasource_id, question)
            
            if result["success"]:
                print(f"✅ SQL生成成功: {result['sql']}")
                print(f"   置信度: {result['confidence']}")
                print(f"   生成时间: {result['generation_time']:.3f}秒")
            else:
                print(f"❌ SQL生成失败: {result['error']}")
        
        print("\n🎉 所有测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    success = await test_vanna_training_and_generation()
    if success:
        print("\n✅ Vanna集成测试成功！")
    else:
        print("\n❌ Vanna集成测试失败！")
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
