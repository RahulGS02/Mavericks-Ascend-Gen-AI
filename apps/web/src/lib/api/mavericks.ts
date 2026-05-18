/**
 * Maverick API Client
 * Handles all maverick-related API calls
 */

import { apiClient } from './client';

export interface MaverickProfile {
  id?: string;
  name: string;
  email: string;
  college: string;
  degree: string;
  branch: string;
  graduation_year: number;
  cgpa: number;
  phone: string;
  github_url?: string;
  linkedin_url?: string;
  resume_url?: string;
  skills?: string[];
  ai_extracted_skills?: Record<string, any>;
  ai_summary?: string;
  profile_status: 'DRAFT' | 'SUBMITTED' | 'UNDER_REVIEW' | 'APPROVED' | 'REJECTED';
  review_notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ResumeUploadResponse {
  id: string;
  resume_url?: string;
  ai_extracted_skills?: string[];
  ai_summary?: string;
  ai_resume_data?: any;
  profile_status: string;
  [key: string]: any; // Allow other fields from MaverickResponse
}

class MaverickAPI {
  /**
   * Register maverick with profile (Public - No auth required)
   */
  async registerMaverickWithProfile(data: {
    name: string;
    email: string;
    password: string;
    phone: string;
    college: string;
    degree: string;
    branch: string;
    graduation_year: number;
    cgpa: number;
    skills: string;
    github_url?: string;
    linkedin_url?: string;
  }): Promise<{
    message: string;
    access_token: string;
    token_type: string;
    user: any;
    maverick_id: string;
    profile_status: string;
  }> {
    // Debug: Log the API base URL
    console.log('🔍 API Base URL:', apiClient.defaults.baseURL);
    console.log('🔍 Environment Variable:', process.env.NEXT_PUBLIC_API_URL);

    // Convert to FormData
    const formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        formData.append(key, value.toString());
      }
    });

    console.log('🔍 Calling endpoint: /mavericks/register');
    console.log('🔍 Full URL will be:', apiClient.defaults.baseURL + '/mavericks/register');

    const response = await apiClient.post('/mavericks/register', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * Create a new maverick profile (HR only)
   */
  async createProfile(data: Partial<MaverickProfile>): Promise<MaverickProfile> {
    const response = await apiClient.post('/mavericks/', data);
    return response.data;
  }

  /**
   * Get maverick profile by ID
   */
  async getProfile(id: string): Promise<MaverickProfile> {
    const response = await apiClient.get(`/mavericks/${id}`);
    return response.data;
  }

  /**
   * Get current user's maverick profile
   */
  async getMyProfile(): Promise<MaverickProfile> {
    const response = await apiClient.get('/mavericks/me');
    return response.data;
  }

  /**
   * Update maverick profile
   */
  async updateProfile(id: string, data: Partial<MaverickProfile>): Promise<MaverickProfile> {
    const response = await apiClient.put(`/mavericks/${id}`, data);
    return response.data;
  }

  /**
   * Upload resume (updates maverick profile with resume)
   */
  async uploadResume(file: File): Promise<ResumeUploadResponse> {
    const formData = new FormData();
    formData.append('resume', file);  // Changed from 'file' to 'resume'

    // IMPORTANT: Manually get token from localStorage and set Authorization header
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('No authentication token found. Please login again.');
    }

    console.log('🔑 Using token for upload:', token.substring(0, 20) + '...');

    const response = await apiClient.patch('/mavericks/my-profile', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${token}`,  // Explicitly set the token
      },
    });
    return response.data;
  }

  /**
   * Submit profile for review
   */
  async submitProfile(id: string): Promise<MaverickProfile> {
    const response = await apiClient.post(`/mavericks/${id}/submit`);
    return response.data;
  }

  /**
   * Parse resume with AI
   */
  async parseResume(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/resume-parser/parse', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * Get all mavericks (for HR)
   */
  async getAllMavericks(params?: {
    skip?: number;
    limit?: number;
    status?: string;
  }): Promise<{ mavericks: MaverickProfile[]; total: number }> {
    const response = await apiClient.get('/mavericks/', { params });
    return response.data;
  }
}

export const maverickAPI = new MaverickAPI();
