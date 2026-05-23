"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import DashboardLayout from '@/components/DashboardLayout';
import {
  Users, DollarSign, Activity, AlertTriangle,
  Database, Shield, Settings, Clock, TrendingUp
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';

interface SystemStats {
  total_users: number;
  users_by_role: Record<string, number>;
  active_users: number;
  inactive_users: number;
  total_mavericks: number;
  total_batches: number;
  total_deployments: number;
  ai_requests_today: number;
  ai_cost_today: number;
  ai_cost_this_month: number;
  failed_logins_today: number;
  system_uptime_hours: number;
  active_sessions: number;
}

export default function SuperAdminDashboard() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<SystemStats | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (user?.role !== 'super_admin') {
      router.push('/dashboard');
      return;
    }

    fetchDashboardData();
  }, [isAuthenticated, user, router]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/admin/dashboard/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading dashboard...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6 p-6 bg-gray-50 min-h-screen">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-1">Super Admin Dashboard</h1>
            <p className="text-base text-gray-600">System-wide monitoring and performance metrics</p>
          </div>
          <div className="flex gap-3">
            <Link
              href="/admin/settings"
              className="px-4 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-100 shadow hover:shadow-md transition-all flex items-center gap-2 font-medium text-sm"
            >
              <Settings className="w-4 h-4" />
              Settings
            </Link>
          </div>
        </div>

        {/* Top Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {/* Total Users */}
          <div className="bg-white rounded-lg shadow-md p-5 border-l-4 border-blue-500 hover:shadow-lg transition-all">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Total Users</p>
                <p className="text-3xl font-bold text-gray-900 my-2">
                  {stats?.total_users || 0}
                </p>
                <p className="text-sm text-gray-600 mt-2 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                  {stats?.active_users || 0} active
                </p>
              </div>
              <div className="ml-4">
                <div className="p-3 bg-blue-50 rounded-xl">
                  <Users className="w-10 h-10 text-blue-600" />
                </div>
              </div>
            </div>
          </div>

          {/* Total Mavericks */}
          <div className="bg-white rounded-lg shadow-md p-5 border-l-4 border-purple-500 hover:shadow-lg transition-all">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Total Mavericks</p>
                <p className="text-3xl font-bold text-gray-900 my-2">
                  {stats?.total_mavericks || 0}
                </p>
                <p className="text-sm text-gray-600 mt-2">
                  Registered trainees
                </p>
              </div>
              <div className="ml-4">
                <div className="p-3 bg-purple-50 rounded-xl">
                  <Users className="w-10 h-10 text-purple-600" />
                </div>
              </div>
            </div>
          </div>

          {/* AI Cost This Month */}
          <div className="bg-white rounded-lg shadow-md p-5 border-l-4 border-green-500 hover:shadow-lg transition-all">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">AI Cost (Month)</p>
                <p className="text-3xl font-bold text-gray-900 my-2">
                  ${stats?.ai_cost_this_month?.toFixed(2) || '0.00'}
                </p>
                <p className="text-sm text-gray-600 mt-2">
                  ${stats?.ai_cost_today?.toFixed(2) || '0.00'} today
                </p>
              </div>
              <div className="ml-4">
                <div className="p-3 bg-green-50 rounded-xl">
                  <DollarSign className="w-10 h-10 text-green-600" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Organization Performance Goals */}
        <div className="bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 rounded-lg shadow-md p-5 border border-blue-200">
          <h2 className="text-xl font-bold text-gray-900 mb-5 flex items-center gap-2">
            <div className="p-2 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg">
              <TrendingUp className="w-5 h-5 text-white" />
            </div>
            Organization Performance Goals
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {/* Hiring Goal */}
            <div className="bg-white rounded-lg p-4 shadow hover:shadow-md transition-shadow border border-blue-100">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <p className="text-sm font-bold text-gray-700">Hiring Target</p>
                  <p className="text-xs text-gray-500">By Q4 2026</p>
                </div>
                <div className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded-full">
                  Active
                </div>
              </div>
              <div className="mt-3">
                <div className="flex items-baseline gap-2 mb-2">
                  <span className="text-3xl font-bold text-gray-900">{stats?.total_mavericks || 0}</span>
                  <span className="text-lg font-semibold text-gray-400">/ 1000</span>
                </div>
                <div className="mt-3">
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-blue-600 h-2.5 rounded-full transition-all duration-500"
                      style={{width: `${Math.min(((stats?.total_mavericks || 0) / 1000) * 100, 100)}%`}}
                    ></div>
                  </div>
                  <p className="text-xs font-semibold text-gray-600 mt-2">
                    {Math.round(((stats?.total_mavericks || 0) / 1000) * 100)}% Complete
                  </p>
                </div>
              </div>
            </div>

            {/* Deployment Goal */}
            <div className="bg-white rounded-lg p-4 shadow hover:shadow-md transition-shadow border border-green-100">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <p className="text-sm font-bold text-gray-700">Deployment Target</p>
                  <p className="text-xs text-gray-500">By Q4 2026</p>
                </div>
                <div className="px-2 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full">
                  Active
                </div>
              </div>
              <div className="mt-3">
                <div className="flex items-baseline gap-2 mb-2">
                  <span className="text-3xl font-bold text-gray-900">{stats?.total_deployments || 0}</span>
                  <span className="text-lg font-semibold text-gray-400">/ 800</span>
                </div>
                <div className="mt-3">
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className="bg-gradient-to-r from-green-500 to-green-600 h-2.5 rounded-full transition-all duration-500"
                      style={{width: `${Math.min(((stats?.total_deployments || 0) / 800) * 100, 100)}%`}}
                    ></div>
                  </div>
                  <p className="text-xs font-semibold text-gray-600 mt-2">
                    {Math.round(((stats?.total_deployments || 0) / 800) * 100)}% Complete
                  </p>
                </div>
              </div>
            </div>

            {/* Active Batches Goal */}
            <div className="bg-white rounded-lg p-4 shadow hover:shadow-md transition-shadow border border-purple-100">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <p className="text-sm font-bold text-gray-700">Active Batches</p>
                  <p className="text-xs text-gray-500">Current Quarter</p>
                </div>
                <div className="px-2 py-1 bg-purple-100 text-purple-700 text-xs font-bold rounded-full">
                  On Track
                </div>
              </div>
              <div className="mt-3">
                <div className="flex items-baseline gap-2 mb-2">
                  <span className="text-3xl font-bold text-gray-900">{stats?.total_batches || 0}</span>
                  <span className="text-lg font-semibold text-gray-400">/ 50</span>
                </div>
                <div className="mt-3">
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-purple-600 h-2.5 rounded-full transition-all duration-500"
                      style={{width: `${Math.min(((stats?.total_batches || 0) / 50) * 100, 100)}%`}}
                    ></div>
                  </div>
                  <p className="text-xs font-semibold text-gray-600 mt-2">
                    {Math.round(((stats?.total_batches || 0) / 50) * 100)}% Complete
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Users by Role */}
        <div className="bg-white rounded-lg shadow-md p-5">
          <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <div className="p-1.5 bg-blue-100 rounded-lg">
              <Users className="w-4 h-4 text-blue-600" />
            </div>
            Users by Role
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {stats?.users_by_role && Object.entries(stats.users_by_role).map(([role, count]) => (
              <div key={role} className="text-center p-3 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg border border-gray-200 hover:shadow-md hover:border-blue-300 transition-all">
                <p className="text-2xl font-bold text-gray-900 mb-1">{count}</p>
                <p className="text-xs text-gray-600 capitalize font-semibold">{role.replace('_', ' ')}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <Link href="/admin/users" className="group bg-white rounded-lg shadow-md p-5 hover:shadow-lg transition-all border-l-4 border-blue-500">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-gradient-to-br from-blue-100 to-blue-200 rounded-lg group-hover:from-blue-200 group-hover:to-blue-300 transition-all">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-base font-bold text-gray-900 group-hover:text-blue-600 transition-colors mb-1">User Management</h3>
                <p className="text-sm text-gray-600">Manage all system users</p>
              </div>
            </div>
          </Link>

          <Link href="/admin/audit-logs" className="group bg-white rounded-lg shadow-md p-5 hover:shadow-lg transition-all border-l-4 border-purple-500">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-gradient-to-br from-purple-100 to-purple-200 rounded-lg group-hover:from-purple-200 group-hover:to-purple-300 transition-all">
                <Shield className="w-6 h-6 text-purple-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-base font-bold text-gray-900 group-hover:text-purple-600 transition-colors mb-1">Audit Logs</h3>
                <p className="text-sm text-gray-600">View system activity trail</p>
              </div>
            </div>
          </Link>

          <Link href="/admin/ai-analytics" className="group bg-white rounded-lg shadow-md p-5 hover:shadow-lg transition-all border-l-4 border-green-500">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-gradient-to-br from-green-100 to-green-200 rounded-lg group-hover:from-green-200 group-hover:to-green-300 transition-all">
                <DollarSign className="w-6 h-6 text-green-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-base font-bold text-gray-900 group-hover:text-green-600 transition-colors mb-1">AI Analytics</h3>
                <p className="text-sm text-gray-600">Monitor AI costs</p>
              </div>
            </div>
          </Link>
        </div>

        {/* System Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div className="bg-white rounded-lg shadow-md p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Database className="w-5 h-5 text-blue-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">Platform Metrics</h3>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <span className="text-gray-700 font-semibold text-sm">Total Mavericks</span>
                <span className="text-xl font-bold text-gray-900">{stats?.total_mavericks || 0}</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <span className="text-gray-700 font-semibold text-sm">Active Batches</span>
                <span className="text-xl font-bold text-gray-900">{stats?.total_batches || 0}</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <span className="text-gray-700 font-semibold text-sm">Total Deployments</span>
                <span className="text-xl font-bold text-gray-900">{stats?.total_deployments || 0}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-green-100 rounded-lg">
                <Activity className="w-5 h-5 text-green-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">AI Usage & Costs</h3>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <span className="text-gray-700 font-semibold text-sm">Requests Today</span>
                <span className="text-xl font-bold text-gray-900">{stats?.ai_requests_today || 0}</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
                <span className="text-gray-700 font-semibold text-sm">Cost Today</span>
                <span className="text-xl font-bold text-green-700">${stats?.ai_cost_today?.toFixed(2) || '0.00'}</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
                <span className="text-gray-700 font-semibold text-sm">Cost This Month</span>
                <span className="text-xl font-bold text-green-700">${stats?.ai_cost_this_month?.toFixed(2) || '0.00'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
