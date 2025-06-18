#!/usr/bin/env python3
"""
直接查询测试 - 绕过智能体，直接使用工具
"""

from src.tools.text2sql_tools import smart_text2sql_query
import json

def direct_query(question: str):
    """直接执行查询，返回清洁的结果"""
    
    print(f"🔍 执行查询: {question}")
    
    # 直接调用工具
    result = smart_text2sql_query.invoke({
        'question': question,
        'database_id': 8,
        'auto_chart': True,
        'chart_title': f'查询结果: {question[:20]}...'
    })
    
    # 解析结果
    try:
        result_data = json.loads(result)
        
        if result_data.get('success'):
            print("✅ 查询成功！")
            
            data = result_data.get('data', {})
            sql = data.get('sql', '')
            results = data.get('results', [])
            total_rows = data.get('total_rows', 0)
            
            print(f"📊 生成的SQL: {sql}")
            print(f"📈 返回行数: {total_rows}")
            
            if results:
                print("📋 查询结果（前5行）:")
                for i, row in enumerate(results[:5]):
                    print(f"  {i+1}. {row}")
            else:
                print("📋 查询结果: 无数据")
                
            # 检查图表信息
            chart_info = data.get('chart_info', {})
            if chart_info.get('status') == 'generating':
                print(f"📊 图表生成中: {chart_info.get('type', '未知')}类型")
            
            return {
                'success': True,
                'sql': sql,
                'results': results,
                'total_rows': total_rows,
                'chart_info': chart_info
            }
        else:
            print(f"❌ 查询失败: {result_data.get('message', '未知错误')}")
            return {'success': False, 'error': result_data.get('error')}
            
    except json.JSONDecodeError as e:
        print(f"❌ 结果解析失败: {e}")
        return {'success': False, 'error': '结果格式错误'}

if __name__ == "__main__":
    # 测试查询
    test_questions = [
        "查看今天仓库收料（入库）信息",
        "统计今日入库物料数量",
        "显示仓库收货情况"
    ]
    
    for question in test_questions:
        print("=" * 60)
        result = direct_query(question)
        print(f"结果: {result.get('success', False)}")
        print()
