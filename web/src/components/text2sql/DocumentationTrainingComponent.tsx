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
import { 
  FileText, 
  Upload, 
  Loader2, 
  CheckCircle, 
  XCircle,
  AlertCircle,
  Download,
  BookOpen
} from "lucide-react";
import { text2sqlApi } from "~/core/api/text2sql";

interface TrainingResult {
  success: boolean;
  message?: string;
  error?: string;
  total?: number;
  successful?: number;
  failed?: number;
}

interface DocumentationTrainingComponentProps {
  datasourceId: number;
}

export function DocumentationTrainingComponent({ datasourceId }: DocumentationTrainingComponentProps) {
  const [isTraining, setIsTraining] = useState(false);
  const [trainingResult, setTrainingResult] = useState<TrainingResult | null>(null);
  const [inputMode, setInputMode] = useState<'text' | 'file'>('text');
  const [documentContent, setDocumentContent] = useState('');
  const [documentType, setDocumentType] = useState<'business' | 'technical' | 'api' | 'other'>('business');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      
      // Read file content
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setDocumentContent(content);
      };
      reader.readAsText(file);
    }
  };

  const handleTraining = async () => {
    if (!documentContent.trim() || isTraining) return;

    try {
      setIsTraining(true);
      setTrainingResult(null);
      
      const result = await text2sqlApi.trainDocumentation(datasourceId, {
        documentation: documentContent,
        doc_type: documentType,
        metadata: {
          doc_type: documentType,
          char_count: documentContent.length,
          source: inputMode === 'file' ? 'file_upload' : 'manual_input',
          file_name: uploadedFile?.name
        }
      });

      setTrainingResult(result);
    } catch (error: any) {
      console.error('文档训练失败:', error);
      setTrainingResult({
        success: false,
        total: 0,
        successful: 0,
        failed: 0,
        error: error.message || '网络错误'
      });
    } finally {
      setIsTraining(false);
    }
  };

  const clearResults = () => {
    setTrainingResult(null);
    setUploadedFile(null);
    setDocumentContent('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const loadSampleDocumentation = () => {
    setDocumentContent(`# 电商系统业务文档

## 用户管理
用户系统包含以下核心功能：
- 用户注册和登录
- 用户信息管理
- 用户权限控制

用户表(users)包含以下字段：
- id: 用户唯一标识
- username: 用户名，必须唯一
- email: 邮箱地址，用于登录和通知
- password_hash: 加密后的密码
- created_at: 注册时间
- updated_at: 最后更新时间

## 订单管理
订单系统负责处理用户的购买行为：
- 订单创建和支付
- 订单状态跟踪
- 订单历史查询

订单表(orders)包含：
- id: 订单唯一标识
- user_id: 关联用户ID
- total_amount: 订单总金额
- status: 订单状态(pending/paid/shipped/completed/cancelled)
- created_at: 订单创建时间

订单项表(order_items)包含：
- id: 订单项唯一标识
- order_id: 关联订单ID
- product_name: 商品名称
- quantity: 购买数量
- unit_price: 单价
- total_price: 小计金额

## 常见查询场景
1. 查询今日订单数量
2. 查询用户的历史订单
3. 查询热销商品排行
4. 查询订单状态分布
5. 查询用户注册趋势`);
    setDocumentType('business');
  };

  const downloadSampleDoc = () => {
    const sampleDoc = `# 数据库业务文档示例

## 系统概述
这是一个电商系统的数据库文档，包含用户、订单、商品等核心业务模块。

## 业务规则
1. 每个用户可以有多个订单
2. 每个订单可以包含多个商品
3. 订单状态包括：待支付、已支付、已发货、已完成、已取消

## 数据字典
- users: 用户信息表
- orders: 订单主表  
- order_items: 订单明细表
- products: 商品信息表

## 常见业务查询
- 统计用户订单数量
- 查询热销商品
- 分析销售趋势
- 用户行为分析`;

    const blob = new Blob([sampleDoc], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_documentation.md';
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
            <BookOpen className="h-5 w-5" />
            文档训练
          </CardTitle>
          <CardDescription>
            添加业务文档、API文档或技术文档，帮助模型理解业务逻辑和数据含义。
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

      {/* 输入方式选择 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">输入方式</CardTitle>
          <CardDescription>
            选择文档内容的输入方式
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Button
              variant={inputMode === 'text' ? 'default' : 'outline'}
              className="h-auto p-4 flex flex-col items-start gap-2"
              onClick={() => setInputMode('text')}
            >
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                <span className="font-medium">文本输入</span>
              </div>
              <p className="text-sm text-left opacity-75">
                直接在文本框中输入或粘贴文档内容
              </p>
            </Button>
            
            <Button
              variant={inputMode === 'file' ? 'default' : 'outline'}
              className="h-auto p-4 flex flex-col items-start gap-2"
              onClick={() => setInputMode('file')}
            >
              <div className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                <span className="font-medium">文件上传</span>
              </div>
              <p className="text-sm text-left opacity-75">
                上传文档文件（支持 .txt, .md 格式）
              </p>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 文档类型选择 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">文档类型</CardTitle>
          <CardDescription>
            选择文档的类型以便更好地处理内容
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid w-full max-w-sm items-center gap-1.5">
            <Label htmlFor="doc-type">文档类型</Label>
            <Select 
              value={documentType} 
              onValueChange={(value: any) => setDocumentType(value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="business">业务文档</SelectItem>
                <SelectItem value="technical">技术文档</SelectItem>
                <SelectItem value="api">API文档</SelectItem>
                <SelectItem value="other">其他</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* 文件上传模式 */}
      {inputMode === 'file' && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg">文档文件上传</CardTitle>
                <CardDescription>
                  上传包含业务文档的文本文件
                </CardDescription>
              </div>
              <Button variant="outline" size="sm" onClick={downloadSampleDoc}>
                <Download className="h-4 w-4 mr-2" />
                下载示例
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid w-full max-w-sm items-center gap-1.5">
              <Label htmlFor="doc-file">选择文档文件</Label>
              <Input
                id="doc-file"
                type="file"
                accept=".txt,.md,.doc,.docx"
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
          </CardContent>
        </Card>
      )}

      {/* 文档内容 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">文档内容</CardTitle>
              <CardDescription>
                输入或编辑要训练的文档内容
              </CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={loadSampleDocumentation}>
              <FileText className="h-4 w-4 mr-2" />
              加载示例
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="输入文档内容..."
            value={documentContent}
            onChange={(e) => setDocumentContent(e.target.value)}
            rows={15}
            className="text-sm"
          />
          
          <div className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              字符数: {documentContent.length}
            </div>
            
            <Button 
              onClick={handleTraining} 
              disabled={isTraining || !documentContent.trim()}
              className="bg-indigo-600 hover:bg-indigo-700"
            >
              {isTraining ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  正在训练...
                </>
              ) : (
                <>
                  <BookOpen className="h-4 w-4 mr-2" />
                  开始文档训练
                </>
              )}
            </Button>
          </div>
          
          {!documentContent.trim() && (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                请输入文档内容后再开始训练
              </AlertDescription>
            </Alert>
          )}
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
                  文档训练成功完成！处理了 {trainingResult.successful || 1} 个文档
                </AlertDescription>
              </Alert>
            ) : (
              <Alert variant="destructive">
                <XCircle className="h-4 w-4" />
                <AlertDescription>
                  文档训练失败: {trainingResult.error || trainingResult.message || '未知错误'}
                </AlertDescription>
              </Alert>
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
