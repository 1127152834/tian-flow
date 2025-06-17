// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * API Management Client
 * API管理相关的接口客户端 - 严格按照ti-flow实现
 */

import { resolveServiceURL } from './resolve-service-url';

// Helper function for API requests
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = resolveServiceURL(endpoint);
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

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

  const response = await apiRequest<any[]>(`api/admin/api-definitions?${searchParams.toString()}`);
  return response.map(convertAPIDefinitionResponse);
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

  return apiRequest<{ count: number }>(`api/admin/api-definitions/count?${searchParams.toString()}`);
}

export async function createAPIDefinition(data: Omit<APIDefinition, 'id' | 'created_at' | 'updated_at'>): Promise<APIDefinition> {
  const response = await apiRequest<any>('api/admin/api-definitions', {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return convertAPIDefinitionResponse(response);
}

export async function getAPIDefinition(id: number): Promise<APIDefinition> {
  const response = await apiRequest<any>(`api/admin/api-definitions/${id}`);
  return convertAPIDefinitionResponse(response);
}

export async function updateAPIDefinition(id: number, data: Partial<APIDefinition>): Promise<APIDefinition> {
  const response = await apiRequest<any>(`api/admin/api-definitions/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
  return convertAPIDefinitionResponse(response);
}

export async function deleteAPIDefinition(id: number): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`api/admin/api-definitions/${id}`, {
    method: 'DELETE',
  });
}

export async function toggleAPIEnabled(id: number): Promise<APIDefinition> {
  const response = await apiRequest<any>(`api/admin/api-definitions/${id}/toggle`, {
    method: 'POST',
  });
  return convertAPIDefinitionResponse(response);
}

export async function executeAPI(id: number, request: APIExecutionRequest): Promise<APIExecutionResult> {
  return apiRequest<APIExecutionResult>(`api/admin/api-definitions/${id}/execute`, {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function testAPIConnection(id: number, testParameters?: Record<string, any>): Promise<any> {
  return apiRequest<any>(`api/admin/api-definitions/${id}/test`, {
    method: 'POST',
    body: JSON.stringify({ test_parameters: testParameters }),
  });
}

// Statistics and Search Functions
export async function getAPIStatistics(): Promise<APIStatistics> {
  return apiRequest<APIStatistics>('api/admin/api-definitions/statistics/summary');
}

export async function getAPICategories(): Promise<{ categories: string[] }> {
  return apiRequest<{ categories: string[] }>('api/admin/api-definitions/categories/list');
}

export async function searchAPIs(query: string, limit?: number): Promise<{ results: APIDefinition[] }> {
  const searchParams = new URLSearchParams();
  searchParams.append('q', query);
  if (limit) searchParams.append('limit', limit.toString());

  return apiRequest<{ results: APIDefinition[] }>(`api/admin/api-definitions/search/query?${searchParams.toString()}`);
}

export async function getRecentAPIs(limit?: number): Promise<{ results: APIDefinition[] }> {
  const searchParams = new URLSearchParams();
  if (limit) searchParams.append('limit', limit.toString());

  return apiRequest<{ results: APIDefinition[] }>(`api/admin/api-definitions/recent/list?${searchParams.toString()}`);
}

// Bulk Operations
export async function bulkUpdateAPIs(data: {
  api_ids: number[];
  category?: string;
  enabled?: boolean;
}): Promise<{ message: string; updated_count: number }> {
  return apiRequest<{ message: string; updated_count: number }>('api/admin/api-definitions/bulk/update', {
    method: 'POST',
    body: JSON.stringify(data),
  });
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

  return apiRequest<APICallLog[]>(`api/admin/api-call-logs?${searchParams.toString()}`);
}

export async function getAPICallLog(id: number): Promise<APICallLog> {
  return apiRequest<APICallLog>(`api/admin/api-call-logs/${id}`);
}

export async function getCallStatistics(params?: {
  api_definition_id?: number;
  days?: number;
}): Promise<CallStatistics> {
  const searchParams = new URLSearchParams();

  if (params?.api_definition_id !== undefined) searchParams.append('api_definition_id', params.api_definition_id.toString());
  if (params?.days !== undefined) searchParams.append('days', params.days.toString());

  return apiRequest<CallStatistics>(`api/admin/api-call-logs/statistics/summary?${searchParams.toString()}`);
}

// Curl Parsing Functions
export async function parseCurlCommand(curlCommand: string): Promise<CurlParseResult> {
  return apiRequest<CurlParseResult>('api/admin/curl-parse/parse', {
    method: 'POST',
    body: JSON.stringify({ curl_command: curlCommand }),
  });
}

export async function importFromCurl(curlCommand: string): Promise<APIDefinition> {
  return apiRequest<APIDefinition>('api/admin/curl-parse/import', {
    method: 'POST',
    body: JSON.stringify({ curl_command: curlCommand }),
  });
}

export async function validateCurlCommand(curlCommand: string): Promise<any> {
  return apiRequest<any>('api/admin/curl-parse/validate', {
    method: 'POST',
    body: JSON.stringify({ curl_command: curlCommand }),
  });
}
