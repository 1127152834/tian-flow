#!/usr/bin/env python3

from src.celery_app import celery_app

def check_task_status(task_id):
    """检查特定任务状态"""
    
    print(f"=== 检查任务状态: {task_id} ===")
    
    # 获取任务状态
    task = celery_app.AsyncResult(task_id)
    
    print(f"任务ID: {task_id}")
    print(f"状态: {task.state}")
    print(f"结果: {task.result}")
    print(f"信息: {task.info}")
    
    if task.state == 'PROGRESS':
        print("进度信息:")
        if isinstance(task.info, dict):
            for key, value in task.info.items():
                print(f"  {key}: {value}")
    
    return task

if __name__ == "__main__":
    # 检查当前活跃的任务
    task_id = "a1153bed-627a-4d96-aaa2-5da483a1ab6f"
    check_task_status(task_id)
