/**
 * Text2SQL API client for Olight
 *
 * Provides TypeScript interfaces and API functions for Text2SQL functionality
 * including SQL generation, training data management, and real-time monitoring.
 */

import { resolveServiceURL } from "./resolve-service-url";

// Types and Interfaces
export interface SQLGenerationRequest {
  datasource_id: number;
  question: string;
  include_explanation?: boolean;
  embedding_model_id?: number;
}

export interface SQLGenerationResponse {
  query_id: number;
  question: string;
  generated_sql: string;
  explanation?: string;
  confidence_score: number;
  similar_examples: Array<{ query: string; usage_count: number }>;
  generation_time_ms: number;
}

export interface SQLExecutionRequest {
  query_id: number;
  limit?: number;
}

export interface SQLExecutionResponse {
  query_id: number;
  status: 'PENDING' | 'SUCCESS' | 'FAILED';
  result_data?: Array<Record<string, any>>;
  result_rows?: number;
  execution_time_ms?: number;
  error_message?: string;
}

export interface TrainingDataRequest {
  datasource_id: number;
  content_type: 'SQL' | 'SCHEMA' | 'DOCUMENTATION' | 'DDL';
  content: string;
  question?: string;
  sql_query?: string;
  table_names?: string[];
  database_schema?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface TrainingDataResponse {
  id: number;
  datasource_id: number;
  content_type: string;
  question?: string;
  sql_query?: string;
  content: string;
  table_names?: string[];
  database_schema?: Record<string, any>;
  metadata?: Record<string, any>;
  content_hash: string;
  is_active: boolean;
  is_validated: boolean;
  validation_score?: number;
  created_at: string;
  updated_at: string;
}

export interface QueryHistory {
  id: number;
  user_question: string;
  generated_sql: string;
  datasource_id: number;
  status: string;
  execution_time_ms?: number;
  result_rows?: number;
  confidence_score?: number;
  model_used?: string;
  explanation?: string;
  created_at: string;
}

export interface TrainingSession {
  id: number;
  datasource_id: number;
  session_name?: string;
  model_version?: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  training_data_count?: number;
  accuracy_score?: number;
  validation_score?: number;
  training_time_seconds?: number;
  started_at: string;
  completed_at?: string;
  notes?: string;
}

export interface Text2SQLStatistics {
  total_queries: number;
  successful_queries: number;
  failed_queries: number;
  average_confidence?: number;
  total_training_data: number;
  training_data_by_type: Record<string, number>;
  last_query_time?: string;
  last_training_time?: string;
}

// Advanced Features Types
export interface QuestionAnswerRequest {
  question: string;
  datasource_id: number;
  execute_sql?: boolean;
  format_result?: boolean;
  include_explanation?: boolean;
  embedding_model_id?: number;
}

export interface QuestionAnswerResponse {
  question: string;
  generated_sql: string;
  explanation?: string;
  confidence_score: number;
  execution_result?: SQLExecutionResponse;
  formatted_answer?: string;
  generation_time_ms: number;
}

export interface SQLPair {
  question: string;
  sql: string;
  explanation?: string;
}

export interface BatchTrainingRequest {
  datasource_id: number;
  database_name?: string;
  sql_pairs: SQLPair[];
  embedding_model_id?: number;
  overwrite_existing?: boolean;
}

export interface BatchTrainingResponse {
  added_count: number;
  skipped_count: number;
  total_pairs: number;
  errors: string[];
  success_rate: number;
}

export interface WebSocketMessage {
  type: 'training_progress' | 'training_completed' | 'training_failed' | 'query_execution' | 'system_status' | 'error';
  datasource_id?: number;
  session_id?: number;
  task_id?: string;
  progress?: number;
  message?: string;
  details?: Record<string, any>;
  timestamp: string;
}

// API Functions
const API_BASE = 'text2sql';

export const text2sqlApi = {
  // SQL Generation and Execution
  async generateSQL(request: SQLGenerationRequest): Promise<SQLGenerationResponse> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/generate`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to generate SQL');
    }

    return response.json();
  },

  async executeSQL(request: SQLExecutionRequest): Promise<SQLExecutionResponse> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/execute`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to execute SQL');
    }

    return response.json();
  },

  // Query History
  async getQueryHistory(params: {
    datasource_id?: number;
    status?: string;
    limit?: number;
    offset?: number;
  } = {}): Promise<{ queries: QueryHistory[]; total: number; limit: number; offset: number }> {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, value.toString());
      }
    });
    
    const response = await fetch(resolveServiceURL(`${API_BASE}/history?${searchParams}`));

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get query history');
    }

    return response.json();
  },

  // Training Data Management
  async addTrainingData(request: TrainingDataRequest): Promise<TrainingDataResponse> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/training`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to add training data');
    }

    return response.json();
  },

  async getTrainingData(params: {
    datasource_id?: number;
    content_type?: string;
    is_active?: boolean;
    limit?: number;
    offset?: number;
  } = {}): Promise<{ training_data: TrainingDataResponse[]; total: number; limit: number; offset: number }> {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, value.toString());
      }
    });
    
    const response = await fetch(resolveServiceURL(`${API_BASE}/training?${searchParams}`));

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get training data');
    }

    return response.json();
  },

  async updateTrainingData(trainingId: number, request: TrainingDataRequest): Promise<TrainingDataResponse> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/training/${trainingId}`), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update training data');
    }

    return response.json();
  },

  async deleteTrainingData(trainingId: number, softDelete: boolean = true): Promise<void> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/training/${trainingId}?soft_delete=${softDelete}`), {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete training data');
    }
  },

  // Training Sessions and Model Management
  async retrainModel(datasourceId: number, forceRebuild: boolean = false): Promise<{ task_id: string; message: string }> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/retrain/${datasourceId}?force_rebuild=${forceRebuild}`), {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to start retraining');
    }

    return response.json();
  },

  async startTrainingSession(request: {
    datasource_id: number;
    session_name?: string;
    model_version?: string;
    training_parameters?: Record<string, any>;
    notes?: string;
  }): Promise<{ session_id: number; task_id: string; status: string }> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/training-session`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to start training session');
    }

    return response.json();
  },

  async getTrainingSessions(params: {
    datasource_id?: number;
    limit?: number;
    offset?: number;
  } = {}): Promise<{ sessions: TrainingSession[]; total: number; limit: number; offset: number }> {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, value.toString());
      }
    });
    
    const response = await fetch(resolveServiceURL(`${API_BASE}/training-sessions?${searchParams}`));

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get training sessions');
    }

    return response.json();
  },

  async getTrainingSessionStatus(sessionId: number): Promise<TrainingSession> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/training-session/${sessionId}`));

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get training session status');
    }

    return response.json();
  },

  // Statistics and Utilities
  async getStatistics(datasourceId?: number): Promise<Text2SQLStatistics> {
    const params = datasourceId ? `?datasource_id=${datasourceId}` : '';
    const response = await fetch(resolveServiceURL(`${API_BASE}/statistics${params}`));

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get statistics');
    }

    return response.json();
  },

  async getTrainingSummary(datasourceId: number): Promise<{
    total_items: number;
    total_validated: number;
    by_type: Record<string, { count: number; validated_count: number; avg_validation_score?: number }>;
  }> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/datasource/${datasourceId}/training-summary`));

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get training summary');
    }

    return response.json();
  },

  async generateEmbeddings(request: {
    datasource_id: number;
    training_data_ids?: number[];
  }): Promise<{ task_id: string; status: string; success: boolean; message?: string }> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/generate-embeddings`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to start embedding generation');
    }

    return response.json();
  },

  async cleanupOldData(daysToKeep: number = 30): Promise<{ task_id: string; status: string }> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/cleanup`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ days_to_keep: daysToKeep }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to start cleanup');
    }

    return response.json();
  },

  // WebSocket Connection
  createWebSocket(datasourceId: number): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // For WebSocket, we need to construct the URL differently
    const baseUrl = resolveServiceURL(`${API_BASE}/ws/${datasourceId}`);
    const wsUrl = baseUrl.replace(/^http/, 'ws');
    return new WebSocket(wsUrl);
  },

  // Advanced Features - Question Answer Mode
  async answerQuestion(request: QuestionAnswerRequest): Promise<QuestionAnswerResponse> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/answer`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to answer question');
    }

    return response.json();
  },

  async batchTrainSQLPairs(request: BatchTrainingRequest): Promise<BatchTrainingResponse> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/batch-train`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to batch train SQL pairs');
    }

    return response.json();
  },

  // DDL Training
  async trainDDL(datasourceId: number, request: {
    auto_extract?: boolean;
    database_name?: string;
    ddl_content?: string;
    embedding_model_id?: number;
    skip_existing?: boolean;
  }): Promise<{
    success: boolean;
    message?: string;
    error?: string;
    total_items?: number;
    successful_items?: number;
    failed_items?: number;
    training_time?: number;
    details?: any[];
  }> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/train-ddl`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ datasource_id: datasourceId, ...request }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to train DDL');
    }

    return response.json();
  },

  // Documentation Training
  async trainDocumentation(datasourceId: number, request: {
    documentation: string;
    doc_type: 'business' | 'technical' | 'api' | 'other';
    embedding_model_id?: number;
    metadata?: Record<string, any>;
  }): Promise<{
    success: boolean;
    message?: string;
    error?: string;
    total?: number;
    successful?: number;
    failed?: number;
  }> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/train-documentation`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ datasource_id: datasourceId, ...request }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to train documentation');
    }

    return response.json();
  },

  // SQL Training
  async trainSQL(datasourceId: number, request: {
    sql_pairs: Array<{ question: string; sql: string }>;
    embedding_model_id?: number;
  }): Promise<{
    success: boolean;
    message?: string;
    error?: string;
    total?: number;
    successful?: number;
    failed?: number;
  }> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/train-sql`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ datasource_id: datasourceId, ...request }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to train SQL');
    }

    return response.json();
  },

  // Health Check
  async healthCheck(): Promise<{ status: string; service: string; timestamp: string }> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/health`));

    if (!response.ok) {
      throw new Error('Text2SQL service is not healthy');
    }

    return response.json();
  },
};
