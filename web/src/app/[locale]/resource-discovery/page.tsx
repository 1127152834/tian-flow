'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { Button } from '~/components/ui/button';
import { Input } from '~/components/ui/input';
import { Textarea } from '~/components/ui/textarea';
import { Badge } from '~/components/ui/badge';
import { Slider } from '~/components/ui/slider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '~/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '~/components/ui/tabs';
import { Alert, AlertDescription } from '~/components/ui/alert';
import { Loader2, Search, Brain, Settings, Database, Zap, Target, Clock, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';

import { resourceDiscoveryApi, ResourceTestRequest, ResourceTestResponse, ResourceTestResult } from '~/core/api/resource-discovery';

export default function ResourceDiscoveryTestPage() {
  const [query, setQuery] = useState<string>('');
  const [topK, setTopK] = useState<number>(5);
  const [minConfidence, setMinConfidence] = useState<number>(0.1);
  const [selectedResourceTypes, setSelectedResourceTypes] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [testResult, setTestResult] = useState<ResourceTestResponse | null>(null);
  const [matches, setMatches] = useState<ResourceTestResult[]>([]);
  const [bestMatch, setBestMatch] = useState<ResourceTestResult | null>(null);

  // 预定义查询示例
  const predefinedQueries = [
    '查询数据库中的用户信息',
    '调用API获取产品数据',
    '执行SQL统计分析',
    '获取订单相关信息',
    '查找库存管理数据',
    '分析销售趋势数据'
  ];

  // 资源类型选项
  const resourceTypes = [
    { value: 'api', label: 'API接口' },
    { value: 'database', label: '数据库' },
    { value: 'text2sql', label: 'Text2SQL' },
    { value: 'tool', label: '系统工具' },
    { value: 'knowledge_base', label: '知识库' }
  ];

  // 执行资源匹配测试
  const performResourceMatching = async () => {
    if (!query.trim()) {
      toast.error('请输入查询内容');
      return;
    }

    setLoading(true);
    try {
      const request: ResourceTestRequest = {
        query: query.trim(),
        top_k: topK,
        min_confidence: minConfidence,
        resource_types: selectedResourceTypes.length > 0 ? selectedResourceTypes : undefined
      };

      const result = await resourceDiscoveryApi.testResourceMatching(request);
      
      setTestResult(result);
      setMatches(result.matches);
      setBestMatch(result.best_match);
      
      toast.success(`找到 ${result.total_matches} 个匹配结果`);
    } catch (error) {
      console.error('资源匹配失败:', error);
      toast.error(error instanceof Error ? error.message : '资源匹配失败');
      setTestResult(null);
      setMatches([]);
      setBestMatch(null);
    } finally {
      setLoading(false);
    }
  };

  // 使用预定义查询
  const usePredefinedQuery = (predefinedQuery: string) => {
    setQuery(predefinedQuery);
  };

  // 获取置信度颜色
  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'high': return 'bg-green-100 text-green-800 border-green-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-orange-100 text-orange-800 border-orange-200';
      default: return 'bg-red-100 text-red-800 border-red-200';
    }
  };

  // 获取置信度标签
  const getConfidenceLabel = (confidence: string) => {
    switch (confidence) {
      case 'high': return '高置信度';
      case 'medium': return '中等置信度';
      case 'low': return '低置信度';
      default: return '极低置信度';
    }
  };

  // 获取资源类型图标
  const getResourceTypeIcon = (type: string) => {
    switch (type) {
      case 'api': return <Zap className="h-4 w-4" />;
      case 'database': return <Database className="h-4 w-4" />;
      case 'text2sql': return <Brain className="h-4 w-4" />;
      case 'tool': return <Settings className="h-4 w-4" />;
      default: return <Target className="h-4 w-4" />;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Brain className="h-8 w-8 text-purple-600" />
            资源发现测试
          </h1>
          <p className="text-muted-foreground mt-2">
            测试用户查询的资源发现和匹配效果
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 测试参数配置 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              测试参数
            </CardTitle>
            <CardDescription>
              配置资源发现测试的参数
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* 匹配数量 */}
            <div>
              <label className="text-sm font-medium mb-2 block">
                匹配数量: {topK}
              </label>
              <Slider
                value={[topK]}
                onValueChange={(value) => setTopK(value[0])}
                max={20}
                min={1}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>1</span>
                <span>20</span>
              </div>
            </div>

            {/* 最低置信度 */}
            <div>
              <label className="text-sm font-medium mb-2 block">
                最低置信度: {(minConfidence * 100).toFixed(0)}%
              </label>
              <Slider
                value={[minConfidence]}
                onValueChange={(value) => setMinConfidence(value[0])}
                max={1}
                min={0}
                step={0.1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>0%</span>
                <span>100%</span>
              </div>
            </div>

            {/* 资源类型过滤 */}
            <div>
              <label className="text-sm font-medium mb-2 block">资源类型过滤</label>
              <Select
                value={selectedResourceTypes.join(',')}
                onValueChange={(value) => setSelectedResourceTypes(value ? value.split(',') : [])}
              >
                <SelectTrigger>
                  <SelectValue placeholder="选择资源类型（可选）" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">全部类型</SelectItem>
                  {resourceTypes.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* 预定义查询 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              预定义查询
            </CardTitle>
            <CardDescription>
              点击使用常见的查询示例
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 gap-2">
              {predefinedQueries.map((predefinedQuery, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => usePredefinedQuery(predefinedQuery)}
                  className="justify-start text-left h-auto py-2 px-3"
                >
                  {predefinedQuery}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 查询输入 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            测试查询
          </CardTitle>
          <CardDescription>
            输入要测试的用户查询
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="请输入要测试的用户查询，例如：查询数据库中的用户信息"
            className="min-h-24"
          />
          
          <div className="flex justify-between items-center">
            <div className="text-sm text-muted-foreground">
              {query.length} 字符
            </div>
            
            <Button 
              onClick={performResourceMatching}
              disabled={loading || !query.trim()}
              size="lg"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  测试中...
                </>
              ) : (
                <>
                  <Brain className="h-4 w-4 mr-2" />
                  开始测试
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 测试结果 */}
      {testResult && (
        <div className="space-y-6">
          {/* 结果概览 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                测试结果概览
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{testResult.total_matches}</div>
                  <div className="text-sm text-muted-foreground">匹配资源</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {testResult.processing_time.toFixed(3)}s
                  </div>
                  <div className="text-sm text-muted-foreground">处理时间</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{testResult.parameters.top_k}</div>
                  <div className="text-sm text-muted-foreground">请求数量</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {(testResult.parameters.min_confidence * 100).toFixed(0)}%
                  </div>
                  <div className="text-sm text-muted-foreground">最低置信度</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 最佳匹配 */}
          {bestMatch && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  最佳匹配
                </CardTitle>
                <CardDescription>
                  置信度最高的匹配资源
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    {getResourceTypeIcon(bestMatch.resource_type)}
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold">{bestMatch.resource_name}</h3>
                      <Badge className={getConfidenceColor(bestMatch.confidence)}>
                        {getConfidenceLabel(bestMatch.confidence)}
                      </Badge>
                      <Badge variant="outline">{bestMatch.resource_type}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{bestMatch.description}</p>
                    <div className="flex gap-4 text-sm">
                      <span>相似度: <strong>{(bestMatch.similarity_score * 100).toFixed(1)}%</strong></span>
                      <span>置信度: <strong>{(bestMatch.confidence_score * 100).toFixed(1)}%</strong></span>
                    </div>
                    {bestMatch.capabilities && bestMatch.capabilities.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {bestMatch.capabilities.slice(0, 3).map((capability, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {capability}
                          </Badge>
                        ))}
                        {bestMatch.capabilities.length > 3 && (
                          <Badge variant="secondary" className="text-xs">
                            +{bestMatch.capabilities.length - 3} 更多
                          </Badge>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 所有匹配结果 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="h-5 w-5" />
                所有匹配结果
              </CardTitle>
              <CardDescription>
                按置信度排序的所有匹配资源
              </CardDescription>
            </CardHeader>
            <CardContent>
              {matches.length === 0 ? (
                <Alert>
                  <AlertDescription>
                    没有找到匹配的资源。请尝试调整查询内容或降低最低置信度。
                  </AlertDescription>
                </Alert>
              ) : (
                <div className="space-y-4">
                  {matches.map((match, index) => (
                    <div key={match.resource_id} className="border rounded-lg p-4 space-y-3">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-muted-foreground">#{index + 1}</span>
                          {getResourceTypeIcon(match.resource_type)}
                          <h4 className="font-medium">{match.resource_name}</h4>
                          <Badge className={getConfidenceColor(match.confidence)}>
                            {getConfidenceLabel(match.confidence)}
                          </Badge>
                          <Badge variant="outline">{match.resource_type}</Badge>
                        </div>
                        <div className="text-right text-sm">
                          <div>相似度: <strong>{(match.similarity_score * 100).toFixed(1)}%</strong></div>
                          <div>置信度: <strong>{(match.confidence_score * 100).toFixed(1)}%</strong></div>
                        </div>
                      </div>

                      <p className="text-sm text-muted-foreground">{match.description}</p>

                      {match.capabilities && match.capabilities.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {match.capabilities.map((capability, capIndex) => (
                            <Badge key={capIndex} variant="secondary" className="text-xs">
                              {capability}
                            </Badge>
                          ))}
                        </div>
                      )}

                      <div className="text-xs text-muted-foreground">
                        <strong>匹配原因:</strong> {match.reasoning}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
