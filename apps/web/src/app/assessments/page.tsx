"use client";

import { useEffect, useState } from 'react';
import { Search, ClipboardList, Eye, TrendingUp, Users, CheckCircle, XCircle, Info, Calendar } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import Link from 'next/link';
import DashboardLayout from '@/components/DashboardLayout';

interface Assessment {
  id: string;
  title: string;  // Changed from 'name' to 'title' to match API
  description?: string;
  job_id: string;
  batch_id: string;
  max_marks: number;
  passing_marks: number;
  duration_minutes?: number;
  scheduled_date?: string;
  total_attempts: number;
  passed_count: number;  // Changed from 'passed_attempts' to 'passed_count'
  failed_count: number;
  created_at: string;
  updated_at?: string;
  created_by: string;
}

interface AssessmentStats {
  total_assessments: number;
  assessments_not_used: number;
  mavericks_need_retake: number;
  scheduled_assessments: number;
  completion_rate: number;
  overall_pass_rate: number;
  total_attempts: number;
  passed_attempts: number;
}

export default function AssessmentsPage() {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [stats, setStats] = useState<AssessmentStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchAssessments();
    fetchStatistics();
  }, [searchTerm]);

  const fetchAssessments = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/assessments/', {
        params: {
          page: 1,
          page_size: 100,
          search: searchTerm || undefined,
        }
      });
      setAssessments(response.data?.assessments || []);
    } catch (error) {
      console.error('Failed to fetch assessments:', error);
      toast.error('Failed to load assessments');
      setAssessments([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await apiClient.get('/assessments/statistics');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch assessment statistics:', error);
    }
  };

  const filteredAssessments = assessments.filter(assessment =>
    assessment.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    assessment.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Use API statistics or fallback to defaults
  const displayStats = stats || {
    total_assessments: 0,
    assessments_not_used: 0,
    mavericks_need_retake: 0,
    scheduled_assessments: 0,
    completion_rate: 0,
    overall_pass_rate: 0,
    total_attempts: 0,
    passed_attempts: 0,
  };

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-3xl font-bold text-blue-900 mb-2">Assessments</h1>
              <p className="text-gray-600">View and manage assessment results</p>
            </div>
          </div>

          {/* Info Notice - Pipeline-Driven Workflow */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-blue-900 mb-1">
                Pipeline-Driven Assessment Creation
              </h3>
              <p className="text-sm text-blue-800">
                Assessments are created through the <strong>Batch Timeline</strong> when scheduling pipeline jobs.
                Go to <Link href="/batches" className="underline font-medium hover:text-blue-900">Batches</Link> →
                Select a batch → Timeline tab → Schedule an ASSESSMENT job.
              </p>
            </div>
            <Link
              href="/batches"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors whitespace-nowrap"
            >
              <Calendar className="w-4 h-4 mr-2" />
              Go to Batches
            </Link>
          </div>
        </div>

        {/* Stats Cards - ACTIONABLE METRICS */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          {/* Card 1: Total Assessments */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Assessments</p>
                <p className="text-2xl font-bold text-blue-900">{displayStats.total_assessments}</p>
                <p className="text-xs text-gray-500 mt-1">{displayStats.assessments_not_used} not being used</p>
              </div>
              <ClipboardList className="w-8 h-8 text-blue-500" />
            </div>
          </div>

          {/* Card 2: Mavericks Need Retake (ACTIONABLE!) */}
          <div className={`bg-white rounded-lg shadow-sm border-2 p-4 ${displayStats.mavericks_need_retake > 0 ? 'border-red-300 bg-red-50' : 'border-gray-200'}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 font-medium">Need Retake</p>
                <p className={`text-2xl font-bold ${displayStats.mavericks_need_retake > 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {displayStats.mavericks_need_retake}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {displayStats.mavericks_need_retake > 0 ? 'failed their last attempt' : 'all mavericks passed!'}
                </p>
              </div>
              <Users className={`w-8 h-8 ${displayStats.mavericks_need_retake > 0 ? 'text-red-500' : 'text-green-500'}`} />
            </div>
          </div>

          {/* Card 3: Completion Rate (ACTIONABLE!) */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Completion Rate</p>
                <p className={`text-2xl font-bold ${displayStats.completion_rate >= 80 ? 'text-green-600' : displayStats.completion_rate >= 50 ? 'text-orange-600' : 'text-red-600'}`}>
                  {displayStats.completion_rate}%
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {displayStats.scheduled_assessments} scheduled
                </p>
              </div>
              <TrendingUp className={`w-8 h-8 ${displayStats.completion_rate >= 80 ? 'text-green-500' : 'text-orange-500'}`} />
            </div>
          </div>

          {/* Card 4: Overall Pass Rate */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Overall Pass Rate</p>
                <p className={`text-2xl font-bold ${displayStats.overall_pass_rate >= 70 ? 'text-green-600' : displayStats.overall_pass_rate >= 50 ? 'text-orange-600' : 'text-red-600'}`}>
                  {displayStats.overall_pass_rate}%
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {displayStats.passed_attempts} / {displayStats.total_attempts} passed
                </p>
              </div>
              <CheckCircle className={`w-8 h-8 ${displayStats.overall_pass_rate >= 70 ? 'text-green-500' : 'text-orange-500'}`} />
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search assessments by title or description..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Assessments Table */}
        {loading ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
            <p className="mt-4 text-gray-600">Loading assessments...</p>
          </div>
        ) : filteredAssessments.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center text-gray-500">
            <ClipboardList className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium">No assessments found</p>
            <p className="text-sm mt-2">Create your first assessment to evaluate mavericks</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Assessment</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Scheduled Date</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Marks</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Attempts</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Pass Rate</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Results</th>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredAssessments.map((assessment) => {
                    const passRate = assessment.total_attempts > 0
                      ? Math.round(((assessment.passed_count || 0) / assessment.total_attempts) * 100)
                      : 0;

                    return (
                      <tr key={assessment.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{assessment.title || 'Untitled Assessment'}</div>
                            {assessment.description && (
                              <div className="text-xs text-gray-500">{assessment.description.substring(0, 50)}{assessment.description.length > 50 ? '...' : ''}</div>
                            )}
                            {assessment.duration_minutes && (
                              <div className="text-xs text-gray-500">{assessment.duration_minutes} minutes</div>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">
                            {assessment.scheduled_date
                              ? new Date(assessment.scheduled_date).toLocaleDateString()
                              : 'Not scheduled'
                            }
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">{assessment.max_marks} marks</div>
                          <div className="text-xs text-gray-500">Pass: {assessment.passing_marks}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm font-semibold text-blue-600">{assessment.total_attempts}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <div className="w-full max-w-[100px] bg-gray-200 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full ${passRate >= 70 ? 'bg-green-500' : passRate >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
                                style={{ width: `${passRate}%` }}
                              ></div>
                            </div>
                            <span className="text-sm font-semibold">{passRate}%</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex flex-col gap-1">
                            <div className="flex items-center gap-1">
                              <CheckCircle className="w-3 h-3 text-green-600" />
                              <span className="text-xs text-green-700 font-medium">{assessment.passed_count || 0} Passed</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <XCircle className="w-3 h-3 text-red-600" />
                              <span className="text-xs text-red-700 font-medium">{assessment.failed_count || 0} Failed</span>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <Link
                            href={`/assessments/${assessment.id}`}
                            className="inline-flex items-center px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            View Details
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}