// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * Parameter Editor
 * 参数编辑器 - 严格按照ti-flow实现
 */

'use client';

import React, { useState } from 'react';
import { Plus, Trash2, Edit } from 'lucide-react';
import { Button } from '~/components/ui/button';
import { Input } from '~/components/ui/input';
import { Textarea } from '~/components/ui/textarea';
import { Label } from '~/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { Badge } from '~/components/ui/badge';
import { Switch } from '~/components/ui/switch';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle 
} from '~/components/ui/dialog';

import { type Parameter, ParameterType, DataType } from '~/core/api/api-management';

const ParameterTypeNames = {
  [ParameterType.QUERY]: '查询参数',
  [ParameterType.HEADER]: '请求头',
  [ParameterType.PATH]: '路径参数',
  [ParameterType.BODY]: '请求体',
  [ParameterType.FORM]: '表单参数',
};

const DataTypeNames = {
  [DataType.STRING]: '字符串',
  [DataType.INTEGER]: '整数',
  [DataType.FLOAT]: '浮点数',
  [DataType.BOOLEAN]: '布尔值',
  [DataType.ARRAY]: '数组',
  [DataType.OBJECT]: '对象',
  [DataType.FILE]: '文件',
};

const ParameterTypeColors = {
  [ParameterType.QUERY]: 'bg-blue-100 text-blue-800',
  [ParameterType.HEADER]: 'bg-green-100 text-green-800',
  [ParameterType.PATH]: 'bg-purple-100 text-purple-800',
  [ParameterType.BODY]: 'bg-orange-100 text-orange-800',
  [ParameterType.FORM]: 'bg-yellow-100 text-yellow-800',
};

interface ParameterEditorProps {
  parameters: Parameter[];
  onChange: (parameters: Parameter[]) => void;
}

export function ParameterEditor({ parameters, onChange }: ParameterEditorProps) {
  const [showDialog, setShowDialog] = useState(false);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [currentParameter, setCurrentParameter] = useState<Parameter>({
    name: '',
    description: '',
    parameter_type: ParameterType.QUERY,
    data_type: DataType.STRING,
    required: false,
  });

  const handleAddParameter = () => {
    setEditingIndex(null);
    setCurrentParameter({
      name: '',
      description: '',
      parameter_type: ParameterType.QUERY,
      data_type: DataType.STRING,
      required: false,
    });
    setShowDialog(true);
  };

  const handleEditParameter = (index: number) => {
    setEditingIndex(index);
    const param = parameters[index];
    if (!param) return;

    setCurrentParameter({
      name: param.name || '',
      description: param.description || '',
      parameter_type: param.parameter_type,
      data_type: param.data_type,
      required: param.required,
      default_value: param.default_value,
      min_length: param.min_length,
      max_length: param.max_length,
      pattern: param.pattern,
      minimum: param.minimum,
      maximum: param.maximum,
      min_items: param.min_items,
      max_items: param.max_items,
      item_type: param.item_type,
      enum_values: param.enum_values,
      example: param.example,
    });
    setShowDialog(true);
  };

  const handleSaveParameter = () => {
    if (!currentParameter.name.trim()) {
      return;
    }

    const newParameters = [...parameters];
    if (editingIndex !== null) {
      newParameters[editingIndex] = currentParameter;
    } else {
      newParameters.push(currentParameter);
    }
    
    onChange(newParameters);
    setShowDialog(false);
  };

  const handleDeleteParameter = (index: number) => {
    const newParameters = parameters.filter((_, i) => i !== index);
    onChange(newParameters);
  };

  const handleParameterChange = (field: keyof Parameter, value: any) => {
    setCurrentParameter(prev => ({ ...prev, [field]: value }));
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>参数定义</CardTitle>
        <CardDescription>定义API的输入参数，包括查询参数、请求头、路径参数等</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* 参数列表 */}
        <div className="space-y-2">
          {parameters.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              暂无参数定义
            </div>
          ) : (
            parameters.map((param, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50"
              >
                <div className="flex-1 space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{param.name}</span>
                    <Badge 
                      variant="secondary" 
                      className={ParameterTypeColors[param.parameter_type]}
                    >
                      {ParameterTypeNames[param.parameter_type]}
                    </Badge>
                    <Badge variant="outline">
                      {DataTypeNames[param.data_type]}
                    </Badge>
                    {param.required && (
                      <Badge variant="destructive" className="text-xs">
                        必需
                      </Badge>
                    )}
                  </div>
                  {param.description && (
                    <p className="text-sm text-muted-foreground">
                      {param.description}
                    </p>
                  )}
                  {param.default_value !== undefined && (
                    <p className="text-xs text-muted-foreground">
                      默认值: {String(param.default_value)}
                    </p>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleEditParameter(index)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteParameter(index)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* 添加按钮 */}
        <Button
          variant="outline"
          onClick={handleAddParameter}
          className="w-full"
        >
          <Plus className="h-4 w-4 mr-2" />
          添加参数
        </Button>

        {/* 参数编辑对话框 */}
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>
                {editingIndex !== null ? '编辑参数' : '添加参数'}
              </DialogTitle>
              <DialogDescription>
                配置参数的基本信息和验证规则
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              {/* 基本信息 */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="param-name">参数名称 *</Label>
                  <Input
                    id="param-name"
                    value={currentParameter.name}
                    onChange={(e) => handleParameterChange('name', e.target.value)}
                    placeholder="输入参数名称"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="param-type">参数类型 *</Label>
                  <select
                    id="param-type"
                    value={currentParameter.parameter_type}
                    onChange={(e) => handleParameterChange('parameter_type', Number(e.target.value))}
                    className="w-full px-3 py-2 border border-input bg-background rounded-md text-sm"
                  >
                    {Object.entries(ParameterTypeNames).map(([value, label]) => (
                      <option key={value} value={value}>
                        {label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="param-description">参数描述</Label>
                <Textarea
                  id="param-description"
                  value={currentParameter.description || ''}
                  onChange={(e) => handleParameterChange('description', e.target.value)}
                  placeholder="输入参数描述"
                  rows={2}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="data-type">数据类型 *</Label>
                  <select
                    id="data-type"
                    value={currentParameter.data_type}
                    onChange={(e) => handleParameterChange('data_type', Number(e.target.value))}
                    className="w-full px-3 py-2 border border-input bg-background rounded-md text-sm"
                  >
                    {Object.entries(DataTypeNames).map(([value, label]) => (
                      <option key={value} value={value}>
                        {label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="default-value">默认值</Label>
                  <Input
                    id="default-value"
                    value={currentParameter.default_value || ''}
                    onChange={(e) => handleParameterChange('default_value', e.target.value)}
                    placeholder="输入默认值"
                  />
                </div>
              </div>

              {/* 验证规则 */}
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="required"
                    checked={currentParameter.required}
                    onCheckedChange={(checked) => handleParameterChange('required', checked)}
                  />
                  <Label htmlFor="required">必需参数</Label>
                </div>

                {/* 字符串验证 */}
                {currentParameter.data_type === DataType.STRING && (
                  <div className="grid grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="min-length">最小长度</Label>
                      <Input
                        id="min-length"
                        type="number"
                        min={0}
                        value={currentParameter.min_length || ''}
                        onChange={(e) => handleParameterChange('min_length', e.target.value ? Number(e.target.value) : undefined)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="max-length">最大长度</Label>
                      <Input
                        id="max-length"
                        type="number"
                        min={0}
                        value={currentParameter.max_length || ''}
                        onChange={(e) => handleParameterChange('max_length', e.target.value ? Number(e.target.value) : undefined)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="pattern">正则表达式</Label>
                      <Input
                        id="pattern"
                        value={currentParameter.pattern || ''}
                        onChange={(e) => handleParameterChange('pattern', e.target.value)}
                        placeholder="^[a-zA-Z0-9]+$"
                      />
                    </div>
                  </div>
                )}

                {/* 数值验证 */}
                {(currentParameter.data_type === DataType.INTEGER || currentParameter.data_type === DataType.FLOAT) && (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="minimum">最小值</Label>
                      <Input
                        id="minimum"
                        type="number"
                        value={currentParameter.minimum || ''}
                        onChange={(e) => handleParameterChange('minimum', e.target.value ? Number(e.target.value) : undefined)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="maximum">最大值</Label>
                      <Input
                        id="maximum"
                        type="number"
                        value={currentParameter.maximum || ''}
                        onChange={(e) => handleParameterChange('maximum', e.target.value ? Number(e.target.value) : undefined)}
                      />
                    </div>
                  </div>
                )}

                {/* 数组验证 */}
                {currentParameter.data_type === DataType.ARRAY && (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="min-items">最小元素数</Label>
                      <Input
                        id="min-items"
                        type="number"
                        min={0}
                        value={currentParameter.min_items || ''}
                        onChange={(e) => handleParameterChange('min_items', e.target.value ? Number(e.target.value) : undefined)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="max-items">最大元素数</Label>
                      <Input
                        id="max-items"
                        type="number"
                        min={0}
                        value={currentParameter.max_items || ''}
                        onChange={(e) => handleParameterChange('max_items', e.target.value ? Number(e.target.value) : undefined)}
                      />
                    </div>
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="example">示例值</Label>
                  <Input
                    id="example"
                    value={currentParameter.example || ''}
                    onChange={(e) => handleParameterChange('example', e.target.value)}
                    placeholder="输入示例值"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-4 border-t">
              <Button
                variant="outline"
                onClick={() => setShowDialog(false)}
              >
                取消
              </Button>
              <Button onClick={handleSaveParameter}>
                {editingIndex !== null ? '更新' : '添加'}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  );
}
