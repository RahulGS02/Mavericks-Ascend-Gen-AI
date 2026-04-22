// Shared TypeScript types between frontend and backend

export type UserRole = 'maverick' | 'trainer' | 'hr' | 'manager' | 'super_admin';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  isActive: boolean;
  createdAt: string;
  lastLogin?: string;
}

export interface Maverick {
  id: string;
  userId: string;
  college: string;
  degree: string;
  graduationYear: number;
  phone?: string;
  resumeUrl?: string;
  skills: string[];
  aiExtractedSkills?: string[];
  aiSummary?: string;
  profileStatus: 'pending_review' | 'shortlisted' | 'rejected' | 'assigned';
  deploymentStatus: 'in_training' | 'ready_for_deployment' | 'deployed';
}

export interface Pipeline {
  id: string;
  name: string;
  description?: string;
  createdBy: string;
  createdAt: string;
  isTemplate: boolean;
  status: string;
}

export interface PipelineJob {
  id: string;
  pipelineId: string;
  jobName: string;
  jobType: 'training' | 'assessment' | 'deployment';
  sequenceOrder: number;
  isMandatory: boolean;
  durationDays: number;
  description?: string;
  metadata?: Record<string, any>;
}

export interface Batch {
  id: string;
  name: string;
  pipelineId: string;
  startDate: string;
  expectedEndDate: string;
  trainerId?: string;
  status: 'active' | 'completed' | 'on_hold';
}

export interface Assessment {
  id: string;
  jobId: string;
  maverickId: string;
  batchId: string;
  attemptNumber: number;
  marksObtained: number;
  maxMarks: number;
  passed: boolean;
  assessedOn: string;
  assessedBy: string;
}

export interface Deployment {
  id: string;
  maverickId: string;
  batchId: string;
  projectName: string;
  vertical: string;
  competency: string;
  roleTitle: string;
  deploymentDate: string;
  deployedBy: string;
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}
