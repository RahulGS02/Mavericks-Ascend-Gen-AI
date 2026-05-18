"use client";

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { ArrowLeft, Building2, Calendar, CheckCircle, XCircle, Clock, User, Briefcase, MapPin, FileText, Users } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';

interface DeploymentRequestDetail {
  id: string;
  maverick_id?: string;
  maverick_name?: string;
  role_title: string;
  role_description?: string;
  required_skills: string[];
  preferred_skills: string[];
  project_name?: string;
  vertical?: string;
  competency?: string;
  justification?: string;
  requested_by: string;
  requested_by_name?: string;
  approved_by?: string;
  approved_at?: string;
  rejection_reason?: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  created_at: string;
  updated_at: string;
}

export default function DeploymentDetailPage() {
  const router = useRouter();
  const params = useParams();
  const [deployment, setDeployment] = useState<DeploymentRequestDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      fetchDeploymentDetail();
    }
  }, [params.id]);

  const fetchDeploymentDetail = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get(`/deployments/requests/${params.id}`);
      setDeployment(response.data);
    } catch (error) {
      console.error('Failed to fetch deployment details:', error);
      toast.error('Failed to load deployment details');
      router.push('/deployments');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PENDING':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
            <Clock className="w-4 h-4 mr-1" />
            Pending Review
          </span>
        );
      case 'APPROVED':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
            <CheckCircle className="w-4 h-4 mr-1" />
            Approved
          </span>
        );
      case 'REJECTED':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
            <XCircle className="w-4 h-4 mr-1" />
            Rejected
          </span>
        );
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!deployment) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="text-center">
            <p className="text-gray-600">Deployment request not found</p>
            <button
              onClick={() => router.push('/deployments')}
              className="mt-4 text-blue-600 hover:text-blue-800"
            >
              Back to Deployments
            </button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6 max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.push('/deployments')}
            className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Deployments
          </button>
          
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-blue-900 mb-2">{deployment.role_title}</h1>
              <div className="flex items-center gap-3 text-sm text-gray-600">
                <span className="flex items-center">
                  <Calendar className="w-4 h-4 mr-1" />
                  Created {new Date(deployment.created_at).toLocaleDateString()}
                </span>
                <span>•</span>
                <span className="flex items-center">
                  <User className="w-4 h-4 mr-1" />
                  Requested by {deployment.requested_by_name || 'Unknown'}
                </span>
              </div>
            </div>
            <div>
              {getStatusBadge(deployment.status)}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content - 2 columns */}
          <div className="lg:col-span-2 space-y-6">
            {/* Role Description */}
            {deployment.role_description && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-blue-600" />
                  Role Description
                </h2>
                <p className="text-gray-700 whitespace-pre-line">{deployment.role_description}</p>
              </div>
            )}

            {/* Required Skills */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">Required Skills</h2>
              <div className="flex flex-wrap gap-2">
                {deployment.required_skills && deployment.required_skills.length > 0 ? (
                  deployment.required_skills.map((skill, idx) => (
                    <span key={idx} className="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-red-100 text-red-800">
                      {skill}
                    </span>
                  ))
                ) : (
                  <span className="text-gray-500">No required skills specified</span>
                )}
              </div>
            </div>

            {/* Preferred Skills */}
            {deployment.preferred_skills && deployment.preferred_skills.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-3">Preferred Skills</h2>
                <div className="flex flex-wrap gap-2">
                  {deployment.preferred_skills.map((skill, idx) => (
                    <span key={idx} className="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Justification */}
            {deployment.justification && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-3">Justification</h2>
                <p className="text-gray-700 whitespace-pre-line">{deployment.justification}</p>
              </div>
            )}

            {/* Rejection Reason */}
            {deployment.status === 'REJECTED' && deployment.rejection_reason && (
              <div className="bg-red-50 rounded-lg border border-red-200 p-6">
                <h2 className="text-lg font-semibold text-red-900 mb-3 flex items-center">
                  <XCircle className="w-5 h-5 mr-2" />
                  Rejection Reason
                </h2>
                <p className="text-red-700">{deployment.rejection_reason}</p>
              </div>
            )}
          </div>

          {/* Sidebar - 1 column */}
          <div className="space-y-6">
            {/* Assignment Status */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-4">Assignment</h3>
              {deployment.maverick_name ? (
                <div className="flex items-center">
                  <div className="flex-shrink-0 h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
                    <Users className="w-5 h-5 text-green-600" />
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">{deployment.maverick_name}</p>
                    <p className="text-xs text-gray-500">Assigned Maverick</p>
                  </div>
                </div>
              ) : (
                <div className="bg-yellow-50 rounded-lg p-3 border border-yellow-200">
                  <p className="text-sm text-yellow-800 font-medium">Not assigned</p>
                  <p className="text-xs text-yellow-600 mt-1">No maverick assigned yet</p>
                </div>
              )}
            </div>

            {/* Project Details */}
            {deployment.project_name && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-4">Project Details</h3>
                <div className="space-y-3">
                  <div className="flex items-start">
                    <Building2 className="w-4 h-4 text-gray-400 mt-0.5 mr-2" />
                    <div>
                      <p className="text-xs text-gray-500">Project</p>
                      <p className="text-sm font-medium text-gray-900">{deployment.project_name}</p>
                    </div>
                  </div>
                  {deployment.vertical && (
                    <div className="flex items-start">
                      <Briefcase className="w-4 h-4 text-gray-400 mt-0.5 mr-2" />
                      <div>
                        <p className="text-xs text-gray-500">Vertical</p>
                        <p className="text-sm font-medium text-gray-900">{deployment.vertical}</p>
                      </div>
                    </div>
                  )}
                  {deployment.competency && (
                    <div className="flex items-start">
                      <MapPin className="w-4 h-4 text-gray-400 mt-0.5 mr-2" />
                      <div>
                        <p className="text-xs text-gray-500">Competency</p>
                        <p className="text-sm font-medium text-gray-900">{deployment.competency}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Approval Info */}
            {deployment.status === 'APPROVED' && deployment.approved_at && (
              <div className="bg-green-50 rounded-lg border border-green-200 p-6">
                <h3 className="text-sm font-semibold text-green-900 mb-3 flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Approved
                </h3>
                <p className="text-sm text-green-700">
                  Approved on {new Date(deployment.approved_at).toLocaleDateString()}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
