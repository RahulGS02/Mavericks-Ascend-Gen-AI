"use client";

import { useEffect, useState } from 'react';
import { Search, Plus, Calendar, Users, BookOpen, TrendingUp, Eye, Edit, GitBranch } from 'lucide-react';
import { batchAPI } from '@/lib/api/batch';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import Link from 'next/link';
import DashboardLayout from '@/components/DashboardLayout';

interface Batch {
  id: string;
  name: string;
  description?: string;
  category?: string;
  pipeline_id: string;
  start_date: string;
  end_date: string;
  max_capacity: number;
  current_enrollment: number;
  trainer_id?: string;
  status: 'ACTIVE' | 'COMPLETED' | 'DRAFT';
  created_at: string;
  focus_areas?: string[];
}

interface Pipeline {
  id: string;
  name: string;
  description?: string;
}

interface BatchProgress {
  [batchId: string]: number;
}

export default function BatchesPage() {
  const [batches, setBatches] = useState<Batch[]>([]);
  const [pipelines, setPipelines] = useState<Map<string, Pipeline>>(new Map());
  const [batchProgress, setBatchProgress] = useState<BatchProgress>({});
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'ACTIVE' | 'DRAFT' | 'COMPLETED'>('all');

  useEffect(() => {
    fetchBatches();
  }, [searchTerm, statusFilter]);

  const fetchBatches = async () => {
    setLoading(true);
    try {
      const response = await batchAPI.getAllBatches({
        status: statusFilter === 'all' ? undefined : statusFilter,
        page: 1,
        page_size: 100,
        search: searchTerm || undefined,
      });
      const batchesData = response?.batches || [];
      setBatches(batchesData);

      // Fetch pipeline names for all unique pipeline_ids
      const uniquePipelineIds = [...new Set(batchesData.map(b => b.pipeline_id))];
      const pipelineMap = new Map<string, Pipeline>();

      await Promise.all(
        uniquePipelineIds.map(async (pipelineId) => {
          try {
            const pipelineResponse = await apiClient.get(`/pipelines/${pipelineId}`);
            pipelineMap.set(pipelineId, pipelineResponse.data);
          } catch (err) {
            console.error(`Failed to fetch pipeline ${pipelineId}:`, err);
          }
        })
      );

      setPipelines(pipelineMap);

      // Fetch job progress for each batch
      const progressMap: BatchProgress = {};
      await Promise.all(
        batchesData.map(async (batch) => {
          try {
            const progressResponse = await apiClient.get(`/job-progress/batch/${batch.id}`);
            progressMap[batch.id] = progressResponse.data.overall_completion || 0;
          } catch (err) {
            // If no progress data, default to 0
            progressMap[batch.id] = 0;
          }
        })
      );

      setBatchProgress(progressMap);
    } catch (error) {
      console.error('Failed to fetch batches:', error);
      toast.error('Failed to load batches');
      setBatches([]);
    } finally {
      setLoading(false);
    }
  };

  const getProgress = (batchId: string) => {
    // Return actual job progress if available, otherwise 0
    return Math.round(batchProgress[batchId] || 0);
  };

  const filteredBatches = batches.filter(batch =>
    batch.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    batch.category?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const stats = {
    total: batches.length,
    active: batches.filter(b => b.status === 'ACTIVE').length,
    draft: batches.filter(b => b.status === 'DRAFT').length,
    completed: batches.filter(b => b.status === 'COMPLETED').length,
    totalEnrolled: batches.reduce((sum, b) => sum + b.current_enrollment, 0),
    totalCapacity: batches.reduce((sum, b) => sum + b.max_capacity, 0),
  };

  const avgUtilization = stats.totalCapacity > 0 
    ? Math.round((stats.totalEnrolled / stats.totalCapacity) * 100) 
    : 0;

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-blue-900 mb-2">Batches</h1>
            <p className="text-gray-600">Manage training batches, enrollments, and progress tracking</p>
          </div>
          <Link
            href="/batches/create"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5 mr-2" />
            Create Batch
          </Link>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-600">Total</div>
            <div className="text-2xl font-bold text-blue-900">{stats.total}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-600">Active</div>
            <div className="text-2xl font-bold text-green-600">{stats.active}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-600">Draft</div>
            <div className="text-2xl font-bold text-yellow-600">{stats.draft}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-600">Completed</div>
            <div className="text-2xl font-bold text-purple-600">{stats.completed}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-600">Enrolled</div>
            <div className="text-2xl font-bold text-orange-600">{stats.totalEnrolled}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-600">Utilization</div>
            <div className="text-2xl font-bold text-indigo-600">{avgUtilization}%</div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by batch name or category..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as any)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="ACTIVE">Active</option>
              <option value="DRAFT">Draft</option>
              <option value="COMPLETED">Completed</option>
            </select>
          </div>
        </div>

        {/* Batches Grid */}
        {loading ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
            <p className="mt-4 text-gray-600">Loading batches...</p>
          </div>
        ) : filteredBatches.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center text-gray-500">
            <BookOpen className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium">No batches found</p>
            <p className="text-sm mt-2">Create a new batch to get started</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredBatches.map((batch) => {
              const progress = getProgress(batch.id);
              const utilization = Math.round((batch.current_enrollment / batch.max_capacity) * 100);

              return (
                <div key={batch.id} className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-lg transition-shadow">
                  {/* Header */}
                  <div className="p-6 border-b border-gray-200">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 flex-1">{batch.name}</h3>
                      {batch.status === 'ACTIVE' && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                          Active
                        </span>
                      )}
                      {batch.status === 'DRAFT' && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                          Draft
                        </span>
                      )}
                      {batch.status === 'COMPLETED' && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">
                          Completed
                        </span>
                      )}
                    </div>
                    <div className="flex gap-2 mt-2">
                      {batch.category && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-blue-50 text-blue-700 border border-blue-200">
                          {batch.category}
                        </span>
                      )}
                      {pipelines.get(batch.pipeline_id) && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-purple-50 text-purple-700 border border-purple-200">
                          <GitBranch className="w-3 h-3 mr-1" />
                          {pipelines.get(batch.pipeline_id)?.name}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Body */}
                  <div className="p-6 space-y-4">
                    {/* Description */}
                    {batch.description && (
                      <p className="text-sm text-gray-600 line-clamp-2">{batch.description}</p>
                    )}

                    {/* Progress */}
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">Job Completion</span>
                        <span className={`font-semibold ${
                          progress >= 80 ? 'text-green-600' :
                          progress >= 50 ? 'text-blue-600' :
                          progress >= 25 ? 'text-yellow-600' :
                          'text-gray-600'
                        }`}>{progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all ${
                            progress >= 80 ? 'bg-green-600' :
                            progress >= 50 ? 'bg-blue-600' :
                            progress >= 25 ? 'bg-yellow-600' :
                            'bg-gray-400'
                          }`}
                          style={{ width: `${progress}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Enrollment */}
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">Enrollment</span>
                        <span className="font-semibold text-green-600">{utilization}%</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-gray-400" />
                        <span className="text-sm font-medium">
                          {batch.current_enrollment} / {batch.max_capacity} Mavericks
                        </span>
                      </div>
                    </div>

                    {/* Dates */}
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Calendar className="w-4 h-4" />
                      <span>
                        {new Date(batch.start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                        {' - '}
                        {new Date(batch.end_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                      </span>
                    </div>

                    {/* Focus Areas */}
                    {batch.focus_areas && batch.focus_areas.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {batch.focus_areas.slice(0, 3).map((area, idx) => (
                          <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-700">
                            {area}
                          </span>
                        ))}
                        {batch.focus_areas.length > 3 && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-600">
                            +{batch.focus_areas.length - 3} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Footer */}
                  <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex gap-2">
                    <Link
                      href={`/batches/${batch.id}`}
                      className="flex-1 inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      View Details
                    </Link>
                    <Link
                      href={`/batches/${batch.id}/edit`}
                      className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-50"
                    >
                      <Edit className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}