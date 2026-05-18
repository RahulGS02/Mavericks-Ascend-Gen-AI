"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { 
  ArrowLeft, Search, Download, Filter, SortAsc, SortDesc, 
  CheckCircle, XCircle, Calendar, Clock, Award, Users, User 
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';

interface AssessmentAttempt {
  id: string;
  assessment_id: string;
  maverick_id: string;
  maverick_name: string;
  maverick_email: string;
  batch_id: string;
  marks_obtained: number;
  max_marks: number;
  percentage: number;
  passed: boolean;
  feedback: string | null;
  evaluated_by: string | null;
  evaluated_at: string;
  created_at: string;
}

interface AssessmentDetail {
  assessment_id: string;
  assessment_title: string;
  assessment_description: string | null;
  duration_minutes: number | null;
  batch_id: string;
  batch_name: string;
  trainer_id: string | null;
  trainer_name: string | null;
  max_marks: number;
  passing_marks: number;
  total_attempts: number;
  attempts: AssessmentAttempt[];
}

export default function AssessmentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const assessmentId = params?.id as string;

  const [loading, setLoading] = useState(true);
  const [assessmentDetail, setAssessmentDetail] = useState<AssessmentDetail | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'marks-high' | 'marks-low' | 'name'>('marks-high');
  const [filterBy, setFilterBy] = useState<'all' | 'passed' | 'failed'>('all');

  useEffect(() => {
    if (assessmentId) {
      fetchAssessmentDetail();
    }
  }, [assessmentId]);

  const fetchAssessmentDetail = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get(`/assessments/${assessmentId}/history`);
      setAssessmentDetail(response.data);
    } catch (error) {
      console.error('Failed to fetch assessment details:', error);
      toast.error('Failed to load assessment details');
    } finally {
      setLoading(false);
    }
  };

  // Filter and sort attempts
  const filteredAttempts = assessmentDetail?.attempts
    .filter(attempt => {
      // Search filter
      const matchesSearch = 
        attempt.maverick_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        attempt.maverick_email.toLowerCase().includes(searchTerm.toLowerCase());
      
      // Pass/Fail filter
      const matchesFilter = 
        filterBy === 'all' ? true :
        filterBy === 'passed' ? attempt.passed :
        !attempt.passed;
      
      return matchesSearch && matchesFilter;
    })
    .sort((a, b) => {
      if (sortBy === 'marks-high') {
        return b.marks_obtained - a.marks_obtained;
      } else if (sortBy === 'marks-low') {
        return a.marks_obtained - b.marks_obtained;
      } else {
        return a.maverick_name.localeCompare(b.maverick_name);
      }
    }) || [];

  const handleExportToExcel = () => {
    if (!assessmentDetail) return;

    // Create CSV content
    const headers = ['Name', 'Email', 'Marks Obtained', 'Max Marks', 'Percentage', 'Status', 'Feedback', 'Evaluated At'];
    const rows = filteredAttempts.map(attempt => [
      attempt.maverick_name,
      attempt.maverick_email,
      attempt.marks_obtained,
      attempt.max_marks,
      `${attempt.percentage}%`,
      attempt.passed ? 'Passed' : 'Failed',
      attempt.feedback || 'N/A',
      new Date(attempt.evaluated_at).toLocaleString()
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    // Download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${assessmentDetail.assessment_title}_results.csv`;
    link.click();
    
    toast.success('Assessment results exported!');
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-gray-500">Loading...</div>
        </div>
      </DashboardLayout>
    );
  }

  if (!assessmentDetail) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-red-500">Assessment not found</div>
        </div>
      </DashboardLayout>
    );
  }

  const passedCount = filteredAttempts.filter(a => a.passed).length;
  const failedCount = filteredAttempts.length - passedCount;

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.back()}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{assessmentDetail.assessment_title}</h1>
              {assessmentDetail.assessment_description && (
                <p className="text-gray-600 mt-1">{assessmentDetail.assessment_description}</p>
              )}
            </div>
          </div>
          <button
            onClick={handleExportToExcel}
            className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Download className="w-4 h-4 mr-2" />
            Export to Excel
          </button>
        </div>

        {/* Assessment Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <div className="text-sm text-gray-600">Batch</div>
                <div className="text-lg font-semibold text-gray-900">{assessmentDetail.batch_name}</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-100 rounded-lg">
                <User className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <div className="text-sm text-gray-600">Trainer</div>
                <div className="text-lg font-semibold text-gray-900">
                  {assessmentDetail.trainer_name || 'Not assigned'}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-yellow-100 rounded-lg">
                <Award className="w-6 h-6 text-yellow-600" />
              </div>
              <div>
                <div className="text-sm text-gray-600">Max Marks</div>
                <div className="text-lg font-semibold text-gray-900">
                  {assessmentDetail.max_marks} (Pass: {assessmentDetail.passing_marks})
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-100 rounded-lg">
                <Clock className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <div className="text-sm text-gray-600">Duration</div>
                <div className="text-lg font-semibold text-gray-900">
                  {assessmentDetail.duration_minutes ? `${assessmentDetail.duration_minutes} min` : 'N/A'}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Summary */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg shadow-lg p-6 mb-6 text-white">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div className="text-blue-100 text-sm">Total Attempts</div>
              <div className="text-3xl font-bold">{assessmentDetail.total_attempts}</div>
            </div>
            <div>
              <div className="text-blue-100 text-sm">Passed</div>
              <div className="text-3xl font-bold text-green-300">{passedCount}</div>
            </div>
            <div>
              <div className="text-blue-100 text-sm">Failed</div>
              <div className="text-3xl font-bold text-red-300">{failedCount}</div>
            </div>
          </div>
        </div>

        {/* Filters & Search */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by name or email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Filter by Pass/Fail */}
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <select
                value={filterBy}
                onChange={(e) => setFilterBy(e.target.value as any)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
              >
                <option value="all">All Mavericks</option>
                <option value="passed">Passed Only</option>
                <option value="failed">Failed Only</option>
              </select>
            </div>

            {/* Sort */}
            <div className="relative">
              <SortAsc className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
              >
                <option value="marks-high">Marks: High to Low</option>
                <option value="marks-low">Marks: Low to High</option>
                <option value="name">Name: A to Z</option>
              </select>
            </div>
          </div>

          <div className="mt-3 text-sm text-gray-600">
            Showing <span className="font-semibold text-gray-900">{filteredAttempts.length}</span> of {assessmentDetail.total_attempts} attempts
          </div>
        </div>

        {/* Maverick Attempts Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Maverick
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Marks
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Percentage
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Evaluated
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredAttempts.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                      No attempts found
                    </td>
                  </tr>
                ) : (
                  filteredAttempts.map((attempt) => (
                    <tr key={attempt.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">{attempt.maverick_name}</div>
                        {attempt.feedback && (
                          <div className="text-xs text-gray-500 mt-1">{attempt.feedback}</div>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-600">{attempt.maverick_email}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm font-semibold text-gray-900">
                          {attempt.marks_obtained} / {attempt.max_marks}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className={`text-sm font-semibold ${
                          attempt.percentage >= 70 ? 'text-green-600' :
                          attempt.percentage >= 50 ? 'text-yellow-600' :
                          'text-red-600'
                        }`}>
                          {attempt.percentage.toFixed(1)}%
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {attempt.passed ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Passed
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            <XCircle className="w-3 h-3 mr-1" />
                            Failed
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-600">
                          {new Date(attempt.evaluated_at).toLocaleDateString()}
                        </div>
                        <div className="text-xs text-gray-500">
                          {new Date(attempt.evaluated_at).toLocaleTimeString()}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
