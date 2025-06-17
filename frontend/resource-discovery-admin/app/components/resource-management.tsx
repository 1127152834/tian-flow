'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { 
  Search, 
  Filter, 
  RefreshCw, 
  Loader2,
  Database,
  Globe,
  Cpu,
  FileText,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Eye,
  Edit,
  Trash2
} from 'lucide-react';
import { toast } from 'sonner';

interface Resource {
  resource_id: string;
  resource_name: string;
  resource_type: 'database' | 'api' | 'tool' | 'text2sql';
  description: string;
  capabilities: string[];
  tags: string[];
  metadata: Record<string, any>;
  is_active: boolean;
  status: 'active' | 'inactive' | 'error';
  vectorization_status: 'completed' | 'pending' | 'failed';
  usage_count: number;
  success_rate: number;
  avg_response_time: number;
  created_at: string;
  updated_at: string;
}

interface ResourceManagementProps {
  onRefresh: () => Promise<void>;
}

export function ResourceManagement({ onRefresh }: ResourceManagementProps) {
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // 加载资源列表
  const loadResources = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/admin/resource-discovery/resources');
      
      if (!response.ok) {
        throw new Error(`API错误: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        setResources(result.data.resources || []);
      } else {
        throw new Error(result.error || '获取资源列表失败');
      }
    } catch (error) {
      console.error('加载资源列表失败:', error);
      toast.error(error instanceof Error ? error.message : '加载资源列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadResources();
  }, []);

  // 过滤资源
  const filteredResources = resources.filter(resource => {
    const matchesSearch = resource.resource_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         resource.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = typeFilter === 'all' || resource.resource_type === typeFilter;
    const matchesStatus = statusFilter === 'all' || resource.status === statusFilter;
    
    return matchesSearch && matchesType && matchesStatus;
  });

  // 获取资源类型图标
  const getResourceTypeIcon = (type: string) => {
    switch (type) {
      case 'database':
        return <Database className="h-4 w-4" />;
      case 'api':
        return <Globe className="h-4 w-4" />;
      case 'tool':
        return <Cpu className="h-4 w-4" />;
      case 'text2sql':
        return <FileText className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'inactive':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
      case 'error':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  // 获取向量化状态图标
  const getVectorizationStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'pending':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* 搜索和过滤 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            资源管理
          </CardTitle>
          <CardDescription>
            查看和管理系统中发现的所有资源
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4 mb-4">
            {/* 搜索框 */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="搜索资源名称或描述..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* 类型过滤 */}
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="资源类型" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">所有类型</SelectItem>
                <SelectItem value="database">数据库</SelectItem>
                <SelectItem value="api">API</SelectItem>
                <SelectItem value="tool">工具</SelectItem>
                <SelectItem value="text2sql">Text2SQL</SelectItem>
              </SelectContent>
            </Select>

            {/* 状态过滤 */}
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="状态" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">所有状态</SelectItem>
                <SelectItem value="active">活跃</SelectItem>
                <SelectItem value="inactive">非活跃</SelectItem>
                <SelectItem value="error">错误</SelectItem>
              </SelectContent>
            </Select>

            {/* 刷新按钮 */}
            <Button onClick={loadResources} disabled={loading} variant="outline">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              刷新
            </Button>
          </div>

          {/* 统计信息 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{resources.length}</div>
              <div className="text-sm text-blue-600">总资源数</div>
            </div>
            <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {resources.filter(r => r.status === 'active').length}
              </div>
              <div className="text-sm text-green-600">活跃资源</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">
                {resources.filter(r => r.vectorization_status === 'completed').length}
              </div>
              <div className="text-sm text-yellow-600">已向量化</div>
            </div>
            <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{filteredResources.length}</div>
              <div className="text-sm text-purple-600">筛选结果</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 资源列表 */}
      <Card>
        <CardHeader>
          <CardTitle>资源列表</CardTitle>
          <CardDescription>
            显示 {filteredResources.length} 个资源
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin" />
              <span className="ml-2">加载中...</span>
            </div>
          ) : filteredResources.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              没有找到匹配的资源
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>资源名称</TableHead>
                    <TableHead>类型</TableHead>
                    <TableHead>状态</TableHead>
                    <TableHead>向量化</TableHead>
                    <TableHead>使用次数</TableHead>
                    <TableHead>成功率</TableHead>
                    <TableHead>响应时间</TableHead>
                    <TableHead>操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredResources.map((resource) => (
                    <TableRow key={resource.resource_id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{resource.resource_name}</div>
                          <div className="text-sm text-gray-500 truncate max-w-xs">
                            {resource.description}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getResourceTypeIcon(resource.resource_type)}
                          <span className="capitalize">{resource.resource_type}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(resource.status)}>
                          {resource.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getVectorizationStatusIcon(resource.vectorization_status)}
                          <span className="text-sm capitalize">{resource.vectorization_status}</span>
                        </div>
                      </TableCell>
                      <TableCell>{resource.usage_count}</TableCell>
                      <TableCell>{resource.success_rate.toFixed(1)}%</TableCell>
                      <TableCell>{resource.avg_response_time}ms</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button size="sm" variant="outline">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button size="sm" variant="outline">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button size="sm" variant="outline">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
