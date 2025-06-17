#!/usr/bin/env python3

from src.celery_app import celery_app

def cancel_task(task_id):
    """取消任务"""
    
    print(f"=== 取消任务: {task_id} ===")
    
    # 撤销任务
    celery_app.control.revoke(task_id, terminate=True)
    
    # 检查任务状态
    task = celery_app.AsyncResult(task_id)
    print(f"任务状态: {task.state}")
    
    return task

if __name__ == "__main__":
    # 取消当前运行的任务
    task_id = "a1153bed-627a-4d96-aaa2-5da483a1ab6f"
    cancel_task(task_id)
