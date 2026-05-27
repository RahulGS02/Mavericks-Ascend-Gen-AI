"use client";

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  Users, BookOpen, Calendar, TrendingUp, CheckCircle,
  Circle, Clock, Trophy, Medal, Award, Target,
  ChevronLeft, ArrowLeft
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';
import { useAuthStore } from '@/store/authStore';

interface ProgressStep {
  order: number;
  job_id: string;
  title: string;
  type: string;
  is_optional: boolean;
  status: string;
  completion_percentage: number;
  score: number | null;
  is_current: boolean;
}

interface LeaderboardEntry {
  id: string;
  name: string;
  average_score: number;
  total_assessments: number;
  passed_count: number;
  overall_progress: number;
  rank: number;
  is_current_user: boolean;
}

interface BatchDetail {
  batch_id: string;
  batch_name: string;
  pipeline_name: string;
  trainer_name: string;
  status: string;
  start_date: string | null;
  end_date: string | null;
  total_students: number;
  my_progress: {
    overall_completion: number;
    completed_jobs: number;
    total_jobs: number;
    steps: ProgressStep[];
  };
  leaderboard: LeaderboardEntry[];
}

type Tab = 'progress' | 'leaderboard';

export default function BatchDetailPage() {
  const router = useRouter();
  const params = useParams();
  const batchId = params.batchId as string;
  const { user, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<BatchDetail | null>(null);
  const [tab, setTab] = useState<Tab>('progress');

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'maverick') {
      router.push('/login');
      return;
    }
    if (batchId) fetchBatchDetail();
  }, [isAuthenticated, user, batchId, router]);

  const fetchBatchDetail = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get(`/maverick/dashboard/batch/${batchId}`);
      setData(res.data);
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to load batch details';
      toast.error(msg);
      router.push('/student/batch');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto" />
            <p className="mt-4 text-gray-600">Loading batch details...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!data) return null;

  const { my_progress, leaderboard } = data;

  const getStepIcon = (step: ProgressStep) => {
    if (step.status === 'COMPLETED') return <CheckCircle className="w-6 h-6 text-green-600" />;
    if (step.is_current) return <Clock className="w-6 h-6 text-blue-600 animate-pulse" />;
    if (step.status === 'SKIPPED') return <Circle className="w-6 h-6 text-gray-300" />;
    return <Circle className="w-6 h-6 text-gray-300" />;
  };

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Trophy className="w-5 h-5 text-yellow-500" />;
    if (rank === 2) return <Medal className="w-5 h-5 text-gray-400" />;
    if (rank === 3) return <Medal className="w-5 h-5 text-orange-500" />;
    return null;
  };

  const getRankStyle = (rank: number) => {
    if (rank === 1) return 'bg-yellow-50 border-yellow-300';
    if (rank === 2) return 'bg-gray-50 border-gray-300';
    if (rank === 3) return 'bg-orange-50 border-orange-300';
    return 'bg-white border-gray-200';
  };

  return (
    <DashboardLayout>
      <div className="p-6 max-w-5xl mx-auto space-y-6">
        {/* Back link */}
        <button
          onClick={() => router.push('/student/batch')}
          className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          All My Batches
        </button>

        {/* Batch Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg p-6 text-white">
          <h1 className="text-2xl font-bold mb-4">{data.batch_name}</h1>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <BookOpen className="w-4 h-4 opacity-80" />
              <div>
                <div className="text-blue-200 text-xs">Pipeline</div>
                <div className="font-medium">{data.pipeline_name}</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 opacity-80" />
              <div>
                <div className="text-blue-200 text-xs">Trainer</div>
                <div className="font-medium">{data.trainer_name}</div>
              </div>
            </div>
            {data.start_date && (
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 opacity-80" />
                <div>
                  <div className="text-blue-200 text-xs">Started</div>
                  <div className="font-medium">
                    {new Date(data.start_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                  </div>
                </div>
              </div>
            )}
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 opacity-80" />
              <div>
                <div className="text-blue-200 text-xs">Students</div>
                <div className="font-medium">{data.total_students}</div>
              </div>
            </div>
          </div>
        </div>

        {/* Progress Summary Cards */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white rounded-lg border border-gray-200 p-4 text-center">
            <div className="text-3xl font-bold text-blue-600">{my_progress.overall_completion}%</div>
            <div className="text-sm text-gray-500 mt-1">Overall Progress</div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4 text-center">
            <div className="text-3xl font-bold text-green-600">
              {my_progress.completed_jobs}/{my_progress.total_jobs}
            </div>
            <div className="text-sm text-gray-500 mt-1">Jobs Completed</div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4 text-center">
            <div className="text-3xl font-bold text-purple-600">
              #{leaderboard.find(e => e.is_current_user)?.rank ?? '–'}
            </div>
            <div className="text-sm text-gray-500 mt-1">Your Rank</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setTab('progress')}
              className={`flex-1 py-3 text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
                tab === 'progress'
                  ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <TrendingUp className="w-4 h-4" />
              My Progress
            </button>
            <button
              onClick={() => setTab('leaderboard')}
              className={`flex-1 py-3 text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
                tab === 'leaderboard'
                  ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Trophy className="w-4 h-4" />
              Leaderboard
            </button>
          </div>

          {/* Tab: My Progress */}
          {tab === 'progress' && (
            <div className="p-6">
              {my_progress.steps.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No pipeline jobs found for this batch.</p>
              ) : (
                <div className="space-y-3">
                  {my_progress.steps.map((step, index) => (
                    <div key={step.job_id} className="flex items-start gap-4">
                      {/* Step indicator + connector */}
                      <div className="flex flex-col items-center">
                        <div className="flex-shrink-0">{getStepIcon(step)}</div>
                        {index < my_progress.steps.length - 1 && (
                          <div className={`w-0.5 h-8 mt-1 ${step.status === 'COMPLETED' ? 'bg-green-300' : 'bg-gray-200'}`} />
                        )}
                      </div>

                      {/* Step content */}
                      <div className={`flex-1 pb-2 rounded-lg px-4 py-3 border ${
                        step.is_current
                          ? 'border-blue-400 bg-blue-50'
                          : step.status === 'COMPLETED'
                          ? 'border-green-200 bg-green-50'
                          : 'border-gray-200 bg-gray-50'
                      }`}>
                        <div className="flex items-center justify-between flex-wrap gap-2">
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-gray-900">
                              {step.order}. {step.title}
                            </span>
                            <span className={`text-xs px-2 py-0.5 rounded-full ${
                              step.type === 'TRAINING' ? 'bg-blue-100 text-blue-700' :
                              step.type === 'ASSESSMENT' ? 'bg-purple-100 text-purple-700' :
                              'bg-gray-100 text-gray-600'
                            }`}>
                              {step.type}
                            </span>
                            {step.is_optional && (
                              <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700">Optional</span>
                            )}
                            {step.is_current && (
                              <span className="text-xs px-2 py-0.5 rounded-full bg-blue-600 text-white">Current</span>
                            )}
                          </div>
                          <div className="flex items-center gap-3 text-sm">
                            {step.score !== null && (
                              <span className="font-semibold text-purple-700">Score: {step.score}%</span>
                            )}
                            <span className="font-semibold text-gray-700">{step.completion_percentage}%</span>
                          </div>
                        </div>
                        <div className="mt-2 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className={`h-1.5 rounded-full ${
                              step.status === 'COMPLETED' ? 'bg-green-500' :
                              step.is_current ? 'bg-blue-500' : 'bg-gray-300'
                            }`}
                            style={{ width: `${step.completion_percentage}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Tab: Leaderboard */}
          {tab === 'leaderboard' && (
            <div className="p-6">
              {leaderboard.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No students in this batch yet.</p>
              ) : (
                <div className="space-y-3">
                  {leaderboard.map((entry) => (
                    <div
                      key={entry.id}
                      className={`border rounded-lg p-4 transition-all ${
                        entry.is_current_user
                          ? 'border-blue-500 bg-blue-50 shadow-sm'
                          : `${getRankStyle(entry.rank)} hover:border-gray-300`
                      }`}
                    >
                      <div className="flex items-center justify-between gap-4">
                        {/* Rank + Name */}
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold border-2 text-sm flex-shrink-0 ${
                            entry.rank === 1 ? 'bg-yellow-100 border-yellow-300 text-yellow-700' :
                            entry.rank === 2 ? 'bg-gray-100 border-gray-300 text-gray-600' :
                            entry.rank === 3 ? 'bg-orange-100 border-orange-300 text-orange-700' :
                            'bg-blue-50 border-blue-200 text-blue-700'
                          }`}>
                            {entry.rank <= 3 ? getRankIcon(entry.rank) : `#${entry.rank}`}
                          </div>
                          <div className="min-w-0">
                            <div className="flex items-center gap-1 flex-wrap">
                              <span className="font-semibold text-gray-900 truncate">{entry.name}</span>
                              {entry.is_current_user && (
                                <span className="text-xs text-blue-600 font-medium">(You)</span>
                              )}
                            </div>
                            {entry.rank === 1 && (
                              <p className="text-xs text-yellow-600 font-medium">Top Performer</p>
                            )}
                          </div>
                        </div>

                        {/* Stats */}
                        <div className="flex items-center gap-6 text-sm flex-shrink-0">
                          <div className="text-center">
                            <div className="text-xs text-gray-500 mb-0.5">Progress</div>
                            <div className="font-semibold text-gray-800">{entry.overall_progress}%</div>
                          </div>
                          <div className="text-center">
                            <div className="text-xs text-gray-500 mb-0.5">Assessments</div>
                            <div className="font-semibold text-gray-800">
                              {entry.passed_count}/{entry.total_assessments}
                            </div>
                          </div>
                          {entry.rank <= 10 && (
                            <div className="hidden sm:flex items-center gap-1 text-green-600">
                              <Target className="w-3.5 h-3.5" />
                              <span className="text-xs font-medium">Top 10</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              <p className="mt-4 text-xs text-gray-400 text-center">
                Rankings based on assessment scores (70%) + overall progress (30%).
              </p>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
