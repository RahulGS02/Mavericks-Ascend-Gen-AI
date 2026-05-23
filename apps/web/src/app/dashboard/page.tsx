"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import DashboardLayout from '@/components/DashboardLayout';
import MaverickDistributionPieChart from '@/components/MaverickDistributionPieChart';
import { Users, BookOpen, Briefcase, TrendingUp, AlertTriangle, Inbox, UserX, Loader2, MessageSquare } from 'lucide-react';
import { apiClient } from '@/lib/api/client';

interface DashboardStat {
  label: string;
  value: string | number;
  change: string;
  positive: boolean;
  icon: string;
  actionable: boolean;
  action_url?: string;
  description: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [stats, setStats] = useState<DashboardStat[]>([]);
  const [loading, setLoading] = useState(true);
  const [recentProfiles, setRecentProfiles] = useState<any[]>([]);
  const [pieChartData, setPieChartData] = useState<any>(null);
  const [deploymentRate, setDeploymentRate] = useState<number>(0);
  const [trainerFeedback, setTrainerFeedback] = useState<any[]>([]);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    // Redirect Super Admin to their dedicated dashboard
    if (user?.role === 'super_admin') {
      router.push('/admin/dashboard');
      return;
    }

    if (user?.role === 'hr') {
      fetchHRDashboardData();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated, user, router]);

  const fetchHRDashboardData = async () => {
    try {
      setLoading(true);
      const [statsResponse, activityResponse, feedbackResponse] = await Promise.all([
        apiClient.get('/hr/dashboard/stats'),
        apiClient.get('/hr/dashboard/recent-activity'),
        apiClient.get('/hr/dashboard/trainer-feedback')
      ]);

      setStats(statsResponse.data.stats || []);
      setRecentProfiles(activityResponse.data.recent_profiles || []);
      setPieChartData(statsResponse.data.pie_chart_data || null);
      setDeploymentRate(statsResponse.data.summary?.deployment_rate || 0);
      setTrainerFeedback(feedbackResponse.data.recent_feedback || []);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getIcon = (iconName: string) => {
    const iconMap: Record<string, any> = {
      users: <Users className="w-6 h-6 text-blue-600" />,
      alert: <UserX className="w-6 h-6 text-orange-600" />,
      inbox: <Inbox className="w-6 h-6 text-purple-600" />,
      book: <BookOpen className="w-6 h-6 text-green-600" />,
      trending: <TrendingUp className="w-6 h-6 text-blue-600" />,
      warning: <AlertTriangle className="w-6 h-6 text-red-600" />,
    };
    return iconMap[iconName] || <Users className="w-6 h-6 text-gray-600" />;
  };

  if (!user) {
    return null;
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Page Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-blue-900">HR Dashboard</h1>
          <p className="mt-1 text-sm text-gray-600">
            Welcome back, {user.name}! Monitor and manage your training platform.
          </p>
        </div>

        {/* Top Section: Deployment Rate & Maverick Distribution */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-900" />
          </div>
        ) : (
          <>
            {/* Analytics Overview - Compact Charts */}
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-3 mb-4">
              {/* Deployment Rate - Compact */}
              <div className="bg-white rounded-lg shadow p-4">
                <h3 className="text-sm font-bold text-blue-900 mb-2">Deployment Rate</h3>
                <div className="flex items-center justify-between">
                  <div className="relative w-24 h-24">
                    <svg className="transform -rotate-90 w-24 h-24">
                      <circle
                        cx="48"
                        cy="48"
                        r="42"
                        stroke="#e5e7eb"
                        strokeWidth="8"
                        fill="transparent"
                      />
                      <circle
                        cx="48"
                        cy="48"
                        r="42"
                        stroke="#1e3a8a"
                        strokeWidth="8"
                        fill="transparent"
                        strokeDasharray={`${2 * Math.PI * 42}`}
                        strokeDashoffset={`${2 * Math.PI * 42 * (1 - deploymentRate / 100)}`}
                        strokeLinecap="round"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center flex-col">
                      <span className="text-xl font-bold text-blue-900">{deploymentRate}%</span>
                    </div>
                  </div>
                  <div className="flex-1 ml-4">
                    <p className="text-xs text-gray-600 leading-relaxed">
                      Of mavericks who completed training have been successfully deployed
                    </p>
                  </div>
                </div>
              </div>

              {/* Maverick Distribution Pie Chart - Compact */}
              <div className="bg-white rounded-lg shadow p-4 lg:col-span-2">
                <h3 className="text-sm font-bold text-blue-900 mb-2">Maverick Distribution</h3>
                {pieChartData ? (
                  <MaverickDistributionPieChart data={pieChartData} compact={true} />
                ) : (
                  <div className="flex items-center justify-center h-32 text-gray-500 text-xs">
                    No data available
                  </div>
                )}
              </div>
            </div>

            {/* Compact Stats Grid */}
            <div className="grid grid-cols-2 gap-4 mb-6 md:grid-cols-3 lg:grid-cols-6">
              {stats.map((stat, index) => {
                const StatCard = stat.actionable && stat.action_url ? Link : 'div';
                const cardProps = stat.actionable && stat.action_url ? { href: stat.action_url } : {};

                return (
                  <StatCard
                    key={index}
                    {...cardProps}
                    className={`bg-white rounded-lg shadow p-4 transition-all ${
                      stat.actionable ? 'hover:shadow-lg cursor-pointer hover:border-blue-900 border-2 border-transparent' : 'hover:shadow-md'
                    }`}
                    title={stat.description}
                  >
                    <div className="text-center">
                      <div className="flex justify-center mb-2">
                        {getIcon(stat.icon)}
                      </div>
                      <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">
                        {stat.label}
                      </p>
                      <p className="text-2xl font-bold text-blue-900">
                        {stat.value}
                      </p>
                      <p className={`text-xs mt-1 ${stat.positive ? 'text-green-600' : 'text-orange-600'}`}>
                        {stat.change}
                      </p>
                    </div>
                  </StatCard>
                );
              })}
            </div>
          </>
        )}

        {/* Recent Activity & Quick Actions - Compact */}
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 mb-4">
          {/* Recent Profile Submissions */}
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-blue-900">
                Recent Profiles
              </h3>
              <Link href="/hr/pending" className="text-xs text-blue-900 hover:underline font-semibold">
                View All →
              </Link>
            </div>
            <div className="space-y-2">
              {loading ? (
                <p className="text-xs text-gray-500">Loading...</p>
              ) : recentProfiles.length === 0 ? (
                <p className="text-xs text-gray-500 py-3 text-center">No recent submissions</p>
              ) : (
                recentProfiles.slice(0, 3).map((profile) => (
                  <div
                    key={profile.id}
                    className="flex items-center justify-between p-2 bg-gray-50 rounded hover:bg-gray-100 transition"
                  >
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-blue-900 font-bold text-xs">
                          {profile.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="font-medium text-gray-900 text-xs truncate">
                          {profile.name}
                        </p>
                        <p className="text-xs text-gray-500 truncate">
                          {profile.email}
                        </p>
                      </div>
                    </div>
                    <span className={`px-1.5 py-0.5 text-xs font-semibold rounded flex-shrink-0 ${
                      profile.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      profile.status === 'approved' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {profile.status.charAt(0).toUpperCase() + profile.status.slice(1, 4)}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Quick Actions for HR */}
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-bold text-blue-900 mb-3">
              Quick Actions
            </h3>
            <div className="space-y-2">
              <Link
                href="/hr/pending"
                className="flex items-center justify-between p-2.5 bg-blue-50 border border-blue-200 rounded hover:bg-blue-100 hover:border-blue-900 transition group"
              >
                <div className="flex items-center gap-2">
                  <Users className="w-5 h-5 text-blue-900 flex-shrink-0" />
                  <div className="min-w-0">
                    <p className="font-semibold text-blue-900 text-xs">Review Profiles</p>
                    <p className="text-xs text-blue-600 truncate">Approve/reject mavericks</p>
                  </div>
                </div>
                <span className="text-blue-900 text-sm font-bold group-hover:translate-x-1 transition-transform flex-shrink-0">→</span>
              </Link>

              <Link
                href="/batches/create"
                className="flex items-center justify-between p-2.5 bg-green-50 border border-green-200 rounded hover:bg-green-100 hover:border-green-700 transition group"
              >
                <div className="flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-green-700 flex-shrink-0" />
                  <div className="min-w-0">
                    <p className="font-semibold text-green-700 text-xs">Create Batch</p>
                    <p className="text-xs text-green-600 truncate">Start new training</p>
                  </div>
                </div>
                <span className="text-green-700 text-sm font-bold group-hover:translate-x-1 transition-transform flex-shrink-0">→</span>
              </Link>

              <Link
                href="/mavericks?filter=unassigned"
                className="flex items-center justify-between p-2.5 bg-orange-50 border border-orange-200 rounded hover:bg-orange-100 hover:border-orange-600 transition group"
              >
                <div className="flex items-center gap-2">
                  <UserX className="w-5 h-5 text-orange-600 flex-shrink-0" />
                  <div className="min-w-0">
                    <p className="font-semibold text-orange-600 text-xs">Assign to Batches</p>
                    <p className="text-xs text-orange-500 truncate">Place in training</p>
                  </div>
                </div>
                <span className="text-orange-600 text-sm font-bold group-hover:translate-x-1 transition-transform flex-shrink-0">→</span>
              </Link>
            </div>
          </div>
        </div>

        {/* Trainer Feedback Section - Compact */}
        {trainerFeedback && trainerFeedback.length > 0 && (
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-blue-900 flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-blue-900" />
                Recent Trainer Feedback
              </h3>
            </div>
            <div className="space-y-2">
              {trainerFeedback.slice(0, 3).map((feedback: any) => (
                <div
                  key={feedback.id}
                  className="border border-gray-200 rounded p-3 hover:bg-gray-50 transition"
                >
                  <div className="flex items-start justify-between mb-1.5">
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-gray-900 text-sm">
                        {feedback.trainer_name}
                      </p>
                      <p className="text-xs text-gray-500 truncate">
                        by {feedback.maverick_name} • {feedback.batch_name}
                      </p>
                    </div>
                    <div className="flex items-center gap-0.5 flex-shrink-0 ml-2">
                      {[...Array(5)].map((_, i) => (
                        <span
                          key={i}
                          className={`text-sm ${
                            i < (feedback.subject_knowledge + feedback.communication_skills + feedback.session_quality + feedback.doubt_resolution) / 4
                              ? 'text-yellow-400'
                              : 'text-gray-300'
                          }`}
                        >
                          ★
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="grid grid-cols-4 gap-1.5 text-xs mb-2">
                    <div className="text-center bg-gray-50 rounded px-1 py-0.5">
                      <span className="text-gray-500">Subj:</span>{' '}
                      <span className="font-bold text-blue-900">{feedback.subject_knowledge}</span>
                    </div>
                    <div className="text-center bg-gray-50 rounded px-1 py-0.5">
                      <span className="text-gray-500">Comm:</span>{' '}
                      <span className="font-bold text-blue-900">{feedback.communication_skills}</span>
                    </div>
                    <div className="text-center bg-gray-50 rounded px-1 py-0.5">
                      <span className="text-gray-500">Qual:</span>{' '}
                      <span className="font-bold text-blue-900">{feedback.session_quality}</span>
                    </div>
                    <div className="text-center bg-gray-50 rounded px-1 py-0.5">
                      <span className="text-gray-500">Supp:</span>{' '}
                      <span className="font-bold text-blue-900">{feedback.doubt_resolution}</span>
                    </div>
                  </div>
                  {feedback.positive_feedback && (
                    <p className="text-xs text-gray-700 bg-green-50 p-1.5 rounded leading-relaxed">
                      <span className="font-semibold text-green-800">✓ </span>
                      {feedback.positive_feedback}
                    </p>
                  )}
                  {feedback.areas_for_improvement && (
                    <p className="text-xs text-gray-700 bg-orange-50 p-1.5 rounded mt-1.5 leading-relaxed">
                      <span className="font-semibold text-orange-800">⚠ </span>
                      {feedback.areas_for_improvement}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
