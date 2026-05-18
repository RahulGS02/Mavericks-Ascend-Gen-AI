/**
 * Batch API Client
 * Handles all batch-related API calls
 */

import { apiClient } from './client';

export interface Batch {
  id: string;
  name: string;
  description?: string;
  pipeline_id: string;
  category?: string;
  focus_areas?: string[];
  required_skills?: string[];
  preferred_skills?: string[];
  target_role?: string;
  start_date: string;
  end_date: string;
  max_capacity: number;
  current_enrollment: number;
  trainer_id?: string;
  created_by: string;
  status: 'DRAFT' | 'ACTIVE' | 'COMPLETED' | 'CANCELLED';
  created_at: string;
  updated_at: string;
}

export interface BatchListResponse {
  batches: Batch[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

class BatchAPI {
  /**
   * Get all active batches
   */
  async getActiveBatches(params?: {
    page?: number;
    page_size?: number;
  }): Promise<BatchListResponse> {
    const response = await apiClient.get('/batches/', {
      params: { ...params, status: 'ACTIVE' }
    });
    return response.data;
  }

  /**
   * Get all batches with filters
   */
  async getAllBatches(params?: {
    page?: number;
    page_size?: number;
    status?: string;
    search?: string;
  }): Promise<BatchListResponse> {
    const response = await apiClient.get('/batches/', { params });
    return response.data;
  }

  /**
   * Get batch by ID
   */
  async getBatchById(id: string): Promise<Batch> {
    const response = await apiClient.get(`/batches/${id}`);
    return response.data;
  }

  /**
   * Get batch with enrolled mavericks
   */
  async getBatchWithMavericks(id: string): Promise<{
    batch: Batch;
    mavericks: any[];
  }> {
    const response = await apiClient.get(`/batches/${id}/mavericks`);
    return response.data;
  }

  /**
   * Assign maverick to batch
   */
  async assignMaverickToBatch(batchId: string, maverickId: string, notes?: string): Promise<any> {
    const response = await apiClient.post(`/batches/${batchId}/assign`, {
      maverick_id: maverickId,
      notes
    });
    return response.data;
  }

  /**
   * Bulk assign mavericks to batch
   */
  async bulkAssignMavericks(batchId: string, maverickIds: string[]): Promise<any> {
    const response = await apiClient.post(`/batches/${batchId}/bulk-assign`, {
      maverick_ids: maverickIds
    });
    return response.data;
  }
}

export const batchAPI = new BatchAPI();
