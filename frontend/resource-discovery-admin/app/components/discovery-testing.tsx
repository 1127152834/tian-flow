'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Slider } from '@/components/ui/slider';
import { 
  Search, 
  Loader2,
  Target,
  TrendingUp,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Database,
  Globe,
  Cpu,
  FileText,
  Zap
} from 'lucide-react';
import { toast } from 'sonner';

interface DiscoveryResult {
  resource_id: string;
  resource_name: string;
  resource_type: string;
  description: string;
  confidence_score: number;
  similarity_score: number;
  reasoning: string;
}

interface TestResult {
  success: boolean;
  query: string;
  matches: DiscoveryResult[];
  total_matches: number;
  response_time: number;
  best_match?: DiscoveryResult;
}

export function DiscoveryTesting() {
  const [query, setQuery] = useState('');
  const [maxResults, setMaxResults] = useState([5]);
  const [minConfidence, setMinConfidence] = useState([0.3]);
  const [loading, setLoading] = useState(false);
  const [testResult, setTestResult] = useState<TestResult | null>(null);

  // 预定义查询示例
  const predefinedQueries = [
    '查询数据库中的用户信息',
    '调用API获取天气数据',
    '执行SQL统计分析',
    '使用系统工具处理文件',
    '获取产品销售数据',
    '分析客户行为趋势'
  ];

  // 执行资源发现测试
  const performDiscoveryTest = async () => {
    if (!query.trim()) {
      toast.error('请输入查询内容');
      return;
    }

    try {
      setLoading(true);
      const startTime = Date.now();
      
      const response = await fetch('/api/admin/resource-discovery/discover', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_query: query.trim(),
          max_results: maxResults[0],
          min_confidence: minConfidence[0]
        }),
      });

      if (!response.ok) {
        throw new Error(`API错误: ${response.status}`);
      }

      const result = await response.json();
      const responseTime = Date.now() - startTime;

      if (result.success) {
        const testResult: TestResult = {
          success: true,
          query: query.trim(),
          matches: result.data.matches || [],
          total_matches: result.data.matches?.length || 0,
          response_time: responseTime,
          best_match: result.data.matches?.[0] || undefined
        };

        setTestResult(testResult);
        
        toast.success('发现测试完成', {
          description: `找到 ${testResult.total_matches} 个匹配资源`
        });
      } else {
        throw new Error(result.error || '资源发现失败');
      }
    } catch (error) {
      console.error('资源发现测试失败:', error);
      toast.error(error instanceof Error ? error.message : '资源发现测试失败');
      setTestResult(null);
    } finally {
      setLoading(false);
    }
  };

  // 使用预定义查询
  const usePredefinedQuery = (predefinedQuery: string) => {
    setQuery(predefinedQuery);
  };

  // 获取置信度颜色
  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'confidence-high';
    if (score >= 0.6) return 'confidence-medium';
    return 'confidence-low';
  };

  // 获取置信度标签
  const getConfidenceLabel = (score: number) => {
    if (score >= 0.8) return '高置信度';
    if (score >= 0.6) return '中等置信度';
    return '低置信度';
  };

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

  return (
    <div className="space-y-6">
      {/* 测试配置 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            智能资源发现测试
          </CardTitle>
          <CardDescription>
            测试系统的智能资源发现和匹配能力
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* 查询输入 */}
          <div className="space-y-2">
            <label className="text-sm font-medium">查询内容</label>
            <Textarea
              placeholder="输入您的查询，例如：查询数据库中的用户信息..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              rows={3}
            />
          </div>

          {/* 预定义查询 */}
          <div className="space-y-2">
            <label className="text-sm font-medium">快速选择</label>
            <div className="flex flex-wrap gap-2">
              {predefinedQueries.map((predefinedQuery, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => usePredefinedQuery(predefinedQuery)}
                  className="text-xs"
                >
                  {predefinedQuery}
                </Button>
              ))}
            </div>
          </div>

          {/* 参数配置 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">
                最大结果数: {maxResults[0]}
              </label>
              <Slider
                value={maxResults}
                onValueChange={setMaxResults}
                max={20}
                min={1}
                step={1}
                className="w-full"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">
                最小置信度: {minConfidence[0].toFixed(1)}
              </label>
              <Slider
                value={minConfidence}
                onValueChange={setMinConfidence}
                max={1}
                min={0}
                step={0.1}
                className="w-full"
              />
            </div>
          </div>

          {/* 测试按钮 */}
          <Button 
            onClick={performDiscoveryTest} 
            disabled={loading || !query.trim()}
            className="w-full"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                测试中...
              </>
            ) : (
              <>
                <Target className="h-4 w-4 mr-2" />
                开始测试
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* 测试结果 */}
      {testResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              测试结果
            </CardTitle>
            <CardDescription>
              查询: "{testResult.query}"
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* 结果概览 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{testResult.total_matches}</div>
                <div className="text-sm text-blue-600">匹配资源</div>
              </div>
              <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{testResult.response_time}ms</div>
                <div className="text-sm text-green-600">响应时间</div>
              </div>
              <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {testResult.best_match ? testResult.best_match.confidence_score.toFixed(2) : 'N/A'}
                </div>
                <div className="text-sm text-purple-600">最高置信度</div>
              </div>
            </div>

            {/* 最佳匹配 */}
            {testResult.best_match && (
              <div className="space-y-2">
                <h4 className="font-medium flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                  最佳匹配
                </h4>
                <Card className="border-green-200 dark:border-green-800">
                  <CardContent className="pt-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          {getResourceTypeIcon(testResult.best_match.resource_type)}
                          <span className="font-medium">{testResult.best_match.resource_name}</span>
                          <Badge className={getConfidenceColor(testResult.best_match.confidence_score)}>
                            {getConfidenceLabel(testResult.best_match.confidence_score)}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          {testResult.best_match.description}
                        </p>
                        <div className="text-xs text-gray-500">
                          置信度: {testResult.best_match.confidence_score.toFixed(3)} | 
                          相似度: {testResult.best_match.similarity_score.toFixed(3)}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* 所有匹配结果 */}
            {testResult.matches.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-medium">所有匹配结果</h4>
                <div className="space-y-2">
                  {testResult.matches.map((match, index) => (
                    <Card key={match.resource_id} className="border-gray-200 dark:border-gray-700">
                      <CardContent className="pt-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="text-sm font-medium text-gray-500">#{index + 1}</span>
                              {getResourceTypeIcon(match.resource_type)}
                              <span className="font-medium">{match.resource_name}</span>
                              <Badge className={getConfidenceColor(match.confidence_score)}>
                                {match.confidence_score.toFixed(2)}
                              </Badge>
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                              {match.description}
                            </p>
                            <div className="text-xs text-gray-500">
                              相似度: {match.similarity_score.toFixed(3)} | 
                              类型: {match.resource_type}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* 无结果提示 */}
            {testResult.total_matches === 0 && (
              <div className="text-center py-8">
                <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">未找到匹配的资源</h3>
                <p className="text-gray-500 mb-4">
                  尝试调整查询内容或降低最小置信度阈值
                </p>
                <Button variant="outline" onClick={() => setMinConfidence([0.1])}>
                  <Zap className="h-4 w-4 mr-2" />
                  降低置信度阈值
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
