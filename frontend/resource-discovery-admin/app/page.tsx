'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge, Tabs, TabsContent, TabsList, TabsTrigger, Alert, AlertDescription, Progress } from '../components/ui/index';
import { 
  Brain, 
  Database, 
  Search, 
  Settings, 
  RefreshCw, 
  Loader2,
  Activity,
  TrendingUp,
  Zap,
  CheckCircle2,
  AlertTriangle,
  Info,
  BarChart3,
  Globe,
  Cpu,
  HardDrive
} from 'lucide-react';
import { toast } from 'sonner';

// 组件导入
import { SystemOverview } from './components/system-overview';
import { ResourceManagement } from './components/resource-management';
import { DiscoveryTesting } from './components/discovery-testing';
import { SystemSettings } from './components/system-settings';

interface SystemStats {
  total_resources: number;
  active_resources: number;
  vectorization_rate: number;
  by_type: {
    [key: string]: {
      total: number;
      active: number;
    };
  };
}

export default function ResourceDiscoveryAdmin() {
  const [loading, setLoading] = useState(false);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  // 加载系统统计信息
  const loadSystemStats = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/admin/resource-discovery/statistics');
      
      if (!response.ok) {
        throw new Error(`API错误: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        setSystemStats(result.data);
      } else {
        throw new Error(result.error || '获取统计信息失败');
      }
    } catch (error) {
      console.error('加载系统统计失败:', error);
      toast.error(error instanceof Error ? error.message : '加载系统统计失败');
    } finally {
      setLoading(false);
    }
  };

  // 执行系统同步
  const performSync = async (forceFullSync = false) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/admin/resource-discovery/sync?force_full_sync=${forceFullSync}`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error(`API错误: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        toast.success('同步完成', {
          description: result.message
        });
        await loadSystemStats(); // 重新加载统计信息
      } else {
        throw new Error(result.error || '同步失败');
      }
    } catch (error) {
      console.error('系统同步失败:', error);
      toast.error(error instanceof Error ? error.message : '系统同步失败');
    } finally {
      setLoading(false);
    }
  };

  // 页面加载时获取统计信息
  useEffect(() => {
    loadSystemStats();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* 页面头部 */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Brain className="h-8 w-8 text-blue-600" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    DeerFlow 资源发现
                  </h1>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    智能资源发现与管理系统
                  </p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                onClick={loadSystemStats}
                disabled={loading}
                size="sm"
              >
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                刷新
              </Button>
              
              <Button
                onClick={() => performSync(false)}
                disabled={loading}
                size="sm"
              >
                <Zap className="h-4 w-4 mr-2" />
                增量同步
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* 主要内容区域 */}
      <div className="container mx-auto px-6 py-6">
        {/* 系统状态卡片 */}
        {systemStats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">总资源数</CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemStats.total_resources}</div>
                <p className="text-xs text-muted-foreground">
                  活跃: {systemStats.active_resources}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">向量化率</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemStats.vectorization_rate.toFixed(1)}%</div>
                <Progress value={systemStats.vectorization_rate} className="mt-2" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">系统状态</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                  <span className="text-sm font-medium">运行正常</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  所有服务正常运行
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">资源类型</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{Object.keys(systemStats.by_type).length}</div>
                <p className="text-xs text-muted-foreground">
                  数据库、API、工具等
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* 主要功能标签页 */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              系统概览
            </TabsTrigger>
            <TabsTrigger value="resources" className="flex items-center gap-2">
              <Database className="h-4 w-4" />
              资源管理
            </TabsTrigger>
            <TabsTrigger value="testing" className="flex items-center gap-2">
              <Search className="h-4 w-4" />
              发现测试
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              系统设置
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <SystemOverview 
              systemStats={systemStats} 
              onRefresh={loadSystemStats}
              onSync={performSync}
            />
          </TabsContent>

          <TabsContent value="resources" className="space-y-4">
            <ResourceManagement onRefresh={loadSystemStats} />
          </TabsContent>

          <TabsContent value="testing" className="space-y-4">
            <DiscoveryTesting />
          </TabsContent>

          <TabsContent value="settings" className="space-y-4">
            <SystemSettings onRefresh={loadSystemStats} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
