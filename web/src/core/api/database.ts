// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * Database API client for Olight.
 * Re-exports database datasource functionality for compatibility.
 */

import {
  listDatabaseDatasources,
  createDatabaseDatasource,
  getDatabaseDatasource,
  updateDatabaseDatasource,
  deleteDatabaseDatasource,
  testDatabaseConnection,
  getDatabaseSchema,
  formatConnectionStatus,
  getConnectionStatusColor,
  formatDatabaseType,
  type DatabaseDatasource,
  type DatabaseDatasourceCreate,
  type DatabaseDatasourceUpdate,
  type DatabaseDatasourceListResponse,
  type ConnectionTestResponse,
  type DatabaseTable,
  type DatabaseSchemaResponse
} from "./database-datasource";

// Export types
export type {
  DatabaseDatasource,
  DatabaseDatasourceCreate,
  DatabaseDatasourceUpdate,
  DatabaseDatasourceListResponse,
  ConnectionTestResponse,
  DatabaseTable,
  DatabaseSchemaResponse
};

// Database API object for compatibility with existing code
export const databaseApi = {
  // Datasource management
  getDatasources: listDatabaseDatasources,
  createDatasource: createDatabaseDatasource,
  getDatasource: getDatabaseDatasource,
  updateDatasource: updateDatabaseDatasource,
  deleteDatasource: deleteDatabaseDatasource,
  
  // Connection testing
  testConnection: testDatabaseConnection,
  
  // Schema operations
  getSchema: getDatabaseSchema,
  
  // Utility functions
  formatConnectionStatus,
  getConnectionStatusColor,
  formatDatabaseType
};

// Export individual functions for direct import
export {
  listDatabaseDatasources as getDatasources,
  createDatabaseDatasource as createDatasource,
  getDatabaseDatasource as getDatasource,
  updateDatabaseDatasource as updateDatasource,
  deleteDatabaseDatasource as deleteDatasource,
  testDatabaseConnection as testConnection,
  getDatabaseSchema as getSchema,
  formatConnectionStatus,
  getConnectionStatusColor,
  formatDatabaseType
};
