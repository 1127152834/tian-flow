"use client";

import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "~/components/ui/dialog";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Label } from "~/components/ui/label";
import { Textarea } from "~/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select";
import { Badge } from "~/components/ui/badge";
import { Loader2, Save, X, RefreshCw } from "lucide-react";
import { type TrainingDataRequest, type TrainingDataResponse } from "~/core/api/text2sql";

interface EditTrainingDataDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  item: TrainingDataResponse | null;
  onSave: (data: TrainingDataRequest) => Promise<void>;
  loading?: boolean;
}

const CONTENT_TYPES = [
  { value: 'SQL', label: 'SQL Query' },
  { value: 'SCHEMA', label: 'Database Schema' },
  { value: 'DOCUMENTATION', label: 'Documentation' },
  { value: 'DDL', label: 'DDL Statement' },
];

export function EditTrainingDataDialog({
  open,
  onOpenChange,
  item,
  onSave,
  loading = false
}: EditTrainingDataDialogProps) {
  const [formData, setFormData] = useState<Partial<TrainingDataRequest>>({
    content_type: 'SQL',
    content: '',
    question: '',
    sql_query: '',
    table_name: '',
    column_name: '',
    metadata: {},
  });
  const [hasChanges, setHasChanges] = useState(false);
  const [originalData, setOriginalData] = useState<Partial<TrainingDataRequest> | null>(null);

  // Initialize form data when item changes
  useEffect(() => {
    if (item) {
      const initialData = {
        datasource_id: item.datasource_id,
        content_type: item.content_type as any,
        content: item.content,
        question: item.question || '',
        sql_query: item.sql_query || '',
        table_name: item.table_name || '',
        column_name: item.column_name || '',
        metadata: item.metadata || {},
      };
      setFormData(initialData);
      setOriginalData(initialData);
      setHasChanges(false);
    }
  }, [item]);

  // Check for changes whenever formData updates
  useEffect(() => {
    if (originalData) {
      const changed = item?.content_type === 'SQL' ? (
        // 对于 SQL 类型，主要检查 sql_query 和 question 的变化
        formData.sql_query !== originalData.sql_query ||
        formData.question !== originalData.question ||
        formData.table_name !== originalData.table_name ||
        formData.column_name !== originalData.column_name
      ) : (
        // 对于其他类型，检查 content 的变化
        formData.content !== originalData.content ||
        formData.question !== originalData.question ||
        formData.sql_query !== originalData.sql_query ||
        formData.table_name !== originalData.table_name ||
        formData.column_name !== originalData.column_name
      );
      setHasChanges(changed);
    }
  }, [formData, originalData]);

  const handleSave = async () => {
    if (!item || !formData.content?.trim()) return;

    const request: TrainingDataRequest = {
      datasource_id: item.datasource_id,
      content_type: formData.content_type as any,
      content: item?.content_type === 'SQL' ?
        // 对于 SQL 类型，content 保持原样（组合内容），但会在后端重新生成
        item.content :
        formData.content.trim(),
      question: formData.question?.trim() || undefined,
      sql_query: formData.sql_query?.trim() || undefined,
      table_name: formData.table_name?.trim() || undefined,
      column_name: formData.column_name?.trim() || undefined,
      metadata: formData.metadata || {},
    };

    await onSave(request);
  };

  // Remove the handleTableNamesChange function since we're using single table_name now

  if (!item) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="w-300 max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            编辑训练数据
            <Badge variant="outline">{item.content_type}</Badge>
          </DialogTitle>
          <DialogDescription>
            修改训练数据内容，保存后将自动重新生成向量嵌入
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Content Type - Read Only */}
          <div className="space-y-2">
            <Label>内容类型</Label>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-sm">
                {CONTENT_TYPES.find(t => t.value === item?.content_type)?.label || item?.content_type}
              </Badge>
              <span className="text-xs text-muted-foreground">
                (内容类型不可修改)
              </span>
            </div>
          </div>

          {/* Dynamic fields based on content type */}
          {item?.content_type === 'SQL' && (
            <div className="space-y-2">
              <Label htmlFor="question">问题描述 <span className="text-red-500">*</span></Label>
              <Input
                id="question"
                value={formData.question || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, question: e.target.value }))}
                placeholder="描述这个SQL查询要解决的问题..."
                required
              />
            </div>
          )}

          {item?.content_type === 'DDL' && (
            <div className="space-y-2">
              <Label htmlFor="table_name">表名</Label>
              <Input
                id="table_name"
                value={formData.table_name || ''}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  table_name: e.target.value
                }))}
                placeholder="表名..."
              />
            </div>
          )}

          {/* Content */}
          <div className="space-y-2">
            <Label htmlFor="content">
              {item?.content_type === 'SQL' ? 'SQL查询' :
               item?.content_type === 'DDL' ? 'DDL语句' :
               item?.content_type === 'SCHEMA' ? '数据库架构' :
               item?.content_type === 'DOCUMENTATION' ? '文档内容' : '内容'}
              <span className="text-red-500">*</span>
            </Label>
            <Textarea
              id="content"
              value={
                // 对于 SQL 类型，显示 sql_query 字段而不是 content 字段
                item?.content_type === 'SQL' ? (formData.sql_query || '') : (formData.content || '')
              }
              onChange={(e) => {
                if (item?.content_type === 'SQL') {
                  // 对于 SQL 类型，更新 sql_query 字段
                  setFormData(prev => ({ ...prev, sql_query: e.target.value }));
                } else {
                  // 对于其他类型，更新 content 字段
                  setFormData(prev => ({ ...prev, content: e.target.value }));
                }
              }}
              placeholder={
                item?.content_type === 'SQL' ? 'SELECT * FROM users WHERE...' :
                item?.content_type === 'DDL' ? 'CREATE TABLE users (\n  id INTEGER PRIMARY KEY,\n  name VARCHAR(100)\n);' :
                item?.content_type === 'SCHEMA' ? '数据库架构信息，表结构描述...' :
                item?.content_type === 'DOCUMENTATION' ? '业务文档、技术文档或API文档内容...' :
                '内容...'
              }
              className="min-h-[200px] font-mono text-sm"
              required
            />
          </div>

          {/* SQL Query field - different logic for different types */}
          {item?.content_type === 'SQL' ? (
            // For SQL type, this is the actual SQL content (read-only info)
            <div className="space-y-2">
              <Label>SQL查询内容</Label>
              <div className="text-xs text-muted-foreground mb-2">
                SQL类型的训练数据，SQL内容已包含在上面的"SQL查询"字段中
              </div>
            </div>
          ) : (
            // For other types, allow adding related SQL
            <div className="space-y-2">
              <Label htmlFor="sql_query">
                相关SQL查询（可选）
                {item?.content_type === 'DDL' && <span className="text-xs text-muted-foreground ml-2">- 可以添加使用此表的示例查询</span>}
                {item?.content_type === 'SCHEMA' && <span className="text-xs text-muted-foreground ml-2">- 可以添加基于此架构的示例查询</span>}
                {item?.content_type === 'DOCUMENTATION' && <span className="text-xs text-muted-foreground ml-2">- 可以添加文档中提到的SQL示例</span>}
              </Label>
              <Textarea
                id="sql_query"
                value={formData.sql_query || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, sql_query: e.target.value }))}
                placeholder={
                  item?.content_type === 'DDL' ? 'SELECT * FROM table_name WHERE...' :
                  item?.content_type === 'SCHEMA' ? 'SELECT column1, column2 FROM...' :
                  '与此文档相关的SQL查询示例...'
                }
                className="min-h-[100px] font-mono text-sm"
              />
            </div>
          )}

          {/* Table Name - for SQL and other types */}
          {item?.content_type !== 'DDL' && (
            <div className="space-y-2">
              <Label htmlFor="table_name">
                主要表名（可选）
                {item?.content_type === 'SQL' && <span className="text-xs text-muted-foreground ml-2">- SQL查询的主要表</span>}
                {item?.content_type === 'SCHEMA' && <span className="text-xs text-muted-foreground ml-2">- 架构的主要表</span>}
                {item?.content_type === 'DOCUMENTATION' && <span className="text-xs text-muted-foreground ml-2">- 文档提到的主要表</span>}
              </Label>
              <Input
                id="table_name"
                value={formData.table_name || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, table_name: e.target.value }))}
                placeholder={
                  item?.content_type === 'SQL' ? 'users' :
                  item?.content_type === 'SCHEMA' ? 'main_table' :
                  '主要表名...'
                }
              />
            </div>
          )}

          {/* Metadata Display */}
          {item.created_at && (
            <div className="space-y-2">
              <Label>元数据</Label>
              <div className="text-sm text-muted-foreground space-y-1">
                <div>创建时间: {new Date(item.created_at).toLocaleString('zh-CN')}</div>
                {item.updated_at && (
                  <div>更新时间: {new Date(item.updated_at).toLocaleString('zh-CN')}</div>
                )}
                <div>内容哈希: {item.content_hash}</div>
                {item.embedding_vector && (
                  <div>向量维度: {item.embedding_vector.length}</div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="space-y-3 pt-4 border-t">
          {/* Change indicator */}
          {hasChanges && (
            <div className="flex items-center gap-2 text-sm text-amber-600 bg-amber-50 p-2 rounded">
              <RefreshCw className="h-4 w-4" />
              <span>检测到内容变更，保存后将自动重新训练向量嵌入</span>
            </div>
          )}

          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={loading}
            >
              <X className="h-4 w-4 mr-2" />
              取消
            </Button>
            <Button
              onClick={handleSave}
              disabled={loading || !formData.content?.trim() || !hasChanges}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Save className="h-4 w-4 mr-2" />
              )}
              {loading ? '保存并重新训练中...' : hasChanges ? '保存并重新训练' : '保存'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
