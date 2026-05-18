"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { TrendingUp, CheckCircle, Clock, Circle, Target } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';
import { useAuthStore } from '@/store/authStore';

interface ProgressData {
  progress: {
    overall_completion: number;
    completed_jobs: number;
    total_jobs: number;
    pipeline_name: string;
    steps: Array<{
      order: number;
      job_id: string;
      title: string;
      type: string;
      is_optional: boolean;
      status: string;
      completion_percentage: number;
      score: number | null;
      is_current: boolean;
    }>;
  };
}

export default function StudentProgressPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [progressData, setProgressData] = useState<ProgressData | null>(null);

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'maverick') {
      router.push('/login');
      return;
    }
    fetchProgress();
  }, [isAuthenticated, user, router]);

  const fetchProgress = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/maverick/dashboard/overview');
      setProgressData(response.data);
    } catch (error) {
      console.error('Failed to fetch progress:', error);
      toast.error('Failed to load progress data');
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
            <p className="mt-4 text-gray-600">Loading progress...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!progressData?.progress) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No Progress Data</h2>
            <p className="text-gray-600">You are not assigned to any batch yet. Please contact HR.</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const { progress } = progressData;

  const getStatusIcon = (status: string, is_current: boolean) => {
    if (status === 'COMPLETED') return <CheckCircle className="w-6 h-6 text-green-600" />;
    if (is_current) return <Clock className="w-6 h-6 text-blue-600" />;
    if (status === 'SKIPPED') return <Circle className="w-6 h-6 text-gray-400" />;
    return <Circle className="w-6 h-6 text-gray-300" />;
  };

  return (
    <DashboardLayout>
      <div className="p-6 max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">My Learning Progress</h1>
              <p className="text-gray-600">{progress.pipeline_name}</p>
            </div>
            <div className="text-right">
              <div className="text-5xl font-bold text-blue-600 mb-1">{progress.overall_completion}%</div>
              <p className="text-gray-600">{progress.completed_jobs} of {progress.total_jobs} completed</p>
            </div>
          </div>
        </div>

        {/* Progress Steps */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-blue-600" />
            Detailed Progress
          </h2>

          <div className="space-y-4">
            {progress.steps.map((step, index) => (
              <div
                key={step.job_id}
                className={`border rounded-lg p-4 ${
                  step.is_current ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 mt-1">
                    {getStatusIcon(step.status, step.is_current)}
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {step.order}. {step.title}
                      </h3>
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                          {step.type}
                        </span>
                        {step.is_optional && (
                          <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-700 rounded">
                            Optional
                          </span>
                        )}
                        {step.is_current && (
                          <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded">
                            Current
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <div>Status: <span className="font-medium">{step.status}</span></div>
                      <div>Progress: <span className="font-medium">{step.completion_percentage}%</span></div>
                      {step.score !== null && (
                        <div>Score: <span className="font-medium">{step.score}%</span></div>
                      )}
                    </div>

                    {/* Progress Bar */}
                    <div className="mt-3 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          step.status === 'COMPLETED' ? 'bg-green-600' :
                          step.is_current ? 'bg-blue-600' : 'bg-gray-300'
                        }`}
                        style={{ width: `${step.completion_percentage}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
