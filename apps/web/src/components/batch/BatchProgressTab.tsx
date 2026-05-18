"use client";

import { useEffect, useState } from 'react';
import { BarChart3, Users, CheckCircle, Clock, XCircle, AlertCircle, TrendingUp, Award } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';

interface MaverickProgress {
  maverick_id: string;
  maverick_name: string;
  completed_jobs: number;
  total_jobs: number;
  completion_percentage: number;
  has_scheduled_jobs?: boolean;
  has_initialized?: boolean;
}

interface BatchProgressData {
  batch_id: string;
  batch_name: string;
  pipeline_id: string;
  pipeline_name: string;
  total_mavericks: number;
  total_jobs: number;
  overall_completion: number;
  maverick_progress: MaverickProgress[];
}

interface BatchProgressTabProps {
  batchId: string;
  batchName: string;
}

export default function BatchProgressTab({ batchId, batchName }: BatchProgressTabProps) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<BatchProgressData | null>(null);

  useEffect(() => {
    fetchProgress();
  }, [batchId]);

  const fetchProgress = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get(`/job-progress/batch/${batchId}`);
      setData(response.data);
    } catch (error) {
      console.error('Failed to fetch batch progress:', error);
      toast.error('Failed to load progress data');
    } finally {
      setLoading(false);
    }
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 50) return 'bg-blue-500';
    if (percentage >= 25) return 'bg-yellow-500';
    return 'bg-gray-300';
  };

  const getProgressTextColor = (percentage: number) => {
    if (percentage >= 80) return 'text-green-700';
    if (percentage >= 50) return 'text-blue-700';
    if (percentage >= 25) return 'text-yellow-700';
    return 'text-gray-700';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!data || data.total_mavericks === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
        <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">No Progress Data</h3>
        <p className="text-gray-600 mb-4">
          No mavericks are enrolled in this batch yet, or progress tracking hasn't been initialized.
        </p>
      </div>
    );
  }

  // Calculate statistics
  const completedMavericks = data.maverick_progress.filter(m => m.completion_percentage === 100).length;
  const onTrackMavericks = data.maverick_progress.filter(m =>
    m.completion_percentage >= 50 &&
    m.completion_percentage < 100 &&
    m.has_initialized
  ).length;

  // Only show "needs attention" if:
  // 1. Jobs are initialized/scheduled AND
  // 2. Completion is < 50%
  // Don't flag mavericks if jobs aren't even scheduled yet
  const needsAttentionMavericks = data.maverick_progress.filter(m =>
    m.has_initialized &&
    m.has_scheduled_jobs &&
    m.completion_percentage < 50
  ).length;

  return (
    <div className="space-y-6">
      {/* Overall Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Overall Completion */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow-sm border border-blue-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-6 h-6 text-blue-600" />
            <span className={`text-2xl font-bold ${getProgressTextColor(data.overall_completion)}`}>
              {Math.round(data.overall_completion)}%
            </span>
          </div>
          <h3 className="text-sm font-medium text-gray-700">Overall Completion</h3>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className={`${getProgressColor(data.overall_completion)} h-2 rounded-full transition-all`}
              style={{ width: `${data.overall_completion}%` }}
            ></div>
          </div>
        </div>

        {/* Completed */}
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg shadow-sm border border-green-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <CheckCircle className="w-6 h-6 text-green-600" />
            <span className="text-2xl font-bold text-green-700">{completedMavericks}</span>
          </div>
          <h3 className="text-sm font-medium text-gray-700">Completed (100%)</h3>
          <p className="text-xs text-gray-600 mt-1">
            {completedMavericks} of {data.total_mavericks} mavericks
          </p>
        </div>

        {/* On Track */}
        <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg shadow-sm border border-yellow-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <Clock className="w-6 h-6 text-yellow-600" />
            <span className="text-2xl font-bold text-yellow-700">{onTrackMavericks}</span>
          </div>
          <h3 className="text-sm font-medium text-gray-700">On Track (50-99%)</h3>
          <p className="text-xs text-gray-600 mt-1">Making good progress</p>
        </div>

        {/* Needs Attention */}
        <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg shadow-sm border border-red-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <AlertCircle className="w-6 h-6 text-red-600" />
            <span className="text-2xl font-bold text-red-700">{needsAttentionMavericks}</span>
          </div>
          <h3 className="text-sm font-medium text-gray-700">Needs Attention (&lt;50%)</h3>
          <p className="text-xs text-gray-600 mt-1">Requires intervention</p>
        </div>
      </div>

      {/* Pipeline Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-blue-600" />
          <div>
            <h4 className="font-semibold text-gray-900">{data.pipeline_name}</h4>
            <p className="text-sm text-gray-600">{data.total_jobs} total jobs in pipeline</p>
          </div>
        </div>
      </div>

      {/* Per-Maverick Progress */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Users className="w-5 h-5" />
            Individual Progress ({data.total_mavericks} Mavericks)
          </h3>
        </div>

        <div className="divide-y divide-gray-200">
          {data.maverick_progress
            .sort((a, b) => b.completion_percentage - a.completion_percentage)
            .map((maverick, idx) => {
              const isCompleted = maverick.completion_percentage === 100;
              const isOnTrack = maverick.completion_percentage >= 50 && maverick.completion_percentage < 100 && maverick.has_initialized;
              // Only mark as "needs attention" if jobs are initialized AND scheduled
              const needsAttention = maverick.has_initialized && maverick.has_scheduled_jobs && maverick.completion_percentage < 50;
              // If jobs aren't scheduled yet, show "Not Started"
              const notStarted = !maverick.has_initialized || !maverick.has_scheduled_jobs;

              return (
                <div
                  key={maverick.maverick_id}
                  className="p-6 hover:bg-gray-50 transition-colors cursor-pointer"
                  onClick={() => window.location.href = `/batches/${batchId}/progress/${maverick.maverick_id}`}
                >
                  <div className="flex items-center justify-between mb-3">
                    {/* Maverick Info */}
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center w-10 h-10 rounded-full bg-blue-100">
                        <span className="text-blue-700 font-bold">
                          {idx === 0 && isCompleted ? '🏆' : (idx + 1)}
                        </span>
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900">{maverick.maverick_name}</h4>
                        <p className="text-sm text-gray-600">
                          {maverick.completed_jobs} / {maverick.total_jobs} jobs completed
                        </p>
                      </div>
                    </div>

                    {/* Status Badge */}
                    <div className="flex items-center gap-3">
                      {isCompleted && (
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Completed
                        </span>
                      )}
                      {isOnTrack && !notStarted && (
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-800">
                          <Clock className="w-3 h-3 mr-1" />
                          On Track
                        </span>
                      )}
                      {needsAttention && (
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-800">
                          <AlertCircle className="w-3 h-3 mr-1" />
                          Needs Attention
                        </span>
                      )}
                      {notStarted && !isCompleted && (
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-800">
                          <Clock className="w-3 h-3 mr-1" />
                          Not Started
                        </span>
                      )}
                      <span className={`text-2xl font-bold ${getProgressTextColor(maverick.completion_percentage)}`}>
                        {Math.round(maverick.completion_percentage)}%
                      </span>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`${getProgressColor(maverick.completion_percentage)} h-3 rounded-full transition-all flex items-center justify-end pr-2`}
                      style={{ width: `${maverick.completion_percentage}%` }}
                    >
                      {maverick.completion_percentage > 10 && (
                        <span className="text-xs font-semibold text-white">
                          {maverick.completed_jobs}/{maverick.total_jobs}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
        </div>
      </div>

      {/* Top Performer Highlight */}
      {completedMavericks > 0 && (
        <div className="bg-gradient-to-r from-yellow-50 to-amber-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-center gap-3">
            <Award className="w-8 h-8 text-yellow-600" />
            <div>
              <h3 className="font-bold text-gray-900">🏆 Top Performer</h3>
              <p className="text-sm text-gray-600">
                {data.maverick_progress.find(m => m.completion_percentage === 100)?.maverick_name || 'N/A'}
                {' '}completed all {data.total_jobs} jobs!
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
