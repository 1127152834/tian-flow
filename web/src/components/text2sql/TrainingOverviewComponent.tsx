"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { Badge } from "~/components/ui/badge";
import { Progress } from "~/components/ui/progress";
import { useToast } from "~/hooks/use-toast";
import {
  Brain,
  Database,
  FileText,
  BarChart3,
  BookOpen,
  TestTube,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Zap,
  RefreshCw
} from "lucide-react";
import { useState } from "react";
import type { Text2SQLStatistics } from "~/core/api/text2sql";
import { text2sqlApi } from "~/core/api/text2sql";

interface TrainingOverviewComponentProps {
  datasourceId: number;
  statistics: Text2SQLStatistics | null;
  onTabChange: (tab: string) => void;
}

export function TrainingOverviewComponent({
  datasourceId,
  statistics,
  onTabChange
}: TrainingOverviewComponentProps) {
  const { toast } = useToast();
  const [isGeneratingEmbeddings, setIsGeneratingEmbeddings] = useState(false);
  const [isRetrainingModel, setIsRetrainingModel] = useState(false);
  
  const getTrainingProgress = () => {
    if (!statistics) return 0;
    const totalPossibleData = 100; // Assume 100 is a good baseline
    return Math.min((statistics.total_training_data / totalPossibleData) * 100, 100);
  };

  const getModelQuality = () => {
    if (!statistics || statistics.total_queries === 0) return 0;
    return Math.round((statistics.successful_queries / statistics.total_queries) * 100);
  };

  const getTrainingRecommendations = () => {
    const recommendations: Array<{
      type: 'warning' | 'info';
      title: string;
      description: string;
      action: () => void;
      actionText: string;
    }> = [];

    if (!statistics) return recommendations;
    
    if (statistics.total_training_data < 10) {
      recommendations.push({
        type: 'warning',
        title: '训练数据不足',
        description: '建议添加更多训练数据以提高模型性能',
        action: () => onTabChange('sql'),
        actionText: '添加SQL训练数据'
      });
    }
    
    if (statistics.training_data_by_type.DDL === 0) {
      recommendations.push({
        type: 'info',
        title: '缺少DDL数据',
        description: '导入数据库结构可以帮助模型理解表关系',
        action: () => onTabChange('ddl'),
        actionText: '导入DDL'
      });
    }
    
    if (statistics.training_data_by_type.DOCUMENTATION === 0) {
      recommendations.push({
        type: 'info',
        title: '缺少文档数据',
        description: '添加业务文档可以提高查询理解能力',
        action: () => onTabChange('documentation'),
        actionText: '添加文档'
      });
    }
    
    return recommendations;
  };

  const handleGenerateEmbeddings = async () => {
    setIsGeneratingEmbeddings(true);
    try {
      const result = await text2sqlApi.generateEmbeddings({
        datasource_id: datasourceId
      });

      toast({
        title: "向量嵌入生成已启动",
        description: `任务ID: ${result.task_id}。向量嵌入将在后台生成，请稍后查看结果。`,
      });
    } catch (error) {
      toast({
        title: "生成向量嵌入失败",
        description: error instanceof Error ? error.message : "未知错误",
        variant: "destructive",
      });
    } finally {
      setIsGeneratingEmbeddings(false);
    }
  };

  const handleRetrainModel = async () => {
    setIsRetrainingModel(true);
    try {
      const result = await text2sqlApi.retrainModel(datasourceId, true);

      toast({
        title: "模型重训练已启动",
        description: `任务ID: ${result.task_id}。模型将在后台重新训练，请稍后查看结果。`,
      });
    } catch (error) {
      toast({
        title: "重训练模型失败",
        description: error instanceof Error ? error.message : "未知错误",
        variant: "destructive",
      });
    } finally {
      setIsRetrainingModel(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 训练进度概览 */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">训练数据总量</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistics?.total_training_data || 0}</div>
            <p className="text-xs text-muted-foreground">
              训练样本数量
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">模型质量</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{getModelQuality()}%</div>
            <p className="text-xs text-muted-foreground">
              查询成功率
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">总查询数</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistics?.total_queries || 0}</div>
            <p className="text-xs text-muted-foreground">
              {statistics?.successful_queries || 0} 成功, {statistics?.failed_queries || 0} 失败
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">平均置信度</CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {statistics?.average_confidence 
                ? Math.round(statistics.average_confidence * 100)
                : 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              模型置信度
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 训练进度 */}
      <Card>
        <CardHeader>
          <CardTitle>训练进度</CardTitle>
          <CardDescription>
            当前模型训练状态和数据完整性
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">数据完整性</span>
              <span className="text-sm text-muted-foreground">{getTrainingProgress().toFixed(0)}%</span>
            </div>
            <Progress value={getTrainingProgress()} className="h-2" />
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4">
            {Object.entries(statistics?.training_data_by_type || {}).map(([type, count]) => (
              <div key={type} className="text-center">
                <div className="text-2xl font-bold">{count}</div>
                <div className="text-xs text-muted-foreground">{type}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 快速操作 */}
      <Card>
        <CardHeader>
          <CardTitle>快速操作</CardTitle>
          <CardDescription>
            选择合适的训练方式继续优化模型
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Button 
            className="w-full justify-start"
            variant="outline"
            onClick={() => onTabChange('ddl')}
          >
            <Database className="h-4 w-4 mr-2" />
            DDL训练 - 导入数据库表结构
          </Button>
          
          <Button 
            className="w-full justify-start"
            variant="outline"
            onClick={() => onTabChange('sql')}
          >
            <Brain className="h-4 w-4 mr-2" />
            SQL训练 - 添加问答示例
          </Button>
          
          <Button 
            className="w-full justify-start"
            variant="outline"
            onClick={() => onTabChange('documentation')}
          >
            <FileText className="h-4 w-4 mr-2" />
            文档训练 - 添加业务文档
          </Button>
          
          <Button
            className="w-full justify-start"
            variant="outline"
            onClick={() => onTabChange('test')}
          >
            <TestTube className="h-4 w-4 mr-2" />
            模型测试 - 测试生成效果
          </Button>

          <div className="border-t pt-3 mt-3">
            <p className="text-sm text-muted-foreground mb-3">模型优化操作</p>

            <Button
              className="w-full justify-start mb-2"
              variant="outline"
              onClick={handleGenerateEmbeddings}
              disabled={isGeneratingEmbeddings}
            >
              <Zap className="h-4 w-4 mr-2" />
              {isGeneratingEmbeddings ? "生成中..." : "生成向量嵌入"}
            </Button>

            <Button
              className="w-full justify-start"
              variant="outline"
              onClick={handleRetrainModel}
              disabled={isRetrainingModel}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              {isRetrainingModel ? "重训练中..." : "重新训练模型"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 训练建议 */}
      {getTrainingRecommendations().length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5" />
              训练建议
            </CardTitle>
            <CardDescription>
              基于当前数据状态的优化建议
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {getTrainingRecommendations().map((rec, index) => (
              <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant={rec.type === 'warning' ? 'destructive' : 'secondary'}>
                      {rec.type === 'warning' ? '警告' : '建议'}
                    </Badge>
                    <span className="font-medium">{rec.title}</span>
                  </div>
                  <p className="text-sm text-muted-foreground">{rec.description}</p>
                </div>
                <Button size="sm" onClick={rec.action}>
                  {rec.actionText}
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* 最近活动 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            最近活动
          </CardTitle>
          <CardDescription>
            最近的训练和查询活动
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {statistics?.last_training_time && (
              <div className="flex items-center gap-3">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <div className="flex-1">
                  <p className="text-sm font-medium">最后训练时间</p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(statistics.last_training_time).toLocaleString('zh-CN')}
                  </p>
                </div>
              </div>
            )}
            
            {statistics?.last_query_time && (
              <div className="flex items-center gap-3">
                <CheckCircle className="h-4 w-4 text-blue-500" />
                <div className="flex-1">
                  <p className="text-sm font-medium">最后查询时间</p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(statistics.last_query_time).toLocaleString('zh-CN')}
                  </p>
                </div>
              </div>
            )}
            
            {!statistics?.last_training_time && !statistics?.last_query_time && (
              <div className="text-center py-8 text-muted-foreground">
                <Clock className="h-8 w-8 mx-auto mb-2" />
                <p>暂无活动记录</p>
                <p className="text-sm">开始训练后这里会显示活动历史</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
