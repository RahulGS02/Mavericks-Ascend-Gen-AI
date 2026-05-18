"use client";

import { useEffect, useState } from 'react';
import { Trophy, Award, TrendingUp, Target, Medal } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';

interface MaverickPerformance {
  id: string;
  name: string;
  email: string;
  rank: number;
  average_score: number;
  total_assessments: number;
  passed_count: number;
}

interface LeaderboardData {
  batch_id: string;
  batch_name: string;
  pipeline_name: string;
  trainer_name: string;
  start_date: string;
  total_students: number;
  batch_mates: MaverickPerformance[];
}

interface Props {
  batchId: string;
  batchName: string;
}

export default function BatchLeaderboardTab({ batchId, batchName }: Props) {
  const [loading, setLoading] = useState(true);
  const [leaderboard, setLeaderboard] = useState<LeaderboardData | null>(null);

  useEffect(() => {
    fetchLeaderboard();
  }, [batchId]);

  const fetchLeaderboard = async () => {
    setLoading(true);
    try {
      // Using a dedicated batch leaderboard endpoint for HR/trainers
      const response = await apiClient.get(`/batches/${batchId}/leaderboard`);
      setLeaderboard(response.data);
    } catch (error: any) {
      console.error('Failed to fetch leaderboard:', error);
      toast.error('Failed to load leaderboard');
    } finally {
      setLoading(false);
    }
  };

  const getRankBadge = (rank: number) => {
    if (rank === 1) {
      return (
        <div className="flex items-center gap-2 px-3 py-1 bg-gradient-to-r from-yellow-400 to-yellow-500 text-white rounded-full font-bold">
          <Trophy className="w-5 h-5" />
          <span>#{rank}</span>
        </div>
      );
    } else if (rank === 2) {
      return (
        <div className="flex items-center gap-2 px-3 py-1 bg-gradient-to-r from-gray-300 to-gray-400 text-gray-900 rounded-full font-bold">
          <Medal className="w-5 h-5" />
          <span>#{rank}</span>
        </div>
      );
    } else if (rank === 3) {
      return (
        <div className="flex items-center gap-2 px-3 py-1 bg-gradient-to-r from-orange-400 to-orange-500 text-white rounded-full font-bold">
          <Medal className="w-5 h-5" />
          <span>#{rank}</span>
        </div>
      );
    } else {
      return (
        <div className="flex items-center gap-2 px-3 py-1 bg-gray-100 text-gray-700 rounded-full font-semibold">
          <span>#{rank}</span>
        </div>
      );
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!leaderboard || leaderboard.batch_mates.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
        <Trophy className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No Performance Data Yet</h3>
        <p className="text-gray-600">
          Leaderboard will be available once mavericks complete assessments
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Target className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-600">Total Students</div>
              <div className="text-2xl font-bold text-gray-900">{leaderboard.total_students}</div>
            </div>
          </div>
        </div>

        {/* Add more stat cards here if needed */}
      </div>

      {/* Leaderboard Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50">
          <div className="flex items-center gap-3">
            <Trophy className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-bold text-gray-900">Batch Leaderboard</h2>
          </div>
          <p className="text-sm text-gray-600 mt-1">
            Rankings based on assessment performance
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rank
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Maverick
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Assessments
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Pass Rate
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Score
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {leaderboard.batch_mates.map((maverick, index) => {
                const passRate = maverick.total_assessments > 0
                  ? (maverick.passed_count / maverick.total_assessments) * 100
                  : 0;

                return (
                  <tr
                    key={maverick.id}
                    className={`hover:bg-gray-50 transition-colors ${
                      index < 3 ? 'bg-yellow-50/30' : ''
                    }`}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getRankBadge(maverick.rank)}
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <div className="font-semibold text-gray-900">{maverick.name}</div>
                        <div className="text-sm text-gray-500">{maverick.email}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="text-sm font-medium text-gray-900">
                        {maverick.passed_count}/{maverick.total_assessments}
                      </div>
                      <div className="text-xs text-gray-500">completed</div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className={`text-lg font-bold ${getScoreColor(passRate)}`}>
                        {passRate.toFixed(0)}%
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className={`text-lg font-bold ${getScoreColor(maverick.average_score)}`}>
                        {maverick.average_score.toFixed(1)}%
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
