/**
 * Resource Discovery API client for DeerFlow
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

export const resourceDiscoveryApi = {
  // 注意：discoverResources 接口已移除
  // 资源发现现在通过智能体工具提供，不再是用户API
  // 请使用智能体工具进行资源发现

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

  // Resource Synchronization
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
