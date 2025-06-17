#!/usr/bin/env python3

import json
from src.celery_app import celery_app

def check_celery_tasks():
    """检查 Celery 任务状态"""
    
    print("=== Celery 任务状态检查 ===")
    
    # 获取活跃任务
    inspect = celery_app.control.inspect()
    
    # 活跃任务
    active_tasks = inspect.active()
    if active_tasks:
        print(f"✅ 活跃任务:")
        for worker, tasks in active_tasks.items():
            print(f"  Worker: {worker}")
            for task in tasks:
                print(f"    - {task['name']} [{task['id']}]")
                print(f"      参数: {task.get('args', [])}")
                print(f"      开始时间: {task.get('time_start', 'N/A')}")
    else:
        print("❌ 没有活跃任务")
    
    # 预定任务
    scheduled_tasks = inspect.scheduled()
    if scheduled_tasks:
        print(f"\n✅ 预定任务:")
        for worker, tasks in scheduled_tasks.items():
            print(f"  Worker: {worker}")
            for task in tasks:
                print(f"    - {task['request']['name']} [{task['request']['id']}]")
    else:
        print("\n❌ 没有预定任务")
    
    # 保留任务
    reserved_tasks = inspect.reserved()
    if reserved_tasks:
        print(f"\n✅ 保留任务:")
        for worker, tasks in reserved_tasks.items():
            print(f"  Worker: {worker}")
            for task in tasks:
                print(f"    - {task['name']} [{task['id']}]")
    else:
        print("\n❌ 没有保留任务")
    
    # 统计信息
    stats = inspect.stats()
    if stats:
        print(f"\n✅ Worker 统计:")
        for worker, stat in stats.items():
            print(f"  Worker: {worker}")
            print(f"    总任务: {stat.get('total', 'N/A')}")
            print(f"    池大小: {stat.get('pool', {}).get('max-concurrency', 'N/A')}")
            print(f"    进程数: {stat.get('pool', {}).get('processes', 'N/A')}")

if __name__ == "__main__":
    check_celery_tasks()
