// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * Response Config Editor
 * 响应配置编辑器 - 简化版本
 */

'use client';

import React from 'react';
import { Input } from '~/components/ui/input';
import { Label } from '~/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';

import type { ResponseConfig } from '~/core/api/api-management';
import { ResponseType } from '~/core/api/api-management';

interface ResponseConfigEditorProps {
  responseConfig: ResponseConfig;
  onChange: (responseConfig: ResponseConfig) => void;
}

export function ResponseConfigEditor({ responseConfig, onChange }: ResponseConfigEditorProps) {
  const handleChange = (field: keyof ResponseConfig, value: any) => {
    onChange({ ...responseConfig, [field]: value });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>响应配置</CardTitle>
        <CardDescription>配置API响应的处理方式</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="response-type">响应类型</Label>
            <select
              id="response-type"
              value={responseConfig.response_type}
              onChange={(e) => handleChange('response_type', Number(e.target.value))}
              className="w-full px-3 py-2 border border-input bg-background rounded-md text-sm"
            >
              <option value={ResponseType.JSON}>JSON</option>
              <option value={ResponseType.XML}>XML</option>
              <option value={ResponseType.TEXT}>文本</option>
              <option value={ResponseType.HTML}>HTML</option>
            </select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="content-type">内容类型</Label>
            <Input
              id="content-type"
              value={responseConfig.content_type}
              onChange={(e) => handleChange('content_type', e.target.value)}
              placeholder="application/json"
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="encoding">编码格式</Label>
          <Input
            id="encoding"
            value={responseConfig.encoding}
            onChange={(e) => handleChange('encoding', e.target.value)}
            placeholder="utf-8"
          />
        </div>

        <div className="p-3 bg-muted rounded-lg">
          <p className="text-sm text-muted-foreground">
            响应配置用于指定如何解析和处理API返回的数据。默认配置适用于大多数JSON API。
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
