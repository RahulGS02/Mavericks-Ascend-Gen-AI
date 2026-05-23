"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import DashboardLayout from '@/components/DashboardLayout';
import { 
  TrendingUp, TrendingDown, Users, GraduationCap, Briefcase, 
  Target, Award, Clock, BarChart3, PieChart, Activity 
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';

interface AnalyticsData {
  summary: any;
  hiring: any;
  training: any;
  deployment: any;
  performance: any;
  users: any;
  trends: any;
  period: any;
}

export default function AdminAnalyticsPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [days, setDays] = useState(30);
  const [dateRange, setDateRange] = useState('30days');
  const [yAxisMetric1, setYAxisMetric1] = useState('hiring');
  const [yAxisMetric2, setYAxisMetric2] = useState('deployments');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (user?.role !== 'super_admin') {
      router.push('/dashboard');
      return;
    }

    fetchAnalytics();
  }, [isAuthenticated, user, router, days]);

  const handleDateRangeChange = (range: string) => {
    setDateRange(range);
    switch(range) {
      case '30days': setDays(30); break;
      case '90days': setDays(90); break;
      case '2months': setDays(60); break;
      case '6months': setDays(180); break;
      case '1year': setDays(365); break;
      case '2years': setDays(730); break;
      default: setDays(30);
    }
  };

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/admin/analytics/organization?days=${days}`);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (!analytics) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <p className="text-red-600">Failed to load analytics data</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-4 bg-gray-50 min-h-screen space-y-4">
        {/* Compact Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Organization Analytics</h1>
            <p className="text-sm text-gray-600">Performance insights and metrics</p>
          </div>
          <div className="flex flex-wrap gap-1.5 text-xs">
            <button onClick={() => handleDateRangeChange('30days')} className={`px-3 py-1.5 rounded font-medium transition-all ${dateRange === '30days' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'}`}>
              30D
            </button>
            <button onClick={() => handleDateRangeChange('90days')} className={`px-3 py-1.5 rounded font-medium transition-all ${dateRange === '90days' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'}`}>
              90D
            </button>
            <button onClick={() => handleDateRangeChange('2months')} className={`px-3 py-1.5 rounded font-medium transition-all ${dateRange === '2months' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'}`}>
              2M
            </button>
            <button onClick={() => handleDateRangeChange('6months')} className={`px-3 py-1.5 rounded font-medium transition-all ${dateRange === '6months' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'}`}>
              6M
            </button>
            <button onClick={() => handleDateRangeChange('1year')} className={`px-3 py-1.5 rounded font-medium transition-all ${dateRange === '1year' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'}`}>
              1Y
            </button>
            <button onClick={() => handleDateRangeChange('2years')} className={`px-3 py-1.5 rounded font-medium transition-all ${dateRange === '2years' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'}`}>
              2Y
            </button>
          </div>
        </div>

        {/* Compact Trend Graph */}
        <div className="bg-white rounded-lg shadow border border-gray-200">
          {/* Compact Header */}
          <div className="bg-gradient-to-r from-blue-500 to-purple-500 px-4 py-3 flex flex-col lg:flex-row justify-between items-start lg:items-center gap-3">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-white" />
              <h2 className="text-base font-bold text-white">Trend Analysis</h2>
            </div>
            <div className="flex flex-wrap gap-2 text-xs">
              <select
                value={yAxisMetric1}
                onChange={(e) => setYAxisMetric1(e.target.value)}
                className="bg-white text-gray-900 px-2 py-1 border-0 rounded text-xs font-medium focus:ring-1 focus:ring-blue-400"
              >
                <option value="hiring">Registrations</option>
                <option value="deployments">Deployments</option>
                <option value="assessments">Assessments</option>
                <option value="batches">Batches</option>
                <option value="approvals">Approvals</option>
              </select>
              <span className="text-white self-center">vs</span>
              <select
                value={yAxisMetric2}
                onChange={(e) => setYAxisMetric2(e.target.value)}
                className="bg-white text-gray-900 px-2 py-1 border-0 rounded text-xs font-medium focus:ring-1 focus:ring-green-400"
              >
                <option value="hiring">Registrations</option>
                <option value="deployments">Deployments</option>
                <option value="assessments">Assessments</option>
                <option value="batches">Batches</option>
                <option value="approvals">Approvals</option>
              </select>
            </div>
          </div>

          {/* Professional Graph Canvas */}
          <div className="p-4">
            {analytics?.trends?.registrations && analytics.trends.registrations.length > 0 ? (
              <div className="relative bg-gradient-to-br from-gray-50 to-white rounded-xl shadow-sm border border-gray-200" style={{ height: '360px' }}>
                {/* Left Y-Axis - More granular labels */}
                <div className="absolute left-2 top-6 bottom-12 w-16 flex flex-col justify-between text-sm text-blue-600 font-semibold">
                  {(() => {
                    const metric1Values = analytics.trends.registrations.map((item: any) => {
                      if (yAxisMetric1 === 'hiring') return item.registrations || 0;
                      if (yAxisMetric1 === 'deployments') return item.deployments || 0;
                      if (yAxisMetric1 === 'assessments') return item.assessments || 0;
                      if (yAxisMetric1 === 'batches') return item.active_batches || 0;
                      if (yAxisMetric1 === 'approvals') return item.approvals || 0;
                      return 0;
                    });
                    const maxVal1 = Math.max(...metric1Values, 1);
                    const roundedMax = Math.ceil(maxVal1 / 10) * 10; // Round up to nearest 10
                    const step = roundedMax / 8; // 9 labels (0 to max in 8 steps)
                    const labels = [];
                    for (let i = 8; i >= 0; i--) {
                      labels.push(Math.round(step * i));
                    }
                    return labels.map((val, idx) => (
                      <div key={idx} className="text-right pr-2 leading-none">{val}</div>
                    ));
                  })()}
                </div>

                {/* Right Y-Axis - More granular labels */}
                <div className="absolute right-2 top-6 bottom-12 w-16 flex flex-col justify-between text-sm text-green-600 font-semibold">
                  {(() => {
                    const metric2Values = analytics.trends.registrations.map((item: any) => {
                      if (yAxisMetric2 === 'hiring') return item.registrations || 0;
                      if (yAxisMetric2 === 'deployments') return item.deployments || 0;
                      if (yAxisMetric2 === 'assessments') return item.assessments || 0;
                      if (yAxisMetric2 === 'batches') return item.active_batches || 0;
                      if (yAxisMetric2 === 'approvals') return item.approvals || 0;
                      return 0;
                    });
                    const maxVal2 = Math.max(...metric2Values, 1);
                    const roundedMax = Math.ceil(maxVal2 / 10) * 10; // Round up to nearest 10
                    const step = roundedMax / 8; // 9 labels (0 to max in 8 steps)
                    const labels = [];
                    for (let i = 8; i >= 0; i--) {
                      labels.push(Math.round(step * i));
                    }
                    return labels.map((val, idx) => (
                      <div key={idx} className="text-left pl-2 leading-none">{val}</div>
                    ));
                  })()}
                </div>

                {/* Graph Area - Professional spacing */}
                <div className="absolute" style={{ left: '72px', right: '72px', top: '24px', bottom: '48px' }}>
                  {/* Grid Lines - 9 levels matching Y-axis */}
                  <div className="absolute inset-0 flex flex-col justify-between">
                    {[0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
                      <div key={i} className="border-t border-gray-200" style={{ borderStyle: i === 8 ? 'solid' : 'dashed', opacity: i === 8 ? 1 : 0.5 }}></div>
                    ))}
                  </div>

                  {/* SVG Chart - Smooth Lines */}
                  <svg className="w-full h-full" viewBox="0 0 1000 100" preserveAspectRatio="none">
                    <defs>
                      <linearGradient id="blueGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.15" />
                        <stop offset="100%" stopColor="#3B82F6" stopOpacity="0.02" />
                      </linearGradient>
                      <linearGradient id="greenGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor="#10B981" stopOpacity="0.08" />
                        <stop offset="100%" stopColor="#10B981" stopOpacity="0.01" />
                      </linearGradient>
                      <filter id="softShadow">
                        <feGaussianBlur in="SourceAlpha" stdDeviation="1"/>
                        <feOffset dx="0" dy="1" result="offsetblur"/>
                        <feComponentTransfer>
                          <feFuncA type="linear" slope="0.2"/>
                        </feComponentTransfer>
                        <feMerge>
                          <feMergeNode/>
                          <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                      </filter>
                    </defs>

                    {/* Primary Metric Line */}
                    {(() => {
                      const metric1Values = analytics.trends.registrations.map((item: any) => {
                        if (yAxisMetric1 === 'hiring') return item.registrations || 0;
                        if (yAxisMetric1 === 'deployments') return item.deployments || 0;
                        if (yAxisMetric1 === 'assessments') return item.assessments || 0;
                        if (yAxisMetric1 === 'batches') return item.active_batches || 0;
                        if (yAxisMetric1 === 'approvals') return item.approvals || 0;
                        return 0;
                      });

                      const maxVal1 = Math.max(...metric1Values, 1);
                      const roundedMax1 = Math.ceil(maxVal1 / 10) * 10;
                      const dataPoints1 = analytics.trends.registrations.map((item: any, idx: number) => {
                        let value = 0;
                        if (yAxisMetric1 === 'hiring') value = item.registrations || 0;
                        if (yAxisMetric1 === 'deployments') value = item.deployments || 0;
                        if (yAxisMetric1 === 'assessments') value = item.assessments || 0;
                        if (yAxisMetric1 === 'batches') value = item.active_batches || 0;
                        if (yAxisMetric1 === 'approvals') value = item.approvals || 0;

                        const x = (idx / Math.max(analytics.trends.registrations.length - 1, 1)) * 1000;
                        const y = 100 - ((value / roundedMax1) * 95);
                        return { x, y, value };
                      });

                      const pathData1 = `M ${dataPoints1.map(p => `${p.x},${p.y}`).join(' L ')}`;
                      const fillPathData1 = `${pathData1} L 1000,100 L 0,100 Z`;

                      return (
                        <>
                          <path d={fillPathData1} fill="url(#blueGradient)" opacity="0.6" />
                          <path d={pathData1} stroke="#3B82F6" strokeWidth="3" fill="none" strokeLinecap="round" strokeLinejoin="round" filter="url(#softShadow)" />
                        </>
                      );
                    })()}

                    {/* Secondary Metric Line */}
                    {(() => {
                      const metric2Values = analytics.trends.registrations.map((item: any) => {
                        if (yAxisMetric2 === 'hiring') return item.registrations || 0;
                        if (yAxisMetric2 === 'deployments') return item.deployments || 0;
                        if (yAxisMetric2 === 'assessments') return item.assessments || 0;
                        if (yAxisMetric2 === 'batches') return item.active_batches || 0;
                        if (yAxisMetric2 === 'approvals') return item.approvals || 0;
                        return 0;
                      });

                      const maxVal2 = Math.max(...metric2Values, 1);
                      const roundedMax2 = Math.ceil(maxVal2 / 10) * 10;
                      const dataPoints2 = analytics.trends.registrations.map((item: any, idx: number) => {
                        let value = 0;
                        if (yAxisMetric2 === 'hiring') value = item.registrations || 0;
                        if (yAxisMetric2 === 'deployments') value = item.deployments || 0;
                        if (yAxisMetric2 === 'assessments') value = item.assessments || 0;
                        if (yAxisMetric2 === 'batches') value = item.active_batches || 0;
                        if (yAxisMetric2 === 'approvals') value = item.approvals || 0;

                        const x = (idx / Math.max(analytics.trends.registrations.length - 1, 1)) * 1000;
                        const y = 100 - ((value / roundedMax2) * 95);
                        return { x, y, value };
                      });

                      const pathData2 = `M ${dataPoints2.map(p => `${p.x},${p.y}`).join(' L ')}`;
                      const fillPathData2 = `${pathData2} L 1000,100 L 0,100 Z`;

                      return (
                        <>
                          <path d={fillPathData2} fill="url(#greenGradient)" opacity="0.4" />
                          <path d={pathData2} stroke="#10B981" strokeWidth="2.5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="10,6" filter="url(#softShadow)" />
                        </>
                      );
                    })()}
                  </svg>
                </div>

                {/* X-Axis Labels */}
                <div className="absolute bottom-4 left-20 right-20 flex justify-between text-sm text-gray-600 font-medium">
                  <div>{new Date(analytics.trends.registrations[0].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</div>
                  <div className="text-gray-400">Timeline</div>
                  <div>{new Date(analytics.trends.registrations[analytics.trends.registrations.length - 1].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</div>
                </div>
                {/* Professional Legend */}
                <div className="px-6 pb-4 flex flex-wrap justify-center items-center gap-6 text-sm border-t border-gray-100 pt-4">
                  <div className="flex items-center gap-3">
                    <svg width="50" height="4" className="flex-shrink-0">
                      <line x1="0" y1="2" x2="50" y2="2" stroke="#3B82F6" strokeWidth="3" strokeLinecap="round"/>
                    </svg>
                    <span className="text-gray-700 font-semibold">
                      {yAxisMetric1 === 'hiring' ? 'New Registrations' :
                       yAxisMetric1 === 'deployments' ? 'Deployments' :
                       yAxisMetric1 === 'assessments' ? 'Assessments' :
                       yAxisMetric1 === 'batches' ? 'Active Batches' : 'Approvals'}
                    </span>
                    <span className="text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded">Left Axis</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <svg width="50" height="4" className="flex-shrink-0">
                      <line x1="0" y1="2" x2="50" y2="2" stroke="#10B981" strokeWidth="2.5" strokeDasharray="8,4" strokeLinecap="round"/>
                    </svg>
                    <span className="text-gray-700 font-semibold">
                      {yAxisMetric2 === 'hiring' ? 'New Registrations' :
                       yAxisMetric2 === 'deployments' ? 'Deployments' :
                       yAxisMetric2 === 'assessments' ? 'Assessments' :
                       yAxisMetric2 === 'batches' ? 'Active Batches' : 'Approvals'}
                    </span>
                    <span className="text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded">Right Axis</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-500 bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-200">
                    <Clock className="w-4 h-4" />
                    <span className="font-medium">Last {days} days</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center p-8 text-center" style={{height: '320px'}}>
                <div>
                  <BarChart3 className="w-12 h-12 text-gray-300 mx-auto mb-2" />
                  <p className="text-sm text-gray-500">No data available</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Compact Metrics */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {/* Total Mavericks */}
          <div className="bg-white rounded-lg shadow-sm p-3 border-l-4 border-blue-500">
            <div className="flex items-center justify-between mb-1">
              <p className="text-xs font-semibold text-gray-500 uppercase">Mavericks</p>
              <Users className="w-4 h-4 text-blue-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{analytics.summary.total_mavericks}</p>
            <p className="text-xs text-gray-500 mt-0.5">+{analytics.hiring.new_in_period} new</p>
          </div>

          {/* Active Batches */}
          <div className="bg-white rounded-lg shadow-sm p-3 border-l-4 border-purple-500">
            <div className="flex items-center justify-between mb-1">
              <p className="text-xs font-semibold text-gray-500 uppercase">Batches</p>
              <GraduationCap className="w-4 h-4 text-purple-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{analytics.summary.active_batches}</p>
            <p className="text-xs text-gray-500 mt-0.5">{analytics.training.total_batches} total</p>
          </div>

          {/* Total Deployments */}
          <div className="bg-white rounded-lg shadow-sm p-3 border-l-4 border-green-500">
            <div className="flex items-center justify-between mb-1">
              <p className="text-xs font-semibold text-gray-500 uppercase">Deployed</p>
              <Briefcase className="w-4 h-4 text-green-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{analytics.summary.total_deployments}</p>
            <p className="text-xs text-gray-500 mt-0.5">{analytics.deployment.active_deployments} active</p>
          </div>

          {/* Assessment Pass Rate */}
          <div className="bg-white rounded-lg shadow-sm p-3 border-l-4 border-orange-500">
            <div className="flex items-center justify-between mb-1">
              <p className="text-xs font-semibold text-gray-500 uppercase">Pass Rate</p>
              <Award className="w-4 h-4 text-orange-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{analytics.training.assessment_pass_rate}%</p>
            <p className="text-xs text-gray-500 mt-0.5">{analytics.training.total_assessments} tests</p>
          </div>
        </div>

        {/* Hiring & Onboarding */}
        <div className="bg-white rounded-lg shadow p-5">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Users className="w-5 h-5 text-blue-600" />
            Hiring & Onboarding Metrics
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm font-medium text-gray-600 mb-1">Approval Rate</p>
              <p className="text-2xl font-bold text-blue-600">{analytics.hiring.approval_rate}%</p>
              <p className="text-xs text-gray-500 mt-1">{analytics.hiring.approved} approved</p>
            </div>
            <div className="p-4 bg-yellow-50 rounded-lg">
              <p className="text-sm font-medium text-gray-600 mb-1">Pending Review</p>
              <p className="text-2xl font-bold text-yellow-600">{analytics.hiring.pending_review}</p>
              <p className="text-xs text-gray-500 mt-1">Awaiting action</p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm font-medium text-gray-600 mb-1">New Registrations</p>
              <p className="text-2xl font-bold text-green-600">{analytics.hiring.new_in_period}</p>
              <p className="text-xs text-gray-500 mt-1">Last {days} days</p>
            </div>
            <div className="p-4 bg-red-50 rounded-lg">
              <p className="text-sm font-medium text-gray-600 mb-1">Rejected</p>
              <p className="text-2xl font-bold text-red-600">{analytics.hiring.rejected}</p>
              <p className="text-xs text-gray-500 mt-1">Not qualified</p>
            </div>
          </div>
        </div>

        {/* Training Effectiveness */}
        <div className="bg-white rounded-lg shadow p-5">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <GraduationCap className="w-5 h-5 text-purple-600" />
            Training Effectiveness
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-sm font-medium text-gray-600 mb-1">Assessment Pass Rate</p>
              <p className="text-2xl font-bold text-purple-600">{analytics.training.assessment_pass_rate}%</p>
              <p className="text-xs text-gray-500 mt-1">{analytics.training.passed_assessments}/{analytics.training.total_assessments} passed</p>
            </div>
            <div className="p-4 bg-indigo-50 rounded-lg">
              <p className="text-sm font-medium text-gray-600 mb-1">Avg Assessment Score</p>
              <p className="text-2xl font-bold text-indigo-600">{analytics.training.avg_assessment_score}%</p>
              <p className="text-xs text-gray-500 mt-1">Overall performance</p>
            </div>
            <div className="p-4 bg-pink-50 rounded-lg">
              <p className="text-sm font-medium text-gray-600 mb-1">Trainer Rating</p>
              <p className="text-2xl font-bold text-pink-600">{analytics.training.avg_trainer_rating}/5</p>
              <p className="text-xs text-gray-500 mt-1">{analytics.training.total_feedback_received} feedbacks</p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-3 bg-gray-50 rounded-lg flex justify-between items-center">
              <span className="text-sm font-medium text-gray-600">Completed Batches</span>
              <span className="text-xl font-bold text-gray-900">{analytics.training.completed_batches}</span>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg flex justify-between items-center">
              <span className="text-sm font-medium text-gray-600">Active Batches</span>
              <span className="text-xl font-bold text-gray-900">{analytics.training.active_batches}</span>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg flex justify-between items-center">
              <span className="text-sm font-medium text-gray-600">Total Batches</span>
              <span className="text-xl font-bold text-gray-900">{analytics.training.total_batches}</span>
            </div>
          </div>
        </div>

        {/* Deployment Metrics */}
        <div className="bg-white rounded-lg shadow p-5">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-green-600" />
            Deployment Metrics
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm font-medium text-gray-600 mb-1">Deployment Rate</p>
              <p className="text-2xl font-bold text-green-600">{analytics.deployment.deployment_rate}%</p>
              <p className="text-xs text-gray-500 mt-1">Of approved mavericks</p>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm font-medium text-gray-600 mb-1">Avg Time to Deploy</p>
              <p className="text-2xl font-bold text-blue-600">{analytics.deployment.avg_time_to_deploy_days}</p>
              <p className="text-xs text-gray-500 mt-1">Days from approval</p>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-sm font-medium text-gray-600 mb-1">Recent Deployments</p>
              <p className="text-2xl font-bold text-purple-600">{analytics.deployment.recent_deployments}</p>
              <p className="text-xs text-gray-500 mt-1">Last {days} days</p>
            </div>
            <div className="p-4 bg-yellow-50 rounded-lg">
              <p className="text-sm font-medium text-gray-600 mb-1">Pending Requests</p>
              <p className="text-2xl font-bold text-yellow-600">{analytics.deployment.pending_requests}</p>
              <p className="text-xs text-gray-500 mt-1">Awaiting approval</p>
            </div>
          </div>
        </div>

        {/* Batch Performance & Deployment by Vertical */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Top Performing Batches */}
          <div className="bg-white rounded-lg shadow p-5">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-600" />
              Top Performing Batches
            </h2>
            <div className="space-y-3">
              {analytics.performance.batch_performance && analytics.performance.batch_performance.slice(0, 5).map((batch: any, index: number) => (
                <div key={batch.batch_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div className="flex items-center gap-3 flex-1">
                    <div className={`flex items-center justify-center w-8 h-8 rounded-full font-bold text-white text-sm ${
                      index === 0 ? 'bg-yellow-500' :
                      index === 1 ? 'bg-gray-400' :
                      index === 2 ? 'bg-orange-600' :
                      'bg-gray-300'
                    }`}>
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold text-gray-900 text-sm">{batch.batch_name}</p>
                      <p className="text-xs text-gray-500">{batch.enrolled} students · {batch.status}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-green-600">{batch.pass_rate}%</p>
                    <p className="text-xs text-gray-500">Pass Rate</p>
                  </div>
                </div>
              ))}
              {(!analytics.performance.batch_performance || analytics.performance.batch_performance.length === 0) && (
                <p className="text-gray-500 text-center py-4">No batch data available</p>
              )}
            </div>
          </div>

          {/* Deployment by Vertical */}
          <div className="bg-white rounded-lg shadow p-5">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <PieChart className="w-5 h-5 text-green-600" />
              Deployments by Vertical
            </h2>
            <div className="space-y-3">
              {analytics.deployment.by_vertical && analytics.deployment.by_vertical.map((item: any) => {
                const totalDeployments = analytics.deployment.total_deployments || 1;
                const percentage = ((item.count / totalDeployments) * 100).toFixed(1);

                return (
                  <div key={item.vertical} className="space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">{item.vertical}</span>
                      <span className="text-sm font-bold text-gray-900">{item.count} ({percentage}%)</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div
                        className="bg-gradient-to-r from-green-500 to-green-600 h-2.5 rounded-full transition-all"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
              {(!analytics.deployment.by_vertical || analytics.deployment.by_vertical.length === 0) && (
                <p className="text-gray-500 text-center py-4">No deployment data available</p>
              )}
            </div>
          </div>
        </div>

        {/* Registration Trends */}
        {analytics.trends.registrations && analytics.trends.registrations.length > 0 && (
          <div className="bg-white rounded-lg shadow p-5">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-600" />
              Registration Trends
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
              {analytics.trends.registrations.map((item: any) => (
                <div key={item.date} className="p-3 bg-gray-50 rounded-lg text-center">
                  <p className="text-xs text-gray-500 mb-1">{new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</p>
                  <p className="text-2xl font-bold text-blue-600">{item.registrations}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Performance Insights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow-lg p-5 text-white">
            <div className="flex items-center gap-3 mb-3">
              <Target className="w-8 h-8" />
              <h3 className="text-lg font-bold">Best Performing Batch</h3>
            </div>
            {analytics.performance.best_batch ? (
              <>
                <p className="text-2xl font-extrabold mb-1">{analytics.performance.best_batch.batch_name}</p>
                <p className="text-blue-100">Pass Rate: {analytics.performance.best_batch.pass_rate}%</p>
                <p className="text-sm text-blue-100">{analytics.performance.best_batch.enrolled} students enrolled</p>
              </>
            ) : (
              <p className="text-blue-100">No data available</p>
            )}
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow-lg p-5 text-white">
            <div className="flex items-center gap-3 mb-3">
              <TrendingUp className="w-8 h-8" />
              <h3 className="text-lg font-bold">Deployment Success</h3>
            </div>
            <p className="text-2xl font-extrabold mb-1">{analytics.deployment.deployment_rate}%</p>
            <p className="text-green-100">Of approved mavericks deployed</p>
            <p className="text-sm text-green-100">{analytics.deployment.active_deployments} currently active</p>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg shadow-lg p-5 text-white">
            <div className="flex items-center gap-3 mb-3">
              <Clock className="w-8 h-8" />
              <h3 className="text-lg font-bold">Time to Deploy</h3>
            </div>
            <p className="text-2xl font-extrabold mb-1">{analytics.deployment.avg_time_to_deploy_days} days</p>
            <p className="text-purple-100">Average from approval to deployment</p>
            <p className="text-sm text-purple-100">Pipeline efficiency metric</p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
