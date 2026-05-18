"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import {
  TrendingUp,
  Users,
  BarChart3,
  CheckCircle,
  Activity,
  AlertTriangle,
  Award,
  BookOpen,
  Calendar,
  Target
} from 'lucide-react';

interface AnalyticsData {
  trainer_name: string;
  summary: {
    total_students: number;
    total_batches: number;
    active_batches: number;
    total_jobs_scheduled: number;
    completed_jobs: number;
    completion_rate: number;
    avg_student_progress: number;
    sessions_conducted: number;
    avg_trainer_rating: number;
    date_range_days: number;
  };
  assessment_stats: {
    total_assessments: number;
    total_attempts: number;
    passed_attempts: number;
    failed_attempts: number;
    pass_rate: number;
    avg_score: number;
  };
  progress_distribution: {
    "0-25": number;
    "26-50": number;
    "51-75": number;
    "76-100": number;
  };
  at_risk_students: Array<{
    name: string;
    email: string;
    progress: number;
    batch_name: string;
    batch_id: string;
  }>;
  batch_performance: Array<{
    batch_id: string;
    batch_name: string;
    students: number;
    jobs_scheduled: number;
    jobs_completed: number;
    completion_rate: number;
    status: string;
  }>;
  weekly_activity: Array<{
    date: string;
    sessions: number;
    assessments: number;
  }>;
}

export default function TrainerAnalyticsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState('30');
  const [data, setData] = useState<AnalyticsData | null>(null);

  useEffect(() => {
    fetchAnalytics();
  }, [dateRange]);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/trainer/analytics/overview', {
        params: { days: parseInt(dateRange) }
      });
      setData(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      toast.error('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading analytics...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!data) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-yellow-800">No analytics data available</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const getProgressColor = (progress: number) => {
    if (progress >= 75) return 'text-green-600 bg-green-50';
    if (progress >= 50) return 'text-blue-600 bg-blue-50';
    if (progress >= 25) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case 'ACTIVE': return 'bg-green-100 text-green-800';
      case 'PLANNED': return 'bg-blue-100 text-blue-800';
      case 'COMPLETED': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <DashboardLayout>
      <div className="p-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Training Analytics</h1>
              <p className="text-gray-600 mt-2">
                Welcome {data.trainer_name}! Here's your performance insights for the last {dateRange} days.
              </p>
            </div>
            <div>
              <select
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="7">Last 7 days</option>
                <option value="30">Last 30 days</option>
                <option value="90">Last 90 days</option>
              </select>
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Students */}
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg shadow-lg p-6">
            <Users className="w-8 h-8 mb-3 opacity-80" />
            <div className="text-3xl font-bold mb-1">{data.summary.total_students}</div>
            <div className="text-sm opacity-90">Total Students</div>
            <div className="text-xs opacity-75 mt-2">{data.summary.active_batches} active batches</div>
          </div>

          {/* Completion Rate */}
          <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg shadow-lg p-6">
            <CheckCircle className="w-8 h-8 mb-3 opacity-80" />
            <div className="text-3xl font-bold mb-1">{data.summary.completion_rate}%</div>
            <div className="text-sm opacity-90">Completion Rate</div>
            <div className="text-xs opacity-75 mt-2">{data.summary.completed_jobs}/{data.summary.total_jobs_scheduled} jobs</div>
          </div>

          {/* Student Progress */}
          <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-lg shadow-lg p-6">
            <TrendingUp className="w-8 h-8 mb-3 opacity-80" />
            <div className="text-3xl font-bold mb-1">{data.summary.avg_student_progress}%</div>
            <div className="text-sm opacity-90">Avg. Student Progress</div>
            <div className="text-xs opacity-75 mt-2">Across all students</div>
          </div>

          {/* Trainer Rating */}
          <div className="bg-gradient-to-br from-amber-500 to-amber-600 text-white rounded-lg shadow-lg p-6">
            <Award className="w-8 h-8 mb-3 opacity-80" />
            <div className="text-3xl font-bold mb-1">{data.summary.avg_trainer_rating}/5.0</div>
            <div className="text-sm opacity-90">Trainer Rating</div>
            <div className="text-xs opacity-75 mt-2">Student feedback</div>
          </div>
        </div>

        {/* Assessment Performance & Weekly Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Assessment Performance */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Assessment Performance</h3>
                <p className="text-sm text-gray-600">{data.assessment_stats.total_assessments} total assessments</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">{data.assessment_stats.total_attempts}</div>
                <div className="text-sm text-gray-600">Total Attempts</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{data.assessment_stats.pass_rate}%</div>
                <div className="text-sm text-gray-600">Pass Rate</div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 border border-green-200 rounded-lg">
                <div className="text-xl font-semibold text-green-600">{data.assessment_stats.passed_attempts}</div>
                <div className="text-xs text-gray-600">Passed</div>
              </div>
              <div className="text-center p-3 border border-red-200 rounded-lg">
                <div className="text-xl font-semibold text-red-600">{data.assessment_stats.failed_attempts}</div>
                <div className="text-xs text-gray-600">Failed</div>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Average Score</span>
                <span className="text-lg font-bold text-blue-600">{data.assessment_stats.avg_score}%</span>
              </div>
            </div>
          </div>

          {/* Weekly Activity */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Activity className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Weekly Activity</h3>
                <p className="text-sm text-gray-600">Last 7 days</p>
              </div>
            </div>

            <div className="space-y-3">
              {data.weekly_activity.map((day, index) => (
                <div key={index} className="flex items-center gap-4">
                  <div className="w-20 text-sm font-medium text-gray-700">{day.date}</div>
                  <div className="flex-1 flex gap-2">
                    <div className="flex-1 bg-blue-100 rounded-full h-8 flex items-center px-3">
                      <Calendar className="w-3 h-3 text-blue-600 mr-2" />
                      <span className="text-sm font-medium text-blue-900">{day.sessions}</span>
                    </div>
                    <div className="flex-1 bg-green-100 rounded-full h-8 flex items-center px-3">
                      <BookOpen className="w-3 h-3 text-green-600 mr-2" />
                      <span className="text-sm font-medium text-green-900">{day.assessments}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200 flex gap-4 text-xs text-gray-600">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-100 rounded"></div>
                <span>Training Sessions</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-100 rounded"></div>
                <span>Assessments</span>
              </div>
            </div>
          </div>
        </div>

        {/* Student Progress Distribution */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-green-100 rounded-lg">
              <Target className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Student Progress Distribution</h3>
              <p className="text-sm text-gray-600">How your students are performing</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-6 bg-red-50 rounded-lg border-2 border-red-200">
              <div className="text-3xl font-bold text-red-600 mb-2">{data.progress_distribution["0-25"]}</div>
              <div className="text-sm font-medium text-gray-700 mb-1">0-25% Complete</div>
              <div className="text-xs text-gray-500">Needs attention</div>
            </div>
            <div className="text-center p-6 bg-yellow-50 rounded-lg border-2 border-yellow-200">
              <div className="text-3xl font-bold text-yellow-600 mb-2">{data.progress_distribution["26-50"]}</div>
              <div className="text-sm font-medium text-gray-700 mb-1">26-50% Complete</div>
              <div className="text-xs text-gray-500">Making progress</div>
            </div>
            <div className="text-center p-6 bg-blue-50 rounded-lg border-2 border-blue-200">
              <div className="text-3xl font-bold text-blue-600 mb-2">{data.progress_distribution["51-75"]}</div>
              <div className="text-sm font-medium text-gray-700 mb-1">51-75% Complete</div>
              <div className="text-xs text-gray-500">On track</div>
            </div>
            <div className="text-center p-6 bg-green-50 rounded-lg border-2 border-green-200">
              <div className="text-3xl font-bold text-green-600 mb-2">{data.progress_distribution["76-100"]}</div>
              <div className="text-sm font-medium text-gray-700 mb-1">76-100% Complete</div>
              <div className="text-xs text-gray-500">Excellent</div>
            </div>
          </div>
        </div>

        {/* At-Risk Students & Batch Performance */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* At-Risk Students */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Students At Risk</h3>
                <p className="text-sm text-gray-600">Progress below 30%</p>
              </div>
            </div>

            {data.at_risk_students.length === 0 ? (
              <div className="text-center py-8 bg-green-50 rounded-lg">
                <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
                <p className="text-green-700 font-medium">Great job!</p>
                <p className="text-sm text-gray-600">All students are on track</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-80 overflow-y-auto">
                {data.at_risk_students.map((student, index) => (
                  <div
                    key={index}
                    className="p-4 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors cursor-pointer"
                    onClick={() => router.push(`/batches/${student.batch_id}`)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <div className="font-semibold text-gray-900">{student.name}</div>
                        <div className="text-xs text-gray-600">{student.email}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-red-600">{student.progress}%</div>
                        <div className="text-xs text-gray-500">Progress</div>
                      </div>
                    </div>
                    <div className="text-xs text-gray-600">
                      Batch: {student.batch_name}
                    </div>
                    <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-red-600 h-2 rounded-full"
                        style={{ width: `${student.progress}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Top Performing Batches */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-green-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Batch Performance</h3>
                <p className="text-sm text-gray-600">Ranked by completion rate</p>
              </div>
            </div>

            <div className="space-y-3 max-h-80 overflow-y-auto">
              {data.batch_performance.map((batch, index) => (
                <div
                  key={batch.batch_id}
                  className="p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                  onClick={() => router.push(`/batches/${batch.batch_id}`)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                          index === 0 ? 'bg-yellow-400 text-yellow-900' :
                          index === 1 ? 'bg-gray-300 text-gray-700' :
                          index === 2 ? 'bg-amber-600 text-white' :
                          'bg-gray-200 text-gray-600'
                        }`}>
                          {index + 1}
                        </div>
                        <div className="font-semibold text-gray-900">{batch.batch_name}</div>
                      </div>
                      <div className="text-xs text-gray-600 ml-8">
                        {batch.students} students · {batch.jobs_completed}/{batch.jobs_scheduled} jobs
                      </div>
                    </div>
                    <div className="text-right ml-3">
                      <div className={`text-lg font-bold ${
                        batch.completion_rate >= 75 ? 'text-green-600' :
                        batch.completion_rate >= 50 ? 'text-blue-600' :
                        batch.completion_rate >= 25 ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {batch.completion_rate}%
                      </div>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${getStatusColor(batch.status)}`}>
                        {batch.status}
                      </span>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 ml-8">
                    <div
                      className={`h-2 rounded-full ${
                        batch.completion_rate >= 75 ? 'bg-green-600' :
                        batch.completion_rate >= 50 ? 'bg-blue-600' :
                        batch.completion_rate >= 25 ? 'bg-yellow-600' :
                        'bg-red-600'
                      }`}
                      style={{ width: `${batch.completion_rate}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
