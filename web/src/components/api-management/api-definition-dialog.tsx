// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * API Definition Dialog
 * API定义对话框 - 严格按照ti-flow实现
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '~/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { Switch } from '~/components/ui/switch';
import { useToast } from '~/hooks/use-toast';

import {
  HTTPMethod,
  AuthType,
  apiManagementClient
} from '~/core/api/api-management';
import type {
  APIDefinition,
  AuthConfig,
  Parameter,
  ResponseConfig,
  RateLimit,
} from '~/core/api/api-management';
import { ParameterEditor } from './parameter-editor';
import { AuthConfigEditor } from './auth-config-editor';
import { ResponseConfigEditor } from './response-config-editor';
import { RateLimitEditor } from './rate-limit-editor';

const apiDefinitionSchema = z.object({
  name: z.string().min(1, '名称不能为空').max(100, '名称不能超过100个字符'),
  description: z.string().min(1, '描述不能为空').max(500, '描述不能超过500个字符'),
  category: z.string().min(1, '分类不能为空').max(50, '分类不能超过50个字符'),
  method: z.nativeEnum(HTTPMethod),
  url: z.string().url('请输入有效的URL'),
  timeout_seconds: z.number().min(5, '超时时间不能少于5秒').max(300, '超时时间不能超过300秒'),
  enabled: z.boolean(),
});

type APIDefinitionFormData = z.infer<typeof apiDefinitionSchema>;

interface APIDefinitionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  apiDefinition?: APIDefinition | null;
  onSuccess?: () => void;
}

export function APIDefinitionDialog({
  open,
  onOpenChange,
  apiDefinition,
  onSuccess,
}: APIDefinitionDialogProps) {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('basic');
  
  // 表单状态
  const [headers, setHeaders] = useState<Record<string, string>>({});
  const [authConfig, setAuthConfig] = useState<AuthConfig>({
    auth_type: AuthType.NONE,
  });
  const [parameters, setParameters] = useState<Parameter[]>([]);
  const [responseConfig, setResponseConfig] = useState<ResponseConfig>({
    response_type: 1, // JSON
    content_type: 'application/json',
    encoding: 'utf-8',
    fields: [],
    success_conditions: {},
  });
  const [rateLimit, setRateLimit] = useState<RateLimit>({
    enabled: false,
    rate_limit_type: 0,
    max_requests: 100,
    time_window_seconds: 60,
    block_on_limit: true,
  });

  const form = useForm<APIDefinitionFormData>({
    resolver: zodResolver(apiDefinitionSchema),
    defaultValues: {
      name: '',
      description: '',
      category: 'general',
      method: HTTPMethod.GET,
      url: '',
      timeout_seconds: 30,
      enabled: true,
    },
  });

  // 初始化表单数据
  useEffect(() => {
    if (apiDefinition) {
      form.reset({
        name: apiDefinition.name,
        description: apiDefinition.description,
        category: apiDefinition.category,
        method: apiDefinition.method,
        url: apiDefinition.url,
        timeout_seconds: apiDefinition.timeout_seconds,
        enabled: apiDefinition.enabled,
      });
      setHeaders(apiDefinition.headers || {});
      setAuthConfig(apiDefinition.auth_config);
      setParameters(apiDefinition.parameters || []);
      setResponseConfig(apiDefinition.response_config);
      setRateLimit(apiDefinition.rate_limit);
    } else {
      // 重置为默认值
      form.reset({
        name: '',
        description: '',
        category: 'general',
        method: HTTPMethod.GET,
        url: '',
        timeout_seconds: 30,
        enabled: true,
      });
      setHeaders({});
      setAuthConfig({ auth_type: AuthType.NONE });
      setParameters([]);
      setResponseConfig({
        response_type: 1,
        content_type: 'application/json',
        encoding: 'utf-8',
        fields: [],
        success_conditions: {},
      });
      setRateLimit({
        enabled: false,
        rate_limit_type: 0,
        max_requests: 100,
        time_window_seconds: 60,
        block_on_limit: true,
      });
    }
  }, [apiDefinition, form]);

  const onSubmit = async (data: APIDefinitionFormData) => {
    try {
      setLoading(true);

      const apiData = {
        ...data,
        headers,
        auth_config: authConfig,
        parameters,
        response_config: responseConfig,
        rate_limit: rateLimit,
      };

      if (apiDefinition?.id) {
        // 更新
        await apiManagementClient.updateAPIDefinition(apiDefinition.id, apiData);
        toast({
          title: '更新成功',
          description: `API "${data.name}" 已更新`,
        });
      } else {
        // 创建
        await apiManagementClient.createAPIDefinition(apiData);
        toast({
          title: '创建成功',
          description: `API "${data.name}" 已创建`,
        });
      }

      onSuccess?.();
    } catch (error: any) {
      toast({
        title: '操作失败',
        description: error.response?.data?.detail || '操作失败，请重试',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {apiDefinition ? '编辑API定义' : '创建API定义'}
          </DialogTitle>
          <DialogDescription>
            配置API的基本信息、认证、参数和响应处理
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="basic">基本信息</TabsTrigger>
              <TabsTrigger value="auth">认证配置</TabsTrigger>
              <TabsTrigger value="parameters">参数定义</TabsTrigger>
              <TabsTrigger value="response">响应配置</TabsTrigger>
              <TabsTrigger value="advanced">高级设置</TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>基本信息</CardTitle>
                  <CardDescription>配置API的基本信息和HTTP设置</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">API名称 *</Label>
                      <Input
                        id="name"
                        {...form.register('name')}
                        placeholder="输入API名称"
                      />
                      {form.formState.errors.name && (
                        <p className="text-sm text-red-600">
                          {form.formState.errors.name.message}
                        </p>
                      )}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="category">分类 *</Label>
                      <Input
                        id="category"
                        {...form.register('category')}
                        placeholder="输入分类"
                      />
                      {form.formState.errors.category && (
                        <p className="text-sm text-red-600">
                          {form.formState.errors.category.message}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="description">描述 *</Label>
                    <Textarea
                      id="description"
                      {...form.register('description')}
                      placeholder="输入API描述"
                      rows={3}
                    />
                    {form.formState.errors.description && (
                      <p className="text-sm text-red-600">
                        {form.formState.errors.description.message}
                      </p>
                    )}
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="method">HTTP方法 *</Label>
                      <select
                        id="method"
                        {...form.register('method', { valueAsNumber: true })}
                        className="w-full px-3 py-2 border border-input bg-background rounded-md text-sm"
                      >
                        <option value={HTTPMethod.GET}>GET</option>
                        <option value={HTTPMethod.POST}>POST</option>
                        <option value={HTTPMethod.PUT}>PUT</option>
                        <option value={HTTPMethod.DELETE}>DELETE</option>
                        <option value={HTTPMethod.PATCH}>PATCH</option>
                        <option value={HTTPMethod.HEAD}>HEAD</option>
                        <option value={HTTPMethod.OPTIONS}>OPTIONS</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="timeout_seconds">超时时间(秒) *</Label>
                      <Input
                        id="timeout_seconds"
                        type="number"
                        min={5}
                        max={300}
                        {...form.register('timeout_seconds', { valueAsNumber: true })}
                      />
                      {form.formState.errors.timeout_seconds && (
                        <p className="text-sm text-red-600">
                          {form.formState.errors.timeout_seconds.message}
                        </p>
                      )}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="enabled">启用状态</Label>
                      <div className="flex items-center space-x-2 pt-2">
                        <Switch
                          id="enabled"
                          checked={form.watch('enabled')}
                          onCheckedChange={(checked) => form.setValue('enabled', checked)}
                        />
                        <Label htmlFor="enabled">
                          {form.watch('enabled') ? '已启用' : '已禁用'}
                        </Label>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="url">API地址 *</Label>
                    <Input
                      id="url"
                      {...form.register('url')}
                      placeholder="https://api.example.com/endpoint"
                    />
                    {form.formState.errors.url && (
                      <p className="text-sm text-red-600">
                        {form.formState.errors.url.message}
                      </p>
                    )}
                  </div>

                  {/* 请求头编辑器 */}
                  <div className="space-y-2">
                    <Label>默认请求头</Label>
                    <div className="space-y-2">
                      {Object.entries(headers).map(([key, value], index) => (
                        <div key={index} className="flex gap-2">
                          <Input
                            placeholder="Header名称"
                            value={key}
                            onChange={(e) => {
                              const newHeaders = { ...headers };
                              delete newHeaders[key];
                              newHeaders[e.target.value] = value;
                              setHeaders(newHeaders);
                            }}
                          />
                          <Input
                            placeholder="Header值"
                            value={value}
                            onChange={(e) => {
                              setHeaders({ ...headers, [key]: e.target.value });
                            }}
                          />
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              const newHeaders = { ...headers };
                              delete newHeaders[key];
                              setHeaders(newHeaders);
                            }}
                          >
                            删除
                          </Button>
                        </div>
                      ))}
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => setHeaders({ ...headers, '': '' })}
                      >
                        添加请求头
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="auth">
              <AuthConfigEditor
                authConfig={authConfig}
                onChange={setAuthConfig}
              />
            </TabsContent>

            <TabsContent value="parameters">
              <ParameterEditor
                parameters={parameters}
                onChange={setParameters}
              />
            </TabsContent>

            <TabsContent value="response">
              <ResponseConfigEditor
                responseConfig={responseConfig}
                onChange={setResponseConfig}
              />
            </TabsContent>

            <TabsContent value="advanced">
              <RateLimitEditor
                rateLimit={rateLimit}
                onChange={setRateLimit}
              />
            </TabsContent>
          </Tabs>

          <div className="flex justify-end space-x-2 pt-4 border-t">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              取消
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? '保存中...' : (apiDefinition ? '更新' : '创建')}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
