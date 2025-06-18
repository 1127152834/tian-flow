// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { Search, Database, Activity, TestTube, Loader2, AlertCircle } from "lucide-react";
import { useState, useEffect } from "react";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "~/components/ui/card";
import { Alert, AlertDescription } from "~/components/ui/alert";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Badge } from "~/components/ui/badge";
import { Separator } from "~/components/ui/separator";
import { toast } from "sonner";
import { resourceDiscoveryApi, type ResourceRegistryResponse } from "~/core/api/resource-discovery";

// 系统概览组件
function SystemOverview() {
  const [stats, setStats] = useState({
    totalResources: 0,
    activeResources: 0,
    vectorizedResources: 0,
    avgResponseTime: 0
  });
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [discovering, setDiscovering] = useState(false);
  const [syncTaskId, setSyncTaskId] = useState<string | null>(null);
  const [discoveryResult, setDiscoveryResult] = useState<any>(null);
  const [detailedStats, setDetailedStats] = useState<any>(null);

  useEffect(() => {
    fetchStatistics();
  }, []);

  // 定时刷新统计数据
  useEffect(() => {
    const interval = setInterval(() => {
      if (!syncing && !discovering) {
        fetchStatistics();
      }
    }, 10000); // 每10秒刷新一次

    return () => clearInterval(interval);
  }, [syncing, discovering]);

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

      // 保存详细统计信息
      setDetailedStats(data);
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
      // 使用增量同步API，默认为增量同步（force_full_sync=false）
      const result = await resourceDiscoveryApi.incrementalSync(false, true);

      if (result.success && result.task_id) {
        setSyncTaskId(result.task_id);
        toast.success('增量同步任务已启动', {
          description: result.message || '正在后台执行增量资源同步...'
        });
      } else {
        setSyncing(false);
        toast.error('启动增量同步失败', {
          description: result.message || '无法启动增量同步任务'
        });
      }
    } catch (error) {
      setSyncing(false);
      console.error('Incremental sync failed:', error);
      toast.error('增量同步失败', {
        description: error instanceof Error ? error.message : '增量资源同步失败'
      });
    }
  };

  const handleDiscoverResources = async () => {
    try {
      setDiscovering(true);
      const result = await resourceDiscoveryApi.discoverResourcesManual();

      if (result.success) {
        setDiscoveryResult(result);
        const summary = result.discovery_summary;
        toast.success('资源发现完成', {
          description: `发现 ${summary.total_discovered} 个资源：${summary.new_resources} 新增，${summary.existing_resources} 现有，${summary.missing_resources} 缺失`
        });
        // 刷新统计数据
        fetchStatistics();
      } else {
        toast.error('资源发现失败', {
          description: result.message || '无法发现系统资源'
        });
      }
    } catch (error) {
      console.error('Resource discovery failed:', error);
      toast.error('资源发现失败', {
        description: error instanceof Error ? error.message : '资源发现过程中发生错误'
      });
    } finally {
      setDiscovering(false);
    }
  };

  const handleFullSync = async () => {
    try {
      setSyncing(true);
      // 使用增量同步API，但强制全量同步（force_full_sync=true）
      const result = await resourceDiscoveryApi.incrementalSync(true, true);

      if (result.success && result.task_id) {
        setSyncTaskId(result.task_id);
        toast.success('全量同步任务已启动', {
          description: result.message || '正在后台执行全量资源同步...'
        });
      } else {
        setSyncing(false);
        toast.error('启动全量同步失败', {
          description: result.message || '无法启动全量同步任务'
        });
      }
    } catch (error) {
      setSyncing(false);
      console.error('Full sync failed:', error);
      toast.error('全量同步失败', {
        description: error instanceof Error ? error.message : '全量资源同步失败'
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
            <div className="mt-2 text-xs text-muted-foreground">
              {detailedStats?.resource_statistics ? (
                Object.entries(detailedStats.resource_statistics).map(([type, stat]: [string, any]) => (
                  <div key={type}>• {type}: {stat.total}个</div>
                ))
              ) : (
                <div>加载中...</div>
              )}
            </div>
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
            <div className="mt-2 text-xs text-muted-foreground">
              {detailedStats?.vectorization_breakdown ? (
                Object.entries(detailedStats.vectorization_breakdown).map(([status, count]: [string, any]) => (
                  <div key={status}>• {status === 'completed' ? '已完成' : status === 'pending' ? '待处理' : status}: {count}个</div>
                ))
              ) : (
                <>
                  <div>• 已完成: {stats.vectorizedResources}个</div>
                  <div>• 待处理: {stats.totalResources - stats.vectorizedResources}个</div>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">平均响应时间</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{loading ? '...' : Math.round(stats.avgResponseTime)}ms</div>
            <p className="text-xs text-muted-foreground">基于最近30天查询</p>
            <div className="mt-2 text-xs text-muted-foreground">
              数据来源: 资源匹配历史记录
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 详细向量化状态 */}
      {detailedStats?.resource_statistics && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">向量化详细状态</CardTitle>
            <CardDescription>
              各类型资源的向量化进度
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(detailedStats.resource_statistics).map(([type, stat]: [string, any]) => (
                <div key={type} className="p-3 border rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium">{type}</span>
                    <Badge variant={stat.vectorized === stat.total ? "default" : "secondary"}>
                      {stat.vectorized}/{stat.total}
                    </Badge>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${stat.total > 0 ? (stat.vectorized / stat.total) * 100 : 0}%` }}
                    ></div>
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {stat.total > 0 ? Math.round((stat.vectorized / stat.total) * 100) : 0}% 完成
                  </div>
                </div>
              ))}
            </div>

            {/* 总体向量化状态 */}
            {detailedStats.vectorization_breakdown && (
              <div className="mt-4 pt-4 border-t">
                <h4 className="font-medium mb-2">总体状态分布</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {Object.entries(detailedStats.vectorization_breakdown).map(([status, count]: [string, any]) => (
                    <div key={status} className="text-center p-2 bg-muted rounded">
                      <div className="text-lg font-bold">{count}</div>
                      <div className="text-xs text-muted-foreground">
                        {status === 'completed' ? '已完成' :
                         status === 'pending' ? '待处理' :
                         status === 'in_progress' ? '处理中' :
                         status === 'failed' ? '失败' : status}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* 操作按钮 */}
      <div className="space-y-3">
        <div className="flex gap-2">
          <Button onClick={handleDiscoverResources} disabled={syncing || discovering}>
            {discovering ? '发现中...' : '发现资源'}
          </Button>
          <Button onClick={handleSync} disabled={syncing || discovering}>
            {syncing ? '增量同步中...' : '增量同步'}
          </Button>
          <Button
            variant="outline"
            onClick={() => handleFullSync()}
            disabled={syncing || discovering}
          >
            全量同步
          </Button>
          <Button variant="outline" onClick={fetchStatistics} disabled={syncing || discovering}>
            刷新数据
          </Button>
        </div>

        {/* 同步说明 */}
        <div className="text-sm text-muted-foreground bg-muted/50 p-3 rounded-lg">
          <div className="space-y-1">
            <div><strong>发现资源：</strong>手动扫描系统中的所有资源，显示新增、现有、缺失的资源状态</div>
            <div><strong>增量同步：</strong>智能检测资源变更，只同步新增、修改或删除的资源，速度快，推荐日常使用</div>
            <div><strong>全量同步：</strong>重新扫描所有资源并完全重建索引，耗时较长，适用于系统初始化或故障恢复</div>
          </div>
        </div>

        {/* 数据来源说明 */}
        <div className="text-sm bg-blue-50 border border-blue-200 p-3 rounded-lg">
          <h4 className="font-medium text-blue-800 mb-2">📊 数据来源说明</h4>
          <div className="space-y-1 text-blue-700">
            <div><strong>总资源数：</strong>来自 resource_registry 表，包含所有已注册的系统资源</div>
            <div><strong>向量化状态：</strong>基于资源的 vectorization_status 字段统计</div>
            <div><strong>响应时间：</strong>基于最近30天的 resource_match_history 查询记录计算平均值</div>
            <div><strong>Text2SQL资源：</strong>部分资源可能仍在向量化处理中，这是正常现象</div>
          </div>
        </div>
      </div>

      {/* 资源发现结果 */}
      {discoveryResult && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">资源发现结果</CardTitle>
            <CardDescription>
              最近一次资源发现的详细结果
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* 统计概览 */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {discoveryResult.discovery_summary.new_resources}
                </div>
                <div className="text-sm text-green-700">新增资源</div>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {discoveryResult.discovery_summary.existing_resources}
                </div>
                <div className="text-sm text-blue-700">现有资源</div>
              </div>
              <div className="text-center p-3 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {discoveryResult.discovery_summary.missing_resources}
                </div>
                <div className="text-sm text-yellow-700">缺失资源</div>
              </div>
              <div className="text-center p-3 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {discoveryResult.discovery_summary.total_discovered}
                </div>
                <div className="text-sm text-purple-700">总计发现</div>
              </div>
            </div>

            {/* 向量化状态 */}
            <div>
              <h4 className="font-medium mb-2">向量化状态</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {Object.entries(discoveryResult.discovery_summary.vectorization_stats).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between p-2 bg-muted rounded">
                    <span className="text-sm capitalize">{status}</span>
                    <Badge variant="outline">{count as number}</Badge>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 同步进度提示 */}
      {syncing && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <span className="text-sm text-blue-800 font-medium">
              智能资源同步进行中...
            </span>
          </div>
          <p className="text-xs text-blue-600 mt-2">
            任务ID: {syncTaskId || '未知'}
          </p>
          <p className="text-xs text-blue-600">
            请等待任务完成，统计数据将自动更新
          </p>
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
  const [testQuery, setTestQuery] = useState('');
  const [testResult, setTestResult] = useState<any>(null);
  const [testing, setTesting] = useState(false);

  // 测试资源发现功能
  const testResourceDiscovery = async () => {
    if (!testQuery.trim()) {
      toast.error('请输入测试查询');
      return;
    }

    setTesting(true);
    try {
      const response = await resourceDiscoveryApi.testResourceMatching({
        query: testQuery.trim(),
        top_k: 5,
        min_confidence: 0.1
      });

      setTestResult(response);
      toast.success(`找到 ${response.total_matches} 个匹配结果`);
    } catch (error) {
      console.error('测试失败:', error);
      toast.error(error instanceof Error ? error.message : '测试失败');
      setTestResult(null);
    } finally {
      setTesting(false);
    }
  };

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

      {/* 测试功能 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <TestTube className="h-4 w-4" />
            测试资源发现
          </CardTitle>
          <CardDescription>
            测试智能体的资源发现功能
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="输入测试查询，例如：查询数据库中的用户信息"
              value={testQuery}
              onChange={(e) => setTestQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && testResourceDiscovery()}
            />
            <Button
              onClick={testResourceDiscovery}
              disabled={testing || !testQuery.trim()}
              size="sm"
            >
              {testing ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  测试中
                </>
              ) : (
                <>
                  <Search className="h-4 w-4 mr-2" />
                  测试
                </>
              )}
            </Button>
          </div>

          {/* 测试结果 */}
          {testResult && (
            <div className="space-y-3">
              <div className="flex items-center gap-4 text-sm">
                <Badge variant="outline">
                  {testResult.total_matches} 个匹配
                </Badge>
                <span className="text-muted-foreground">
                  处理时间: {testResult.processing_time.toFixed(3)}s
                </span>
              </div>

              {testResult.matches.length > 0 ? (
                <div className="space-y-2">
                  {testResult.matches.slice(0, 3).map((match: any, index: number) => (
                    <div key={match.resource_id} className="border rounded p-3 space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">#{index + 1}</span>
                        <span className="font-medium">{match.resource_name}</span>
                        <Badge variant="secondary" className="text-xs">
                          {match.resource_type}
                        </Badge>
                        <Badge
                          variant={match.confidence === 'high' ? 'default' : 'outline'}
                          className="text-xs"
                        >
                          {(match.confidence_score * 100).toFixed(0)}%
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {match.description}
                      </p>
                    </div>
                  ))}

                  {testResult.matches.length > 3 && (
                    <p className="text-sm text-muted-foreground text-center">
                      还有 {testResult.matches.length - 3} 个结果...
                    </p>
                  )}
                </div>
              ) : (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    未找到匹配的资源，请尝试其他查询或降低置信度阈值。
                  </AlertDescription>
                </Alert>
              )}
            </div>
          )}
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
