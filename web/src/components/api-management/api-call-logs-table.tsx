// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * API Call Logs Table
 * API调用日志表格 - 严格按照ti-flow实现
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Eye, Filter, Download } from 'lucide-react';
import { Button } from '~/components/ui/button';
import { Input } from '~/components/ui/input';
import { Badge } from '~/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '~/components/ui/table';
import { useToast } from '~/hooks/use-toast';

import { type APICallLog, listAPICallLogs } from '~/core/api/api-management';

export function APICallLogsTable() {
  const { toast } = useToast();
  const [logs, setLogs] = useState<APICallLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadLogs();
  }, [searchQuery]);

  const loadLogs = async () => {
    try {
      setLoading(true);
      const data = await listAPICallLogs({
        limit: 50,
        session_id: searchQuery || undefined,
      });
      setLogs(data);
    } catch (error) {
      toast({
        title: '加载失败',
        description: '无法加载调用日志',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (log: APICallLog) => {
    if (log.error_message) {
      return <Badge variant="destructive">失败</Badge>;
    } else if (log.status_code && log.status_code >= 200 && log.status_code < 300) {
      return <Badge variant="default">成功</Badge>;
    } else if (log.status_code && log.status_code >= 400) {
      return <Badge variant="destructive">错误</Badge>;
    } else {
      return <Badge variant="secondary">未知</Badge>;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('zh-CN');
  };

  const formatDuration = (ms?: number) => {
    if (!ms) return 'N/A';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>API调用日志</CardTitle>
            <CardDescription>查看API调用历史和执行结果</CardDescription>
          </div>
          <div className="flex gap-2">
            <Input
              placeholder="搜索会话ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-64"
            />
            <Button variant="outline" size="sm">
              <Filter className="h-4 w-4 mr-2" />
              筛选
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <p className="mt-2 text-muted-foreground">加载中...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground">暂无调用日志</p>
          </div>
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>API ID</TableHead>
                  <TableHead>会话ID</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead>状态码</TableHead>
                  <TableHead>执行时间</TableHead>
                  <TableHead>调用时间</TableHead>
                  <TableHead>操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {logs.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell className="font-medium">
                      {log.api_definition_id}
                    </TableCell>
                    <TableCell>
                      {log.session_id ? (
                        <code className="text-xs bg-muted px-1 py-0.5 rounded">
                          {log.session_id}
                        </code>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {getStatusBadge(log)}
                    </TableCell>
                    <TableCell>
                      {log.status_code ? (
                        <Badge 
                          variant="outline"
                          className={
                            log.status_code >= 200 && log.status_code < 300
                              ? 'border-green-200 text-green-800'
                              : log.status_code >= 400
                              ? 'border-red-200 text-red-800'
                              : 'border-yellow-200 text-yellow-800'
                          }
                        >
                          {log.status_code}
                        </Badge>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {formatDuration(log.execution_time_ms)}
                    </TableCell>
                    <TableCell className="text-sm">
                      {formatDate(log.created_at)}
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
