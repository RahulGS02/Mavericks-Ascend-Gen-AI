"use client";

import { useEffect, useState } from 'react';
import { Download, AlertTriangle, CheckCircle, Users, Target, Clock, Activity, Loader2, TrendingUp, AlertCircle, BarChart3, Award, Brain, Trophy, Star } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';

interface TopPerformer {
  maverick_id: string;
  name: string;
  email: string;
  pass_rate: number;
  avg_score: number;
  combined_score: number;
}

interface BatchWithTopPerformer {
  batch_id: string;
  batch_name: string;
  batch_status: string;
  total_enrolled: number;
  top_performer: TopPerformer;
}

export default function AnalyticsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [dateRange, setDateRange] = useState('30');
  const [data, setData] = useState(null);
  const [topPerformers, setTopPerformers] = useState<BatchWithTopPerformer[]>([]);

  useEffect(() => {
    fetchAnalytics();
    fetchTopPerformers();
  }, [dateRange]);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/analytics/overview', {
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

  const fetchTopPerformers = async () => {
    try {
      const response = await apiClient.get('/batches/top-performers', {
        params: { limit: 10 }
      });
      setTopPerformers(response.data?.batches || []);
    } catch (error) {
      console.error('Failed to fetch top performers:', error);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const response = await apiClient.get('/analytics/export/excel', {
        params: { days: parseInt(dateRange) },
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `HR_Analytics_Report_${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('📊 Report exported successfully!');
    } catch (error) {
      console.error('Export failed:', error);
      toast.error('Failed to export report');
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-96">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-blue-900 mb-2">HR Analytics & Insights</h1>
            <p className="text-gray-600">Real-time actionable insights for strategic decision-making</p>
          </div>
          <div className="flex gap-3">
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
            </select>
            <button
              onClick={handleExport}
              disabled={exporting}
              className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {exporting ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Download className="w-4 h-4 mr-2" />}
              Export Excel Report
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg shadow p-6">
            <Users className="w-8 h-8 mb-2 opacity-80" />
            <div className="text-3xl font-bold">{data?.summary?.total_mavericks || 0}</div>
            <div className="text-sm opacity-90">Total Mavericks</div>
          </div>
          <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg shadow p-6">
            <Activity className="w-8 h-8 mb-2 opacity-80" />
            <div className="text-3xl font-bold">{data?.summary?.active_batches || 0}</div>
            <div className="text-sm opacity-90">Active Batches</div>
          </div>
          <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-lg shadow p-6">
            <AlertCircle className="w-8 h-8 mb-2 opacity-80" />
            <div className="text-3xl font-bold">{data?.summary?.pending_reviews || 0}</div>
            <div className="text-sm opacity-90">Pending Reviews</div>
          </div>
          <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-lg shadow p-6">
            <Target className="w-8 h-8 mb-2 opacity-80" />
            <div className="text-3xl font-bold">{data?.summary?.deployment_requests || 0}</div>
            <div className="text-sm opacity-90">Deployment Requests</div>
          </div>
        </div>

        {/* KEY INSIGHTS GRID */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">

          {/* INSIGHT 1: Training Effectiveness */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <CheckCircle className={`w-6 h-6 ${data?.insights?.training_effectiveness?.success_rate >= 80 ? 'text-green-500' : 'text-yellow-500'}`} />
                <h3 className="text-lg font-semibold text-gray-900">1. Training Effectiveness</h3>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                data?.insights?.training_effectiveness?.success_rate >= 80 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
              }`}>
                {data?.insights?.training_effectiveness?.status || 'N/A'}
              </span>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Success Rate</span>
                <span className="text-2xl font-bold text-blue-900">{data?.insights?.training_effectiveness?.success_rate || 0}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-green-500 h-3 rounded-full transition-all"
                  style={{ width: `${data?.insights?.training_effectiveness?.success_rate || 0}%` }}
                ></div>
              </div>
              <div className="grid grid-cols-2 gap-3 pt-2">
                <div className="bg-green-50 p-3 rounded">
                  <div className="text-sm text-gray-600">Passed</div>
                  <div className="text-xl font-bold text-green-700">{data?.insights?.training_effectiveness?.passed_attempts || 0}</div>
                </div>
                <div className="bg-red-50 p-3 rounded">
                  <div className="text-sm text-gray-600">Failed</div>
                  <div className="text-xl font-bold text-red-700">{data?.insights?.training_effectiveness?.failed_attempts || 0}</div>
                </div>
              </div>
            </div>
          </div>

          {/* INSIGHT 2: Deployment Pipeline */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Clock className="w-6 h-6 text-blue-500" />
                <h3 className="text-lg font-semibold text-gray-900">2. Deployment Pipeline Health</h3>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                data?.insights?.deployment_pipeline?.avg_days_to_deploy <= 90 ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'
              }`}>
                {data?.insights?.deployment_pipeline?.status || 'N/A'}
              </span>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Avg Days to Deploy</span>
                <span className="text-2xl font-bold text-blue-900">{data?.insights?.deployment_pipeline?.avg_days_to_deploy || 0} days</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Deployment Success</span>
                <span className="text-xl font-bold text-green-600">{data?.insights?.deployment_pipeline?.deployment_success_rate || 0}%</span>
              </div>
              <div className="grid grid-cols-2 gap-3 pt-2">
                <div className="bg-blue-50 p-3 rounded">
                  <div className="text-sm text-gray-600">Training Complete</div>
                  <div className="text-xl font-bold text-blue-700">{data?.insights?.deployment_pipeline?.training_complete_count || 0}</div>
                </div>
                <div className="bg-green-50 p-3 rounded">
                  <div className="text-sm text-gray-600">Deployed</div>
                  <div className="text-xl font-bold text-green-700">{data?.insights?.deployment_pipeline?.deployed_count || 0}</div>
                </div>
              </div>
            </div>
          </div>

          {/* INSIGHT 3: At-Risk Mavericks */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-6 h-6 text-red-500" />
                <h3 className="text-lg font-semibold text-gray-900">3. At-Risk Mavericks</h3>
              </div>
              {data?.insights?.at_risk?.count > 0 && (
                <span className="px-3 py-1 rounded-full text-sm font-semibold bg-red-100 text-red-700">
                  Action Needed
                </span>
              )}
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Require Intervention</span>
                <span className="text-2xl font-bold text-red-600">{data?.insights?.at_risk?.count || 0}</span>
              </div>
              {data?.insights?.at_risk?.mavericks?.length > 0 ? (
                <div className="max-h-40 overflow-y-auto space-y-2 pt-2">
                  {data.insights.at_risk.mavericks.slice(0, 5).map((maverick, idx) => (
                    <div key={idx} className="flex justify-between items-center p-2 bg-red-50 rounded">
                      <span className="text-sm text-gray-900">{maverick.name}</span>
                      <span className="text-xs font-semibold text-red-600">{maverick.failed_attempts} failures</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-4 bg-green-50 rounded text-center">
                  <CheckCircle className="w-8 h-8 mx-auto text-green-500 mb-2" />
                  <p className="text-sm text-green-700 font-medium">All mavericks performing well! 🎉</p>
                </div>
              )}
            </div>
          </div>

          {/* TOP PERFORMERS BY BATCH */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Trophy className="w-6 h-6 text-yellow-500" />
                <h3 className="text-lg font-semibold text-gray-900">Top Performers by Batch</h3>
              </div>
              <span className="px-3 py-1 rounded-full text-sm font-semibold bg-yellow-100 text-yellow-700">
                {topPerformers.length} Batches
              </span>
            </div>
            <div className="space-y-3">
              {topPerformers.length > 0 ? (
                <div className="max-h-80 overflow-y-auto space-y-3">
                  {topPerformers.map((batch, idx) => (
                    <div
                      key={batch.batch_id}
                      className="p-3 border border-gray-200 rounded-lg hover:border-blue-400 hover:shadow-md transition-all cursor-pointer bg-gradient-to-r from-white to-blue-50"
                      onClick={() => router.push(`/batches/${batch.batch_id}`)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <Star className="w-4 h-4 text-yellow-500" />
                            <span className="font-semibold text-gray-900">{batch.batch_name}</span>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {batch.total_enrolled} enrolled • Status: {batch.batch_status}
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-yellow-600">
                            {batch.top_performer.combined_score}
                          </div>
                          <div className="text-xs text-gray-500">Score</div>
                        </div>
                      </div>
                      <div className="border-t border-gray-200 pt-2 mt-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                              <span className="text-yellow-700 font-bold text-sm">
                                {batch.top_performer.name.charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <div>
                              <p className="text-sm font-medium text-gray-900">{batch.top_performer.name}</p>
                              <p className="text-xs text-gray-500">{batch.top_performer.email}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-semibold text-green-600">{batch.top_performer.pass_rate}%</p>
                            <p className="text-xs text-gray-500">Pass Rate</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-4 bg-gray-50 rounded text-center">
                  <Activity className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                  <p className="text-sm text-gray-600">No performance data available</p>
                </div>
              )}
            </div>
          </div>

          {/* INSIGHT 4: Resource Utilization */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Activity className="w-6 h-6 text-purple-500" />
                <h3 className="text-lg font-semibold text-gray-900">4. Resource Utilization</h3>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                data?.insights?.resource_utilization?.status === 'optimal' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
              }`}>
                {data?.insights?.resource_utilization?.status?.replace('_', ' ') || 'N/A'}
              </span>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Utilization Rate</span>
                <span className="text-2xl font-bold text-purple-900">{data?.insights?.resource_utilization?.utilization_rate || 0}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-purple-500 h-3 rounded-full transition-all"
                  style={{ width: `${data?.insights?.resource_utilization?.utilization_rate || 0}%` }}
                ></div>
              </div>
              <div className="grid grid-cols-2 gap-3 pt-2">
                <div className="bg-purple-50 p-3 rounded">
                  <div className="text-sm text-gray-600">Total Capacity</div>
                  <div className="text-xl font-bold text-purple-700">{data?.insights?.resource_utilization?.total_capacity || 0}</div>
                </div>
                <div className="bg-blue-50 p-3 rounded">
                  <div className="text-sm text-gray-600">Enrolled</div>
                  <div className="text-xl font-bold text-blue-700">{data?.insights?.resource_utilization?.total_enrolled || 0}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* MORE INSIGHTS */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">

          {/* INSIGHT 5: Skill Gaps */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Brain className="w-6 h-6 text-indigo-500" />
              <h3 className="text-lg font-semibold text-gray-900">5. Top Skill Gaps</h3>
            </div>
            <div className="space-y-2">
              {data?.insights?.skill_gaps?.gaps?.slice(0, 5).map((gap, idx) => (
                <div key={idx} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                  <span className="text-sm text-gray-900">{gap.skill}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-indigo-600">{gap.avg_proficiency}%</span>
                    <span className={`w-2 h-2 rounded-full ${gap.avg_proficiency < 40 ? 'bg-red-500' : 'bg-yellow-500'}`}></span>
                  </div>
                </div>
              )) || <p className="text-sm text-gray-500">No skill gaps identified</p>}
            </div>
          </div>

          {/* INSIGHT 6: Profile Review Backlog */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Users className="w-6 h-6 text-cyan-500" />
              <h3 className="text-lg font-semibold text-gray-900">6. Profile Review Status</h3>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Pending Reviews</span>
                <span className="text-2xl font-bold text-cyan-900">{data?.insights?.profile_backlog?.pending_count || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Approved (Last 7d)</span>
                <span className="text-lg font-semibold text-green-600">{data?.insights?.profile_backlog?.approved_last_week || 0}</span>
              </div>
              <div className="pt-2 border-t">
                <div className="text-sm text-gray-600">Daily Review Rate</div>
                <div className="text-xl font-bold text-blue-900">{data?.insights?.profile_backlog?.daily_review_rate || 0} / day</div>
              </div>
            </div>
          </div>

          {/* INSIGHT 7: In-Demand Skills */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-6 h-6 text-emerald-500" />
              <h3 className="text-lg font-semibold text-gray-900">7. In-Demand Skills</h3>
            </div>
            <div className="space-y-2">
              {data?.insights?.in_demand_skills?.slice(0, 5).map((item, idx) => (
                <div key={idx} className="flex justify-between items-center p-2 bg-emerald-50 rounded">
                  <span className="text-sm text-gray-900">{item.skill}</span>
                  <span className="text-sm font-bold text-emerald-700">{item.demand_count}</span>
                </div>
              )) || <p className="text-sm text-gray-500">No demand data available</p>}
            </div>
          </div>
        </div>

        {/* BATCH PERFORMANCE & TRAINER EFFECTIVENESS */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* INSIGHT 8: Batch Performance */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-6 h-6 text-blue-500" />
              <h3 className="text-lg font-semibold text-gray-900">8. Top Performing Batches</h3>
            </div>
            <div className="space-y-2">
              {data?.insights?.batch_performance?.batches?.slice(0, 5).map((batch, idx) => (
                <div key={idx} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="text-sm text-gray-900">{batch.batch_name}</span>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      batch.success_rate >= 80 ? 'bg-green-100 text-green-700' :
                      batch.success_rate >= 60 ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      {batch.success_rate}%
                    </span>
                  </div>
                </div>
              )) || <p className="text-sm text-gray-500">No batch data available</p>}
            </div>
          </div>

          {/* INSIGHT 9: Trainer Effectiveness */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Award className="w-6 h-6 text-amber-500" />
              <h3 className="text-lg font-semibold text-gray-900">9. Trainer Effectiveness</h3>
            </div>
            <div className="space-y-2">
              {data?.insights?.trainer_effectiveness?.trainers?.slice(0, 5).map((trainer, idx) => (
                <div key={idx} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="text-sm text-gray-900">{trainer.trainer_name}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-amber-600">⭐ {trainer.avg_rating.toFixed(1)}</span>
                    <span className="text-xs text-gray-500">({trainer.feedback_count})</span>
                  </div>
                </div>
              )) || <p className="text-sm text-gray-500">No trainer data available</p>}
            </div>
            {data?.insights?.trainer_effectiveness?.avg_platform_rating > 0 && (
              <div className="mt-4 pt-4 border-t">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Platform Average</span>
                  <span className="text-lg font-bold text-amber-600">⭐ {data.insights.trainer_effectiveness.avg_platform_rating.toFixed(2)}</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ACTION RECOMMENDATIONS */}
        {data && (
          <div className="mt-6 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-4">📊 Key Recommendations</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {data?.insights?.at_risk?.count > 0 && (
                <div className="bg-white rounded-lg p-4 border border-red-200">
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5" />
                    <div>
                      <p className="font-semibold text-gray-900">Priority Action</p>
                      <p className="text-sm text-gray-600 mt-1">{data.insights.at_risk.count} mavericks need immediate intervention</p>
                    </div>
                  </div>
                </div>
              )}
              {data?.insights?.profile_backlog?.pending_count > 10 && (
                <div className="bg-white rounded-lg p-4 border border-yellow-200">
                  <div className="flex items-start gap-2">
                    <Clock className="w-5 h-5 text-yellow-500 mt-0.5" />
                    <div>
                      <p className="font-semibold text-gray-900">Review Backlog</p>
                      <p className="text-sm text-gray-600 mt-1">{data.insights.profile_backlog.pending_count} profiles pending review</p>
                    </div>
                  </div>
                </div>
              )}
              {data?.insights?.resource_utilization?.status !== 'optimal' && (
                <div className="bg-white rounded-lg p-4 border border-blue-200">
                  <div className="flex items-start gap-2">
                    <Activity className="w-5 h-5 text-blue-500 mt-0.5" />
                    <div>
                      <p className="font-semibold text-gray-900">Resource Planning</p>
                      <p className="text-sm text-gray-600 mt-1">Utilization is {data.insights.resource_utilization.status.replace('_', ' ')}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

      </div>
    </DashboardLayout>
  );
}