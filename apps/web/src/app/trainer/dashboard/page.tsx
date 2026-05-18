"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  BookOpen,
  Users,
  Star,
  Calendar,
  ClipboardCheck,
  AlertTriangle,
  CalendarPlus,
  TrendingUp,
  Clock,
  Video,
  CheckCircle,
  ArrowRight
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';

interface Stat {
  label: string;
  value: string | number;
  total?: number;
  change: string;
  positive: boolean;
  icon: string;
  description: string;
}

interface Batch {
  id: string;
  name: string;
  description?: string;
  pipeline_name: string;
  status: string;
  current_enrollment: number;
  max_capacity?: number;
  start_date?: string;
  end_date?: string;
  progress_percentage: number;
  category?: string;
}

interface CalendarSession {
  id: string;
  title: string;
  batch_name: string;
  batch_id: string;
  job_type: string;
  scheduled_start: string;
  scheduled_end?: string;
  meeting_link?: string;
  attendance_required: boolean;
  status: string;
}

interface QuickAction {
  label: string;
  count: number;
  action: string;
  link: string;
  icon: string;
  urgent: boolean;
}

interface DashboardData {
  trainer_name: string;
  trainer_email: string;
  stats: Stat[];
  batches: Batch[];
  calendar: CalendarSession[];
  quick_actions: QuickAction[];
  recent_activity: any[];
}

const iconMap: Record<string, any> = {
  'book-open': BookOpen,
  'users': Users,
  'star': Star,
  'calendar': Calendar,
  'clipboard-check': ClipboardCheck,
  'alert-triangle': AlertTriangle,
  'calendar-plus': CalendarPlus,
};

export default function TrainerDashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/trainer/dashboard/overview');
      setDashboardData(response.data);
    } catch (error: any) {
      console.error('Failed to fetch dashboard data:', error);
      toast.error('Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'planned':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
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

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Trainer Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Welcome back, {dashboardData.trainer_name}! Here's an overview of your training batches and activities.
          </p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {dashboardData.stats.map((stat, index) => {
            const IconComponent = iconMap[stat.icon] || BookOpen;
            return (
              <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 rounded-lg ${stat.positive ? 'bg-blue-50' : 'bg-gray-50'}`}>
                    <IconComponent className={`w-6 h-6 ${stat.positive ? 'text-blue-600' : 'text-gray-600'}`} />
                  </div>
                  {stat.total !== undefined && (
                    <span className="text-sm text-gray-500">/ {stat.total}</span>
                  )}
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-1">{stat.value}</h3>
                <p className="text-sm font-medium text-gray-700 mb-1">{stat.label}</p>
                <p className="text-xs text-gray-500">{stat.change}</p>
              </div>
            );
          })}
        </div>

        {/* Quick Actions */}
        {dashboardData.quick_actions.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {dashboardData.quick_actions.map((action, index) => {
                const IconComponent = iconMap[action.icon] || AlertTriangle;
                return (
                  <button
                    key={index}
                    onClick={() => router.push(action.link)}
                    className={`bg-white rounded-lg shadow-sm border-2 p-6 text-left hover:shadow-md transition-all ${
                      action.urgent ? 'border-red-300 hover:border-red-400' : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className={`p-2 rounded-lg ${action.urgent ? 'bg-red-50' : 'bg-blue-50'}`}>
                        <IconComponent className={`w-5 h-5 ${action.urgent ? 'text-red-600' : 'text-blue-600'}`} />
                      </div>
                      <span className={`text-2xl font-bold ${action.urgent ? 'text-red-600' : 'text-blue-600'}`}>
                        {action.count}
                      </span>
                    </div>
                    <h3 className="font-semibold text-gray-900 mb-1">{action.label}</h3>
                    <p className="text-sm text-gray-600 mb-3">{action.action}</p>
                    <div className="flex items-center text-sm text-blue-600 font-medium">
                      View Details
                      <ArrowRight className="w-4 h-4 ml-1" />
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* My Batches - Takes 2 columns */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">My Batches</h2>
                <button
                  onClick={() => router.push('/trainer/batches')}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center"
                >
                  View All
                  <ArrowRight className="w-4 h-4 ml-1" />
                </button>
              </div>

              {dashboardData.batches.length === 0 ? (
                <div className="text-center py-12">
                  <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No batches assigned yet</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {dashboardData.batches.slice(0, 4).map((batch) => (
                    <button
                      key={batch.id}
                      onClick={() => router.push(`/batches/${batch.id}`)}
                      className="bg-gray-50 rounded-lg p-4 text-left hover:bg-gray-100 transition-colors border border-gray-200"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <h3 className="font-semibold text-gray-900 text-sm line-clamp-1">{batch.name}</h3>
                        <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(batch.status)}`}>
                          {batch.status}
                        </span>
                      </div>

                      <p className="text-xs text-gray-600 mb-2">{batch.pipeline_name}</p>

                      <div className="flex items-center text-xs text-gray-500 mb-3">
                        <Users className="w-3 h-3 mr-1" />
                        {batch.current_enrollment} {batch.max_capacity ? `/ ${batch.max_capacity}` : ''} students
                      </div>

                      {/* Progress Bar */}
                      <div className="mb-2">
                        <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                          <span>Progress</span>
                          <span>{Math.round(batch.progress_percentage)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all"
                            style={{ width: `${batch.progress_percentage}%` }}
                          />
                        </div>
                      </div>

                      <div className="text-xs text-gray-500">
                        {formatDate(batch.start_date)} - {formatDate(batch.end_date)}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Upcoming Sessions Calendar - Takes 1 column */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Upcoming Sessions</h2>
                <Calendar className="w-5 h-5 text-gray-400" />
              </div>

              {dashboardData.calendar.length === 0 ? (
                <div className="text-center py-12">
                  <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-sm text-gray-500">No upcoming sessions</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {dashboardData.calendar.map((session) => {
                    const sessionDate = new Date(session.scheduled_start);
                    const isToday = sessionDate.toDateString() === new Date().toDateString();

                    return (
                      <div
                        key={session.id}
                        className={`border rounded-lg p-3 hover:shadow-sm transition-shadow ${
                          isToday ? 'border-blue-300 bg-blue-50' : 'border-gray-200'
                        }`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <h3 className="font-medium text-sm text-gray-900 mb-1">{session.title}</h3>
                            <p className="text-xs text-gray-600 mb-1">{session.batch_name}</p>
                          </div>
                          <span className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded">
                            {session.job_type}
                          </span>
                        </div>

                        <div className="flex items-center text-xs text-gray-600 mb-2">
                          <Clock className="w-3 h-3 mr-1" />
                          {formatDate(session.scheduled_start)} at {formatTime(session.scheduled_start)}
                        </div>

                        {session.meeting_link && (
                          <a
                            href={session.meeting_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center text-xs text-blue-600 hover:text-blue-700"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <Video className="w-3 h-3 mr-1" />
                            Join Meeting
                          </a>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

