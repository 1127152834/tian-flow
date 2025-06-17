// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { Search, Database, Activity } from "lucide-react";
import { useState, useEffect } from "react";
import { useLanguage } from "~/contexts/language-context";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Badge } from "~/components/ui/badge";
import { Separator } from "~/components/ui/separator";
import { toast } from "sonner";
import { resourceDiscoveryApi, type ResourceRegistryResponse } from "~/core/api/resource-discovery";

// 系统概览组件
function SystemOverview() {
  const { t } = useLanguage();
  const [stats, setStats] = useState({
    totalResources: 0,
    activeResources: 0,
    vectorizedResources: 0,
    avgResponseTime: 0
  });
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncTaskId, setSyncTaskId] = useState<string | null>(null);
  const [syncProgress, setSyncProgress] = useState(0);
  const [syncMessage, setSyncMessage] = useState('');
  const [syncStep, setSyncStep] = useState('');
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);

  useEffect(() => {
    fetchStatistics();
  }, []);

  // WebSocket连接管理
  const connectWebSocket = (taskId: string) => {
    // 关闭现有连接
    if (websocket) {
      websocket.close();
    }

    // 创建新的WebSocket连接
    const wsUrl = `ws://localhost:8000/api/ws/progress/${taskId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket连接已建立:', taskId);
      setWebsocket(ws);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('收到WebSocket消息:', data);

        // 更新进度信息
        setSyncProgress(data.progress || 0);
        setSyncMessage(data.message || '');
        setSyncStep(data.current_step || '');

        if (data.status === 'completed') {
          setSyncing(false);
          setSyncTaskId(null);
          setSyncProgress(100);
          setSyncMessage('同步完成');
          toast.success('同步完成', {
            description: '资源同步和向量化已完成'
          });
          fetchStatistics();
          ws.close();
        } else if (data.status === 'failed') {
          setSyncing(false);
          setSyncTaskId(null);
          setSyncProgress(0);
          setSyncMessage('同步失败');
          toast.error('同步失败', {
            description: data.error || '同步过程中发生错误'
          });
          ws.close();
        }
      } catch (error) {
        console.error('解析WebSocket消息失败:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket错误:', error);
      toast.error('连接错误', {
        description: '无法建立实时连接，将使用轮询方式'
      });
      // 回退到轮询方式
      fallbackToPolling(taskId);
    };

    ws.onclose = () => {
      console.log('WebSocket连接已关闭');
      setWebsocket(null);
    };
  };

  // 回退到轮询方式
  const fallbackToPolling = (taskId: string) => {
    const interval = setInterval(async () => {
      try {
        const taskStatus = await resourceDiscoveryApi.getTaskStatus(taskId);

        setSyncProgress(taskStatus.progress || 0);
        setSyncMessage(taskStatus.message || '');
        setSyncStep(taskStatus.current_step || '');

        if (taskStatus.status === 'completed') {
          setSyncing(false);
          setSyncTaskId(null);
          setSyncProgress(100);
          setSyncMessage('同步完成');
          toast.success('同步完成', {
            description: '资源同步和向量化已完成'
          });
          fetchStatistics();
          clearInterval(interval);
        } else if (taskStatus.status === 'failed') {
          setSyncing(false);
          setSyncTaskId(null);
          setSyncProgress(0);
          setSyncMessage('同步失败');
          toast.error('同步失败', {
            description: taskStatus.error || '同步过程中发生错误'
          });
          clearInterval(interval);
        }
      } catch (error) {
        console.error('轮询检查任务状态失败:', error);
      }
    }, 2000);

    // 清理函数
    setTimeout(() => clearInterval(interval), 300000); // 5分钟后停止轮询
  };

  // 监控同步任务进度
  useEffect(() => {
    if (syncTaskId && syncing) {
      // 优先使用WebSocket
      connectWebSocket(syncTaskId);
    }

    // 清理函数
    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [syncTaskId, syncing]);

  const fetchStatistics = async () => {
    try {
      setLoading(true);
      const data = await resourceDiscoveryApi.getStatistics();
      const resourceStats = data.resource_statistics || {};
      const matchStats = data.match_statistics || {};

      const totalResources = Object.values(resourceStats).reduce((sum: number, stat: any) => sum + (stat.total || 0), 0);
      const activeResources = Object.values(resourceStats).reduce((sum: number, stat: any) => sum + (stat.active || 0), 0);
      const vectorizedResources = Object.values(resourceStats).reduce((sum: number, stat: any) => sum + (stat.vectorized || 0), 0);

      setStats({
        totalResources,
        activeResources,
        vectorizedResources,
        avgResponseTime: matchStats.avg_response_time || 0
      });
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
      toast.error('获取统计信息失败', {
        description: error instanceof Error ? error.message : '未知错误'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    try {
      setSyncing(true);
      const result = await resourceDiscoveryApi.syncResources(false);

      if (result.success && result.task_id) {
        setSyncTaskId(result.task_id);
        toast.success('同步任务已启动', {
          description: result.message || '正在后台执行资源同步...'
        });
      } else {
        setSyncing(false);
        toast.error('启动同步失败', {
          description: result.message || '无法启动同步任务'
        });
      }
    } catch (error) {
      setSyncing(false);
      console.error('Sync failed:', error);
      toast.error('同步失败', {
        description: error instanceof Error ? error.message : '资源同步失败'
      });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">系统概览</h3>
        <p className="text-sm text-muted-foreground">
          查看资源发现系统的整体状态和性能指标
        </p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">总资源数</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{loading ? '...' : stats.totalResources}</div>
            <p className="text-xs text-muted-foreground">
              {stats.activeResources} 活跃资源
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">已向量化</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{loading ? '...' : stats.vectorizedResources}</div>
            <p className="text-xs text-muted-foreground">
              {stats.totalResources > 0 ? Math.round(stats.vectorizedResources / stats.totalResources * 100) : 0}% 完成率
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">平均响应时间</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{loading ? '...' : Math.round(stats.avgResponseTime)}ms</div>
            <p className="text-xs text-muted-foreground">系统性能</p>
          </CardContent>
        </Card>
      </div>

      {/* 操作按钮 */}
      <div className="flex gap-2">
        <Button onClick={handleSync} disabled={syncing}>
          {syncing ? '同步中...' : '同步资源'}
        </Button>
        <Button variant="outline" onClick={fetchStatistics} disabled={syncing}>
          刷新数据
        </Button>
      </div>

      {/* 同步进度提示 */}
      {syncing && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span className="text-sm text-blue-800 font-medium">
                资源同步进行中...
              </span>
            </div>

            {/* 进度条 */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs text-blue-700">
                <span>{syncStep || '准备中...'}</span>
                <span>{syncProgress}%</span>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${syncProgress}%` }}
                ></div>
              </div>
              {syncMessage && (
                <p className="text-xs text-blue-600 mt-1">{syncMessage}</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// 资源管理组件
function ResourceManagement() {
  const [resources, setResources] = useState<ResourceRegistryResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchResources();
  }, []);

  const fetchResources = async () => {
    try {
      setLoading(true);
      const data = await resourceDiscoveryApi.getResources({ limit: 100 });
      setResources(data);
    } catch (error) {
      console.error('Failed to fetch resources:', error);
      toast.error('获取资源列表失败', {
        description: error instanceof Error ? error.message : '未知错误'
      });
    } finally {
      setLoading(false);
    }
  };

  const filteredResources = resources.filter((resource) =>
    resource.resource_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    resource.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">资源管理</h3>
        <p className="text-sm text-muted-foreground">管理系统中发现的所有资源</p>
      </div>

      {/* 搜索框 */}
      <div className="flex items-center space-x-2">
        <Search className="h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="搜索资源..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="max-w-sm"
        />
      </div>

      {/* 资源列表 */}
      <div className="space-y-2">
        {loading ? (
          <div className="text-center py-8">加载中...</div>
        ) : filteredResources.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">未找到资源</div>
        ) : (
          filteredResources.map((resource) => (
            <Card key={resource.id}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium">{resource.resource_name}</h4>
                      <Badge variant="secondary">{resource.resource_type}</Badge>
                      <Badge variant={resource.is_active ? "default" : "outline"}>
                        {resource.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      {resource.description || "无描述"}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={resource.vectorization_status === 'completed' ? "default" : "outline"}>
                      {resource.vectorization_status || "pending"}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

// 智能体工具说明组件
function AgentToolsInfo() {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">智能体工具</h3>
        <p className="text-sm text-muted-foreground">资源发现现在通过智能体工具提供</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">资源发现工具</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="font-medium mb-2">discover_resources</h4>
            <p className="text-sm text-muted-foreground mb-3">
              智能体可以使用此工具根据用户查询找到最相关的系统资源。
            </p>
            <div className="bg-muted p-3 rounded-md">
              <code className="text-sm">
                discover_resources(<br />
                &nbsp;&nbsp;query="查询用户数据库信息",<br />
                &nbsp;&nbsp;top_k=5,<br />
                &nbsp;&nbsp;min_confidence=0.3<br />
                )
              </code>
            </div>
          </div>

          <div>
            <h4 className="font-medium mb-2">get_available_tools</h4>
            <p className="text-sm text-muted-foreground mb-3">
              获取系统中所有可用的工具列表及其对应的资源类型。
            </p>
          </div>

          <div>
            <h4 className="font-medium mb-2">get_resource_details</h4>
            <p className="text-sm text-muted-foreground mb-3">
              获取特定资源的详细信息，包括元数据、能力和使用方法。
            </p>
          </div>

          <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-950 rounded-md">
            <p className="text-sm text-blue-700 dark:text-blue-300">
              💡 <strong>提示：</strong>资源发现现在是智能体的核心能力，用户可以通过对话直接请求相关资源，
              智能体会自动调用这些工具来找到最合适的资源。
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// 主组件
export function ResourceDiscoveryTab() {

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold">资源发现</h2>
        <p className="text-muted-foreground">
          智能发现和管理系统资源，包括数据库、API、工具和Text2SQL资源。
        </p>
      </div>

      <Separator />

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">系统概览</TabsTrigger>
          <TabsTrigger value="resources">资源管理</TabsTrigger>
          <TabsTrigger value="tools">智能体工具</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <SystemOverview />
        </TabsContent>

        <TabsContent value="resources">
          <ResourceManagement />
        </TabsContent>

        <TabsContent value="tools">
          <AgentToolsInfo />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// 设置图标和名称
ResourceDiscoveryTab.icon = Search;
ResourceDiscoveryTab.displayName = "Resource Discovery";

export default ResourceDiscoveryTab;
