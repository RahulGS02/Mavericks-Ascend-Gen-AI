"use client";

import { useEffect, useState } from 'react';
import { Search, Plus, GitBranch, Eye, Edit, Trash2, Copy, Calendar } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import Link from 'next/link';
import DashboardLayout from '@/components/DashboardLayout';

interface Pipeline {
  id: string;
  name: string;
  description?: string;
  status: string; // DRAFT, ACTIVE, COMPLETED, ARCHIVED
  created_by: string;
  created_at: string;
  updated_at?: string;
  jobs?: Array<{
    id: string;
    name: string;
    job_type: string;
    sequence_order: number;
    duration_days?: number;
  }>;
}

export default function PipelinesPage() {
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  useEffect(() => {
    fetchPipelines();
  }, [searchTerm, categoryFilter]);

  const fetchPipelines = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/pipelines/', {
        params: {
          page: 1,
          page_size: 100,
          search: searchTerm || undefined,
          category: categoryFilter === 'all' ? undefined : categoryFilter,
        }
      });
      setPipelines(response.data?.pipelines || []);
    } catch (error) {
      console.error('Failed to fetch pipelines:', error);
      toast.error('Failed to load pipelines');
      setPipelines([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this pipeline?')) return;
    
    try {
      await apiClient.delete(`/pipelines/${id}`);
      toast.success('Pipeline deleted successfully');
      fetchPipelines();
    } catch (error) {
      console.error('Failed to delete pipeline:', error);
      toast.error('Failed to delete pipeline');
    }
  };

  const handleDuplicate = async (id: string, name: string) => {
    try {
      const newName = `Copy of ${name}`;
      const response = await apiClient.post(`/pipelines/${id}/clone`, null, {
        params: { new_name: newName, include_jobs: true }
      });
      toast.success(`Pipeline cloned as "${newName}"`);
      fetchPipelines();
    } catch (error) {
      console.error('Failed to clone pipeline:', error);
      toast.error('Failed to clone pipeline');
    }
  };

  const filteredPipelines = pipelines.filter(pipeline =>
    pipeline.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    pipeline.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const stats = {
    total: pipelines.length,
    active: pipelines.filter(p => p.status === 'ACTIVE').length,
    inactive: pipelines.filter(p => p.status !== 'ACTIVE').length,
  };

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-blue-900 mb-2">Training Pipelines</h1>
            <p className="text-gray-600">Manage training program templates and job sequences</p>
          </div>
          <Link
            href="/pipelines/create"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5 mr-2" />
            Create Pipeline
          </Link>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Pipelines</p>
                <p className="text-2xl font-bold text-blue-900">{stats.total}</p>
              </div>
              <GitBranch className="w-8 h-8 text-blue-500" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active</p>
                <p className="text-2xl font-bold text-green-600">{stats.active}</p>
              </div>
              <GitBranch className="w-8 h-8 text-green-500" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Inactive</p>
                <p className="text-2xl font-bold text-gray-600">{stats.inactive}</p>
              </div>
              <GitBranch className="w-8 h-8 text-gray-400" />
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search pipelines..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Pipelines Grid */}
        {loading ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
            <p className="mt-4 text-gray-600">Loading pipelines...</p>
          </div>
        ) : filteredPipelines.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center text-gray-500">
            <GitBranch className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium">No pipelines found</p>
            <p className="text-sm mt-2">Create your first training pipeline template</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPipelines.map((pipeline) => (
              <div key={pipeline.id} className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-lg transition-shadow">
                {/* Header */}
                <div className="p-6 border-b border-gray-200">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg font-semibold text-gray-900 flex-1">{pipeline.name}</h3>
                    {pipeline.status === 'ACTIVE' && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                        Active
                      </span>
                    )}
                    {pipeline.status === 'DRAFT' && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                        Draft
                      </span>
                    )}
                    {pipeline.status === 'COMPLETED' && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">
                        Completed
                      </span>
                    )}
                    {pipeline.status === 'ARCHIVED' && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                        Archived
                      </span>
                    )}
                  </div>
                </div>

                {/* Body */}
                <div className="p-6 space-y-4">
                  {pipeline.description && (
                    <p className="text-sm text-gray-600 line-clamp-3">{pipeline.description}</p>
                  )}

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Total Jobs</span>
                      <span className="font-semibold text-blue-600">{pipeline.jobs?.length || 0}</span>
                    </div>
                    {pipeline.jobs && pipeline.jobs.length > 0 && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Duration</span>
                        <span className="font-semibold text-gray-900">
                          {pipeline.jobs.reduce((sum, j) => sum + (j.duration_days || 0), 0)} days
                        </span>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <Calendar className="w-4 h-4" />
                      <span>Created {new Date(pipeline.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                {/* Footer */}
                <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex gap-2">
                  <Link
                    href={`/pipelines/${pipeline.id}`}
                    className="flex-1 inline-flex items-center justify-center px-3 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
                  >
                    <Eye className="w-4 h-4 mr-1" />
                    View
                  </Link>
                  <Link
                    href={`/pipelines/${pipeline.id}/edit`}
                    className="inline-flex items-center justify-center px-3 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-50"
                  >
                    <Edit className="w-4 h-4" />
                  </Link>
                  <button
                    onClick={() => handleDuplicate(pipeline.id, pipeline.name)}
                    className="inline-flex items-center justify-center px-3 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-50"
                    title="Clone Pipeline"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(pipeline.id)}
                    className="inline-flex items-center justify-center px-3 py-2 border border-red-300 text-red-700 text-sm font-medium rounded-md hover:bg-red-50"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}