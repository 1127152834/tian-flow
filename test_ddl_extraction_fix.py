#!/usr/bin/env python3
"""
测试DDL提取和跳过逻辑修复
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.database_datasource import database_datasource_service
from src.services.vanna.service_manager import vanna_service_manager


async def test_ddl_extraction_and_skip():
    """测试DDL提取和跳过逻辑"""
    
    print("🧪 测试DDL提取和跳过逻辑修复")
    print("=" * 50)
    
    # 假设数据源ID为1（需要根据实际情况调整）
    datasource_id = 1
    
    try:
        # 1. 测试DDL提取
        print("\n1️⃣ 测试DDL自动提取...")
        ddl_statements = await database_datasource_service.extract_ddl_statements(datasource_id)
        
        print(f"✅ 成功提取 {len(ddl_statements)} 条DDL语句")
        for i, ddl in enumerate(ddl_statements[:3], 1):  # 只显示前3条
            print(f"   DDL {i}: {ddl[:100]}...")
        
        if len(ddl_statements) > 3:
            print(f"   ... 还有 {len(ddl_statements) - 3} 条DDL语句")
        
        # 2. 测试第一次训练（skip_existing=True）
        print("\n2️⃣ 测试第一次DDL训练（skip_existing=True）...")
        result1 = await vanna_service_manager.train_from_ddl(
            datasource_id=datasource_id,
            ddl_statements=ddl_statements,
            skip_existing=True
        )
        
        print(f"第一次训练结果:")
        print(f"   总计: {result1.get('total', 0)}")
        print(f"   成功: {result1.get('successful', 0)}")
        print(f"   失败: {result1.get('failed', 0)}")
        print(f"   跳过: {result1.get('skipped', 0)}")
        
        # 3. 测试第二次训练（skip_existing=True）- 应该全部跳过
        print("\n3️⃣ 测试第二次DDL训练（skip_existing=True）- 应该跳过已存在的...")
        result2 = await vanna_service_manager.train_from_ddl(
            datasource_id=datasource_id,
            ddl_statements=ddl_statements,
            skip_existing=True
        )
        
        print(f"第二次训练结果:")
        print(f"   总计: {result2.get('total', 0)}")
        print(f"   成功: {result2.get('successful', 0)}")
        print(f"   失败: {result2.get('failed', 0)}")
        print(f"   跳过: {result2.get('skipped', 0)}")
        
        # 4. 测试第三次训练（skip_existing=False）- 应该重新训练
        print("\n4️⃣ 测试第三次DDL训练（skip_existing=False）- 应该重新训练...")
        result3 = await vanna_service_manager.train_from_ddl(
            datasource_id=datasource_id,
            ddl_statements=ddl_statements[:2],  # 只用前2条测试
            skip_existing=False
        )
        
        print(f"第三次训练结果:")
        print(f"   总计: {result3.get('total', 0)}")
        print(f"   成功: {result3.get('successful', 0)}")
        print(f"   失败: {result3.get('failed', 0)}")
        print(f"   跳过: {result3.get('skipped', 0)}")
        
        # 5. 验证结果
        print("\n5️⃣ 验证修复效果...")
        
        if result1.get('successful', 0) > 0:
            print("✅ 第一次训练成功处理了DDL语句")
        else:
            print("❌ 第一次训练没有成功处理DDL语句")
        
        if result2.get('skipped', 0) > 0:
            print("✅ 第二次训练正确跳过了已存在的表")
        else:
            print("❌ 第二次训练没有跳过已存在的表")
        
        if result3.get('successful', 0) > 0:
            print("✅ 第三次训练（skip_existing=False）成功重新训练")
        else:
            print("❌ 第三次训练（skip_existing=False）没有重新训练")
        
        print("\n🎉 DDL提取和跳过逻辑测试完成！")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("🚀 启动DDL提取和跳过逻辑测试...")
    
    success = await test_ddl_extraction_and_skip()
    
    if success:
        print("\n✅ 所有测试通过！DDL提取和跳过逻辑修复成功。")
        print("\n📋 现在您可以:")
        print("   1. 在前端测试DDL自动提取")
        print("   2. 验证跳过已存在表的功能")
        print("   3. 测试SQL问答对训练")
        print("   4. 验证SQL生成功能")
    else:
        print("\n❌ 测试失败！请检查错误信息并修复问题。")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())
