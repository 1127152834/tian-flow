#!/usr/bin/env python3
"""
测试资源发现的 Celery 任务功能

这个脚本测试：
1. 启动资源同步任务
2. 监控任务进度
3. 获取任务结果
4. 验证资源发现功能
"""

import time
import requests
import json
from typing import Dict, Any

def test_sync_task():
    """测试资源同步任务"""
    print("🔄 启动资源同步任务...")
    
    # 启动同步任务
    response = requests.post("http://localhost:8000/api/resource-discovery/sync?force_full_sync=false")
    
    if response.status_code != 200:
        print(f"❌ 启动任务失败: {response.status_code} - {response.text}")
        return None
    
    result = response.json()
    print(f"✅ 任务已启动: {result}")
    
    task_id = result.get('task_id')
    if not task_id:
        print("❌ 没有获取到任务ID")
        return None
    
    return task_id

def monitor_task(task_id: str, max_wait_seconds: int = 120):
    """监控任务进度"""
    print(f"👀 监控任务进度: {task_id}")
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait_seconds:
        try:
            response = requests.get(f"http://localhost:8000/api/resource-discovery/tasks/{task_id}/status")
            
            if response.status_code != 200:
                print(f"❌ 获取任务状态失败: {response.status_code}")
                time.sleep(2)
                continue
            
            status_data = response.json()
            status = status_data.get('status', 'UNKNOWN')
            
            print(f"📊 任务状态: {status}")
            
            if status == 'SUCCESS':
                result = status_data.get('result', {})
                print(f"✅ 任务完成: {result.get('message', 'No message')}")
                print(f"📈 处理结果: {result.get('processed_changes', {})}")
                print(f"⏱️  处理时间: {result.get('total_processing_time', 'Unknown')}")
                return True
            elif status == 'FAILURE':
                print(f"❌ 任务失败: {status_data.get('result', 'Unknown error')}")
                return False
            elif status in ['PENDING', 'STARTED', 'RETRY']:
                print(f"⏳ 任务进行中...")
                time.sleep(3)
            else:
                print(f"🤔 未知状态: {status}")
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ 监控任务时出错: {e}")
            time.sleep(2)
    
    print(f"⏰ 监控超时 ({max_wait_seconds}秒)")
    return False

def test_resource_discovery():
    """测试资源发现功能"""
    print("🔍 测试资源发现功能...")
    
    test_queries = [
        "查询数据库",
        "API管理",
        "文本转SQL",
        "系统工具"
    ]
    
    for query in test_queries:
        print(f"\n🔎 查询: '{query}'")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/resource-discovery/discover",
                json={
                    "user_query": query,
                    "max_results": 3,
                    "min_confidence": 0.1
                }
            )
            
            if response.status_code != 200:
                print(f"❌ 查询失败: {response.status_code} - {response.text}")
                continue
            
            result = response.json()
            matches = result.get('matches', [])
            
            print(f"📊 找到 {len(matches)} 个匹配资源:")
            for i, match in enumerate(matches[:3], 1):
                print(f"  {i}. {match.get('resource_name', 'Unknown')} "
                      f"({match.get('resource_type', 'Unknown')}) "
                      f"- 置信度: {match.get('confidence_score', 0):.2f}")
                
        except Exception as e:
            print(f"❌ 查询 '{query}' 时出错: {e}")

def test_statistics():
    """测试统计信息"""
    print("\n📊 获取统计信息...")
    
    try:
        response = requests.get("http://localhost:8000/api/resource-discovery/statistics")
        
        if response.status_code != 200:
            print(f"❌ 获取统计信息失败: {response.status_code}")
            return
        
        stats = response.json()
        resource_stats = stats.get('resource_statistics', {})
        
        print("📈 资源统计:")
        total_resources = 0
        total_active = 0
        total_vectorized = 0
        
        for resource_type, counts in resource_stats.items():
            total = counts.get('total', 0)
            active = counts.get('active', 0)
            vectorized = counts.get('vectorized', 0)
            
            total_resources += total
            total_active += active
            total_vectorized += vectorized
            
            print(f"  {resource_type}: {total} 总计, {active} 活跃, {vectorized} 已向量化")
        
        print(f"\n🎯 总计: {total_resources} 资源, {total_active} 活跃, {total_vectorized} 已向量化")
        
        match_stats = stats.get('match_statistics', {})
        print(f"🔍 查询统计: {match_stats.get('total_queries', 0)} 次查询, "
              f"平均响应时间: {match_stats.get('avg_response_time', 0):.2f}ms")
        
    except Exception as e:
        print(f"❌ 获取统计信息时出错: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试资源发现 Celery 任务功能\n")
    
    # 1. 测试同步任务
    task_id = test_sync_task()
    if not task_id:
        print("❌ 无法启动同步任务，退出测试")
        return
    
    print()
    
    # 2. 监控任务进度
    success = monitor_task(task_id)
    if not success:
        print("❌ 任务执行失败或超时")
        return
    
    print()
    
    # 3. 测试统计信息
    test_statistics()
    
    # 4. 测试资源发现
    test_resource_discovery()
    
    print("\n🎉 所有测试完成！")

if __name__ == "__main__":
    main()
