/**
 * HR Workflow API Client
 * Handles all HR-related API calls for reviewing mavericks
 */

import { apiClient } from './client';

export interface MaverickResponse {
  id: string;
  user_id: string;
  name: string;
  email: string;
  phone?: string;
  college?: string;
  degree?: string;
  branch?: string;
  graduation_year?: number;
  cgpa?: number;
  skills: string[];
  resume_url?: string;
  github_url?: string;
  linkedin_url?: string;
  ai_extracted_skills?: string[];
  ai_summary?: string;
  ai_resume_data?: {
    personal_info?: any;
    education?: any[];
    experience?: any[];
    skills?: any;
    projects?: any[];
    certifications?: any[];
    total_experience_years?: number;
    summary?: string;
  };
  profile_status: 'pending' | 'approved' | 'rejected';
  deployment_status: string;
  current_batch_id?: string;
  reviewed_by?: string;
  review_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface MaverickListResponse {
  mavericks: MaverickResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ReviewResponse {
  success: boolean;
  maverick_id: string;
  new_status: string;
  message: string;
}

export interface BatchListResponse {
  batches: {
    id: string;
    name: string;
    pipeline_id: string;
    start_date: string;
    end_date?: string;
    status: string;
  }[];
  total: number;
}

class HRAPI {
  /**
   * Get pending profiles for review
   */
  async getPendingProfiles(params?: {
    page?: number;
    page_size?: number;
    search?: string;
  }): Promise<MaverickListResponse> {
    const response = await apiClient.get('/hr/pending-profiles', { params });
    return response.data;
  }

  /**
   * Get all mavericks with filters
   */
  async getAllMavericks(params?: {
    page?: number;
    page_size?: number;
    search?: string;
    profile_status?: string;
    deployment_status?: string;
  }): Promise<MaverickListResponse> {
    const response = await apiClient.get('/mavericks/', { params });
    return response.data;
  }

  /**
   * Get maverick by ID
   */
  async getMaverickById(id: string): Promise<MaverickResponse> {
    const response = await apiClient.get(`/mavericks/${id}`);
    return response.data;
  }

  /**
   * Approve (shortlist) a maverick profile
   */
  async approveMaverick(maverickId: string, notes?: string): Promise<ReviewResponse> {
    const response = await apiClient.post(`/hr/shortlist/${maverickId}`, null, {
      params: { notes }
    });
    return response.data;
  }

  /**
   * Reject a maverick profile
   */
  async rejectMaverick(maverickId: string, reason?: string): Promise<ReviewResponse> {
    const response = await apiClient.post(`/hr/reject/${maverickId}`, null, {
      params: { reason }
    });
    return response.data;
  }

  /**
   * Assign maverick to batch
   */
  async assignToBatch(maverickId: string, batchId: string): Promise<any> {
    const response = await apiClient.patch(`/mavericks/${maverickId}`, {
      current_batch_id: batchId
    });
    return response.data;
  }

  /**
   * Get all batches
   */
  async getAllBatches(params?: {
    page?: number;
    page_size?: number;
    status?: string;
  }): Promise<BatchListResponse> {
    const response = await apiClient.get('/batches/', { params });
    return response.data;
  }
}

export const hrAPI = new HRAPI();
