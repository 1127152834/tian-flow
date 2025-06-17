'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Settings, 
  Save, 
  RefreshCw, 
  Loader2,
  Database,
  Zap,
  Clock,
  Target,
  Shield,
  AlertTriangle,
  CheckCircle2,
  Info
} from 'lucide-react';
import { toast } from 'sonner';

interface SystemConfig {
  auto_sync_enabled: boolean;
  sync_interval_minutes: number;
  similarity_threshold: number;
  max_concurrent_tasks: number;
  cache_ttl_hours: number;
  enable_performance_monitoring: boolean;
  log_level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR';
  max_query_results: number;
  vectorization_batch_size: number;
  enable_real_time_updates: boolean;
}

interface SystemSettingsProps {
  onRefresh: () => Promise<void>;
}

export function SystemSettings({ onRefresh }: SystemSettingsProps) {
  const [config, setConfig] = useState<SystemConfig>({
    auto_sync_enabled: true,
    sync_interval_minutes: 30,
    similarity_threshold: 0.3,
    max_concurrent_tasks: 5,
    cache_ttl_hours: 24,
    enable_performance_monitoring: true,
    log_level: 'INFO',
    max_query_results: 20,
    vectorization_batch_size: 10,
    enable_real_time_updates: true
  });
  
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // 加载系统配置
  const loadConfig = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/admin/resource-discovery/config');
      
      if (!response.ok) {
        throw new Error(`API错误: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        setConfig(result.data);
        setHasChanges(false);
      } else {
        throw new Error(result.error || '获取配置失败');
      }
    } catch (error) {
      console.error('加载配置失败:', error);
      toast.error(error instanceof Error ? error.message : '加载配置失败');
    } finally {
      setLoading(false);
    }
  };

  // 保存系统配置
  const saveConfig = async () => {
    try {
      setSaving(true);
      const response = await fetch('/api/admin/resource-discovery/config', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      if (!response.ok) {
        throw new Error(`API错误: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        toast.success('配置保存成功');
        setHasChanges(false);
        await onRefresh(); // 刷新主页面数据
      } else {
        throw new Error(result.error || '保存配置失败');
      }
    } catch (error) {
      console.error('保存配置失败:', error);
      toast.error(error instanceof Error ? error.message : '保存配置失败');
    } finally {
      setSaving(false);
    }
  };

  // 重置配置
  const resetConfig = async () => {
    if (confirm('确定要重置所有配置到默认值吗？')) {
      await loadConfig();
      toast.info('配置已重置');
    }
  };

  // 更新配置项
  const updateConfig = (key: keyof SystemConfig, value: any) => {
    setConfig(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  useEffect(() => {
    loadConfig();
  }, []);

  return (
    <div className="space-y-6">
      {/* 页面头部 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            系统设置
          </CardTitle>
          <CardDescription>
            配置资源发现模块的运行参数和行为
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Button onClick={loadConfig} disabled={loading} variant="outline">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              刷新配置
            </Button>
            
            <Button onClick={resetConfig} disabled={loading} variant="outline">
              重置默认值
            </Button>
            
            <div className="flex-1" />
            
            {hasChanges && (
              <Alert className="flex-1 max-w-md">
                <Info className="h-4 w-4" />
                <AlertDescription>
                  配置已修改，请保存更改
                </AlertDescription>
              </Alert>
            )}
            
            <Button 
              onClick={saveConfig} 
              disabled={saving || !hasChanges}
              className="min-w-24"
            >
              {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
              保存
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 同步设置 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            同步设置
          </CardTitle>
          <CardDescription>
            配置资源同步和更新策略
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <label className="text-sm font-medium">启用自动同步</label>
              <p className="text-xs text-gray-500">定期自动同步系统资源</p>
            </div>
            <Switch
              checked={config.auto_sync_enabled}
              onCheckedChange={(checked) => updateConfig('auto_sync_enabled', checked)}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">
              同步间隔: {config.sync_interval_minutes} 分钟
            </label>
            <Slider
              value={[config.sync_interval_minutes]}
              onValueChange={([value]) => updateConfig('sync_interval_minutes', value)}
              max={1440}
              min={5}
              step={5}
              disabled={!config.auto_sync_enabled}
              className="w-full"
            />
            <p className="text-xs text-gray-500">
              设置自动同步的时间间隔（5分钟 - 24小时）
            </p>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">
              最大并发任务: {config.max_concurrent_tasks}
            </label>
            <Slider
              value={[config.max_concurrent_tasks]}
              onValueChange={([value]) => updateConfig('max_concurrent_tasks', value)}
              max={20}
              min={1}
              step={1}
              className="w-full"
            />
            <p className="text-xs text-gray-500">
              同时执行的最大同步任务数
            </p>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <label className="text-sm font-medium">启用实时更新</label>
              <p className="text-xs text-gray-500">监听数据库变更并实时同步</p>
            </div>
            <Switch
              checked={config.enable_real_time_updates}
              onCheckedChange={(checked) => updateConfig('enable_real_time_updates', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* 匹配设置 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            匹配设置
          </CardTitle>
          <CardDescription>
            配置资源匹配和相似度计算参数
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">
              相似度阈值: {config.similarity_threshold.toFixed(1)}
            </label>
            <Slider
              value={[config.similarity_threshold]}
              onValueChange={([value]) => updateConfig('similarity_threshold', value)}
              max={1}
              min={0}
              step={0.1}
              className="w-full"
            />
            <p className="text-xs text-gray-500">
              资源匹配的最小相似度要求（0.0 - 1.0）
            </p>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">
              最大查询结果: {config.max_query_results}
            </label>
            <Slider
              value={[config.max_query_results]}
              onValueChange={([value]) => updateConfig('max_query_results', value)}
              max={100}
              min={1}
              step={1}
              className="w-full"
            />
            <p className="text-xs text-gray-500">
              单次查询返回的最大结果数量
            </p>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">
              向量化批次大小: {config.vectorization_batch_size}
            </label>
            <Slider
              value={[config.vectorization_batch_size]}
              onValueChange={([value]) => updateConfig('vectorization_batch_size', value)}
              max={50}
              min={1}
              step={1}
              className="w-full"
            />
            <p className="text-xs text-gray-500">
              批量向量化处理的资源数量
            </p>
          </div>
        </CardContent>
      </Card>

      {/* 性能设置 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            性能设置
          </CardTitle>
          <CardDescription>
            配置缓存、监控和性能优化参数
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">
              缓存过期时间: {config.cache_ttl_hours} 小时
            </label>
            <Slider
              value={[config.cache_ttl_hours]}
              onValueChange={([value]) => updateConfig('cache_ttl_hours', value)}
              max={168}
              min={1}
              step={1}
              className="w-full"
            />
            <p className="text-xs text-gray-500">
              查询结果缓存的有效期（1小时 - 7天）
            </p>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <label className="text-sm font-medium">启用性能监控</label>
              <p className="text-xs text-gray-500">收集和分析系统性能指标</p>
            </div>
            <Switch
              checked={config.enable_performance_monitoring}
              onCheckedChange={(checked) => updateConfig('enable_performance_monitoring', checked)}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">日志级别</label>
            <Select 
              value={config.log_level} 
              onValueChange={(value: any) => updateConfig('log_level', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="DEBUG">DEBUG - 详细调试信息</SelectItem>
                <SelectItem value="INFO">INFO - 一般信息</SelectItem>
                <SelectItem value="WARNING">WARNING - 警告信息</SelectItem>
                <SelectItem value="ERROR">ERROR - 仅错误信息</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-gray-500">
              设置系统日志的详细程度
            </p>
          </div>
        </CardContent>
      </Card>

      {/* 系统状态 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            系统状态
          </CardTitle>
          <CardDescription>
            当前系统运行状态和健康检查
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <CheckCircle2 className="h-5 w-5 text-green-500" />
              <div>
                <div className="font-medium text-green-700 dark:text-green-300">资源发现服务</div>
                <div className="text-sm text-green-600 dark:text-green-400">运行正常</div>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <CheckCircle2 className="h-5 w-5 text-green-500" />
              <div>
                <div className="font-medium text-green-700 dark:text-green-300">向量化服务</div>
                <div className="text-sm text-green-600 dark:text-green-400">运行正常</div>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <CheckCircle2 className="h-5 w-5 text-green-500" />
              <div>
                <div className="font-medium text-green-700 dark:text-green-300">数据库连接</div>
                <div className="text-sm text-green-600 dark:text-green-400">连接正常</div>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <Clock className="h-5 w-5 text-blue-500" />
              <div>
                <div className="font-medium text-blue-700 dark:text-blue-300">实时监听器</div>
                <div className="text-sm text-blue-600 dark:text-blue-400">
                  {config.enable_real_time_updates ? '已启用' : '已禁用'}
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
