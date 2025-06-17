// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * API Management Tab
 * API管理标签页 - 严格按照ti-flow实现
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Plus, Search, Filter, MoreHorizontal, Play, Settings, Trash2, Edit, Copy, Globe } from 'lucide-react';

import { useLanguage } from '~/contexts/language-context';

import type { Tab } from './types';
import { Button } from '~/components/ui/button';
import { Input } from '~/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { Badge } from '~/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '~/components/ui/tabs';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator
} from '~/components/ui/dropdown-menu';
import { useToast } from '~/hooks/use-toast';

import {
  type APIDefinition,
  HTTPMethod,
  type APIStatistics,
  type CallStatistics,
  listAPIDefinitions,
  deleteAPIDefinition,
  toggleAPIEnabled,
  getAPIStatistics,
  getCallStatistics,
  getAPICategories
} from '~/core/api/api-management';
import { APIDefinitionDialog } from '~/components/api-management/api-definition-dialog';
import { APIExecutionDialog } from '~/components/api-management/api-execution-dialog';
import { CurlImportDialog } from '~/components/api-management/curl-import-dialog';
import { APICallLogsTable } from '~/components/api-management/api-call-logs-table';

const HTTPMethodColors = {
  [HTTPMethod.GET]: 'bg-green-100 text-green-800',
  [HTTPMethod.POST]: 'bg-blue-100 text-blue-800',
  [HTTPMethod.PUT]: 'bg-yellow-100 text-yellow-800',
  [HTTPMethod.DELETE]: 'bg-red-100 text-red-800',
  [HTTPMethod.PATCH]: 'bg-purple-100 text-purple-800',
  [HTTPMethod.HEAD]: 'bg-gray-100 text-gray-800',
  [HTTPMethod.OPTIONS]: 'bg-gray-100 text-gray-800',
};

const HTTPMethodNames = {
  [HTTPMethod.GET]: 'GET',
  [HTTPMethod.POST]: 'POST',
  [HTTPMethod.PUT]: 'PUT',
  [HTTPMethod.DELETE]: 'DELETE',
  [HTTPMethod.PATCH]: 'PATCH',
  [HTTPMethod.HEAD]: 'HEAD',
  [HTTPMethod.OPTIONS]: 'OPTIONS',
};

export const APIManagementTab: Tab = () => {
  const { toast } = useToast();
  const { t } = useLanguage();
  
  // 状态管理
  const [apis, setApis] = useState<APIDefinition[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [categories, setCategories] = useState<string[]>([]);
  const [statistics, setStatistics] = useState<APIStatistics | null>(null);
  const [callStatistics, setCallStatistics] = useState<CallStatistics | null>(null);
  
  // 对话框状态
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showExecutionDialog, setShowExecutionDialog] = useState(false);
  const [showCurlImportDialog, setShowCurlImportDialog] = useState(false);
  const [selectedAPI, setSelectedAPI] = useState<APIDefinition | null>(null);

  // 加载数据
  useEffect(() => {
    loadAPIs();
    loadCategories();
    loadStatistics();
  }, [searchQuery, selectedCategory]);

  const loadAPIs = async () => {
    try {
      setLoading(true);
      const data = await listAPIDefinitions({
        search: searchQuery || undefined,
        category: selectedCategory || undefined,
        limit: 100,
      });
      setApis(data);
    } catch (error) {
      toast({
        title: t('settings.apiManagement.messages.loadFailed'),
        description: t('settings.apiManagement.messages.loadFailedDescription'),
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const data = await getAPICategories();
      setCategories(data.categories);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const loadStatistics = async () => {
    try {
      const [apiStats, callStats] = await Promise.all([
        getAPIStatistics(),
        getCallStatistics({ days: 7 }),
      ]);
      setStatistics(apiStats);
      setCallStatistics(callStats);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    }
  };

  // 操作处理
  const handleCreateAPI = () => {
    setSelectedAPI(null);
    setShowCreateDialog(true);
  };

  const handleEditAPI = (api: APIDefinition) => {
    setSelectedAPI(api);
    setShowEditDialog(true);
  };

  const handleExecuteAPI = (api: APIDefinition) => {
    setSelectedAPI(api);
    setShowExecutionDialog(true);
  };

  const handleDeleteAPI = async (api: APIDefinition) => {
    if (!confirm(t('settings.apiManagement.messages.deleteConfirm', { name: api.name }))) {
      return;
    }

    try {
      await deleteAPIDefinition(api.id!);
      toast({
        title: t('settings.apiManagement.messages.deleteSuccess'),
        description: t('settings.apiManagement.messages.deleteSuccessDescription', { name: api.name }),
      });
      loadAPIs();
    } catch (error) {
      toast({
        title: t('settings.apiManagement.messages.deleteFailed'),
        description: t('settings.apiManagement.messages.deleteFailedDescription'),
        variant: 'destructive',
      });
    }
  };

  const handleToggleEnabled = async (api: APIDefinition) => {
    try {
      await toggleAPIEnabled(api.id!);
      const status = api.enabled ? t('settings.apiManagement.actions.disable') : t('settings.apiManagement.actions.enable');
      toast({
        title: t('settings.apiManagement.messages.statusUpdated'),
        description: t('settings.apiManagement.messages.statusUpdatedDescription', { name: api.name, status }),
      });
      loadAPIs();
    } catch (error) {
      toast({
        title: t('settings.apiManagement.messages.updateFailed'),
        description: t('settings.apiManagement.messages.updateFailedDescription'),
        variant: 'destructive',
      });
    }
  };

  const handleCopyAPI = (api: APIDefinition) => {
    const apiData = {
      ...api,
      name: `${api.name} (副本)`,
      id: undefined,
      created_at: undefined,
      updated_at: undefined,
    };
    navigator.clipboard.writeText(JSON.stringify(apiData, null, 2));
    toast({
      title: t('settings.apiManagement.messages.copied'),
      description: t('settings.apiManagement.messages.copiedDescription'),
    });
  };

  const handleDialogSuccess = () => {
    loadAPIs();
    loadStatistics();
    setShowCreateDialog(false);
    setShowEditDialog(false);
    setShowCurlImportDialog(false);
  };

  return (
    <div className="space-y-6">
      {/* 统计卡片 */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{t('settings.apiManagement.statistics.totalApis')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.total_apis}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{t('settings.apiManagement.statistics.enabledApis')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{statistics.enabled_apis}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{t('settings.apiManagement.statistics.sevenDayCalls')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{callStatistics?.total_calls || 0}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{t('settings.apiManagement.statistics.successRate')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {callStatistics?.success_rate?.toFixed(1) || 0}%
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 主要内容 */}
      <Tabs defaultValue="apis" className="space-y-4">
        <TabsList>
          <TabsTrigger value="apis">{t('settings.apiManagement.tabs.apiDefinitions')}</TabsTrigger>
          <TabsTrigger value="logs">{t('settings.apiManagement.tabs.callLogs')}</TabsTrigger>
        </TabsList>

        <TabsContent value="apis" className="space-y-4">
          {/* 工具栏 */}
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div className="flex flex-1 gap-2 max-w-md">
              <div className="relative flex-1">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder={t('settings.apiManagement.actions.searchPlaceholder')}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-8"
                />
              </div>
              {categories.length > 0 && (
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="px-3 py-2 border border-input bg-background rounded-md text-sm"
                >
                  <option value="">{t('settings.apiManagement.actions.allCategories')}</option>
                  {categories.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </select>
              )}
            </div>
            
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setShowCurlImportDialog(true)}
              >
                {t('settings.apiManagement.actions.importCurl')}
              </Button>
              <Button onClick={handleCreateAPI}>
                <Plus className="h-4 w-4 mr-2" />
                {t('settings.apiManagement.actions.newApi')}
              </Button>
            </div>
          </div>

          {/* API列表 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {loading ? (
              <div className="col-span-full text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="mt-2 text-muted-foreground">{t('settings.apiManagement.status.loading')}</p>
              </div>
            ) : apis.length === 0 ? (
              <div className="col-span-full text-center py-8">
                <p className="text-muted-foreground">{t('settings.apiManagement.status.noApis')}</p>
              </div>
            ) : (
              apis.map((api) => (
                <Card key={api.id} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="space-y-1 flex-1 min-w-0">
                        <CardTitle className="text-base truncate">{api.name}</CardTitle>
                        <CardDescription className="text-sm line-clamp-2">
                          {api.description}
                        </CardDescription>
                      </div>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleExecuteAPI(api)}>
                            <Play className="h-4 w-4 mr-2" />
                            {t('settings.apiManagement.actions.execute')}
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleEditAPI(api)}>
                            <Edit className="h-4 w-4 mr-2" />
                            {t('settings.apiManagement.actions.edit')}
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleCopyAPI(api)}>
                            <Copy className="h-4 w-4 mr-2" />
                            {t('settings.apiManagement.actions.copy')}
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            onClick={() => handleToggleEnabled(api)}
                            className={api.enabled ? 'text-orange-600' : 'text-green-600'}
                          >
                            <Settings className="h-4 w-4 mr-2" />
                            {api.enabled ? t('settings.apiManagement.actions.disable') : t('settings.apiManagement.actions.enable')}
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() => handleDeleteAPI(api)}
                            className="text-red-600"
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            {t('settings.apiManagement.actions.delete')}
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Badge 
                          variant="secondary" 
                          className={HTTPMethodColors[api.method]}
                        >
                          {HTTPMethodNames[api.method]}
                        </Badge>
                        <Badge variant={api.enabled ? 'default' : 'secondary'}>
                          {api.enabled ? t('settings.apiManagement.status.enabled') : t('settings.apiManagement.status.disabled')}
                        </Badge>
                        <Badge variant="outline">{api.category}</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground truncate">
                        {api.url}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        <TabsContent value="logs">
          <APICallLogsTable />
        </TabsContent>
      </Tabs>

      {/* 对话框 */}
      <APIDefinitionDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
        onSuccess={handleDialogSuccess}
      />

      <APIDefinitionDialog
        open={showEditDialog}
        onOpenChange={setShowEditDialog}
        apiDefinition={selectedAPI}
        onSuccess={handleDialogSuccess}
      />

      <APIExecutionDialog
        open={showExecutionDialog}
        onOpenChange={setShowExecutionDialog}
        apiDefinition={selectedAPI}
      />

      <CurlImportDialog
        open={showCurlImportDialog}
        onOpenChange={setShowCurlImportDialog}
        onSuccess={handleDialogSuccess}
      />
    </div>
  );
};

APIManagementTab.displayName = "API Management";
APIManagementTab.icon = Globe;
