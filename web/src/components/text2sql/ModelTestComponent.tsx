"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Label } from "~/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select";
import { Alert, AlertDescription } from "~/components/ui/alert";
import { Badge } from "~/components/ui/badge";
import { Separator } from "~/components/ui/separator";
import { ScrollArea } from "~/components/ui/scroll-area";
import { 
  TestTube, 
  Play, 
  Copy, 
  Download, 
  Loader2, 
  CheckCircle, 
  XCircle,
  Clock,
  Lightbulb,
  Database,
  Code
} from "lucide-react";
import { text2sqlApi, type SQLGenerationResponse, type SQLExecutionResponse } from "~/core/api/text2sql";

interface TestResult {
  question: string;
  generated_sql: string;
  explanation?: string;
  confidence_score: number;
  execution_result?: SQLExecutionResponse;
  generated_at: string;
  generation_time_ms: number;
}

interface ModelTestComponentProps {
  datasourceId: number;
}

export function ModelTestComponent({ datasourceId }: ModelTestComponentProps) {
  const [isTesting, setIsTesting] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [testQuestion, setTestQuestion] = useState('');
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [testMode, setTestMode] = useState<'generate' | 'execute'>('generate');
  const [includeExplanation, setIncludeExplanation] = useState(true);

  const loadSampleQuestions = () => {
    return [
      '今天有多少订单？',
      '销售额最高的前10个产品',
      '本月新注册用户数量',
      '查询所有活跃用户',
      '最近7天的订单趋势',
      '用户的平均订单金额'
    ];
  };

  const handleTest = async () => {
    if (!testQuestion.trim()) return;

    try {
      setIsTesting(true);
      
      const response = await text2sqlApi.generateSQL({
        datasource_id: datasourceId,
        question: testQuestion.trim(),
        include_explanation: includeExplanation
      });

      const result: TestResult = {
        question: testQuestion,
        generated_sql: response.generated_sql,
        explanation: response.explanation,
        confidence_score: response.confidence_score,
        generated_at: new Date().toISOString(),
        generation_time_ms: response.generation_time_ms || 0
      };

      // If test mode is execute, also run the SQL
      if (testMode === 'execute') {
        try {
          setIsExecuting(true);
          const executionResult = await text2sqlApi.executeSQL({
            query_id: response.query_id,
            limit: 100
          });
          result.execution_result = executionResult;
        } catch (execError) {
          console.error('SQL execution failed:', execError);
        } finally {
          setIsExecuting(false);
        }
      }

      setTestResults([result, ...testResults.slice(0, 9)]); // Keep last 10 results
      setTestQuestion(''); // Clear input after successful test
    } catch (error: any) {
      console.error('Model test failed:', error);
    } finally {
      setIsTesting(false);
    }
  };

  const handleExecuteSQL = async (result: TestResult, index: number) => {
    try {
      setIsExecuting(true);
      
      // First generate SQL to get query_id
      const response = await text2sqlApi.generateSQL({
        datasource_id: datasourceId,
        question: result.question,
        include_explanation: false
      });

      const executionResult = await text2sqlApi.executeSQL({
        query_id: response.query_id,
        limit: 100
      });

      // Update the result with execution data
      const updatedResults = [...testResults];
      updatedResults[index] = { ...result, execution_result: executionResult };
      setTestResults(updatedResults);
    } catch (error: any) {
      console.error('SQL execution failed:', error);
    } finally {
      setIsExecuting(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const exportResults = () => {
    const exportData = {
      datasource_id: datasourceId,
      test_results: testResults,
      exported_at: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `text2sql_test_results_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.8) return '高';
    if (score >= 0.6) return '中';
    return '低';
  };

  return (
    <div className="w-full space-y-6">
      {/* 标题卡片 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TestTube className="h-5 w-5" />
            模型测试
          </CardTitle>
          <CardDescription>
            测试训练后的模型效果，输入自然语言问题查看生成的SQL查询
          </CardDescription>
        </CardHeader>
      </Card>

      {/* 测试配置 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">测试配置</CardTitle>
          <CardDescription>
            配置测试参数和选项
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label className="text-sm font-medium">嵌入模型配置</Label>
              <div className="space-y-2 mt-2">
                <div className="flex items-center gap-2">
                  <Badge variant="outline">BAAI/bge-m3</Badge>
                  <span className="text-sm text-muted-foreground">嵌入模型</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline">BAAI/bge-reranker-v2-m3</Badge>
                  <span className="text-sm text-muted-foreground">重排序模型</span>
                </div>
              </div>
            </div>

            <div>
              <Label htmlFor="test-mode">测试模式</Label>
              <Select
                value={testMode}
                onValueChange={(value: any) => setTestMode(value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="generate">仅生成SQL</SelectItem>
                  <SelectItem value="execute">生成并执行SQL</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="include-explanation"
              checked={includeExplanation}
              onChange={(e) => setIncludeExplanation(e.target.checked)}
              className="rounded"
            />
            <Label htmlFor="include-explanation">包含解释说明</Label>
          </div>
        </CardContent>
      </Card>

      {/* 测试界面 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">测试问题</CardTitle>
          <CardDescription>
            输入自然语言问题，测试模型的SQL生成能力
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Input
              placeholder="例如：今天有多少订单？"
              value={testQuestion}
              onChange={(e) => setTestQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleTest();
                }
              }}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex flex-wrap gap-2">
              <span className="text-sm text-muted-foreground">快速测试：</span>
              {loadSampleQuestions().slice(0, 3).map((question, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => setTestQuestion(question)}
                  className="text-xs"
                >
                  {question}
                </Button>
              ))}
            </div>
            
            <Button 
              onClick={handleTest} 
              disabled={isTesting || !testQuestion.trim()}
              className="bg-orange-600 hover:bg-orange-700"
            >
              {isTesting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  测试中...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  开始测试
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 测试结果 */}
      {testResults.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg">测试结果</CardTitle>
                <CardDescription>
                  最近的测试结果和SQL生成效果
                </CardDescription>
              </div>
              <Button variant="outline" size="sm" onClick={exportResults}>
                <Download className="h-4 w-4 mr-2" />
                导出结果
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[600px]">
              <div className="space-y-4">
                {testResults.map((result, index) => (
                  <div key={index} className="border rounded-lg p-4 space-y-3">
                    {/* 问题和基本信息 */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">问题 {index + 1}</Badge>
                        <span className={`text-sm font-medium ${getConfidenceColor(result.confidence_score)}`}>
                          置信度: {getConfidenceLabel(result.confidence_score)} ({Math.round(result.confidence_score * 100)}%)
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        <span>{result.generation_time_ms}ms</span>
                        <span>{new Date(result.generated_at).toLocaleTimeString()}</span>
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-sm font-medium mb-1">问题:</div>
                      <div className="text-sm bg-muted p-2 rounded">{result.question}</div>
                    </div>
                    
                    {/* 生成的SQL */}
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <div className="text-sm font-medium">生成的SQL:</div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => copyToClipboard(result.generated_sql)}
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                      <div className="text-sm bg-muted p-2 rounded font-mono">
                        {result.generated_sql}
                      </div>
                    </div>
                    
                    {/* 解释说明 */}
                    {result.explanation && (
                      <div>
                        <div className="text-sm font-medium mb-1 flex items-center gap-1">
                          <Lightbulb className="h-3 w-3" />
                          解释说明:
                        </div>
                        <div className="text-sm text-muted-foreground bg-muted p-2 rounded">
                          {result.explanation}
                        </div>
                      </div>
                    )}
                    
                    {/* 执行结果 */}
                    {result.execution_result ? (
                      <div>
                        <div className="text-sm font-medium mb-1 flex items-center gap-1">
                          <Database className="h-3 w-3" />
                          执行结果:
                        </div>
                        {result.execution_result.status === 'SUCCESS' ? (
                          <div className="space-y-2">
                            <div className="flex items-center gap-2 text-sm">
                              <CheckCircle className="h-4 w-4 text-green-500" />
                              <span>执行成功，返回 {result.execution_result.result_data?.length || 0} 行数据</span>
                              <span className="text-muted-foreground">
                                ({result.execution_result.execution_time_ms}ms)
                              </span>
                            </div>
                            {result.execution_result.result_data && result.execution_result.result_data.length > 0 && (
                              <div className="text-xs bg-muted p-2 rounded max-h-32 overflow-auto">
                                <pre>{JSON.stringify(result.execution_result.result_data.slice(0, 3), null, 2)}</pre>
                                {result.execution_result.result_data.length > 3 && (
                                  <div className="text-muted-foreground mt-1">
                                    ... 还有 {result.execution_result.result_data.length - 3} 行数据
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="flex items-center gap-2 text-sm">
                            <XCircle className="h-4 w-4 text-red-500" />
                            <span>执行失败: {result.execution_result.error_message}</span>
                          </div>
                        )}
                      </div>
                    ) : (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleExecuteSQL(result, index)}
                        disabled={isExecuting}
                      >
                        {isExecuting ? (
                          <>
                            <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                            执行中...
                          </>
                        ) : (
                          <>
                            <Play className="h-3 w-3 mr-1" />
                            执行SQL
                          </>
                        )}
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}

      {/* 空状态 */}
      {testResults.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <TestTube className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-medium mb-2">开始测试模型</h3>
            <p className="text-muted-foreground mb-4">
              输入自然语言问题，测试训练后的模型效果
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {loadSampleQuestions().map((question, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => setTestQuestion(question)}
                >
                  {question}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
