"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Users, Trophy, Medal, TrendingUp, Award, Target, Calendar, BookOpen } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';
import { useAuthStore } from '@/store/authStore';

interface BatchMate {
  id: string;
  name: string;
  email: string;
  average_score: number;
  total_assessments: number;
  passed_count: number;
  overall_progress: number;
  rank: number;
  is_current_user: boolean;
}

interface BatchData {
  batch_id: string;
  batch_name: string;
  pipeline_name: string;
  trainer_name: string;
  start_date: string;
  total_students: number;
  batch_mates: BatchMate[];
}

export default function StudentBatchPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [batchData, setBatchData] = useState<BatchData | null>(null);

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'maverick') {
      router.push('/login');
      return;
    }
    fetchBatchData();
  }, [isAuthenticated, user, router]);

  const fetchBatchData = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/maverick/batch/leaderboard');
      setBatchData(response.data);
    } catch (error) {
      console.error('Failed to fetch batch data:', error);
      toast.error('Failed to load batch information');
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
            <p className="mt-4 text-gray-600">Loading batch information...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!batchData) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
            <Users className="w-12 h-12 text-yellow-600 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No Batch Assigned</h2>
            <p className="text-gray-600">You are not assigned to any batch yet. Please contact HR.</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Trophy className="w-6 h-6 text-yellow-500" />;
    if (rank === 2) return <Medal className="w-6 h-6 text-gray-400" />;
    if (rank === 3) return <Medal className="w-6 h-6 text-orange-600" />;
    return null;
  };

  const getRankBadgeColor = (rank: number) => {
    if (rank === 1) return 'bg-yellow-100 text-yellow-700 border-yellow-300';
    if (rank === 2) return 'bg-gray-100 text-gray-700 border-gray-300';
    if (rank === 3) return 'bg-orange-100 text-orange-700 border-orange-300';
    return 'bg-blue-100 text-blue-700 border-blue-300';
  };

  return (
    <DashboardLayout>
      <div className="p-6 max-w-6xl mx-auto space-y-6">
        {/* Batch Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-lg p-6 text-white">
          <h1 className="text-3xl font-bold mb-4">{batchData.batch_name}</h1>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="flex items-center gap-2">
              <BookOpen className="w-5 h-5" />
              <div>
                <div className="text-blue-100 text-xs">Pipeline</div>
                <div className="font-semibold">{batchData.pipeline_name}</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              <div>
                <div className="text-blue-100 text-xs">Trainer</div>
                <div className="font-semibold">{batchData.trainer_name}</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              <div>
                <div className="text-blue-100 text-xs">Started</div>
                <div className="font-semibold">
                  {new Date(batchData.start_date).toLocaleDateString('en-US', { 
                    month: 'short', 
                    year: 'numeric' 
                  })}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              <div>
                <div className="text-blue-100 text-xs">Total Students</div>
                <div className="font-semibold">{batchData.total_students}</div>
              </div>
            </div>
          </div>
        </div>

        {/* Leaderboard */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-blue-600" />
            Batch Rankings
          </h2>

          <div className="space-y-3">
            {batchData.batch_mates.map((mate) => (
              <div
                key={mate.id}
                className={`border rounded-lg p-4 transition-all ${
                  mate.is_current_user
                    ? 'border-blue-500 bg-blue-50 shadow-md'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  {/* Left: Rank and Name */}
                  <div className="flex items-center gap-4 flex-1">
                    {/* Rank Badge */}
                    <div className={`flex items-center justify-center w-12 h-12 border-2 rounded-full ${getRankBadgeColor(mate.rank)}`}>
                      {mate.rank <= 3 ? (
                        getRankIcon(mate.rank)
                      ) : (
                        <span className="text-xl font-bold">#{mate.rank}</span>
                      )}
                    </div>

                    {/* Name */}
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {mate.name}
                          {mate.is_current_user && (
                            <span className="ml-2 text-sm text-blue-600 font-normal">(You)</span>
                          )}
                        </h3>
                      </div>
                      {mate.rank === 1 && (
                        <p className="text-sm text-yellow-600 font-medium">Top Performer</p>
                      )}
                    </div>
                  </div>

                  {/* Right: Stats (No Scores) */}
                  <div className="flex items-center gap-6 text-sm">
                    <div className="text-center">
                      <div className="text-gray-600 text-xs mb-1">Progress</div>
                      <div className="font-semibold text-gray-900">{mate.overall_progress}%</div>
                    </div>
                    <div className="text-center">
                      <div className="text-gray-600 text-xs mb-1">Assessments</div>
                      <div className="font-semibold text-gray-900">
                        {mate.passed_count}/{mate.total_assessments}
                      </div>
                    </div>
                    {mate.rank <= 10 && (
                      <div className="flex items-center gap-1 text-green-600">
                        <Target className="w-4 h-4" />
                        <span className="text-xs font-medium">Top 10</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Info Note */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-900">
          <p className="font-medium mb-1">Ranking Information</p>
          <p>Rankings are based on overall performance including assessment scores and progress completion. Keep up the great work!</p>
        </div>
      </div>
    </DashboardLayout>
  );
}
