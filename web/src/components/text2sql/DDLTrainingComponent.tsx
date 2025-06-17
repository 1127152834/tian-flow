"use client";

import { useState, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Label } from "~/components/ui/label";
import { Textarea } from "~/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select";
import { Alert, AlertDescription } from "~/components/ui/alert";
import { Badge } from "~/components/ui/badge";
import { Checkbox } from "~/components/ui/checkbox";
import { 
  Database, 
  Upload, 
  FileText, 
  Loader2, 
  CheckCircle, 
  XCircle,
  AlertCircle,
  Download,
  Zap
} from "lucide-react";
import { text2sqlApi } from "~/core/api/text2sql";

interface TrainingResult {
  success: boolean;
  message?: string;
  error?: string;
  total_items?: number;
  successful_items?: number;
  failed_items?: number;
  training_time?: number;
  details?: any[];
}

interface DDLTrainingComponentProps {
  datasourceId: number;
}

export function DDLTrainingComponent({ datasourceId }: DDLTrainingComponentProps) {
  const [isTraining, setIsTraining] = useState(false);
  const [trainingResult, setTrainingResult] = useState<TrainingResult | null>(null);
  const [databaseName, setDatabaseName] = useState('');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [trainingMode, setTrainingMode] = useState<'auto' | 'file'>('auto');
  const [ddlContent, setDdlContent] = useState('');
  const [autoExtract, setAutoExtract] = useState(true); // 默认选中
  const [skipExisting, setSkipExisting] = useState(true); // 默认选中
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleAutoExtraction = async () => {
    if (isTraining) return;

    try {
      setIsTraining(true);
      setTrainingResult(null);
      
      // Call DDL training API with auto extraction
      const result = await text2sqlApi.trainDDL(datasourceId, {
        auto_extract: autoExtract,
        database_name: databaseName.trim() || undefined,
        skip_existing: skipExisting
      });

      setTrainingResult(result);
    } catch (error: any) {
      console.error('DDL训练失败:', error);
      setTrainingResult({
        success: false,
        total_items: 0,
        successful_items: 0,
        failed_items: 0,
        error: error.message || '网络错误'
      });
    } finally {
      setIsTraining(false);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      
      // Read file content
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setDdlContent(content);
      };
      reader.readAsText(file);
    }
  };

  const handleFileTraining = async () => {
    if (!ddlContent.trim() || isTraining) return;

    try {
      setIsTraining(true);
      setTrainingResult(null);
      
      // Call DDL training API with file content
      const result = await text2sqlApi.trainDDL(datasourceId, {
        auto_extract: false,
        ddl_content: ddlContent,
        skip_existing: skipExisting
      });

      setTrainingResult(result);
    } catch (error: any) {
      console.error('DDL训练失败:', error);
      setTrainingResult({
        success: false,
        total_items: 0,
        successful_items: 0,
        failed_items: 0,
        error: error.message || '网络错误'
      });
    } finally {
      setIsTraining(false);
    }
  };

  const clearResults = () => {
    setTrainingResult(null);
    setUploadedFile(null);
    setDdlContent('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const downloadSampleDDL = () => {
    const sampleDDL = `-- 示例DDL文件
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 订单表
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 订单项表
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_name VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL
);

-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);`;

    const blob = new Blob([sampleDDL], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_ddl.sql';
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
            <Database className="h-5 w-5" />
            DDL训练
          </CardTitle>
          <CardDescription>
            导入数据库表结构，让模型理解数据库架构。支持自动提取或上传SQL文件两种方式。
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

      {/* 训练方式选择 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">训练方式</CardTitle>
          <CardDescription>
            选择DDL数据的导入方式
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Button
              variant={trainingMode === 'auto' ? 'default' : 'outline'}
              className="h-auto p-4 flex flex-col items-start gap-2"
              onClick={() => setTrainingMode('auto')}
            >
              <div className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                <span className="font-medium">自动提取</span>
              </div>
              <p className="text-sm text-left opacity-75">
                自动从数据库连接中提取表结构信息
              </p>
            </Button>
            
            <Button
              variant={trainingMode === 'file' ? 'default' : 'outline'}
              className="h-auto p-4 flex flex-col items-start gap-2"
              onClick={() => setTrainingMode('file')}
            >
              <div className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                <span className="font-medium">文件上传</span>
              </div>
              <p className="text-sm text-left opacity-75">
                上传DDL SQL文件或手动输入DDL语句
              </p>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 自动提取模式 */}
      {trainingMode === 'auto' && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">自动提取配置</CardTitle>
            <CardDescription>
              配置自动提取参数，系统将从数据库连接中自动获取表结构
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid w-full max-w-sm items-center gap-1.5">
              <Label htmlFor="database-name">数据库名称（可选）</Label>
              <Input
                id="database-name"
                placeholder="留空则提取所有数据库"
                value={databaseName}
                onChange={(e) => setDatabaseName(e.target.value)}
              />
            </div>

            {/* 训练选项 */}
            <div className="space-y-3">
              <Label className="text-sm font-medium">训练选项</Label>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="auto-extract"
                    checked={autoExtract}
                    onCheckedChange={(checked) => setAutoExtract(checked as boolean)}
                  />
                  <Label htmlFor="auto-extract" className="text-sm">
                    自动提取表结构
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="skip-existing"
                    checked={skipExisting}
                    onCheckedChange={(checked) => setSkipExisting(checked as boolean)}
                  />
                  <Label htmlFor="skip-existing" className="text-sm">
                    跳过已存在的数据
                  </Label>
                </div>
              </div>
            </div>
            
            <Button 
              onClick={handleAutoExtraction} 
              disabled={isTraining}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {isTraining ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  正在提取...
                </>
              ) : (
                <>
                  <Database className="h-4 w-4 mr-2" />
                  开始自动提取
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* 文件上传模式 */}
      {trainingMode === 'file' && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg">DDL文件上传</CardTitle>
                <CardDescription>
                  上传包含CREATE TABLE语句的SQL文件，或直接输入DDL内容
                </CardDescription>
              </div>
              <Button variant="outline" size="sm" onClick={downloadSampleDDL}>
                <Download className="h-4 w-4 mr-2" />
                下载示例
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid w-full max-w-sm items-center gap-1.5">
              <Label htmlFor="ddl-file">选择DDL文件</Label>
              <Input
                id="ddl-file"
                type="file"
                accept=".sql,.txt"
                ref={fileInputRef}
                onChange={handleFileUpload}
              />
            </div>
            
            {uploadedFile && (
              <Alert>
                <FileText className="h-4 w-4" />
                <AlertDescription>
                  已选择文件: {uploadedFile.name} ({(uploadedFile.size / 1024).toFixed(1)} KB)
                </AlertDescription>
              </Alert>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="ddl-content">DDL内容</Label>
              <Textarea
                id="ddl-content"
                placeholder="粘贴或编辑DDL语句..."
                value={ddlContent}
                onChange={(e) => setDdlContent(e.target.value)}
                rows={10}
                className="font-mono text-sm"
              />
            </div>

            {/* 训练选项 */}
            <div className="space-y-3">
              <Label className="text-sm font-medium">训练选项</Label>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="skip-existing-file"
                    checked={skipExisting}
                    onCheckedChange={(checked) => setSkipExisting(checked as boolean)}
                  />
                  <Label htmlFor="skip-existing-file" className="text-sm">
                    跳过已存在的数据
                  </Label>
                </div>
              </div>
            </div>

            <Button
              onClick={handleFileTraining} 
              disabled={isTraining || !ddlContent.trim()}
              className="bg-green-600 hover:bg-green-700"
            >
              {isTraining ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  正在训练...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4 mr-2" />
                  开始DDL训练
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      )}

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
                  DDL训练成功完成！处理了 {trainingResult.successful_items || 0} 条DDL语句
                  {trainingResult.training_time && ` (耗时: ${trainingResult.training_time}ms)`}
                </AlertDescription>
              </Alert>
            ) : (
              <Alert variant="destructive">
                <XCircle className="h-4 w-4" />
                <AlertDescription>
                  DDL训练失败: {trainingResult.error || trainingResult.message || '未知错误'}
                </AlertDescription>
              </Alert>
            )}
            
            {trainingResult.total_items !== undefined && (
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold">{trainingResult.total_items}</div>
                  <div className="text-sm text-muted-foreground">总计</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-green-600">{trainingResult.successful_items || 0}</div>
                  <div className="text-sm text-muted-foreground">成功</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-red-600">{trainingResult.failed_items || 0}</div>
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
