// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * Database datasource API client for DeerFlow.
 * Provides functions to interact with database datasource management endpoints.
 */

import { resolveServiceURL } from "./resolve-service-url";

// Types
export interface DatabaseDatasource {
  id: number;
  name: string;
  description?: string;
  database_type: "MYSQL" | "POSTGRESQL";
  host: string;
  port: number;
  database_name: string;
  username: string;
  readonly_mode: boolean;
  allowed_operations: string[];
  connection_status: "CONNECTED" | "DISCONNECTED" | "ERROR" | "TESTING";
  last_tested_at?: string;
  connection_error?: string;
  created_at?: string;
  updated_at?: string;
}

export interface DatabaseDatasourceCreate {
  name: string;
  description?: string;
  database_type: "MYSQL" | "POSTGRESQL";
  host: string;
  port: number;
  database_name: string;
  username: string;
  password: string;
  readonly_mode: boolean;
  allowed_operations?: string[];
}

export interface DatabaseDatasourceUpdate {
  name?: string;
  description?: string;
  host?: string;
  port?: number;
  database_name?: string;
  username?: string;
  password?: string;
  readonly_mode?: boolean;
  allowed_operations?: string[];
}

export interface DatabaseDatasourceListResponse {
  datasources: DatabaseDatasource[];
  total: number;
  limit: number;
  offset: number;
}

export interface ConnectionTestResponse {
  success: boolean;
  error?: string;
  details?: any;
  tested_at: string;
}

export interface DatabaseTable {
  table_name: string;
  schema_name?: string;
  table_name_only?: string;
  columns: any[];
  column_count: number;
}

export interface DatabaseSchemaResponse {
  tables: DatabaseTable[];
  total_tables: number;
  schema_extracted_at: string;
}

// API Functions
export async function listDatabaseDatasources(params?: {
  database_type?: string;
  connection_status?: string;
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<DatabaseDatasourceListResponse> {
  const searchParams = new URLSearchParams();
  
  if (params?.database_type) searchParams.append("database_type", params.database_type);
  if (params?.connection_status) searchParams.append("connection_status", params.connection_status);
  if (params?.search) searchParams.append("search", params.search);
  if (params?.limit) searchParams.append("limit", params.limit.toString());
  if (params?.offset) searchParams.append("offset", params.offset.toString());

  const url = resolveServiceURL(`database-datasources?${searchParams.toString()}`);
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

export async function createDatabaseDatasource(
  data: DatabaseDatasourceCreate
): Promise<DatabaseDatasource> {
  const response = await fetch(resolveServiceURL("database-datasources"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

export async function getDatabaseDatasource(id: number): Promise<DatabaseDatasource> {
  const response = await fetch(resolveServiceURL(`database-datasources/${id}`));
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

export async function updateDatabaseDatasource(
  id: number,
  data: DatabaseDatasourceUpdate
): Promise<DatabaseDatasource> {
  const response = await fetch(resolveServiceURL(`database-datasources/${id}`), {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

export async function deleteDatabaseDatasource(id: number): Promise<void> {
  const response = await fetch(resolveServiceURL(`database-datasources/${id}`), {
    method: "DELETE",
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
}

export async function testDatabaseConnection(
  id: number,
  timeout?: number
): Promise<ConnectionTestResponse> {
  const body = timeout ? JSON.stringify({ timeout }) : JSON.stringify({});
  
  const response = await fetch(resolveServiceURL(`database-datasources/${id}/test`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body,
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

export async function getDatabaseSchema(id: number): Promise<DatabaseSchemaResponse> {
  const response = await fetch(resolveServiceURL(`database-datasources/${id}/schema`));
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

// Utility functions
export function formatConnectionStatus(status: string): string {
  switch (status) {
    case "CONNECTED":
      return "Connected";
    case "DISCONNECTED":
      return "Disconnected";
    case "ERROR":
      return "Error";
    case "TESTING":
      return "Testing...";
    default:
      return status;
  }
}

export function getConnectionStatusColor(status: string): string {
  switch (status) {
    case "CONNECTED":
      return "green";
    case "DISCONNECTED":
      return "gray";
    case "ERROR":
      return "red";
    case "TESTING":
      return "blue";
    default:
      return "gray";
  }
}

export function formatDatabaseType(type: string): string {
  switch (type) {
    case "MYSQL":
      return "MySQL";
    case "POSTGRESQL":
      return "PostgreSQL";
    default:
      return type;
  }
}
