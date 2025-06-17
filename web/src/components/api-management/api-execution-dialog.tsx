// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * API Execution Dialog
 * API执行对话框 - 严格按照ti-flow实现
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Play, Copy } from 'lucide-react';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle 
} from '~/components/ui/dialog';
import { Button } from '~/components/ui/button';
import { Input } from '~/components/ui/input';
import { Textarea } from '~/components/ui/textarea';
import { Label } from '~/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { Badge } from '~/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '~/components/ui/tabs';
import { useToast } from '~/hooks/use-toast';

import type {
  APIDefinition,
  Parameter,
  APIExecutionResult
} from '~/core/api/api-management';
import {
  ParameterType,
  DataType,
  executeAPI
} from '~/core/api/api-management';

interface APIExecutionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  apiDefinition: APIDefinition | null;
}

export function APIExecutionDialog({
  open,
  onOpenChange,
  apiDefinition,
}: APIExecutionDialogProps) {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [parameters, setParameters] = useState<Record<string, any>>({});
  const [result, setResult] = useState<APIExecutionResult | null>(null);
  const [activeTab, setActiveTab] = useState('parameters');

  // 初始化参数
  useEffect(() => {
    if (apiDefinition) {
      const initialParams: Record<string, any> = {};
      apiDefinition.parameters.forEach((param) => {
        if (param.default_value !== undefined) {
          initialParams[param.name] = param.default_value;
        } else if (param.example !== undefined) {
          initialParams[param.name] = param.example;
        } else {
          initialParams[param.name] = '';
        }
      });
      setParameters(initialParams);
      setResult(null);
      setActiveTab('parameters');
    }
  }, [apiDefinition]);

  const handleParameterChange = (paramName: string, value: any) => {
    setParameters(prev => ({ ...prev, [paramName]: value }));
  };

  const handleExecute = async () => {
    if (!apiDefinition) return;

    try {
      setLoading(true);
      const executionResult = await executeAPI(apiDefinition.id!, {
        parameters,
        session_id: `web_${Date.now()}`,
      });

      setResult(executionResult);
      setActiveTab('result');

      if (executionResult.success) {
        toast({
          title: '执行成功',
          description: `API执行完成，耗时 ${executionResult.execution_time_ms}ms`,
        });
      } else {
        toast({
          title: '执行失败',
          description: executionResult.result.error_message || 'API执行失败',
          variant: 'destructive',
        });
      }
    } catch (error: any) {
      toast({
        title: '执行失败',
        description: error.response?.data?.detail || '网络错误',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCopyResult = () => {
    if (result) {
      navigator.clipboard.writeText(JSON.stringify(result, null, 2));
      toast({
        title: '已复制',
        description: '执行结果已复制到剪贴板',
      });
    }
  };

  const renderParameterInput = (param: Parameter) => {
    const value = parameters[param.name] || '';

    switch (param.data_type) {
      case DataType.BOOLEAN:
        return (
          <select
            value={value.toString()}
            onChange={(e) => handleParameterChange(param.name, e.target.value === 'true')}
            className="w-full px-3 py-2 border border-input bg-background rounded-md text-sm"
          >
            <option value="false">false</option>
            <option value="true">true</option>
          </select>
        );

      case DataType.INTEGER:
        return (
          <Input
            type="number"
            value={value}
            onChange={(e) => handleParameterChange(param.name, parseInt(e.target.value) || 0)}
            placeholder={param.example?.toString() || '输入整数'}
          />
        );

      case DataType.FLOAT:
        return (
          <Input
            type="number"
            step="0.01"
            value={value}
            onChange={(e) => handleParameterChange(param.name, parseFloat(e.target.value) || 0)}
            placeholder={param.example?.toString() || '输入浮点数'}
          />
        );

      case DataType.ARRAY:
      case DataType.OBJECT:
        return (
          <Textarea
            value={typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
            onChange={(e) => {
              try {
                const parsed = JSON.parse(e.target.value);
                handleParameterChange(param.name, parsed);
              } catch {
                handleParameterChange(param.name, e.target.value);
              }
            }}
            placeholder={param.example ? JSON.stringify(param.example, null, 2) : '输入JSON格式数据'}
            rows={4}
          />
        );

      default:
        return (
          <Input
            value={value}
            onChange={(e) => handleParameterChange(param.name, e.target.value)}
            placeholder={param.example?.toString() || param.description || '输入参数值'}
          />
        );
    }
  };

  if (!apiDefinition) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>执行API - {apiDefinition.name}</DialogTitle>
          <DialogDescription>
            配置参数并执行API调用
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="parameters">参数配置</TabsTrigger>
            <TabsTrigger value="result">执行结果</TabsTrigger>
          </TabsList>

          <TabsContent value="parameters" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>API信息</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{apiDefinition.method}</Badge>
                    <span className="text-sm font-mono">{apiDefinition.url}</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {apiDefinition.description}
                  </p>
                </div>
              </CardContent>
            </Card>

            {apiDefinition.parameters.length > 0 ? (
              <Card>
                <CardHeader>
                  <CardTitle>参数配置</CardTitle>
                  <CardDescription>
                    配置API调用所需的参数
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {apiDefinition.parameters.map((param) => (
                    <div key={param.name} className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Label htmlFor={param.name}>
                          {param.name}
                          {param.required && <span className="text-red-500">*</span>}
                        </Label>
                        <Badge variant="outline" className="text-xs">
                          {param.parameter_type === ParameterType.QUERY && 'Query'}
                          {param.parameter_type === ParameterType.HEADER && 'Header'}
                          {param.parameter_type === ParameterType.PATH && 'Path'}
                          {param.parameter_type === ParameterType.BODY && 'Body'}
                          {param.parameter_type === ParameterType.FORM && 'Form'}
                        </Badge>
                        <Badge variant="secondary" className="text-xs">
                          {param.data_type === DataType.STRING && 'String'}
                          {param.data_type === DataType.INTEGER && 'Integer'}
                          {param.data_type === DataType.FLOAT && 'Float'}
                          {param.data_type === DataType.BOOLEAN && 'Boolean'}
                          {param.data_type === DataType.ARRAY && 'Array'}
                          {param.data_type === DataType.OBJECT && 'Object'}
                        </Badge>
                      </div>
                      {param.description && (
                        <p className="text-xs text-muted-foreground">
                          {param.description}
                        </p>
                      )}
                      {renderParameterInput(param)}
                    </div>
                  ))}
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="text-center py-8">
                  <p className="text-muted-foreground">此API无需参数</p>
                </CardContent>
              </Card>
            )}

            <div className="flex justify-end">
              <Button onClick={handleExecute} disabled={loading}>
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    执行中...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    执行API
                  </>
                )}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="result" className="space-y-4">
            {result ? (
              <>
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>执行结果</CardTitle>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={handleCopyResult}
                        >
                          <Copy className="h-4 w-4 mr-2" />
                          复制
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* 执行摘要 */}
                      <div className="grid grid-cols-4 gap-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold">
                            <Badge variant={result.success ? 'default' : 'destructive'}>
                              {result.success ? '成功' : '失败'}
                            </Badge>
                          </div>
                          <div className="text-xs text-muted-foreground">执行状态</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold">
                            {result.result.status_code || 'N/A'}
                          </div>
                          <div className="text-xs text-muted-foreground">状态码</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold">
                            {result.execution_time_ms}ms
                          </div>
                          <div className="text-xs text-muted-foreground">执行时间</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold">
                            {result.session_id?.split('_')[1] || 'N/A'}
                          </div>
                          <div className="text-xs text-muted-foreground">会话ID</div>
                        </div>
                      </div>

                      {/* 错误信息 */}
                      {result.result.error_message && (
                        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                          <p className="text-sm text-red-800">
                            <strong>错误:</strong> {result.result.error_message}
                          </p>
                        </div>
                      )}

                      {/* 响应数据 */}
                      {result.result.parsed_data && (
                        <div className="space-y-2">
                          <Label>响应数据</Label>
                          <Textarea
                            value={JSON.stringify(result.result.parsed_data, null, 2)}
                            readOnly
                            rows={12}
                            className="font-mono text-sm"
                          />
                        </div>
                      )}

                      {/* 原始响应 */}
                      {result.result.raw_content && (
                        <div className="space-y-2">
                          <Label>原始响应</Label>
                          <Textarea
                            value={result.result.raw_content}
                            readOnly
                            rows={6}
                            className="font-mono text-sm"
                          />
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card>
                <CardContent className="text-center py-8">
                  <p className="text-muted-foreground">
                    请先配置参数并执行API
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
