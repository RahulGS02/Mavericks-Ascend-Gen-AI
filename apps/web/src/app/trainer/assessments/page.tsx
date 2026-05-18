"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  FileText,
  Search,
  Filter,
  Download,
  Upload,
  Edit,
  CheckCircle,
  XCircle,
  Clock,
  Users,
  Plus,
  Eye,
  Calendar
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';

interface Assessment {
  id: string;
  title: string;
  description?: string;
  batch_id: string;
  batch_name: string;
  job_id: string;
  job_name: string;
  max_marks: number;
  passing_marks: number;
  duration_minutes: number;
  scheduled_date?: string;
  assessment_link?: string;
  created_at: string;
  total_attempts: number;
  evaluated_count: number;
  pending_count: number;
  pass_rate?: number;
}

interface Batch {
  id: string;
  name: string;
  status: string;
}

export default function TrainerAssessmentsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [batches, setBatches] = useState<Batch[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBatch, setSelectedBatch] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'pending' | 'evaluated'>('all');

  useEffect(() => {
    fetchBatches();
    fetchAssessments();
  }, []);

  const fetchBatches = async () => {
    try {
      const response = await apiClient.get('/trainer/dashboard/batches');
      setBatches(response.data.batches || []);
    } catch (error) {
      console.error('Failed to fetch batches:', error);
    }
  };

  const fetchAssessments = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/assessments/', {
        params: {
          page: 1,
          page_size: 100
        }
      });
      
      // Filter to only assessments in trainer's batches
      const batchIds = batches.map(b => b.id);
      const trainerAssessments = response.data.assessments.filter((a: Assessment) =>
        batchIds.includes(a.batch_id)
      );
      
      setAssessments(trainerAssessments);
    } catch (error: any) {
      console.error('Failed to fetch assessments:', error);
      toast.error('Failed to load assessments');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (batches.length > 0) {
      fetchAssessments();
    }
  }, [batches]);

  const filteredAssessments = assessments.filter((assessment) => {
    const matchesSearch =
      assessment.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      assessment.batch_name?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesBatch = !selectedBatch || assessment.batch_id === selectedBatch;
    
    const matchesStatus =
      filterStatus === 'all' ||
      (filterStatus === 'pending' && assessment.pending_count > 0) ||
      (filterStatus === 'evaluated' && assessment.pending_count === 0 && assessment.evaluated_count > 0);

    return matchesSearch && matchesBatch && matchesStatus;
  });

  const getStatusBadge = (assessment: Assessment) => {
    if (assessment.pending_count > 0) {
      return (
        <span className="px-2 py-1 text-xs font-medium bg-amber-100 text-amber-800 rounded-full">
          {assessment.pending_count} Pending
        </span>
      );
    } else if (assessment.evaluated_count > 0) {
      return (
        <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
          Evaluated
        </span>
      );
    } else {
      return (
        <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">
          No Attempts
        </span>
      );
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not scheduled';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Assessments</h1>
          <p className="text-gray-600">Manage assessments, enter marks, and evaluate student performance</p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Assessments</p>
                <p className="text-2xl font-bold text-gray-900">{assessments.length}</p>
              </div>
              <FileText className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Pending Evaluation</p>
                <p className="text-2xl font-bold text-amber-600">
                  {assessments.reduce((sum, a) => sum + a.pending_count, 0)}
                </p>
              </div>
              <Clock className="w-8 h-8 text-amber-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Evaluated</p>
                <p className="text-2xl font-bold text-green-600">
                  {assessments.reduce((sum, a) => sum + a.evaluated_count, 0)}
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Attempts</p>
                <p className="text-2xl font-bold text-gray-900">
                  {assessments.reduce((sum, a) => sum + a.total_attempts, 0)}
                </p>
              </div>
              <Users className="w-8 h-8 text-blue-600" />
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search assessments..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Batch Filter */}
            <select
              value={selectedBatch}
              onChange={(e) => setSelectedBatch(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Batches</option>
              {batches.map((batch) => (
                <option key={batch.id} value={batch.id}>
                  {batch.name}
                </option>
              ))}
            </select>

            {/* Status Filter */}
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as any)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value="pending">Pending Evaluation</option>
              <option value="evaluated">Evaluated</option>
            </select>
          </div>
        </div>

        {/* Assessments List */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
              <p className="mt-4 text-gray-600">Loading assessments...</p>
            </div>
          ) : filteredAssessments.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium">No assessments found</p>
              <p className="text-sm mt-2">
                {searchTerm || selectedBatch || filterStatus !== 'all'
                  ? 'Try adjusting your filters'
                  : 'No assessments available in your batches'}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Assessment
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Batch
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Details
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Attempts
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredAssessments.map((assessment) => (
                    <tr key={assessment.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{assessment.title}</div>
                          {assessment.scheduled_date && (
                            <div className="text-xs text-gray-500 flex items-center mt-1">
                              <Calendar className="w-3 h-3 mr-1" />
                              {formatDate(assessment.scheduled_date)}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">{assessment.batch_name || 'Unknown'}</div>
                        <div className="text-xs text-gray-500">{assessment.job_name}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-600">
                          Max: {assessment.max_marks} | Pass: {assessment.passing_marks}
                        </div>
                        <div className="text-xs text-gray-500">{assessment.duration_minutes} mins</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm">
                          <div className="text-gray-900">
                            Total: <span className="font-medium">{assessment.total_attempts}</span>
                          </div>
                          <div className="flex gap-2 mt-1">
                            <span className="text-xs text-green-600">
                              ✓ {assessment.evaluated_count}
                            </span>
                            {assessment.pending_count > 0 && (
                              <span className="text-xs text-amber-600">
                                ⏳ {assessment.pending_count}
                              </span>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {getStatusBadge(assessment)}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => router.push(`/trainer/assessments/${assessment.id}/marks`)}
                            className={`inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                              assessment.pending_count > 0
                                ? 'bg-amber-600 text-white hover:bg-amber-700'
                                : 'bg-blue-600 text-white hover:bg-blue-700'
                            }`}
                          >
                            <Edit className="w-4 h-4 mr-1" />
                            Enter Marks
                          </button>
                          <button
                            onClick={() => router.push(`/assessments/${assessment.id}`)}
                            className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            View
                          </button>
                        </div>
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
