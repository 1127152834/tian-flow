"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select";
import { Badge } from "~/components/ui/badge";
import { Alert, AlertDescription } from "~/components/ui/alert";
import {
  BookOpen,
  Trash2,
  Search,
  Filter,
  Loader2,
  CheckCircle,
  XCircle,
  Database,
  FileText,
  Code,
  Book,
  Edit,
  RefreshCw
} from "lucide-react";
import { text2sqlApi, type TrainingDataRequest, type TrainingDataResponse } from "~/core/api/text2sql";
import { EditTrainingDataDialog } from "./EditTrainingDataDialog";
import { useConfirmDialog } from "~/components/ui/confirm-dialog";
import { useSuccessDialog } from "~/components/ui/success-dialog";

interface TrainingDataManagerProps {
  datasourceId: number;
  datasourceName: string;
}

const CONTENT_TYPES = [
  { value: 'SQL', label: 'SQL Query', icon: Code },
  { value: 'SCHEMA', label: 'Database Schema', icon: Database },
  { value: 'DOCUMENTATION', label: 'Documentation', icon: FileText },
  { value: 'DDL', label: 'DDL Statement', icon: Book },
];

export function TrainingDataManager({ datasourceId, datasourceName }: TrainingDataManagerProps) {
  const [trainingData, setTrainingData] = useState<TrainingDataResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState<string>("all");
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<TrainingDataResponse | null>(null);
  const [isRetraining, setIsRetraining] = useState(false);

  // Confirm dialog hook
  const { showConfirm, ConfirmDialog } = useConfirmDialog();

  // Success dialog hook
  const { showSuccess, NotificationDialog: SuccessDialog } = useSuccessDialog();

  useEffect(() => {
    loadTrainingData();
  }, [datasourceId]);

  const loadTrainingData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await text2sqlApi.getTrainingData({
        datasource_id: datasourceId,
        limit: 100,
        offset: 0,
      });
      
      setTrainingData(response.training_data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load training data');
    } finally {
      setLoading(false);
    }
  };



  const handleDeleteTrainingData = async (id: number) => {
    showConfirm({
      title: "删除训练数据",
      description: "确定要删除这条训练数据吗？此操作不可撤销。",
      confirmText: "删除",
      cancelText: "取消",
      type: "danger",
      destructive: true,
      onConfirm: async () => {
        try {
          setLoading(true);
          await text2sqlApi.deleteTrainingData(id, true);
          await loadTrainingData();
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Failed to delete training data');
        } finally {
          setLoading(false);
        }
      }
    });
  };



  const handleEditItem = (item: TrainingDataResponse) => {
    setEditingItem(item);
    setIsEditDialogOpen(true);
  };

  const handleUpdateTrainingData = async (updatedData: TrainingDataRequest) => {
    if (!editingItem) return;

    try {
      setLoading(true);
      setError(null);

      // Update training data
      await text2sqlApi.updateTrainingData(editingItem.id, updatedData);

      // Show success message with auto-retraining info
      showSuccess(
        "训练数据已更新",
        "系统正在后台重新生成向量嵌入，这可能需要几分钟时间。",
        { autoClose: true, autoCloseDelay: 4000 }
      );

      setIsEditDialogOpen(false);
      setEditingItem(null);

      // Reload data to show updated content
      await loadTrainingData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update training data');
    } finally {
      setLoading(false);
    }
  };

  const handleRetrain = async () => {
    showConfirm({
      title: "重新训练模型",
      description: "确定要重新训练模型吗？这将重新生成所有训练数据的向量嵌入，可能需要几分钟时间。",
      confirmText: "开始训练",
      cancelText: "取消",
      type: "warning",
      onConfirm: async () => {
        try {
          setIsRetraining(true);
          setError(null);

          const result = await text2sqlApi.retrainModel({
            datasource_id: datasourceId,
            force_rebuild: true
          });

          // Show success message
          showSuccess(
            "重新训练已开始",
            `任务ID: ${result.task_id}。系统正在后台重新生成向量嵌入，请稍候。`,
            { autoClose: true, autoCloseDelay: 5000 }
          );

        } catch (err) {
          setError(err instanceof Error ? err.message : 'Failed to start retraining');
        } finally {
          setIsRetraining(false);
        }
      }
    });
  };

  const getContentTypeIcon = (type: string) => {
    const contentType = CONTENT_TYPES.find(ct => ct.value === type);
    const Icon = contentType?.icon || FileText;
    return <Icon className="h-4 w-4" />;
  };

  const getContentTypeColor = (type: string) => {
    switch (type) {
      case 'SQL':
        return 'bg-blue-100 text-blue-800';
      case 'SCHEMA':
        return 'bg-green-100 text-green-800';
      case 'DOCUMENTATION':
        return 'bg-purple-100 text-purple-800';
      case 'DDL':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredData = trainingData.filter(item => {
    const matchesSearch = !searchTerm || 
      item.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.question?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.sql_query?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterType === 'all' || item.content_type === filterType;
    
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            数据管理
          </CardTitle>
          <CardDescription>
            管理训练数据，查看和编辑已有的训练示例。数据源: <Badge variant="outline">{datasourceName}</Badge>
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Main Content Layout - 按照 ti-flow 设计 */}
      <div className="grid grid-cols-12 gap-6">
        {/* Left Sidebar - Statistics */}
        <div className="col-span-3 space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">共 {filteredData.length} 条</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button
                variant="outline"
                size="sm"
                className="w-full justify-start"
                onClick={handleRetrain}
                disabled={isRetraining || loading}
              >
                {isRetraining ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4 mr-2" />
                )}
                {isRetraining ? '重新训练中...' : '重新训练模型'}
              </Button>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Filter className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">All Types</span>
                </div>
                
                {CONTENT_TYPES.map(type => {
                  const count = trainingData.filter(item => item.content_type === type.value).length;
                  return (
                    <div key={type.value} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <type.icon className="h-3 w-3" />
                        <span>{type.label}</span>
                      </div>
                      <span className="text-muted-foreground">{count}</span>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Content - Training Data List */}
        <div className="col-span-9">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Training Data ({filteredData.length})</CardTitle>
                <div className="flex items-center gap-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="搜索训练数据..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 w-64"
                    />
                  </div>
                  <Select value={filterType} onValueChange={setFilterType}>
                    <SelectTrigger className="w-[120px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      {CONTENT_TYPES.map(type => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin" />
                </div>
              ) : filteredData.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <BookOpen className="h-8 w-8 mx-auto mb-2" />
                  <p>暂无训练数据</p>
                  <p className="text-sm">添加一些训练示例开始使用</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredData.map((item) => (
                    <div key={item.id} className="border rounded-lg p-4 hover:bg-muted/50 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 space-y-2">
                          <div className="flex items-center gap-2">
                            <Badge className={getContentTypeColor(item.content_type)}>
                              {getContentTypeIcon(item.content_type)}
                              {item.content_type}
                            </Badge>
                            {item.is_validated && (
                              <Badge variant="outline" className="text-green-600">
                                <CheckCircle className="h-3 w-3 mr-1" />
                                已验证
                              </Badge>
                            )}
                            <span className="text-xs text-muted-foreground">
                              {new Date(item.created_at).toLocaleDateString('zh-CN')}
                            </span>
                          </div>
                          
                          {item.question && (
                            <div className="text-sm">
                              <span className="font-medium">问题: </span>
                              <span className="text-muted-foreground">{item.question}</span>
                            </div>
                          )}
                          
                          <div className="text-xs font-mono bg-muted p-2 rounded">
                            {item.content.length > 200 
                              ? `${item.content.substring(0, 200)}...` 
                              : item.content
                            }
                          </div>
                          
                          {item.table_names && item.table_names.length > 0 && (
                            <div className="flex items-center gap-1 flex-wrap">
                              <span className="text-xs text-muted-foreground">表:</span>
                              {item.table_names.map((table, index) => (
                                <Badge key={index} variant="outline" className="text-xs">
                                  {table}
                                </Badge>
                              ))}
                            </div>
                          )}
                        </div>
                        
                        <div className="flex items-center gap-1 ml-4">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEditItem(item)}
                            title="编辑训练数据"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteTrainingData(item.id)}
                            className="text-red-600 hover:text-red-700"
                            title="删除训练数据"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Edit Training Data Dialog */}
      <EditTrainingDataDialog
        open={isEditDialogOpen}
        onOpenChange={setIsEditDialogOpen}
        item={editingItem}
        onSave={handleUpdateTrainingData}
        loading={loading}
      />

      {/* Confirm Dialog */}
      <ConfirmDialog />

      {/* Success Dialog */}
      <SuccessDialog />
    </div>
  );
}
