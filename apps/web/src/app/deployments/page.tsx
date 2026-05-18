"use client";

import { useEffect, useState } from 'react';
import { Search, Rocket, CheckCircle, XCircle, Clock, Filter, TrendingUp, Users, Building2, Calendar, Plus, Trash2, Eye } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';
import DeploymentRequestModal from '@/components/deployment/DeploymentRequestModal';

interface DeploymentRequest {
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
  requested_by_name?: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  created_at: string;
}

interface DeploymentStats {
  total_requirements: number;
  pending: number;
  approved: number;
  rejected: number;
}

export default function DeploymentsPage() {
  const router = useRouter();
  const [deployments, setDeployments] = useState<DeploymentRequest[]>([]);
  const [stats, setStats] = useState<DeploymentStats>({
    total_requirements: 0,
    pending: 0,
    approved: 0,
    rejected: 0
  });
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [verticalFilter, setVerticalFilter] = useState<string>('all');
  const [showDeploymentModal, setShowDeploymentModal] = useState(false);

  useEffect(() => {
    fetchDeployments();
    fetchStats();
  }, [searchTerm, statusFilter, verticalFilter]);

  const fetchDeployments = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/deployments/requests', {
        params: {
          page: 1,
          page_size: 100,
          status_filter: statusFilter === 'all' ? undefined : statusFilter,
        }
      });
      setDeployments(response.data?.requests || []);
    } catch (error) {
      console.error('Failed to fetch deployment requests:', error);
      toast.error('Failed to load deployment requests');
      setDeployments([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await apiClient.get('/deployments/requests/statistics');
      setStats(response.data || {
        total_requirements: 0,
        pending: 0,
        approved: 0,
        rejected: 0
      });
    } catch (error) {
      console.error('Failed to fetch deployment statistics:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this deployment request?')) {
      return;
    }

    try {
      await apiClient.delete(`/deployments/requests/${id}`);
      toast.success('Deployment request deleted successfully');
      fetchDeployments();
      fetchStats();
    } catch (error) {
      console.error('Failed to delete deployment request:', error);
      toast.error('Failed to delete deployment request');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'DEPLOYED':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <CheckCircle className="w-3 h-3 mr-1" />
            Deployed
          </span>
        );
      case 'PENDING':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <Clock className="w-3 h-3 mr-1" />
            Pending
          </span>
        );
      case 'APPROVED':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            <CheckCircle className="w-3 h-3 mr-1" />
            Approved
          </span>
        );
      case 'COMPLETED':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
            <CheckCircle className="w-3 h-3 mr-1" />
            Completed
          </span>
        );
      case 'REJECTED':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <XCircle className="w-3 h-3 mr-1" />
            Rejected
          </span>
        );
      default:
        return null;
    }
  };

  const filteredDeployments = deployments.filter(deployment =>
    deployment.maverick_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    deployment.project_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-blue-900 mb-2">Deployment Requirement Cards</h1>
            <p className="text-gray-600">Post role requirements - HR will find suitable mavericks</p>
          </div>
          <button
            onClick={() => setShowDeploymentModal(true)}
            className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
          >
            <Plus className="w-5 h-5 mr-2" />
            Create Requirement Card
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Requirements</p>
                <p className="text-2xl font-bold text-blue-900">{stats.total_requirements}</p>
              </div>
              <Rocket className="w-8 h-8 text-blue-500" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Approved</p>
                <p className="text-2xl font-bold text-green-600">{stats.approved}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Rejected</p>
                <p className="text-2xl font-bold text-red-600">{stats.rejected}</p>
              </div>
              <XCircle className="w-8 h-8 text-red-500" />
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by role title or skills..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="PENDING">Pending</option>
              <option value="APPROVED">Approved</option>
              <option value="REJECTED">Rejected</option>
            </select>
          </div>
        </div>

        {/* Requirement Cards List */}
        {loading ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
            <p className="mt-4 text-gray-600">Loading requirement cards...</p>
          </div>
        ) : filteredDeployments.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center text-gray-500">
            <Rocket className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium">No requirement cards found</p>
            <p className="text-sm mt-2">Click "Create Requirement Card" to post your first role requirement</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Role Title</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Required Skills</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Assigned Maverick</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Requested By</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredDeployments.map((request) => (
                    <tr key={request.id} className="hover:bg-gray-50 transition-colors">
                      {/* Role Title */}
                      <td className="px-6 py-4">
                        <div className="text-sm font-semibold text-gray-900">{request.role_title}</div>
                        {request.project_name && (
                          <div className="text-xs text-gray-500 mt-1">Project: {request.project_name}</div>
                        )}
                      </td>

                      {/* Required Skills */}
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1">
                          {request.required_skills && request.required_skills.length > 0 ? (
                            request.required_skills.slice(0, 3).map((skill, idx) => (
                              <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                {skill}
                              </span>
                            ))
                          ) : (
                            <span className="text-xs text-gray-400">No skills listed</span>
                          )}
                          {request.required_skills && request.required_skills.length > 3 && (
                            <span className="text-xs text-gray-500">+{request.required_skills.length - 3} more</span>
                          )}
                        </div>
                      </td>

                      {/* Assigned Maverick */}
                      <td className="px-6 py-4">
                        {request.maverick_name ? (
                          <div className="flex items-center">
                            <div className="flex-shrink-0 h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                              <Users className="w-4 h-4 text-green-600" />
                            </div>
                            <div className="ml-2 text-sm font-medium text-gray-900">{request.maverick_name}</div>
                          </div>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            Not assigned
                          </span>
                        )}
                      </td>

                      {/* Requested By */}
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">{request.requested_by_name || 'N/A'}</div>
                      </td>

                      {/* Status */}
                      <td className="px-6 py-4">
                        {getStatusBadge(request.status)}
                      </td>

                      {/* Actions */}
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            className="inline-flex items-center px-3 py-1.5 bg-purple-600 text-white text-sm font-medium rounded-md hover:bg-purple-700 transition-colors"
                            onClick={() => router.push(`/deployments/${request.id}/workflow`)}
                          >
                            <Users className="w-4 h-4 mr-1" />
                            Workflow
                          </button>
                          <button
                            className="inline-flex items-center px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
                            onClick={() => router.push(`/deployments/${request.id}`)}
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            View
                          </button>
                          <button
                            className="inline-flex items-center px-3 py-1.5 bg-red-600 text-white text-sm font-medium rounded-md hover:bg-red-700 transition-colors"
                            onClick={() => handleDelete(request.id)}
                          >
                            <Trash2 className="w-4 h-4 mr-1" />
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Deployment Request Modal */}
      {showDeploymentModal && (
        <DeploymentRequestModal
          onClose={() => setShowDeploymentModal(false)}
          onSuccess={() => {
            setShowDeploymentModal(false);
            fetchDeployments();
            fetchStats();
            toast.success('Deployment requirement card created successfully!');
          }}
        />
      )}
    </DashboardLayout>
  );
}