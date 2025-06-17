// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * Rate Limit Editor
 * 限流配置编辑器 - 简化版本
 */

'use client';

import React from 'react';
import { Input } from '~/components/ui/input';
import { Label } from '~/components/ui/label';
import { Switch } from '~/components/ui/switch';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';

import { type RateLimit } from '~/core/api/api-management';

interface RateLimitEditorProps {
  rateLimit: RateLimit;
  onChange: (rateLimit: RateLimit) => void;
}

export function RateLimitEditor({ rateLimit, onChange }: RateLimitEditorProps) {
  const handleChange = (field: keyof RateLimit, value: any) => {
    onChange({ ...rateLimit, [field]: value });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>限流配置</CardTitle>
        <CardDescription>配置API调用频率限制</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center space-x-2">
          <Switch
            id="rate-limit-enabled"
            checked={rateLimit.enabled}
            onCheckedChange={(checked) => handleChange('enabled', checked)}
          />
          <Label htmlFor="rate-limit-enabled">启用限流</Label>
        </div>

        {rateLimit.enabled && (
          <>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="max-requests">最大请求数</Label>
                <Input
                  id="max-requests"
                  type="number"
                  min={1}
                  value={rateLimit.max_requests}
                  onChange={(e) => handleChange('max_requests', Number(e.target.value))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="time-window">时间窗口(秒)</Label>
                <Input
                  id="time-window"
                  type="number"
                  min={1}
                  value={rateLimit.time_window_seconds}
                  onChange={(e) => handleChange('time_window_seconds', Number(e.target.value))}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="rate-limit-type">限流类型</Label>
              <select
                id="rate-limit-type"
                value={rateLimit.rate_limit_type}
                onChange={(e) => handleChange('rate_limit_type', Number(e.target.value))}
                className="w-full px-3 py-2 border border-input bg-background rounded-md text-sm"
              >
                <option value={0}>无限流</option>
                <option value={1}>每秒限流</option>
                <option value={2}>每分钟限流</option>
                <option value={3}>每小时限流</option>
                <option value={4}>每天限流</option>
              </select>
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="block-on-limit"
                checked={rateLimit.block_on_limit}
                onCheckedChange={(checked) => handleChange('block_on_limit', checked)}
              />
              <Label htmlFor="block-on-limit">达到限制时阻塞请求</Label>
            </div>
          </>
        )}

        <div className="p-3 bg-muted rounded-lg">
          <p className="text-sm text-muted-foreground">
            限流配置用于控制API调用频率，防止过度使用。建议根据API提供商的限制进行配置。
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
