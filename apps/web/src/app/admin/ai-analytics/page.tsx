"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import DashboardLayout from '@/components/DashboardLayout';
import { 
  DollarSign, Activity, TrendingUp, AlertCircle, 
  Zap, BarChart3, Loader2 
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';

interface AIStats {
  is_enabled: boolean;
  total_requests: number;
  input_tokens: number;
  output_tokens: number;
  total_cost_usd: number;
  avg_tokens_per_request: number;
  error_rate_percentage: number;
  cost_per_request_usd: number;
  cost_breakdown: {
    input_cost_usd: number;
    output_cost_usd: number;
  };
}

export default function AIAnalyticsPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<AIStats | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (user?.role !== 'super_admin') {
      router.push('/dashboard');
      return;
    }

    fetchAIStats();
  }, [isAuthenticated, user, router]);

  const fetchAIStats = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/ai/stats/detailed');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch AI stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <Loader2 className="animate-spin h-12 w-12 text-blue-600 mx-auto" />
            <p className="mt-4 text-gray-600">Loading AI analytics...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">AI Cost Analytics</h1>
            <p className="mt-2 text-gray-600">Monitor AI usage and optimize costs</p>
          </div>
          <div className="flex items-center gap-2">
            {stats?.is_enabled ? (
              <span className="px-4 py-2 bg-green-100 text-green-800 rounded-lg flex items-center gap-2">
                <Zap className="w-4 h-4" />
                AI Enabled
              </span>
            ) : (
              <span className="px-4 py-2 bg-red-100 text-red-800 rounded-lg flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                AI Disabled
              </span>
            )}
          </div>
        </div>

        {/* Top Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Total Cost */}
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Cost</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  ${stats?.total_cost_usd.toFixed(2) || '0.00'}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  Lifetime
                </p>
              </div>
              <DollarSign className="w-12 h-12 text-green-500 opacity-20" />
            </div>
          </div>

          {/* Total Requests */}
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Requests</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {stats?.total_requests.toLocaleString() || 0}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  AI API calls
                </p>
              </div>
              <Activity className="w-12 h-12 text-blue-500 opacity-20" />
            </div>
          </div>

          {/* Avg Cost Per Request */}
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Cost/Request</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  ${stats?.cost_per_request_usd.toFixed(4) || '0.0000'}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  Per API call
                </p>
              </div>
              <TrendingUp className="w-12 h-12 text-purple-500 opacity-20" />
            </div>
          </div>

          {/* Error Rate */}
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Error Rate</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {stats?.error_rate_percentage.toFixed(1) || '0.0'}%
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  Failed requests
                </p>
              </div>
              <AlertCircle className="w-12 h-12 text-red-500 opacity-20" />
            </div>
          </div>
        </div>

        {/* Token Usage */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3 mb-4">
              <BarChart3 className="w-5 h-5 text-blue-600" />
              <h3 className="text-lg font-bold text-gray-900">Input Tokens</h3>
            </div>
            <div className="space-y-3">
              <div>
                <p className="text-3xl font-bold text-gray-900">
                  {stats?.input_tokens.toLocaleString() || 0}
                </p>
                <p className="text-sm text-gray-600 mt-1">Total input tokens processed</p>
              </div>
              <div className="pt-3 border-t">
                <p className="text-sm text-gray-600">Cost</p>
                <p className="text-xl font-bold text-green-600">
                  ${stats?.cost_breakdown.input_cost_usd.toFixed(2) || '0.00'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3 mb-4">
              <BarChart3 className="w-5 h-5 text-purple-600" />
              <h3 className="text-lg font-bold text-gray-900">Output Tokens</h3>
            </div>
            <div className="space-y-3">
              <div>
                <p className="text-3xl font-bold text-gray-900">
                  {stats?.output_tokens.toLocaleString() || 0}
                </p>
                <p className="text-sm text-gray-600 mt-1">Total output tokens generated</p>
              </div>
              <div className="pt-3 border-t">
                <p className="text-sm text-gray-600">Cost</p>
                <p className="text-xl font-bold text-green-600">
                  ${stats?.cost_breakdown.output_cost_usd.toFixed(2) || '0.00'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="w-5 h-5 text-green-600" />
              <h3 className="text-lg font-bold text-gray-900">Averages</h3>
            </div>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Avg Tokens/Request</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats?.avg_tokens_per_request.toFixed(0) || 0}
                </p>
              </div>
              <div className="pt-3 border-t">
                <p className="text-sm text-gray-600">Cost Per Request</p>
                <p className="text-xl font-bold text-green-600">
                  ${stats?.cost_per_request_usd.toFixed(4) || '0.0000'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Cost Optimization Tips */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-bold text-blue-900 mb-2">Cost Optimization Tips</h3>
              <ul className="space-y-2 text-sm text-blue-800">
                <li>• Monitor daily costs and set budget alerts</li>
                <li>• Review error rates - failed requests still cost money</li>
                <li>• Consider caching common AI responses</li>
                <li>• Use AI features selectively for high-value operations</li>
                <li>• Regularly review and optimize prompts for efficiency</li>
              </ul>
            </div>
          </div>
        </div>

        {/* AI Controls */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">AI Feature Controls</h2>
          <p className="text-gray-600 mb-6">
            Enable or disable AI features to control costs. Changes take effect immediately.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border border-gray-200 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">Resume Parsing</h4>
              <p className="text-sm text-gray-600 mb-3">Extract skills and experience from resumes</p>
              <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 text-sm">
                Configure
              </button>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">Skill Extraction</h4>
              <p className="text-sm text-gray-600 mb-3">Automatically identify technical skills</p>
              <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 text-sm">
                Configure
              </button>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">Performance Insights</h4>
              <p className="text-sm text-gray-600 mb-3">Generate AI-powered performance analysis</p>
              <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 text-sm">
                Configure
              </button>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
