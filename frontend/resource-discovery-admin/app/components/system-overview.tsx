'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { 
  RefreshCw, 
  Loader2,
  TrendingUp,
  Zap,
  CheckCircle2,
  AlertTriangle,
  Info,
  BarChart3,
  Database,
  Globe,
  Cpu,
  HardDrive,
  Clock,
  Activity
} from 'lucide-react';
import { toast } from 'sonner';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

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

interface SystemOverviewProps {
  systemStats: SystemStats | null;
  onRefresh: () => Promise<void>;
  onSync: (forceFullSync?: boolean) => Promise<void>;
}

interface PerformanceMetrics {
  avg_query_time: number;
  total_queries: number;
  success_rate: number;
  cache_hit_rate: number;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export function SystemOverview({ systemStats, onRefresh, onSync }: SystemOverviewProps) {
  const [loading, setLoading] = useState(false);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics | null>(null);

  // 加载性能指标
  const loadPerformanceMetrics = async () => {
    try {
      // 模拟性能数据（在实际应用中应该从API获取）
      setPerformanceMetrics({
        avg_query_time: 45,
        total_queries: 1247,
        success_rate: 98.5,
        cache_hit_rate: 85.2
      });
    } catch (error) {
      console.error('加载性能指标失败:', error);
    }
  };

  useEffect(() => {
    loadPerformanceMetrics();
  }, []);

  // 准备图表数据
  const chartData = systemStats ? Object.entries(systemStats.by_type).map(([type, stats]) => ({
    name: type,
    total: stats.total,
    active: stats.active,
    inactive: stats.total - stats.active
  })) : [];

  const pieData = systemStats ? Object.entries(systemStats.by_type).map(([type, stats]) => ({
    name: type,
    value: stats.total
  })) : [];

  return (
    <div className="space-y-6">
      {/* 系统健康状态 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            系统健康状态
          </CardTitle>
          <CardDescription>
            实时监控系统运行状态和关键指标
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* 查询性能 */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-blue-500" />
                <span className="text-sm font-medium">平均查询时间</span>
              </div>
              <div className="text-2xl font-bold text-blue-600">
                {performanceMetrics?.avg_query_time || 0}ms
              </div>
              <Badge variant="secondary" className="text-xs">
                优秀 (&lt; 100ms)
              </Badge>
            </div>

            {/* 成功率 */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span className="text-sm font-medium">查询成功率</span>
              </div>
              <div className="text-2xl font-bold text-green-600">
                {performanceMetrics?.success_rate || 0}%
              </div>
              <Progress value={performanceMetrics?.success_rate || 0} className="h-2" />
            </div>

            {/* 缓存命中率 */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <HardDrive className="h-4 w-4 text-purple-500" />
                <span className="text-sm font-medium">缓存命中率</span>
              </div>
              <div className="text-2xl font-bold text-purple-600">
                {performanceMetrics?.cache_hit_rate || 0}%
              </div>
              <Progress value={performanceMetrics?.cache_hit_rate || 0} className="h-2" />
            </div>

            {/* 总查询数 */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-orange-500" />
                <span className="text-sm font-medium">总查询数</span>
              </div>
              <div className="text-2xl font-bold text-orange-600">
                {performanceMetrics?.total_queries || 0}
              </div>
              <Badge variant="outline" className="text-xs">
                今日统计
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 资源分布图表 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 柱状图 */}
        <Card>
          <CardHeader>
            <CardTitle>资源类型分布</CardTitle>
            <CardDescription>各类型资源的数量统计</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="active" fill="#22c55e" name="活跃" />
                  <Bar dataKey="inactive" fill="#ef4444" name="非活跃" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* 饼图 */}
        <Card>
          <CardHeader>
            <CardTitle>资源占比</CardTitle>
            <CardDescription>各类型资源的比例分布</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 快捷操作 */}
      <Card>
        <CardHeader>
          <CardTitle>快捷操作</CardTitle>
          <CardDescription>常用的系统管理操作</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button 
              onClick={() => onSync(false)} 
              disabled={loading}
              className="h-20 flex flex-col gap-2"
            >
              <Zap className="h-6 w-6" />
              <span>增量同步</span>
              <span className="text-xs opacity-75">同步变更的资源</span>
            </Button>

            <Button 
              onClick={() => onSync(true)} 
              disabled={loading}
              variant="outline"
              className="h-20 flex flex-col gap-2"
            >
              <RefreshCw className="h-6 w-6" />
              <span>全量同步</span>
              <span className="text-xs opacity-75">重新同步所有资源</span>
            </Button>

            <Button 
              onClick={onRefresh} 
              disabled={loading}
              variant="secondary"
              className="h-20 flex flex-col gap-2"
            >
              <Activity className="h-6 w-6" />
              <span>刷新状态</span>
              <span className="text-xs opacity-75">更新系统状态</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 系统建议 */}
      {systemStats && systemStats.vectorization_rate < 90 && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            向量化率较低 ({systemStats.vectorization_rate.toFixed(1)}%)，建议执行增量同步以提高系统性能。
          </AlertDescription>
        </Alert>
      )}

      {systemStats && systemStats.active_resources < systemStats.total_resources * 0.8 && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            检测到 {systemStats.total_resources - systemStats.active_resources} 个非活跃资源，
            建议检查资源状态或清理无效资源。
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
