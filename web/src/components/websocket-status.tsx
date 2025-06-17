'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Badge } from '~/components/ui/badge';
import { Button } from '~/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '~/components/ui/tooltip';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '~/components/ui/popover';
import { Wifi, WifiOff, Activity, AlertCircle, CheckCircle } from 'lucide-react';

interface WebSocketStats {
  total_connections: number;
  active_tasks: number;
  task_connections: Record<string, number>;
}

interface WebSocketStatusProps {
  className?: string;
}

export function WebSocketStatus({ className }: WebSocketStatusProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const [stats, setStats] = useState<WebSocketStats | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // 获取 WebSocket 统计信息
  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/ws/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data.data);
        setLastUpdate(new Date());
      }
    } catch (error) {
      console.error('获取WebSocket统计失败:', error);
    }
  };

  // 连接到全局监听器
  const connectWebSocket = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // 已经连接
    }

    setConnectionStatus('connecting');
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    const port = '8000';
    const wsUrl = `${protocol}//${host}:${port}/api/ws/progress/global_listener`;
    
    console.log('连接全局WebSocket监听器:', wsUrl);
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('全局WebSocket连接已建立');
      setIsConnected(true);
      setConnectionStatus('connected');
      setReconnectAttempts(0);
      fetchStats();
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('收到全局WebSocket消息:', data);
        setLastUpdate(new Date());
        
        // 可以在这里处理全局消息，比如任务完成通知等
        if (data.type === 'task_completed') {
          // 刷新统计信息
          fetchStats();
        }
      } catch (error) {
        console.error('解析WebSocket消息失败:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('全局WebSocket错误:', error);
      setConnectionStatus('error');
      setIsConnected(false);
    };

    ws.onclose = (event) => {
      console.log('全局WebSocket连接已关闭:', event.code, event.reason);
      setIsConnected(false);
      setConnectionStatus('disconnected');
      wsRef.current = null;

      // 自动重连逻辑
      if (event.code !== 1000) { // 非正常关闭
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000); // 指数退避，最大30秒
        console.log(`${delay}ms后尝试重连...`);
        
        reconnectTimeoutRef.current = setTimeout(() => {
          setReconnectAttempts(prev => prev + 1);
          connectWebSocket();
        }, delay);
      }
    };
  };

  // 手动重连
  const handleReconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    setReconnectAttempts(0);
    connectWebSocket();
  };

  // 断开连接
  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close(1000, '用户主动断开');
    }
  };

  // 组件挂载时连接
  useEffect(() => {
    connectWebSocket();
    
    // 定期获取统计信息
    const statsInterval = setInterval(fetchStats, 10000); // 每10秒更新一次

    return () => {
      clearInterval(statsInterval);
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      disconnect();
    };
  }, []);

  // 获取状态图标和颜色
  const getStatusInfo = () => {
    switch (connectionStatus) {
      case 'connected':
        return {
          icon: <Wifi className="h-3 w-3" />,
          color: 'bg-green-500',
          text: '已连接',
          variant: 'default' as const
        };
      case 'connecting':
        return {
          icon: <Activity className="h-3 w-3 animate-pulse" />,
          color: 'bg-yellow-500',
          text: '连接中',
          variant: 'secondary' as const
        };
      case 'error':
        return {
          icon: <AlertCircle className="h-3 w-3" />,
          color: 'bg-red-500',
          text: '连接错误',
          variant: 'destructive' as const
        };
      default:
        return {
          icon: <WifiOff className="h-3 w-3" />,
          color: 'bg-gray-500',
          text: '未连接',
          variant: 'outline' as const
        };
    }
  };

  const statusInfo = getStatusInfo();

  return (
    <TooltipProvider>
      <Popover>
        <Tooltip>
          <TooltipTrigger asChild>
            <PopoverTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className={`h-8 px-2 ${className}`}
              >
                <div className="flex items-center gap-2">
                  <div className="relative">
                    {statusInfo.icon}
                    <div 
                      className={`absolute -top-1 -right-1 w-2 h-2 rounded-full ${statusInfo.color}`}
                    />
                  </div>
                  <span className="text-xs font-medium hidden sm:inline">
                    WebSocket
                  </span>
                </div>
              </Button>
            </PopoverTrigger>
          </TooltipTrigger>
          <TooltipContent>
            <p>WebSocket连接状态: {statusInfo.text}</p>
          </TooltipContent>
        </Tooltip>

        <PopoverContent className="w-80" align="end">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-medium">WebSocket 连接状态</h4>
              <Badge variant={statusInfo.variant}>
                {statusInfo.text}
              </Badge>
            </div>

            {/* 连接信息 */}
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">状态:</span>
                <span className="flex items-center gap-1">
                  {statusInfo.icon}
                  {statusInfo.text}
                </span>
              </div>
              
              {reconnectAttempts > 0 && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">重连次数:</span>
                  <span>{reconnectAttempts}</span>
                </div>
              )}

              {lastUpdate && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">最后更新:</span>
                  <span>{lastUpdate.toLocaleTimeString()}</span>
                </div>
              )}
            </div>

            {/* 统计信息 */}
            {stats && (
              <div className="border-t pt-3 space-y-2">
                <h5 className="font-medium text-sm">连接统计</h5>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">总连接数:</span>
                    <span>{stats.total_connections}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">活跃任务:</span>
                    <span>{stats.active_tasks}</span>
                  </div>
                  {Object.keys(stats.task_connections).length > 0 && (
                    <div className="mt-2">
                      <span className="text-muted-foreground text-xs">任务连接:</span>
                      <div className="mt-1 space-y-1">
                        {Object.entries(stats.task_connections).map(([taskId, count]) => (
                          <div key={taskId} className="flex justify-between text-xs">
                            <span className="truncate max-w-32" title={taskId}>
                              {taskId === 'global_listener' ? '全局监听器' : taskId}
                            </span>
                            <span>{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* 操作按钮 */}
            <div className="flex gap-2 pt-2 border-t">
              {connectionStatus === 'connected' ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={disconnect}
                  className="flex-1"
                >
                  断开连接
                </Button>
              ) : (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleReconnect}
                  className="flex-1"
                >
                  重新连接
                </Button>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={fetchStats}
                className="flex-1"
              >
                刷新统计
              </Button>
            </div>
          </div>
        </PopoverContent>
      </Popover>
    </TooltipProvider>
  );
}
