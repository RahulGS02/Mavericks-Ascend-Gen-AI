"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Users,
  FileText,
  CheckCircle,
  Clock,
  Search,
  UserPlus,
  TrendingUp,
  Briefcase,
  ArrowRight,
  XCircle,
  Building2,
  Target,
  AlertCircle
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import { useAuthStore } from '@/store/authStore';
import DashboardLayout from '@/components/DashboardLayout';

interface ManagerStats {
  total_requests: number;
  pending_requests: number;
  approved_requests: number;
  rejected_requests: number;
  active_team_size: number;
  available_talent_count: number;
}

interface DashboardData {
  stats: ManagerStats;
  recent_requests: any[];
  active_team: any[];
  welcome_message: string;
}

export default function ManagerDashboard() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'manager') {
      router.push('/login');
      return;
    }
    fetchDashboardData();
  }, [isAuthenticated, user]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/manager/dashboard/overview');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard:', error);
      toast.error('Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case 'PENDING':
        return 'bg-yellow-100 text-yellow-800';
      case 'APPROVED':
        return 'bg-green-100 text-green-800';
      case 'REJECTED':
        return 'bg-red-100 text-red-800';
      case 'ACTIVE':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div>
            <p className="mt-4 text-gray-600">Loading dashboard...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!dashboardData) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="text-center text-gray-500">No data available</div>
        </div>
      </DashboardLayout>
    );
  }

  const stats = dashboardData.stats;

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Manager Dashboard</h1>
          <p className="text-gray-600 mt-2">
            {dashboardData.welcome_message || `Welcome! Manage your team and deployment requests.`}
          </p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-lg bg-blue-50">
                <FileText className="w-6 h-6 text-blue-600" />
              </div>
              <TrendingUp className="w-5 h-5 text-gray-400" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-1">{stats.total_requests}</h3>
            <p className="text-sm font-medium text-gray-700 mb-1">Total Requests</p>
            <p className="text-xs text-gray-500">All deployment requests</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-lg bg-yellow-50">
                <Clock className="w-6 h-6 text-yellow-600" />
              </div>
              <span className="text-sm text-gray-500">Pending</span>
            </div>
            <h3 className="text-2xl font-bold text-yellow-600 mb-1">{stats.pending_requests}</h3>
            <p className="text-sm font-medium text-gray-700 mb-1">Awaiting Review</p>
            <p className="text-xs text-gray-500">Requests under review</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-lg bg-green-50">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <span className="text-sm text-gray-500">Approved</span>
            </div>
            <h3 className="text-2xl font-bold text-green-600 mb-1">{stats.approved_requests}</h3>
            <p className="text-sm font-medium text-gray-700 mb-1">Approved Requests</p>
            <p className="text-xs text-gray-500">Ready for deployment</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-lg bg-red-50">
                <XCircle className="w-6 h-6 text-red-600" />
              </div>
              <span className="text-sm text-gray-500">Rejected</span>
            </div>
            <h3 className="text-2xl font-bold text-red-600 mb-1">{stats.rejected_requests}</h3>
            <p className="text-sm font-medium text-gray-700 mb-1">Rejected Requests</p>
            <p className="text-xs text-gray-500">Need revision</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-lg bg-purple-50">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
              <Building2 className="w-5 h-5 text-gray-400" />
            </div>
            <h3 className="text-2xl font-bold text-purple-600 mb-1">{stats.active_team_size}</h3>
            <p className="text-sm font-medium text-gray-700 mb-1">Active Team Size</p>
            <p className="text-xs text-gray-500">Currently working</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-lg bg-indigo-50">
                <UserPlus className="w-6 h-6 text-indigo-600" />
              </div>
              <Target className="w-5 h-5 text-gray-400" />
            </div>
            <h3 className="text-2xl font-bold text-indigo-600 mb-1">{stats.available_talent_count}</h3>
            <p className="text-sm font-medium text-gray-700 mb-1">Available Talent</p>
            <p className="text-xs text-gray-500">Ready to deploy</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <button
              onClick={() => router.push('/manager/search')}
              className="bg-white rounded-lg shadow-sm border-2 border-gray-200 p-6 text-left hover:shadow-md transition-all hover:border-blue-300"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="p-2 rounded-lg bg-blue-50">
                  <Search className="w-5 h-5 text-blue-600" />
                </div>
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">Search Talent</h3>
              <p className="text-sm text-gray-600 mb-3">Find skilled candidates for your projects</p>
              <div className="flex items-center text-sm text-blue-600 font-medium">
                Start Searching
                <ArrowRight className="w-4 h-4 ml-1" />
              </div>
            </button>

            <button
              onClick={() => router.push('/deployments/requests')}
              className="bg-white rounded-lg shadow-sm border-2 border-gray-200 p-6 text-left hover:shadow-md transition-all hover:border-green-300"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="p-2 rounded-lg bg-green-50">
                  <FileText className="w-5 h-5 text-green-600" />
                </div>
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">New Request</h3>
              <p className="text-sm text-gray-600 mb-3">Create a new deployment request</p>
              <div className="flex items-center text-sm text-green-600 font-medium">
                Create Request
                <ArrowRight className="w-4 h-4 ml-1" />
              </div>
            </button>

            <button
              onClick={() => router.push('/deployments/requests')}
              className="bg-white rounded-lg shadow-sm border-2 border-gray-200 p-6 text-left hover:shadow-md transition-all hover:border-purple-300"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="p-2 rounded-lg bg-purple-50">
                  <Briefcase className="w-5 h-5 text-purple-600" />
                </div>
                {stats.pending_requests > 0 && (
                  <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-bold rounded-full">
                    {stats.pending_requests}
                  </span>
                )}
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">My Requests</h3>
              <p className="text-sm text-gray-600 mb-3">Track your deployment requests</p>
              <div className="flex items-center text-sm text-purple-600 font-medium">
                View Requests
                <ArrowRight className="w-4 h-4 ml-1" />
              </div>
            </button>

            <button
              onClick={() => router.push('/manager/team')}
              className="bg-white rounded-lg shadow-sm border-2 border-gray-200 p-6 text-left hover:shadow-md transition-all hover:border-orange-300"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="p-2 rounded-lg bg-orange-50">
                  <Users className="w-5 h-5 text-orange-600" />
                </div>
                {stats.active_team_size > 0 && (
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-bold rounded-full">
                    {stats.active_team_size}
                  </span>
                )}
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">My Team</h3>
              <p className="text-sm text-gray-600 mb-3">Manage your active team members</p>
              <div className="flex items-center text-sm text-orange-600 font-medium">
                View Team
                <ArrowRight className="w-4 h-4 ml-1" />
              </div>
            </button>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Requests */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Recent Requests</h2>
              <button
                onClick={() => router.push('/deployments/requests')}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center"
              >
                View All
                <ArrowRight className="w-4 h-4 ml-1" />
              </button>
            </div>

            {dashboardData.recent_requests.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 mb-2">No deployment requests yet</p>
                <p className="text-sm text-gray-400 mb-4">Create your first deployment request to get started</p>
                <button
                  onClick={() => router.push('/manager/search')}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Search Talent
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {dashboardData.recent_requests.slice(0, 5).map((req: any) => (
                  <div
                    key={req.id}
                    className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-all cursor-pointer"
                    onClick={() => router.push('/deployments/requests')}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-gray-900">{req.role_title || 'Untitled Request'}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(req.status)}`}>
                        {req.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      <Building2 className="w-4 h-4 inline mr-1" />
                      {req.project_name || 'No project specified'}
                    </p>
                    {req.required_skills && req.required_skills.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {req.required_skills.slice(0, 4).map((skill: string, idx: number) => (
                          <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded font-medium">
                            {skill}
                          </span>
                        ))}
                        {req.required_skills.length > 4 && (
                          <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded font-medium">
                            +{req.required_skills.length - 4}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Active Team */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Active Team Members</h2>
              <button
                onClick={() => router.push('/manager/team')}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center"
              >
                View All
                <ArrowRight className="w-4 h-4 ml-1" />
              </button>
            </div>

            {dashboardData.active_team.length === 0 ? (
              <div className="text-center py-12">
                <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 mb-2">No active team members yet</p>
                <p className="text-sm text-gray-400 mb-4">Team members will appear here once requests are approved</p>
                <button
                  onClick={() => router.push('/manager/search')}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Find Talent
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {dashboardData.active_team.slice(0, 5).map((member: any) => (
                  <div
                    key={member.id}
                    className="border-2 border-gray-200 rounded-lg p-4 hover:border-purple-300 transition-all cursor-pointer"
                    onClick={() => router.push(`/mavericks/${member.maverick_id}`)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                          {member.maverick_name?.charAt(0) || 'M'}
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900">{member.maverick_name || 'Team Member'}</h3>
                          <p className="text-xs text-gray-500">{member.role || member.competency || 'No role specified'}</p>
                        </div>
                      </div>
                      <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                        ACTIVE
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-2">
                      <Briefcase className="w-4 h-4 inline mr-1" />
                      {member.project_name || 'No project assigned'}
                    </p>
                    {member.start_date && (
                      <p className="text-xs text-gray-500 mt-1">
                        Started: {formatDate(member.start_date)}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
