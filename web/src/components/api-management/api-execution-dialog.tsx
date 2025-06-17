// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * API Execution Dialog
 * API执行对话框 - 严格按照ti-flow实现
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Play, Copy, CheckCircle, XCircle, Clock, Zap, Globe, Code, FileText, AlertCircle } from 'lucide-react';
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
import { Alert, AlertDescription } from '~/components/ui/alert';
import { Separator } from '~/components/ui/separator';
import { APIExecutionHistory } from './api-execution-history';

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
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto w-full" style={{ width: '1200px', maxWidth: '90vw' }}>
        <DialogHeader>
          <DialogTitle>执行API - {apiDefinition.name}</DialogTitle>
          <DialogDescription>
            配置参数并执行API调用
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="parameters">参数配置</TabsTrigger>
            <TabsTrigger value="result">执行结果</TabsTrigger>
            <TabsTrigger value="history">执行历史</TabsTrigger>
          </TabsList>

          <TabsContent value="parameters" className="space-y-6">
            {/* API信息概览 */}
            <Card className="border-l-4 border-l-blue-500 bg-blue-50/50">
              <CardContent className="pt-6">
                <div className="flex items-start gap-4">
                  <div className="p-2 rounded-lg bg-blue-100 text-blue-600">
                    <Globe className="h-6 w-6" />
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold">{apiDefinition.name}</h3>
                      <Badge
                        variant="outline"
                        className={`${
                          apiDefinition.method === 'GET' ? 'border-green-500 text-green-700 bg-green-50' :
                          apiDefinition.method === 'POST' ? 'border-blue-500 text-blue-700 bg-blue-50' :
                          apiDefinition.method === 'PUT' ? 'border-orange-500 text-orange-700 bg-orange-50' :
                          apiDefinition.method === 'DELETE' ? 'border-red-500 text-red-700 bg-red-50' :
                          'border-gray-500 text-gray-700 bg-gray-50'
                        }`}
                      >
                        {apiDefinition.method}
                      </Badge>
                      <Badge variant="secondary">{apiDefinition.category}</Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <Code className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm font-mono bg-white px-2 py-1 rounded border">
                        {apiDefinition.url}
                      </span>
                    </div>
                    {apiDefinition.description && (
                      <p className="text-sm text-muted-foreground">
                        {apiDefinition.description}
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 参数配置 */}
            {apiDefinition.parameters.length > 0 ? (
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <Zap className="h-5 w-5 text-purple-600" />
                    <CardTitle className="text-lg">参数配置</CardTitle>
                  </div>
                  <CardDescription>
                    配置API调用所需的参数，必填参数标有红色星号
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {apiDefinition.parameters.map((param) => (
                    <div key={param.name} className="p-4 border rounded-lg hover:bg-muted/30 transition-colors">
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <Label htmlFor={param.name} className="text-base font-medium">
                              {param.name}
                              {param.required && <span className="text-red-500 ml-1">*</span>}
                            </Label>
                            <div className="flex gap-2">
                              <Badge
                                variant="outline"
                                className={`text-xs ${
                                  param.parameter_type === ParameterType.QUERY ? 'border-blue-500 text-blue-700 bg-blue-50' :
                                  param.parameter_type === ParameterType.HEADER ? 'border-green-500 text-green-700 bg-green-50' :
                                  param.parameter_type === ParameterType.PATH ? 'border-orange-500 text-orange-700 bg-orange-50' :
                                  param.parameter_type === ParameterType.BODY ? 'border-purple-500 text-purple-700 bg-purple-50' :
                                  'border-gray-500 text-gray-700 bg-gray-50'
                                }`}
                              >
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
                          </div>
                        </div>
                        {param.description && (
                          <p className="text-sm text-muted-foreground bg-muted/50 p-2 rounded">
                            {param.description}
                          </p>
                        )}
                        <div className="pt-2">
                          {renderParameterInput(param)}
                        </div>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            ) : (
              <Card className="border-dashed">
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <div className="p-4 rounded-full bg-muted mb-4">
                    <CheckCircle className="h-8 w-8 text-muted-foreground" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">无需参数</h3>
                  <p className="text-muted-foreground text-center">
                    此API不需要任何参数，可以直接执行
                  </p>
                </CardContent>
              </Card>
            )}

            {/* 执行按钮 */}
            <div className="flex justify-between items-center pt-4 border-t">
              <div className="text-sm text-muted-foreground">
                {apiDefinition.parameters.length > 0 && (
                  <>
                    共 {apiDefinition.parameters.length} 个参数，
                    其中 {apiDefinition.parameters.filter(p => p.required).length} 个必填
                  </>
                )}
              </div>
              <Button
                onClick={handleExecute}
                disabled={loading}
                size="lg"
                className="gap-2 min-w-32"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    执行中...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4" />
                    执行API
                  </>
                )}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="result" className="space-y-6">
            {result ? (
              <>
                {/* 执行状态概览 */}
                <Card className={`border-l-4 ${result.success ? 'border-l-green-500 bg-green-50/50' : 'border-l-red-500 bg-red-50/50'}`}>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {result.success ? (
                          <CheckCircle className="h-8 w-8 text-green-600" />
                        ) : (
                          <XCircle className="h-8 w-8 text-red-600" />
                        )}
                        <div>
                          <h3 className="text-lg font-semibold">
                            {result.success ? '执行成功' : '执行失败'}
                          </h3>
                          <p className="text-sm text-muted-foreground">
                            API调用已完成，查看详细结果
                          </p>
                        </div>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleCopyResult}
                        className="gap-2"
                      >
                        <Copy className="h-4 w-4" />
                        复制结果
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* 执行指标 */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Card>
                    <CardContent className="pt-6">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${result.success ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                          {result.success ? <CheckCircle className="h-5 w-5" /> : <XCircle className="h-5 w-5" />}
                        </div>
                        <div>
                          <p className="text-2xl font-bold">
                            {result.result.status_code || 'N/A'}
                          </p>
                          <p className="text-xs text-muted-foreground">HTTP状态码</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="pt-6">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-blue-100 text-blue-600">
                          <Clock className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="text-2xl font-bold">
                            {result.execution_time_ms}
                          </p>
                          <p className="text-xs text-muted-foreground">响应时间(ms)</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="pt-6">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-purple-100 text-purple-600">
                          <Zap className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="text-2xl font-bold">
                            {result.result.data && typeof result.result.data === 'object' ? Object.keys(result.result.data).length : 0}
                          </p>
                          <p className="text-xs text-muted-foreground">响应字段数</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="pt-6">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-orange-100 text-orange-600">
                          <Globe className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="text-lg font-bold truncate">
                            {result.session_id?.slice(-8) || 'N/A'}
                          </p>
                          <p className="text-xs text-muted-foreground">会话ID</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* 错误信息 */}
                {result.result.error_message && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="font-medium">
                      {result.result.error_message}
                    </AlertDescription>
                  </Alert>
                )}

                {/* 响应内容 */}
                <div className="grid gap-6">
                  {/* 结构化响应数据 */}
                  {result.result.data && (
                    <Card>
                      <CardHeader>
                        <div className="flex items-center gap-2">
                          <Code className="h-5 w-5 text-blue-600" />
                          <CardTitle className="text-lg">结构化响应数据</CardTitle>
                        </div>
                        <CardDescription>
                          解析后的JSON响应数据，便于查看和使用
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="relative">
                          <pre className="bg-slate-50 p-4 rounded-lg overflow-auto max-h-96 text-sm border">
                            <code className="language-json">
                              {JSON.stringify(result.result.data, null, 2)}
                            </code>
                          </pre>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="absolute top-2 right-2"
                            onClick={() => navigator.clipboard.writeText(JSON.stringify(result.result.data, null, 2))}
                          >
                            <Copy className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* 原始响应 */}
                  {result.result.raw_response && (
                    <Card>
                      <CardHeader>
                        <div className="flex items-center gap-2">
                          <FileText className="h-5 w-5 text-gray-600" />
                          <CardTitle className="text-lg">原始响应内容</CardTitle>
                        </div>
                        <CardDescription>
                          服务器返回的原始响应内容
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="relative">
                          <Textarea
                            value={result.result.raw_response}
                            readOnly
                            rows={8}
                            className="font-mono text-sm resize-none"
                          />
                          <Button
                            variant="ghost"
                            size="sm"
                            className="absolute top-2 right-2"
                            onClick={() => navigator.clipboard.writeText(result.result.raw_response)}
                          >
                            <Copy className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </>
            ) : (
              <Card className="border-dashed">
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <div className="p-4 rounded-full bg-muted mb-4">
                    <Play className="h-8 w-8 text-muted-foreground" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">准备执行API</h3>
                  <p className="text-muted-foreground text-center max-w-sm">
                    请先在参数配置页面设置必要的参数，然后点击执行按钮开始API调用
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="history" className="space-y-4">
            <APIExecutionHistory apiDefinitionId={apiDefinition.id} />
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
