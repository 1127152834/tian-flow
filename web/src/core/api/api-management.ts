// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * API Management Client
 * API管理相关的接口客户端 - 严格按照ti-flow实现
 */

import { resolveServiceURL } from './resolve-service-url';

// Helper function to convert backend response to frontend types
function convertAPIDefinitionResponse(response: any): APIDefinition {
  return {
    ...response,
    method: response.method as HTTPMethod, // Convert int to enum
    auth_config: response.auth_config as AuthConfig,
    parameters: response.parameters as Parameter[],
    response_config: response.response_config as ResponseConfig,
    rate_limit: response.rate_limit as RateLimit,
  };
}

// 枚举定义
export enum HTTPMethod {
  GET = 0,
  POST = 1,
  PUT = 2,
  DELETE = 3,
  PATCH = 4,
  HEAD = 5,
  OPTIONS = 6,
}

export enum AuthType {
  NONE = 0,
  API_KEY = 1,
  BEARER = 2,
  BASIC = 3,
  OAUTH2 = 4,
  CUSTOM = 5,
}

export enum ParameterType {
  QUERY = 0,
  HEADER = 1,
  PATH = 2,
  BODY = 3,
  FORM = 4,
}

export enum DataType {
  STRING = 0,
  INTEGER = 1,
  FLOAT = 2,
  BOOLEAN = 3,
  ARRAY = 4,
  OBJECT = 5,
  FILE = 6,
}

export enum ResponseType {
  JSON = 1,
  XML = 2,
  TEXT = 3,
  HTML = 4,
  BINARY = 5,
}

export enum FieldRole {
  DATA = 1,
  STATUS = 2,
  MESSAGE = 3,
  ERROR = 4,
  PAGINATION = 5,
}

// 接口定义
export interface AuthConfig {
  auth_type: AuthType;
  api_key?: string;
  api_key_header?: string;
  bearer_token?: string;
  username?: string;
  password?: string;
  oauth2_token?: string;
  oauth2_token_url?: string;
  oauth2_client_id?: string;
  oauth2_client_secret?: string;
  oauth2_scope?: string;
  custom_headers?: Record<string, string>;
  custom_params?: Record<string, string>;
}

export interface Parameter {
  name: string;
  description?: string;
  parameter_type: ParameterType;
  data_type: DataType;
  required: boolean;
  default_value?: any;
  min_length?: number;
  max_length?: number;
  pattern?: string;
  minimum?: number;
  maximum?: number;
  min_items?: number;
  max_items?: number;
  item_type?: DataType;
  enum_values?: any[];
  example?: any;
}

export interface ResponseField {
  name: string;
  path: string;
  role: FieldRole;
  data_type: string;
  description?: string;
  required: boolean;
}

export interface ResponseConfig {
  response_type: ResponseType;
  content_type: string;
  encoding: string;
  fields: ResponseField[];
  primary_data_field?: string;
  status_field?: string;
  message_field?: string;
  success_conditions: Record<string, any>;
}

export interface RateLimit {
  enabled: boolean;
  rate_limit_type: number;
  max_requests: number;
  time_window_seconds: number;
  burst_size?: number;
  block_on_limit: boolean;
  retry_after_seconds?: number;
}

export interface APIDefinition {
  id?: number;
  name: string;
  description: string;
  category: string;
  method: HTTPMethod;
  url: string;
  headers: Record<string, string>;
  timeout_seconds: number;
  auth_config: AuthConfig;
  parameters: Parameter[];
  response_schema?: any;
  response_config: ResponseConfig;
  rate_limit: RateLimit;
  enabled: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface APICallLog {
  id: number;
  api_definition_id: number;
  session_id?: string;
  request_data?: any;
  response_data?: any;
  status_code?: number;
  execution_time_ms?: number;
  error_message?: string;
  created_at: string;
  updated_at?: string;
}

export interface APIExecutionRequest {
  parameters: Record<string, any>;
  session_id?: string;
}

export interface APIExecutionResult {
  success: boolean;
  api_definition_id: number;
  execution_time_ms: number;
  session_id?: string;
  result: {
    success: boolean;
    status_code?: number;
    headers?: Record<string, string>;
    raw_content?: string;
    parsed_data?: any;
    extracted_data?: any;
    error_message?: string;
    execution_time_ms?: number;
  };
}

export interface CurlParseRequest {
  curl_command: string;
}

export interface CurlParseResult {
  success: boolean;
  api_definition?: Partial<APIDefinition>;
  error_message?: string;
}

export interface APIStatistics {
  total_apis: number;
  enabled_apis: number;
  disabled_apis: number;
  category_distribution: Record<string, number>;
  method_distribution: Record<string, number>;
}

export interface CallStatistics {
  total_calls: number;
  success_calls: number;
  failed_calls: number;
  average_response_time: number;
  success_rate: number;
  calls_today: number;
  period_days: number;
  start_date: string;
  end_date: string;
}

// API Definition Management Functions
export async function listAPIDefinitions(params?: {
  skip?: number;
  limit?: number;
  category?: string;
  enabled?: boolean;
  search?: string;
}): Promise<APIDefinition[]> {
  const searchParams = new URLSearchParams();

  if (params?.skip !== undefined) searchParams.append('skip', params.skip.toString());
  if (params?.limit !== undefined) searchParams.append('limit', params.limit.toString());
  if (params?.category) searchParams.append('category', params.category);
  if (params?.enabled !== undefined) searchParams.append('enabled', params.enabled.toString());
  if (params?.search) searchParams.append('search', params.search);

  const response = await fetch(resolveServiceURL(`api-definitions?${searchParams.toString()}`));

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to list API definitions');
  }

  const data = await response.json();
  return data.map(convertAPIDefinitionResponse);
}

export async function countAPIDefinitions(params?: {
  category?: string;
  enabled?: boolean;
  search?: string;
}): Promise<{ count: number }> {
  const searchParams = new URLSearchParams();

  if (params?.category) searchParams.append('category', params.category);
  if (params?.enabled !== undefined) searchParams.append('enabled', params.enabled.toString());
  if (params?.search) searchParams.append('search', params.search);

  const response = await fetch(resolveServiceURL(`api-definitions/count?${searchParams.toString()}`));

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to count API definitions');
  }

  return response.json();
}

export async function createAPIDefinition(data: Omit<APIDefinition, 'id' | 'created_at' | 'updated_at'>): Promise<APIDefinition> {
  const response = await fetch(resolveServiceURL(`api-definitions`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create API definition');
  }

  const result = await response.json();
  return convertAPIDefinitionResponse(result);
}

export async function getAPIDefinition(id: number): Promise<APIDefinition> {
  const response = await fetch(resolveServiceURL(`api-definitions/${id}`));

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get API definition');
  }

  const result = await response.json();
  return convertAPIDefinitionResponse(result);
}

export async function updateAPIDefinition(id: number, data: Partial<APIDefinition>): Promise<APIDefinition> {
  const response = await fetch(resolveServiceURL(`api-definitions/${id}`), {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update API definition');
  }

  const result = await response.json();
  return convertAPIDefinitionResponse(result);
}

export async function deleteAPIDefinition(id: number): Promise<{ message: string }> {
  const response = await fetch(resolveServiceURL(`api-definitions/${id}`), {
    method: 'DELETE',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete API definition');
  }

  return response.json();
}

export async function toggleAPIEnabled(id: number): Promise<APIDefinition> {
  const response = await fetch(resolveServiceURL(`api-definitions/${id}/toggle`), {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to toggle API enabled status');
  }

  const result = await response.json();
  return convertAPIDefinitionResponse(result);
}

export async function executeAPI(id: number, request: APIExecutionRequest): Promise<APIExecutionResult> {
  const response = await fetch(resolveServiceURL(`api-definitions/${id}/execute`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to execute API');
  }

  return response.json();
}

export async function testAPIConnection(id: number, testParameters?: Record<string, any>): Promise<any> {
  const response = await fetch(resolveServiceURL(`api-definitions/${id}/test`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ test_parameters: testParameters }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to test API connection');
  }

  return response.json();
}

// Statistics and Search Functions
export async function getAPIStatistics(): Promise<APIStatistics> {
  const response = await fetch(resolveServiceURL(`api-definitions/statistics/summary`));

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get API statistics');
  }

  return response.json();
}

export async function getAPICategories(): Promise<{ categories: string[] }> {
  const response = await fetch(resolveServiceURL(`api-definitions/categories/list`));

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get API categories');
  }

  return response.json();
}

export async function searchAPIs(query: string, limit?: number): Promise<{ results: APIDefinition[] }> {
  const searchParams = new URLSearchParams();
  searchParams.append('q', query);
  if (limit) searchParams.append('limit', limit.toString());

  const response = await fetch(resolveServiceURL(`api-definitions/search/query?${searchParams.toString()}`));

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to search APIs');
  }

  return response.json();
}

export async function getRecentAPIs(limit?: number): Promise<{ results: APIDefinition[] }> {
  const searchParams = new URLSearchParams();
  if (limit) searchParams.append('limit', limit.toString());

  const response = await fetch(resolveServiceURL(`api-definitions/recent/list?${searchParams.toString()}`));

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get recent APIs');
  }

  return response.json();
}

// Bulk Operations
export async function bulkUpdateAPIs(data: {
  api_ids: number[];
  category?: string;
  enabled?: boolean;
}): Promise<{ message: string; updated_count: number }> {
  const response = await fetch(resolveServiceURL(`api-definitions/bulk/update`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to bulk update APIs');
  }

  return response.json();
}

// API Call Log Functions
export async function listAPICallLogs(params?: {
  skip?: number;
  limit?: number;
  api_definition_id?: number;
  session_id?: string;
  status_code?: number;
  has_error?: boolean;
  start_date?: string;
  end_date?: string;
}): Promise<APICallLog[]> {
  const searchParams = new URLSearchParams();

  if (params?.skip !== undefined) searchParams.append('skip', params.skip.toString());
  if (params?.limit !== undefined) searchParams.append('limit', params.limit.toString());
  if (params?.api_definition_id !== undefined) searchParams.append('api_definition_id', params.api_definition_id.toString());
  if (params?.session_id) searchParams.append('session_id', params.session_id);
  if (params?.status_code !== undefined) searchParams.append('status_code', params.status_code.toString());
  if (params?.has_error !== undefined) searchParams.append('has_error', params.has_error.toString());
  if (params?.start_date) searchParams.append('start_date', params.start_date);
  if (params?.end_date) searchParams.append('end_date', params.end_date);

  const response = await fetch(resolveServiceURL(`api-call-logs?${searchParams.toString()}`));

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to list API call logs');
  }

  return response.json();
}

export async function getAPICallLog(id: number): Promise<APICallLog> {
  const response = await fetch(resolveServiceURL(`api-call-logs/${id}`));

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get API call log');
  }

  return response.json();
}

export async function getCallStatistics(params?: {
  api_definition_id?: number;
  days?: number;
}): Promise<CallStatistics> {
  const searchParams = new URLSearchParams();

  if (params?.api_definition_id !== undefined) searchParams.append('api_definition_id', params.api_definition_id.toString());
  if (params?.days !== undefined) searchParams.append('days', params.days.toString());

  const response = await fetch(resolveServiceURL(`api-call-logs/statistics/summary?${searchParams.toString()}`));

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get call statistics');
  }

  return response.json();
}

// Curl Parsing Functions
export async function parseCurlCommand(curlCommand: string): Promise<CurlParseResult> {
  const response = await fetch(resolveServiceURL(`curl-parse/parse`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ curl_command: curlCommand }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to parse curl command');
  }

  return response.json();
}

export async function importFromCurl(curlCommand: string): Promise<APIDefinition> {
  const response = await fetch(resolveServiceURL(`curl-parse/import`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ curl_command: curlCommand }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to import from curl');
  }

  return response.json();
}

export async function validateCurlCommand(curlCommand: string): Promise<any> {
  const response = await fetch(resolveServiceURL(`curl-parse/validate`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ curl_command: curlCommand }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to validate curl command');
  }

  return response.json();
}

// API Management Client Object
export const apiManagementClient = {
  // API Definition Management
  listAPIDefinitions,
  countAPIDefinitions,
  createAPIDefinition,
  getAPIDefinition,
  updateAPIDefinition,
  deleteAPIDefinition,
  toggleAPIEnabled,
  executeAPI,
  testAPIConnection,

  // Statistics and Search
  getAPIStatistics,
  getAPICategories,
  searchAPIs,
  getRecentAPIs,

  // Bulk Operations
  bulkUpdateAPIs,

  // API Call Logs
  listAPICallLogs,
  getAPICallLog,
  getCallStatistics,

  // Curl Parsing
  parseCurlCommand,
  importFromCurl,
  validateCurlCommand,
};
