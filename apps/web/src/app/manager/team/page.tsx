"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Users,
  Calendar,
  Briefcase,
  User,
  MapPin,
  Mail,
  Phone,
  Building2,
  TrendingUp,
  ArrowRight,
  Search,
  Target,
  Clock
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import { useAuthStore } from '@/store/authStore';
import DashboardLayout from '@/components/DashboardLayout';

export default function ManagerTeam() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [teamMembers, setTeamMembers] = useState<any[]>([]);

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'manager') {
      router.push('/login');
      return;
    }
    fetchTeam();
  }, [isAuthenticated, user]);

  const fetchTeam = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/manager/dashboard/overview');
      setTeamMembers(response.data.active_team || []);
    } catch (error) {
      console.error('Failed to fetch team:', error);
      toast.error('Failed to load team');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const calculateDuration = (startDate: string) => {
    if (!startDate) return 'N/A';
    const start = new Date(startDate);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - start.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays < 30) return `${diffDays} days`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months`;
    return `${Math.floor(diffDays / 365)} years`;
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div>
            <p className="mt-4 text-gray-600">Loading team...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">My Team</h1>
          <p className="text-gray-600 mt-2">
            Manage and track your deployed team members across projects
          </p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-lg bg-purple-50">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
              <TrendingUp className="w-5 h-5 text-gray-400" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-1">{teamMembers.length}</h3>
            <p className="text-sm font-medium text-gray-700 mb-1">Active Team Members</p>
            <p className="text-xs text-gray-500">Currently deployed</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-lg bg-blue-50">
                <Briefcase className="w-6 h-6 text-blue-600" />
              </div>
              <Building2 className="w-5 h-5 text-gray-400" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-1">
              {new Set(teamMembers.map(m => m.project_name)).size}
            </h3>
            <p className="text-sm font-medium text-gray-700 mb-1">Active Projects</p>
            <p className="text-xs text-gray-500">Ongoing assignments</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-lg bg-green-50">
                <Target className="w-6 h-6 text-green-600" />
              </div>
              <Calendar className="w-5 h-5 text-gray-400" />
            </div>
            <h3 className="text-2xl font-bold text-green-600 mb-1">100%</h3>
            <p className="text-sm font-medium text-gray-700 mb-1">Utilization Rate</p>
            <p className="text-xs text-gray-500">All resources deployed</p>
          </div>
        </div>

        {/* Team Members */}
        {teamMembers.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <Users className="w-20 h-20 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No team members yet</h3>
            <p className="text-gray-500 mb-4">
              Start building your team by searching for qualified candidates and creating deployment requests
            </p>
            <div className="flex gap-3 justify-center">
              <button
                onClick={() => router.push('/manager/search')}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center gap-2"
              >
                <Search className="w-5 h-5" />
                Search Talent
              </button>
              <button
                onClick={() => router.push('/manager/dashboard')}
                className="px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        ) : (
          <div>
            {/* Team Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Team Members</h2>
                <p className="text-sm text-gray-600 mt-1">
                  Managing <span className="font-semibold text-purple-600">{teamMembers.length}</span> active team member{teamMembers.length !== 1 ? 's' : ''}
                </p>
              </div>
              <button
                onClick={() => router.push('/manager/search')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center gap-2"
              >
                <Users className="w-4 h-4" />
                Add Team Member
              </button>
            </div>

            {/* Team Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {teamMembers.map((member) => (
                <div
                  key={member.id}
                  className="bg-white rounded-lg shadow-sm border-2 border-gray-200 p-6 hover:shadow-lg hover:border-purple-300 transition-all cursor-pointer"
                  onClick={() => router.push(`/mavericks/${member.maverick_id}`)}
                >
                  {/* Header with Avatar */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold text-xl shadow-md">
                        {member.maverick_name?.charAt(0) || 'M'}
                      </div>
                      <div>
                        <h3 className="font-bold text-gray-900 text-lg">{member.maverick_name || 'Team Member'}</h3>
                        <p className="text-sm text-gray-600">{member.role || member.competency || 'No role'}</p>
                      </div>
                    </div>
                    <span className="px-3 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full border border-green-300">
                      ACTIVE
                    </span>
                  </div>

                  {/* Project Details */}
                  <div className="space-y-3 mb-4 p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-2 text-sm text-gray-700">
                      <div className="p-1.5 bg-white rounded">
                        <Briefcase className="w-4 h-4 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-medium">{member.project_name || 'No project'}</p>
                        <p className="text-xs text-gray-500">Current Project</p>
                      </div>
                    </div>
                    {member.vertical && (
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <div className="p-1.5 bg-white rounded">
                          <Building2 className="w-4 h-4 text-green-600" />
                        </div>
                        <div>
                          <p className="font-medium">{member.vertical}</p>
                          <p className="text-xs text-gray-500">Vertical</p>
                        </div>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-sm text-gray-700">
                      <div className="p-1.5 bg-white rounded">
                        <Clock className="w-4 h-4 text-purple-600" />
                      </div>
                      <div>
                        <p className="font-medium">{calculateDuration(member.start_date)}</p>
                        <p className="text-xs text-gray-500">Duration on project</p>
                      </div>
                    </div>
                  </div>

                  {/* Timeline */}
                  <div className="pt-3 border-t border-gray-200">
                    <div className="flex items-center justify-between text-xs text-gray-600">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        <span>Started: {formatDate(member.start_date)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        router.push(`/mavericks/${member.maverick_id}`);
                      }}
                      className="w-full px-4 py-2.5 border-2 border-purple-300 text-purple-700 rounded-lg hover:bg-purple-50 transition-all font-medium flex items-center justify-center gap-2"
                    >
                      View Full Profile
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
