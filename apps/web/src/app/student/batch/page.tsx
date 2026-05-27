"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Users, BookOpen, Calendar, TrendingUp, CheckCircle,
  ChevronRight, GraduationCap, Clock
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';
import { useAuthStore } from '@/store/authStore';

interface BatchSummary {
  batch_id: string;
  batch_name: string;
  pipeline_name: string;
  status: string;
  start_date: string | null;
  end_date: string | null;
  overall_progress: number;
  completed_jobs: number;
  total_jobs: number;
  is_current: boolean;
}

const STATUS_STYLES: Record<string, string> = {
  ACTIVE: 'bg-green-100 text-green-700',
  PLANNED: 'bg-blue-100 text-blue-700',
  COMPLETED: 'bg-gray-100 text-gray-600',
  ON_HOLD: 'bg-yellow-100 text-yellow-700',
  CANCELLED: 'bg-red-100 text-red-700',
  ARCHIVED: 'bg-gray-100 text-gray-500',
};

export default function MyBatchesPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [batches, setBatches] = useState<BatchSummary[]>([]);

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'maverick') {
      router.push('/login');
      return;
    }
    fetchBatches();
  }, [isAuthenticated, user, router]);

  const fetchBatches = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/maverick/dashboard/batches');
      setBatches(res.data.batches);
    } catch {
      toast.error('Failed to load batches');
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
            <p className="mt-4 text-gray-600">Loading your batches...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (batches.length === 0) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-8 text-center">
            <GraduationCap className="w-14 h-14 text-yellow-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No Batches Assigned</h2>
            <p className="text-gray-600">You have not been assigned to any batch yet. Please contact HR.</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6 max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Batches</h1>
          <p className="text-gray-500 mt-1">
            You are enrolled in {batches.length} batch{batches.length !== 1 ? 'es' : ''}.
            Click any batch to view your progress and rankings.
          </p>
        </div>

        {/* Batch Cards */}
        <div className="space-y-4">
          {batches.map((batch) => (
            <div
              key={batch.batch_id}
              onClick={() => router.push(`/student/batch/${batch.batch_id}`)}
              className={`bg-white rounded-xl border-2 p-5 cursor-pointer hover:shadow-md transition-all ${
                batch.is_current
                  ? 'border-blue-500 shadow-sm'
                  : 'border-gray-200 hover:border-blue-300'
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                {/* Left info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <h2 className="text-lg font-semibold text-gray-900 truncate">
                      {batch.batch_name}
                    </h2>
                    {batch.is_current && (
                      <span className="px-2 py-0.5 text-xs font-medium bg-blue-600 text-white rounded-full">
                        Current
                      </span>
                    )}
                    <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${STATUS_STYLES[batch.status] ?? 'bg-gray-100 text-gray-600'}`}>
                      {batch.status}
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-4 text-sm text-gray-600 mt-2">
                    <span className="flex items-center gap-1">
                      <BookOpen className="w-4 h-4 text-blue-500" />
                      {batch.pipeline_name}
                    </span>
                    {batch.start_date && (
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4 text-green-500" />
                        {new Date(batch.start_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                        {batch.end_date && ` – ${new Date(batch.end_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}`}
                      </span>
                    )}
                    <span className="flex items-center gap-1">
                      <CheckCircle className="w-4 h-4 text-purple-500" />
                      {batch.completed_jobs}/{batch.total_jobs} jobs
                    </span>
                  </div>

                  {/* Progress bar */}
                  <div className="mt-3">
                    <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                      <span>Progress</span>
                      <span className="font-semibold text-gray-700">{batch.overall_progress}%</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-2 bg-blue-500 rounded-full transition-all"
                        style={{ width: `${batch.overall_progress}%` }}
                      />
                    </div>
                  </div>
                </div>

                {/* Right arrow */}
                <div className="flex items-center self-center">
                  <ChevronRight className="w-6 h-6 text-gray-400" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
