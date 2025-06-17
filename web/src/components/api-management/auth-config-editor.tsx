// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * Auth Config Editor
 * 认证配置编辑器 - 严格按照ti-flow实现
 */

'use client';

import React from 'react';
import { Input } from '~/components/ui/input';
import { Textarea } from '~/components/ui/textarea';
import { Label } from '~/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { Badge } from '~/components/ui/badge';

import { type AuthConfig, AuthType } from '~/core/api/api-management';

const AuthTypeNames = {
  [AuthType.NONE]: '无认证',
  [AuthType.API_KEY]: 'API Key',
  [AuthType.BEARER]: 'Bearer Token',
  [AuthType.BASIC]: 'Basic认证',
  [AuthType.OAUTH2]: 'OAuth2',
  [AuthType.CUSTOM]: '自定义认证',
};

interface AuthConfigEditorProps {
  authConfig: AuthConfig;
  onChange: (authConfig: AuthConfig) => void;
}

export function AuthConfigEditor({ authConfig, onChange }: AuthConfigEditorProps) {
  const handleChange = (field: keyof AuthConfig, value: any) => {
    onChange({ ...authConfig, [field]: value });
  };

  const handleCustomHeaderChange = (key: string, value: string, oldKey?: string) => {
    const newHeaders = { ...authConfig.custom_headers };
    if (oldKey && oldKey !== key) {
      delete newHeaders[oldKey];
    }
    if (key && value) {
      newHeaders[key] = value;
    } else if (key) {
      delete newHeaders[key];
    }
    handleChange('custom_headers', newHeaders);
  };

  const handleCustomParamChange = (key: string, value: string, oldKey?: string) => {
    const newParams = { ...authConfig.custom_params };
    if (oldKey && oldKey !== key) {
      delete newParams[oldKey];
    }
    if (key && value) {
      newParams[key] = value;
    } else if (key) {
      delete newParams[key];
    }
    handleChange('custom_params', newParams);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>认证配置</CardTitle>
        <CardDescription>配置API的认证方式和相关参数</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* 认证类型选择 */}
        <div className="space-y-2">
          <Label htmlFor="auth-type">认证类型</Label>
          <select
            id="auth-type"
            value={authConfig.auth_type}
            onChange={(e) => handleChange('auth_type', Number(e.target.value))}
            className="w-full px-3 py-2 border border-input bg-background rounded-md text-sm"
          >
            {Object.entries(AuthTypeNames).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>

        {/* 当前认证类型显示 */}
        <div className="flex items-center gap-2">
          <Badge variant="outline">
            {AuthTypeNames[authConfig.auth_type]}
          </Badge>
        </div>

        {/* API Key 认证 */}
        {authConfig.auth_type === AuthType.API_KEY && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="api-key">API Key *</Label>
                <Input
                  id="api-key"
                  type="password"
                  value={authConfig.api_key || ''}
                  onChange={(e) => handleChange('api_key', e.target.value)}
                  placeholder="输入API Key"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="api-key-header">请求头名称</Label>
                <Input
                  id="api-key-header"
                  value={authConfig.api_key_header || 'X-API-Key'}
                  onChange={(e) => handleChange('api_key_header', e.target.value)}
                  placeholder="X-API-Key"
                />
              </div>
            </div>
          </div>
        )}

        {/* Bearer Token 认证 */}
        {authConfig.auth_type === AuthType.BEARER && (
          <div className="space-y-2">
            <Label htmlFor="bearer-token">Bearer Token *</Label>
            <Input
              id="bearer-token"
              type="password"
              value={authConfig.bearer_token || ''}
              onChange={(e) => handleChange('bearer_token', e.target.value)}
              placeholder="输入Bearer Token"
            />
          </div>
        )}

        {/* Basic 认证 */}
        {authConfig.auth_type === AuthType.BASIC && (
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="username">用户名 *</Label>
              <Input
                id="username"
                value={authConfig.username || ''}
                onChange={(e) => handleChange('username', e.target.value)}
                placeholder="输入用户名"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">密码 *</Label>
              <Input
                id="password"
                type="password"
                value={authConfig.password || ''}
                onChange={(e) => handleChange('password', e.target.value)}
                placeholder="输入密码"
              />
            </div>
          </div>
        )}

        {/* OAuth2 认证 */}
        {authConfig.auth_type === AuthType.OAUTH2 && (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="oauth2-token">访问令牌 *</Label>
              <Input
                id="oauth2-token"
                type="password"
                value={authConfig.oauth2_token || ''}
                onChange={(e) => handleChange('oauth2_token', e.target.value)}
                placeholder="输入OAuth2访问令牌"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="oauth2-token-url">令牌获取URL</Label>
                <Input
                  id="oauth2-token-url"
                  value={authConfig.oauth2_token_url || ''}
                  onChange={(e) => handleChange('oauth2_token_url', e.target.value)}
                  placeholder="https://auth.example.com/oauth/token"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="oauth2-scope">权限范围</Label>
                <Input
                  id="oauth2-scope"
                  value={authConfig.oauth2_scope || ''}
                  onChange={(e) => handleChange('oauth2_scope', e.target.value)}
                  placeholder="read write"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="oauth2-client-id">客户端ID</Label>
                <Input
                  id="oauth2-client-id"
                  value={authConfig.oauth2_client_id || ''}
                  onChange={(e) => handleChange('oauth2_client_id', e.target.value)}
                  placeholder="输入客户端ID"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="oauth2-client-secret">客户端密钥</Label>
                <Input
                  id="oauth2-client-secret"
                  type="password"
                  value={authConfig.oauth2_client_secret || ''}
                  onChange={(e) => handleChange('oauth2_client_secret', e.target.value)}
                  placeholder="输入客户端密钥"
                />
              </div>
            </div>
          </div>
        )}

        {/* 自定义认证 */}
        {authConfig.auth_type === AuthType.CUSTOM && (
          <div className="space-y-4">
            {/* 自定义请求头 */}
            <div className="space-y-2">
              <Label>自定义请求头</Label>
              <div className="space-y-2">
                {Object.entries(authConfig.custom_headers || {}).map(([key, value], index) => (
                  <div key={index} className="flex gap-2">
                    <Input
                      placeholder="Header名称"
                      value={key}
                      onChange={(e) => handleCustomHeaderChange(e.target.value, value, key)}
                    />
                    <Input
                      placeholder="Header值"
                      value={value}
                      onChange={(e) => handleCustomHeaderChange(key, e.target.value)}
                    />
                    <button
                      type="button"
                      onClick={() => handleCustomHeaderChange('', '', key)}
                      className="px-3 py-2 text-sm border border-input bg-background rounded-md hover:bg-muted"
                    >
                      删除
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={() => handleCustomHeaderChange('', '')}
                  className="w-full px-3 py-2 text-sm border border-input bg-background rounded-md hover:bg-muted"
                >
                  添加请求头
                </button>
              </div>
            </div>

            {/* 自定义参数 */}
            <div className="space-y-2">
              <Label>自定义参数</Label>
              <div className="space-y-2">
                {Object.entries(authConfig.custom_params || {}).map(([key, value], index) => (
                  <div key={index} className="flex gap-2">
                    <Input
                      placeholder="参数名称"
                      value={key}
                      onChange={(e) => handleCustomParamChange(e.target.value, value, key)}
                    />
                    <Input
                      placeholder="参数值"
                      value={value}
                      onChange={(e) => handleCustomParamChange(key, e.target.value)}
                    />
                    <button
                      type="button"
                      onClick={() => handleCustomParamChange('', '', key)}
                      className="px-3 py-2 text-sm border border-input bg-background rounded-md hover:bg-muted"
                    >
                      删除
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={() => handleCustomParamChange('', '')}
                  className="w-full px-3 py-2 text-sm border border-input bg-background rounded-md hover:bg-muted"
                >
                  添加参数
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 认证说明 */}
        {authConfig.auth_type !== AuthType.NONE && (
          <div className="p-3 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground">
              {authConfig.auth_type === AuthType.API_KEY && 
                '将在请求头中添加指定的API Key进行认证'}
              {authConfig.auth_type === AuthType.BEARER && 
                '将在Authorization头中添加Bearer Token进行认证'}
              {authConfig.auth_type === AuthType.BASIC && 
                '将使用HTTP Basic认证，用户名和密码会被Base64编码'}
              {authConfig.auth_type === AuthType.OAUTH2 && 
                '将在Authorization头中添加OAuth2访问令牌进行认证'}
              {authConfig.auth_type === AuthType.CUSTOM && 
                '将使用自定义的请求头和参数进行认证'}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
