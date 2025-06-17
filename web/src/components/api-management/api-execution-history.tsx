// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * API Execution History
 * API执行历史记录组件 - 展示API调用历史和统计信息
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Clock, CheckCircle, XCircle, TrendingUp, Activity, BarChart3, Eye, Copy, Server, Timer, Hash } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { Badge } from '~/components/ui/badge';
import { Button } from '~/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '~/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '~/components/ui/dialog';
import { Separator } from '~/components/ui/separator';
import { Alert, AlertDescription } from '~/components/ui/alert';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '~/components/ui/table';
import { useToast } from '~/hooks/use-toast';

import type { APICallLog, CallStatistics } from '~/core/api/api-management';
import { listAPICallLogs, getCallStatistics, getAPICallLog } from '~/core/api/api-management';

interface APIExecutionHistoryProps {
  apiDefinitionId?: number;
  className?: string;
}

export function APIExecutionHistory({ 
  apiDefinitionId, 
  className = '' 
}: APIExecutionHistoryProps) {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<APICallLog[]>([]);
  const [statistics, setStatistics] = useState<CallStatistics | null>(null);
  const [activeTab, setActiveTab] = useState('recent');
  const [selectedLog, setSelectedLog] = useState<APICallLog | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);

  useEffect(() => {
    loadData();
  }, [apiDefinitionId]);

  const loadData = async () => {
    try {
      setLoading(true);

      // 加载调用日志
      const logsResponse = await listAPICallLogs({
        api_definition_id: apiDefinitionId,
        limit: 20,
        skip: 0
      });
      setLogs(logsResponse || []);

      // 加载统计信息
      const statsResponse = await getCallStatistics({ api_definition_id: apiDefinitionId });
      setStatistics(statsResponse);

    } catch (error: any) {
      console.error('Failed to load execution history:', error);
      toast({
        title: '加载失败',
        description: error.message || '无法加载执行历史',
        variant: 'destructive',
      });
      // 设置默认值以避免undefined错误
      setLogs([]);
      setStatistics(null);
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getStatusColor = (statusCode: number | null) => {
    if (!statusCode) return 'bg-gray-100 text-gray-600';
    if (statusCode >= 200 && statusCode < 300) return 'bg-green-100 text-green-600';
    if (statusCode >= 400 && statusCode < 500) return 'bg-yellow-100 text-yellow-600';
    if (statusCode >= 500) return 'bg-red-100 text-red-600';
    return 'bg-blue-100 text-blue-600';
  };

  const handleViewDetail = async (logId: number) => {
    try {
      setLoadingDetail(true);
      const logDetail = await getAPICallLog(logId);
      setSelectedLog(logDetail);
      setDetailDialogOpen(true);
    } catch (error: any) {
      console.error('Failed to load log detail:', error);
      toast({
        title: '加载失败',
        description: error.message || '无法加载执行详情',
        variant: 'destructive',
      });
    } finally {
      setLoadingDetail(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: '已复制',
      description: '内容已复制到剪贴板',
    });
  };

  if (loading) {
    return (
      <div className={`space-y-4 ${className}`}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardContent className="pt-6">
                <div className="animate-pulse space-y-2">
                  <div className="h-4 bg-muted rounded w-1/2"></div>
                  <div className="h-8 bg-muted rounded w-3/4"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* 统计概览 */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-blue-100 text-blue-600">
                  <Activity className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{statistics.total_calls}</p>
                  <p className="text-xs text-muted-foreground">总调用次数</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-green-100 text-green-600">
                  <CheckCircle className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {statistics.total_calls > 0
                      ? ((statistics.success_calls / statistics.total_calls) * 100).toFixed(1)
                      : '0'
                    }%
                  </p>
                  <p className="text-xs text-muted-foreground">成功率</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-purple-100 text-purple-600">
                  <Clock className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {formatDuration(statistics.average_response_time || 0)}
                  </p>
                  <p className="text-xs text-muted-foreground">平均响应时间</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-orange-100 text-orange-600">
                  <TrendingUp className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{statistics.calls_today}</p>
                  <p className="text-xs text-muted-foreground">今日调用</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 执行历史 */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            <CardTitle>执行历史</CardTitle>
          </div>
          <CardDescription>
            最近的API调用记录和详细信息
          </CardDescription>
        </CardHeader>
        <CardContent>
          {logs && logs.length > 0 ? (
            <div className="space-y-4">
              {logs.map((log) => (
                <div 
                  key={log.id} 
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/30 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-lg ${log.error_message ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600'}`}>
                      {log.error_message ? <XCircle className="h-5 w-5" /> : <CheckCircle className="h-5 w-5" />}
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <Badge 
                          variant="outline" 
                          className={getStatusColor(log.status_code)}
                        >
                          {log.status_code || 'ERROR'}
                        </Badge>
                        <span className="text-sm font-medium">
                          {formatDateTime(log.created_at)}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span>耗时: {formatDuration(log.execution_time_ms)}</span>
                        <span>会话: {log.session_id?.slice(-8) || 'N/A'}</span>
                      </div>
                      {log.error_message && (
                        <p className="text-sm text-red-600 bg-red-50 px-2 py-1 rounded">
                          {log.error_message}
                        </p>
                      )}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleViewDetail(log.id)}
                    disabled={loadingDetail}
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="p-4 rounded-full bg-muted mb-4 inline-block">
                <Activity className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">暂无执行记录</h3>
              <p className="text-muted-foreground">
                此API还没有执行记录，执行后将在这里显示历史信息
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 详细记录对话框 */}
      <Dialog open={detailDialogOpen} onOpenChange={setDetailDialogOpen}>
        <DialogContent className="max-w-5xl max-h-[85vh] overflow-y-auto w-full" style={{ width: '1000px', maxWidth: '85vw' }}>
          <DialogHeader>
            <DialogTitle>执行详情</DialogTitle>
          </DialogHeader>

          {selectedLog && (
            <div className="space-y-6">
              {/* 基本信息 */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="pt-4">
                    <div className="flex items-center gap-2">
                      <Server className="h-4 w-4 text-blue-600" />
                      <div>
                        <p className="text-sm text-muted-foreground">状态码</p>
                        <p className="font-semibold">{selectedLog.status_code || 'ERROR'}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-4">
                    <div className="flex items-center gap-2">
                      <Timer className="h-4 w-4 text-purple-600" />
                      <div>
                        <p className="text-sm text-muted-foreground">响应时间</p>
                        <p className="font-semibold">{formatDuration(selectedLog.execution_time_ms)}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-4">
                    <div className="flex items-center gap-2">
                      <Hash className="h-4 w-4 text-green-600" />
                      <div>
                        <p className="text-sm text-muted-foreground">会话ID</p>
                        <p className="font-semibold text-xs">{selectedLog.session_id?.slice(-12) || 'N/A'}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-4">
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-orange-600" />
                      <div>
                        <p className="text-sm text-muted-foreground">执行时间</p>
                        <p className="font-semibold text-xs">{formatDateTime(selectedLog.created_at)}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* 错误信息 */}
              {selectedLog.error_message && (
                <Alert variant="destructive">
                  <XCircle className="h-4 w-4" />
                  <AlertDescription>
                    <div className="flex items-center justify-between">
                      <span>{selectedLog.error_message}</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(selectedLog.error_message || '')}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                  </AlertDescription>
                </Alert>
              )}

              {/* 请求数据 */}
              {selectedLog.request_data && (
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">请求数据</CardTitle>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => copyToClipboard(JSON.stringify(selectedLog.request_data, null, 2))}
                      >
                        <Copy className="h-4 w-4 mr-2" />
                        复制
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm">
                      <code>{JSON.stringify(selectedLog.request_data, null, 2)}</code>
                    </pre>
                  </CardContent>
                </Card>
              )}

              {/* 响应数据 */}
              {selectedLog.response_data && (
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">响应数据</CardTitle>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => copyToClipboard(JSON.stringify(selectedLog.response_data, null, 2))}
                      >
                        <Copy className="h-4 w-4 mr-2" />
                        复制
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm">
                      <code>{JSON.stringify(selectedLog.response_data, null, 2)}</code>
                    </pre>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
