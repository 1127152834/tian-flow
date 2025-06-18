/**
 * Resource Discovery API client for Olight
 *
 * Provides TypeScript interfaces and API functions for Resource Discovery functionality
 * including resource discovery, synchronization, and management.
 */

import { resolveServiceURL } from "./resolve-service-url";

// Types and Interfaces
export interface ResourceDiscoveryRequest {
  user_query: string;
  max_results?: number;
  min_confidence?: number;
  resource_types?: string[];
}

export interface ResourceMatch {
  resource_id: string;
  resource_name: string;
  resource_type: string;
  description?: string;
  capabilities?: string[];
  tags?: string[];
  confidence_score: number;
  similarity_score: number;
  reasoning?: string;
}

export interface ResourceDiscoveryResponse {
  query: string;
  matches: ResourceMatch[];
  total_resources: number;
  processing_time_ms: number;
  timestamp: string;
}

export interface ResourceRegistryResponse {
  id: number;
  resource_id: string;
  resource_name: string;
  resource_type: string;
  description?: string;
  capabilities?: string[];
  tags?: string[];
  metadata?: Record<string, any>;
  is_active: boolean;
  status: string;
  source_table: string;
  source_id: number;
  vectorization_status: string;
  usage_count: number;
  success_rate: number;
  avg_response_time: number;
  vector_updated_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ResourceStatistics {
  resource_statistics: Record<string, {
    total: number;
    active: number;
    vectorized: number;
  }>;
  match_statistics: {
    total_queries: number;
    avg_response_time: number;
    positive_feedback: number;
    negative_feedback: number;
  };
  last_updated: string;
}

export interface SyncResourcesResponse {
  success: boolean;
  message?: string;
  task_id?: string;
  status?: string;
  force_full_sync?: boolean;
}

export interface TaskStatusResponse {
  success: boolean;
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  message: string;
  progress: number;
  current_step?: string;
  total_steps?: number;
  processed_items?: number;
  total_items?: number;
  result?: any;
  error?: string;
}

export interface BatchVectorizationRequest {
  resource_ids: string[];
}

export interface BatchVectorizationResponse {
  success: boolean;
  message?: string;
  task_id?: string;
  total_resources: number;
  successful_resources?: number;
  failed_resources?: number;
  results?: any[];
  total_processing_time_ms?: number;
  timestamp?: string;
  status?: string;
}

export interface SystemStatus {
  id: number;
  operation_type: string;
  status: string;
  total_items?: number;
  successful_items?: number;
  failed_items?: number;
  error_message?: string;
  result_data?: Record<string, any>;
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
  created_at: string;
  updated_at: string;
}

// API Functions
const API_BASE = 'resource-discovery';

// Test Interface Types
export interface ResourceTestRequest {
  query: string;
  top_k?: number;
  min_confidence?: number;
  resource_types?: string[];
}

export interface ResourceTestResult {
  resource_id: string;
  resource_name: string;
  resource_type: string;
  description: string;
  capabilities: string[];
  similarity_score: number;
  confidence_score: number;
  confidence: 'high' | 'medium' | 'low';
  reasoning: string;
  detailed_scores: {
    similarity: number;
    confidence: number;
  };
}

export interface ResourceTestResponse {
  query: string;
  total_matches: number;
  matches: ResourceTestResult[];
  best_match: ResourceTestResult | null;
  processing_time: number;
  parameters: {
    top_k: number;
    min_confidence: number;
    resource_types: string[] | null;
  };
}

export const resourceDiscoveryApi = {
  // Resource Discovery Testing
  async testResourceMatching(request: ResourceTestRequest): Promise<ResourceTestResponse> {
    const response = await fetch(resolveServiceURL(`/api/${API_BASE}/test-match`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: request.query,
        top_k: request.top_k || 5,
        min_confidence: request.min_confidence || 0.1,
        resource_types: request.resource_types || null,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to test resource matching');
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.error || '资源匹配测试失败');
    }

    return result.data;
  },

  // Resource Management
  async getResources(params: {
    resource_type?: string;
    is_active?: boolean;
    vectorization_status?: string;
    skip?: number;
    limit?: number;
  } = {}): Promise<ResourceRegistryResponse[]> {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, value.toString());
      }
    });
    
    const response = await fetch(resolveServiceURL(`${API_BASE}/resources?${searchParams}`));

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get resources');
    }

    return response.json();
  },

  async getResource(resourceId: string): Promise<ResourceRegistryResponse> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/resources/${resourceId}`));

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get resource');
    }

    return response.json();
  },

  // Change Detection
  async detectChanges(previewOnly: boolean = true): Promise<any> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/change-detection?preview_only=${previewOnly}`), {
      method: 'GET',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to detect changes');
    }

    return response.json();
  },

  // Manual Resource Discovery
  async discoverResourcesManual(): Promise<any> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/discover-manual`), {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to discover resources manually');
    }

    return response.json();
  },

  // Incremental Synchronization
  async incrementalSync(forceFullSync: boolean = false, asyncMode: boolean = true): Promise<any> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/incremental-sync?force_full_sync=${forceFullSync}&async_mode=${asyncMode}`), {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to perform incremental sync');
    }

    return response.json();
  },

  // Resource Synchronization (Legacy)
  async syncResources(forceFullSync: boolean = false): Promise<SyncResourcesResponse> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/sync?force_full_sync=${forceFullSync}`), {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to sync resources');
    }

    return response.json();
  },

  // Batch Vectorization
  async vectorizeResources(request: BatchVectorizationRequest): Promise<BatchVectorizationResponse> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/vectorize`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to vectorize resources');
    }

    return response.json();
  },

  // System Status
  async getSystemStatus(params: {
    operation_type?: string;
    status?: string;
    limit?: number;
  } = {}): Promise<SystemStatus[]> {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, value.toString());
      }
    });
    
    const response = await fetch(resolveServiceURL(`${API_BASE}/status?${searchParams}`));

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get system status');
    }

    return response.json();
  },

  // Task Status
  async getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/sync/status/${taskId}`));

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get task status');
    }

    return response.json();
  },

  // Statistics
  async getStatistics(): Promise<ResourceStatistics> {
    const response = await fetch(resolveServiceURL(`${API_BASE}/statistics`));

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get statistics');
    }

    return response.json();
  },
};

export default resourceDiscoveryApi;
