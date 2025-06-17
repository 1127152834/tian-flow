// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * Curl Import Dialog
 * curl导入对话框 - 严格按照ti-flow实现
 */

'use client';

import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle 
} from '~/components/ui/dialog';
import { Button } from '~/components/ui/button';
import { Textarea } from '~/components/ui/textarea';
import { Label } from '~/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { Badge } from '~/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '~/components/ui/tabs';
import { useToast } from '~/hooks/use-toast';

import type {
  CurlParseResult
} from '~/core/api/api-management';
import {
  HTTPMethod,
  AuthType,
  parseCurlCommand,
  importFromCurl
} from '~/core/api/api-management';

interface CurlImportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

const HTTPMethodNames = {
  [HTTPMethod.GET]: 'GET',
  [HTTPMethod.POST]: 'POST',
  [HTTPMethod.PUT]: 'PUT',
  [HTTPMethod.DELETE]: 'DELETE',
  [HTTPMethod.PATCH]: 'PATCH',
  [HTTPMethod.HEAD]: 'HEAD',
  [HTTPMethod.OPTIONS]: 'OPTIONS',
};

const AuthTypeNames = {
  [AuthType.NONE]: '无认证',
  [AuthType.API_KEY]: 'API Key',
  [AuthType.BEARER]: 'Bearer Token',
  [AuthType.BASIC]: 'Basic认证',
  [AuthType.OAUTH2]: 'OAuth2',
  [AuthType.CUSTOM]: '自定义认证',
};

export function CurlImportDialog({
  open,
  onOpenChange,
  onSuccess,
}: CurlImportDialogProps) {
  const { toast } = useToast();
  const [curlCommand, setCurlCommand] = useState('');
  const [parseResult, setParseResult] = useState<CurlParseResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [importing, setImporting] = useState(false);
  const [activeTab, setActiveTab] = useState('input');

  const handleParse = async () => {
    if (!curlCommand.trim()) {
      toast({
        title: '输入错误',
        description: '请输入curl命令',
        variant: 'destructive',
      });
      return;
    }

    try {
      setLoading(true);
      const result = await parseCurlCommand(curlCommand);
      setParseResult(result);
      
      if (result.success) {
        setActiveTab('preview');
        toast({
          title: '解析成功',
          description: 'curl命令解析完成',
        });
      } else {
        toast({
          title: '解析失败',
          description: result.error_message || '无法解析curl命令',
          variant: 'destructive',
        });
      }
    } catch (error: any) {
      toast({
        title: '解析失败',
        description: error.response?.data?.detail || '网络错误',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    if (!parseResult?.success) return;

    try {
      setImporting(true);
      await importFromCurl(curlCommand);
      
      toast({
        title: '导入成功',
        description: 'API定义已创建',
      });
      
      onSuccess?.();
      handleReset();
    } catch (error: any) {
      toast({
        title: '导入失败',
        description: error.response?.data?.detail || '导入失败',
        variant: 'destructive',
      });
    } finally {
      setImporting(false);
    }
  };

  const handleReset = () => {
    setCurlCommand('');
    setParseResult(null);
    setActiveTab('input');
  };

  const handleClose = () => {
    handleReset();
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>导入curl命令</DialogTitle>
          <DialogDescription>
            从curl命令自动创建API定义
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="input">输入curl命令</TabsTrigger>
            <TabsTrigger value="preview" disabled={!parseResult?.success}>
              预览结果
            </TabsTrigger>
          </TabsList>

          <TabsContent value="input" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>curl命令</CardTitle>
                <CardDescription>
                  粘贴您的curl命令，系统将自动解析并创建API定义
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="curl-command">curl命令 *</Label>
                  <Textarea
                    id="curl-command"
                    value={curlCommand}
                    onChange={(e) => setCurlCommand(e.target.value)}
                    placeholder={`curl -X POST 'https://api.example.com/users' \\
  -H 'Content-Type: application/json' \\
  -H 'Authorization: Bearer your-token' \\
  -d '{"name": "John", "email": "john@example.com"}'`}
                    rows={8}
                    className="font-mono text-sm"
                  />
                </div>

                <div className="flex justify-end space-x-2">
                  <Button
                    variant="outline"
                    onClick={handleReset}
                    disabled={loading}
                  >
                    清空
                  </Button>
                  <Button
                    onClick={handleParse}
                    disabled={loading || !curlCommand.trim()}
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        解析中...
                      </>
                    ) : (
                      <>
                        <FileText className="h-4 w-4 mr-2" />
                        解析curl
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* 示例 */}
            <Card>
              <CardHeader>
                <CardTitle>示例</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm font-medium mb-1">GET请求示例:</p>
                    <code className="text-xs bg-muted p-2 rounded block">
                      curl -X GET 'https://api.github.com/users/octocat'
                    </code>
                  </div>
                  <div>
                    <p className="text-sm font-medium mb-1">POST请求示例:</p>
                    <code className="text-xs bg-muted p-2 rounded block">
                      curl -X POST 'https://httpbin.org/post' -H 'Content-Type: application/json' -d '{"{\"key\":\"value\"}"}'
                    </code>
                  </div>
                  <div>
                    <p className="text-sm font-medium mb-1">带认证的请求:</p>
                    <code className="text-xs bg-muted p-2 rounded block">
                      curl -H 'Authorization: Bearer token123' 'https://api.example.com/data'
                    </code>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="preview" className="space-y-4">
            {parseResult?.success && parseResult.api_definition ? (
              <>
                <Card>
                  <CardHeader>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <CardTitle>解析成功</CardTitle>
                    </div>
                    <CardDescription>
                      以下是从curl命令解析出的API定义信息
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* 基本信息 */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-sm font-medium">API名称</Label>
                        <p className="text-sm">{parseResult.api_definition.name}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">分类</Label>
                        <p className="text-sm">{parseResult.api_definition.category}</p>
                      </div>
                    </div>

                    <div>
                      <Label className="text-sm font-medium">描述</Label>
                      <p className="text-sm">{parseResult.api_definition.description}</p>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-sm font-medium">HTTP方法</Label>
                        <Badge variant="outline">
                          {HTTPMethodNames[parseResult.api_definition.method!]}
                        </Badge>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">认证类型</Label>
                        <Badge variant="secondary">
                          {AuthTypeNames[parseResult.api_definition.auth_config?.auth_type || AuthType.NONE]}
                        </Badge>
                      </div>
                    </div>

                    <div>
                      <Label className="text-sm font-medium">URL</Label>
                      <p className="text-sm font-mono bg-muted p-2 rounded">
                        {parseResult.api_definition.url}
                      </p>
                    </div>

                    {/* 请求头 */}
                    {parseResult.api_definition.headers && Object.keys(parseResult.api_definition.headers).length > 0 && (
                      <div>
                        <Label className="text-sm font-medium">请求头</Label>
                        <div className="space-y-1">
                          {Object.entries(parseResult.api_definition.headers).map(([key, value]) => (
                            <div key={key} className="text-sm bg-muted p-2 rounded">
                              <span className="font-medium">{key}:</span> {value}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 参数 */}
                    {parseResult.api_definition.parameters && parseResult.api_definition.parameters.length > 0 && (
                      <div>
                        <Label className="text-sm font-medium">参数 ({parseResult.api_definition.parameters.length}个)</Label>
                        <div className="space-y-2">
                          {parseResult.api_definition.parameters.map((param, index) => (
                            <div key={index} className="flex items-center gap-2 text-sm bg-muted p-2 rounded">
                              <span className="font-medium">{param.name}</span>
                              <Badge variant="outline" className="text-xs">
                                {param.parameter_type === 0 && 'Query'}
                                {param.parameter_type === 1 && 'Header'}
                                {param.parameter_type === 2 && 'Path'}
                                {param.parameter_type === 3 && 'Body'}
                                {param.parameter_type === 4 && 'Form'}
                              </Badge>
                              {param.required && (
                                <Badge variant="destructive" className="text-xs">必需</Badge>
                              )}
                              {param.default_value && (
                                <span className="text-muted-foreground">
                                  默认: {String(param.default_value)}
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                <div className="flex justify-end space-x-2">
                  <Button
                    variant="outline"
                    onClick={() => setActiveTab('input')}
                  >
                    返回编辑
                  </Button>
                  <Button
                    onClick={handleImport}
                    disabled={importing}
                  >
                    {importing ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        导入中...
                      </>
                    ) : (
                      <>
                        <Upload className="h-4 w-4 mr-2" />
                        导入API
                      </>
                    )}
                  </Button>
                </div>
              </>
            ) : parseResult && !parseResult.success ? (
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-red-600" />
                    <CardTitle>解析失败</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-red-600">
                    {parseResult.error_message}
                  </p>
                  <Button
                    variant="outline"
                    onClick={() => setActiveTab('input')}
                    className="mt-4"
                  >
                    返回编辑
                  </Button>
                </CardContent>
              </Card>
            ) : null}
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
