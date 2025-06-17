#!/usr/bin/env python3
"""
测试WebSocket实时进度推送
"""

import asyncio
import websockets
import json
import requests
import time

async def test_websocket_with_task():
    """测试WebSocket连接和任务同步"""
    
    print("🧪 开始WebSocket + 任务同步测试")
    
    # 1. 先启动任务
    print("📤 启动资源同步任务...")
    response = requests.post("http://localhost:8000/api/resource-discovery/sync?force_full_sync=true")
    
    if response.status_code != 200:
        print(f"❌ 启动任务失败: {response.status_code}")
        return
        
    task_data = response.json()
    task_id = task_data.get('task_id')
    
    if not task_id:
        print("❌ 未获取到任务ID")
        return
        
    print(f"✅ 任务已启动: {task_id}")
    
    # 2. 立即建立WebSocket连接
    uri = f'ws://localhost:8000/api/ws/progress/{task_id}'
    print(f"🔌 连接WebSocket: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功")
            
            # 3. 监听进度消息
            message_count = 0
            start_time = time.time()
            
            while True:
                try:
                    # 等待消息，超时时间设置长一点
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    message_count += 1
                    
                    try:
                        data = json.loads(message)
                        progress = data.get('progress', 0)
                        status = data.get('status', '未知')
                        msg = data.get('message', '无')
                        step = data.get('current_step', '')
                        
                        elapsed = time.time() - start_time
                        print(f"📨 消息 {message_count} ({elapsed:.1f}s): 进度={progress}%, 状态={status}, 步骤={step}, 消息={msg}")
                        
                        # 如果任务完成，退出
                        if status in ['completed', 'failed']:
                            print(f"🏁 任务{status}，退出监听")
                            break
                            
                    except json.JSONDecodeError:
                        print(f"📨 消息 {message_count}: {message}")
                        
                except asyncio.TimeoutError:
                    # 检查任务状态
                    status_response = requests.get(f"http://localhost:8000/api/resource-discovery/sync/status/{task_id}")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        task_status = status_data.get('status', '未知')
                        elapsed = time.time() - start_time
                        print(f"⏰ 超时 ({elapsed:.1f}s): 任务状态={task_status}")
                        
                        if task_status in ['completed', 'failed']:
                            print(f"🏁 任务已{task_status}，但WebSocket未收到消息")
                            break
                    else:
                        print("❌ 无法获取任务状态")
                        break
                        
                except Exception as e:
                    print(f"❌ 接收消息异常: {e}")
                    break
                    
            print(f"📊 总共收到 {message_count} 条WebSocket消息")
            
    except Exception as e:
        print(f"❌ WebSocket连接失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_with_task())
