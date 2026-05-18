"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Award, CheckCircle, XCircle, TrendingUp } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';
import { useAuthStore } from '@/store/authStore';

interface AssessmentData {
  assessments: {
    average_score: number;
    total_taken: number;
    passed_count: number;
    scores: Array<{
      assessment_title: string;
      score_percentage: number;
      marks: string;
      passed: boolean;
      attempt_number: number;
      evaluated_at: string;
    }>;
  };
}

export default function StudentAssessmentsPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [assessmentData, setAssessmentData] = useState<AssessmentData | null>(null);

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'maverick') {
      router.push('/login');
      return;
    }
    fetchAssessments();
  }, [isAuthenticated, user, router]);

  const fetchAssessments = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/maverick/dashboard/overview');
      setAssessmentData(response.data);
    } catch (error) {
      console.error('Failed to fetch assessments:', error);
      toast.error('Failed to load assessment data');
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
            <p className="mt-4 text-gray-600">Loading assessments...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!assessmentData?.assessments) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No Assessment Data</h2>
            <p className="text-gray-600">You haven't taken any assessments yet.</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const { assessments } = assessmentData;

  return (
    <DashboardLayout>
      <div className="p-6 max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">My Assessment Scores</h1>

          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-4xl font-bold text-blue-600 mb-1">{assessments.average_score}%</div>
              <div className="text-sm text-gray-600">Average Score</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-4xl font-bold text-green-600 mb-1">{assessments.passed_count}</div>
              <div className="text-sm text-gray-600">Assessments Passed</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-4xl font-bold text-purple-600 mb-1">{assessments.total_taken}</div>
              <div className="text-sm text-gray-600">Total Attempts</div>
            </div>
          </div>
        </div>

        {/* Scores List */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Award className="w-6 h-6 text-yellow-600" />
            All Assessment Attempts
          </h2>

          {assessments.scores.length === 0 ? (
            <p className="text-center text-gray-500 py-8">No assessment scores available</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Assessment</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Score</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Marks</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Attempt</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {assessments.scores.map((score, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">
                        {score.assessment_title}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`text-lg font-bold ${
                          score.passed ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {score.score_percentage}%
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {score.marks}
                      </td>
                      <td className="px-4 py-3">
                        {score.passed ? (
                          <span className="flex items-center gap-1 text-green-600 text-sm font-medium">
                            <CheckCircle className="w-4 h-4" />
                            Passed
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-red-600 text-sm font-medium">
                            <XCircle className="w-4 h-4" />
                            Failed
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        Attempt {score.attempt_number}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {new Date(score.evaluated_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
