"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Label } from "~/components/ui/label";
import { Textarea } from "~/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select";
import { Alert, AlertDescription } from "~/components/ui/alert";
import { Badge } from "~/components/ui/badge";
import { 
  Brain, 
  Plus, 
  Trash2, 
  Save, 
  Loader2, 
  CheckCircle, 
  XCircle,
  AlertCircle,
  Download,
  Upload
} from "lucide-react";
import { text2sqlApi } from "~/core/api/text2sql";

interface SQLPair {
  question: string;
  sql: string;
}

interface TrainingResult {
  success: boolean;
  message?: string;
  error?: string;
  total?: number;
  successful?: number;
  failed?: number;
}

interface SQLTrainingComponentProps {
  datasourceId: number;
}

export function SQLTrainingComponent({ datasourceId }: SQLTrainingComponentProps) {
  const [isTraining, setIsTraining] = useState(false);
  const [trainingResult, setTrainingResult] = useState<TrainingResult | null>(null);
  const [trainingTaskId, setTrainingTaskId] = useState<string | null>(null);
  const [trainingProgress, setTrainingProgress] = useState(0);
  const [trainingMessage, setTrainingMessage] = useState('');
  const [trainingStep, setTrainingStep] = useState('');
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const [sqlPairs, setSqlPairs] = useState<SQLPair[]>([
    { question: '', sql: '' }
  ]);

  const addSqlPair = () => {
    setSqlPairs([...sqlPairs, { question: '', sql: '' }]);
  };

  const removeSqlPair = (index: number) => {
    if (sqlPairs.length > 1) {
      setSqlPairs(sqlPairs.filter((_, i) => i !== index));
    }
  };

  const updateSqlPair = (index: number, field: 'question' | 'sql', value: string) => {
    const updated = [...sqlPairs];
    updated[index][field] = value;
    setSqlPairs(updated);
  };

  const validateSqlPairs = () => {
    return sqlPairs.filter(pair => 
      pair.question.trim() !== '' && pair.sql.trim() !== ''
    );
  };

  // WebSocket连接管理
  const connectWebSocket = (taskId: string) => {
    if (websocket) {
      websocket.close();
    }

    const wsUrl = `ws://localhost:8000/api/ws/progress/${taskId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('SQL训练 WebSocket连接已建立:', taskId);
      setWebsocket(ws);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('收到SQL训练 WebSocket消息:', data);

        setTrainingProgress(data.progress || 0);
        setTrainingMessage(data.message || '');
        setTrainingStep(data.current_step || '');

        if (data.status === 'completed') {
          setIsTraining(false);
          setTrainingTaskId(null);
          setTrainingProgress(100);
          setTrainingMessage('训练完成');
          setTrainingResult({
            success: true,
            total: data.result?.total || 0,
            successful: data.result?.successful || 0,
            failed: data.result?.failed || 0,
            message: '训练完成'
          });
          ws.close();
        } else if (data.status === 'failed') {
          setIsTraining(false);
          setTrainingTaskId(null);
          setTrainingProgress(0);
          setTrainingMessage('训练失败');
          setTrainingResult({
            success: false,
            total: 0,
            successful: 0,
            failed: 0,
            error: data.error || '训练过程中发生错误'
          });
          ws.close();
        }
      } catch (error) {
        console.error('解析SQL训练 WebSocket消息失败:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('SQL训练 WebSocket错误:', error);
    };

    ws.onclose = () => {
      console.log('SQL训练 WebSocket连接已关闭');
      setWebsocket(null);
    };
  };

  // 监控训练任务进度
  useEffect(() => {
    if (trainingTaskId && isTraining) {
      connectWebSocket(trainingTaskId);
    }

    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [trainingTaskId, isTraining]);

  const handleTraining = async () => {
    const validPairs = validateSqlPairs();
    if (validPairs.length === 0 || isTraining) return;

    try {
      setIsTraining(true);
      setTrainingResult(null);
      setTrainingProgress(0);
      setTrainingMessage('启动训练任务...');
      setTrainingStep('');

      const result = await text2sqlApi.trainSQL(datasourceId, {
        sql_pairs: validPairs
      });

      // 如果返回了task_id，使用WebSocket监控
      if (result.task_id) {
        setTrainingTaskId(result.task_id);
      } else {
        // 如果没有task_id，直接显示结果
        setTrainingResult(result);
        setIsTraining(false);
      }
    } catch (error: any) {
      console.error('SQL训练失败:', error);
      setTrainingResult({
        success: false,
        total: 0,
        successful: 0,
        failed: 0,
        error: error.message || '网络错误'
      });
      setIsTraining(false);
      setTrainingProgress(0);
      setTrainingMessage('');
      setTrainingStep('');
    }
  };

  const clearResults = () => {
    setTrainingResult(null);
  };

  const loadSampleData = () => {
    setSqlPairs([
      {
        question: '今天有多少订单？',
        sql: 'SELECT COUNT(*) FROM orders WHERE DATE(created_at) = CURDATE();'
      },
      {
        question: '销售额最高的前10个产品',
        sql: 'SELECT product_name, SUM(amount) as total_sales FROM order_items GROUP BY product_name ORDER BY total_sales DESC LIMIT 10;'
      },
      {
        question: '本月新注册用户数量',
        sql: 'SELECT COUNT(*) FROM users WHERE DATE(created_at) >= DATE_FORMAT(NOW(), "%Y-%m-01");'
      }
    ]);
  };

  const exportTrainingData = () => {
    const validPairs = validateSqlPairs();
    const exportData = {
      datasource_id: datasourceId,
      sql_pairs: validPairs,
      exported_at: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sql_training_data_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="w-full space-y-6">
      {/* 标题卡片 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            SQL训练
          </CardTitle>
          <CardDescription>
            通过添加问答示例来训练模型，教会它如何将自然语言准确转换为SQL查询语句。
          </CardDescription>
        </CardHeader>
      </Card>

      {/* 嵌入模型配置 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">嵌入模型配置</CardTitle>
          <CardDescription>
            当前系统配置的向量化模型
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div>
              <Label className="text-sm font-medium">嵌入模型</Label>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="outline">BAAI/bge-m3</Badge>
                <span className="text-sm text-muted-foreground">默认</span>
              </div>
            </div>
            <div>
              <Label className="text-sm font-medium">重排序模型</Label>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="outline">BAAI/bge-reranker-v2-m3</Badge>
                <span className="text-sm text-muted-foreground">用于结果重排序</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* SQL问答示例 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">问答示例</CardTitle>
              <CardDescription>
                添加自然语言问题和对应的SQL查询，帮助模型学习转换规则
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={loadSampleData}>
                <Save className="h-4 w-4 mr-2" />
                加载示例
              </Button>
              <Button variant="outline" size="sm" onClick={exportTrainingData}>
                <Download className="h-4 w-4 mr-2" />
                导出数据
              </Button>
              <Button variant="outline" size="sm" onClick={addSqlPair}>
                <Plus className="h-4 w-4 mr-2" />
                添加示例
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {sqlPairs.map((pair, index) => (
            <div key={index} className="p-4 border rounded-lg space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-medium">示例 {index + 1}</h4>
                {sqlPairs.length > 1 && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => removeSqlPair(index)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
              
              <div className="space-y-3">
                <div>
                  <Label htmlFor={`question-${index}`}>自然语言问题</Label>
                  <Input
                    id={`question-${index}`}
                    placeholder="例如：今天有多少订单？"
                    value={pair.question}
                    onChange={(e) => updateSqlPair(index, 'question', e.target.value)}
                  />
                </div>
                
                <div>
                  <Label htmlFor={`sql-${index}`}>对应的SQL查询</Label>
                  <Textarea
                    id={`sql-${index}`}
                    placeholder="例如：SELECT COUNT(*) FROM orders WHERE DATE(created_at) = CURDATE();"
                    value={pair.sql}
                    onChange={(e) => updateSqlPair(index, 'sql', e.target.value)}
                    rows={3}
                    className="font-mono text-sm"
                  />
                </div>
              </div>
              
              {pair.question.trim() && pair.sql.trim() && (
                <div className="flex items-center gap-2 text-sm text-green-600">
                  <CheckCircle className="h-4 w-4" />
                  <span>示例有效</span>
                </div>
              )}
            </div>
          ))}

          <div className="pt-4 border-t">
            <div className="flex items-center justify-between mb-4">
              <div className="text-sm text-muted-foreground">
                有效示例：{validateSqlPairs().length} / {sqlPairs.length}
              </div>
              <Button
                onClick={handleTraining}
                disabled={isTraining || validateSqlPairs().length === 0}
                className="bg-purple-600 hover:bg-purple-700"
              >
                {isTraining ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    正在训练...
                  </>
                ) : (
                  <>
                    <Brain className="h-4 w-4 mr-2" />
                    开始SQL训练
                  </>
                )}
              </Button>
            </div>

            {/* 训练进度显示 */}
            {isTraining && (
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-4">
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
                    <span className="text-sm text-purple-800 font-medium">
                      SQL训练进行中...
                    </span>
                  </div>

                  {/* 进度条 */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs text-purple-700">
                      <span>{trainingStep || '准备中...'}</span>
                      <span>{trainingProgress}%</span>
                    </div>
                    <div className="w-full bg-purple-200 rounded-full h-2">
                      <div
                        className="bg-purple-600 h-2 rounded-full transition-all duration-300 ease-out"
                        style={{ width: `${trainingProgress}%` }}
                      ></div>
                    </div>
                    {trainingMessage && (
                      <p className="text-xs text-purple-600 mt-1">{trainingMessage}</p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {validateSqlPairs().length === 0 && sqlPairs.length > 0 && (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  请确保每个示例都包含问题和SQL查询两部分内容
                </AlertDescription>
              </Alert>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 训练结果 */}
      {trainingResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {trainingResult.success ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <XCircle className="h-5 w-5 text-red-500" />
              )}
              训练结果
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {trainingResult.success ? (
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  SQL训练成功完成！处理了 {trainingResult.successful || 0} 个示例
                </AlertDescription>
              </Alert>
            ) : (
              <Alert variant="destructive">
                <XCircle className="h-4 w-4" />
                <AlertDescription>
                  SQL训练失败: {trainingResult.error || trainingResult.message || '未知错误'}
                </AlertDescription>
              </Alert>
            )}
            
            {trainingResult.total !== undefined && (
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold">{trainingResult.total}</div>
                  <div className="text-sm text-muted-foreground">总计</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-green-600">{trainingResult.successful || 0}</div>
                  <div className="text-sm text-muted-foreground">成功</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-red-600">{trainingResult.failed || 0}</div>
                  <div className="text-sm text-muted-foreground">失败</div>
                </div>
              </div>
            )}
            
            <div className="flex gap-2">
              <Button variant="outline" onClick={clearResults}>
                清除结果
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
