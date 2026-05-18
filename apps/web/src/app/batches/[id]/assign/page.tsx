"use client";

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  ArrowLeft,
  Search,
  UserPlus,
  UserMinus,
  Users,
  CheckCircle,
  XCircle,
  GraduationCap,
  Award,
  Filter,
  RefreshCw,
  Mail
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';

interface Batch {
  id: string;
  name: string;
  description?: string;
  current_enrollment: number;
  max_capacity?: number;
  status: string;
}

interface Maverick {
  id: string;
  name: string;
  email: string;
  phone?: string;
  college: string;
  degree?: string;
  branch?: string;
  graduation_year?: number;
  cgpa?: number;
  skills: string[];
  profile_status: string;
  deployment_status: string;
  current_batch_id?: string;
  current_batch_name?: string;
}

export default function BatchAssignMavericksPage() {
  const router = useRouter();
  const params = useParams();
  const batchId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [assigning, setAssigning] = useState<string | null>(null);
  const [batch, setBatch] = useState<Batch | null>(null);
  const [allMavericks, setAllMavericks] = useState<Maverick[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'assigned' | 'unassigned' | 'other_batch'>('all');
  const [selectedBatchFilter, setSelectedBatchFilter] = useState('');
  const [allBatches, setAllBatches] = useState<Batch[]>([]);

  useEffect(() => {
    fetchData();
  }, [batchId]);

  const fetchData = async () => {
    try {
      setLoading(true);

      // Fetch batch details
      const batchResponse = await apiClient.get(`/batches/${batchId}`);
      setBatch(batchResponse.data);

      // Fetch all approved mavericks
      const mavericksResponse = await apiClient.get('/mavericks/', {
        params: {
          page: 1,
          page_size: 1000,
          profile_status: 'APPROVED'
        }
      });
      setAllMavericks(mavericksResponse.data.mavericks || []);

      // Fetch all batches for filter
      const batchesResponse = await apiClient.get('/batches/', {
        params: {
          page: 1,
          page_size: 100
        }
      });
      setAllBatches(batchesResponse.data.batches || []);
    } catch (error: any) {
      console.error('Failed to fetch data:', error);
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleAssignToBatch = async (maverickId: string, maverickName: string) => {
    if (batch && batch.max_capacity && batch.current_enrollment >= batch.max_capacity) {
      toast.error('Batch is at full capacity');
      return;
    }

    setAssigning(maverickId);
    try {
      await apiClient.post(`/batches/${batchId}/assign`, {
        maverick_id: maverickId
      });

      toast.success(`${maverickName} assigned to ${batch?.name}`);
      await fetchData(); // Refresh data
    } catch (error: any) {
      console.error('Failed to assign:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to assign maverick';
      toast.error(typeof errorMessage === 'string' ? errorMessage : 'Failed to assign maverick');
    } finally {
      setAssigning(null);
    }
  };

  const handleUnassignFromBatch = async (maverickId: string, maverickName: string) => {
    if (!confirm(`Remove ${maverickName} from ${batch?.name}?`)) {
      return;
    }

    setAssigning(maverickId);
    try {
      await apiClient.patch(`/mavericks/${maverickId}`, {
        current_batch_id: null
      });

      toast.success(`${maverickName} removed from batch`);
      await fetchData(); // Refresh data
    } catch (error: any) {
      console.error('Failed to unassign:', error);
      toast.error('Failed to remove maverick from batch');
    } finally {
      setAssigning(null);
    }
  };

  const handleReassignToThisBatch = async (maverickId: string, maverickName: string, fromBatchName: string) => {
    if (!confirm(`Move ${maverickName} from "${fromBatchName}" to "${batch?.name}"?`)) {
      return;
    }

    setAssigning(maverickId);
    try {
      // First unassign from current batch
      await apiClient.patch(`/mavericks/${maverickId}`, {
        current_batch_id: null
      });

      // Then assign to this batch
      await apiClient.post(`/batches/${batchId}/assign`, {
        maverick_id: maverickId
      });

      toast.success(`${maverickName} moved to ${batch?.name}`);
      await fetchData(); // Refresh data
    } catch (error: any) {
      console.error('Failed to reassign:', error);
      toast.error('Failed to move maverick to this batch');
    } finally {
      setAssigning(null);
    }
  };

  // Filter mavericks based on search and filters
  const filteredMavericks = allMavericks.filter((maverick) => {
    // Search filter
    const matchesSearch =
      maverick.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      maverick.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      maverick.college?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      maverick.skills.some(skill => skill.toLowerCase().includes(searchTerm.toLowerCase()));

    if (!matchesSearch) return false;

    // Status filter
    const isInThisBatch = maverick.current_batch_id === batchId;
    const isInOtherBatch = maverick.current_batch_id && maverick.current_batch_id !== batchId;
    const isUnassigned = !maverick.current_batch_id;

    if (filterStatus === 'assigned' && !isInThisBatch) return false;
    if (filterStatus === 'unassigned' && !isUnassigned) return false;
    if (filterStatus === 'other_batch' && !isInOtherBatch) return false;

    // Batch filter
    if (selectedBatchFilter && maverick.current_batch_id !== selectedBatchFilter) return false;

    return true;
  });

  // Categorize mavericks
  const assignedToThisBatch = filteredMavericks.filter(m => m.current_batch_id === batchId);
  const assignedToOtherBatch = filteredMavericks.filter(m => m.current_batch_id && m.current_batch_id !== batchId);
  const unassignedMavericks = filteredMavericks.filter(m => !m.current_batch_id);

  const getStatusBadge = (maverick: Maverick) => {
    if (maverick.current_batch_id === batchId) {
      return (
        <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
          <CheckCircle className="w-3 h-3 mr-1" />
          In This Batch
        </span>
      );
    } else if (maverick.current_batch_id) {
      return (
        <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
          <Users className="w-3 h-3 mr-1" />
          {maverick.current_batch_name || 'Other Batch'}
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">
          <XCircle className="w-3 h-3 mr-1" />
          Unassigned
        </span>
      );
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
            <p className="mt-4 text-gray-600">Loading mavericks...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!batch) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="text-center text-red-600">Batch not found</div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.push(`/batches/${batchId}`)}
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to Batch Details
          </button>

          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Assign Mavericks
              </h1>
              <p className="text-gray-600">
                Batch: <span className="font-semibold">{batch.name}</span>
              </p>
              <div className="flex items-center gap-4 mt-2 text-sm">
                <span className="text-gray-600">
                  Current Enrollment: <span className="font-semibold text-gray-900">{batch.current_enrollment}</span>
                  {batch.max_capacity && <span className="text-gray-500"> / {batch.max_capacity}</span>}
                </span>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  batch.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
                  batch.status === 'PLANNED' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {batch.status}
                </span>
              </div>
            </div>

            <button
              onClick={fetchData}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </button>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Mavericks</p>
                <p className="text-2xl font-bold text-gray-900">{allMavericks.length}</p>
              </div>
              <Users className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">In This Batch</p>
                <p className="text-2xl font-bold text-green-600">{assignedToThisBatch.length}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Unassigned</p>
                <p className="text-2xl font-bold text-gray-900">{unassignedMavericks.length}</p>
              </div>
              <XCircle className="w-8 h-8 text-gray-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">In Other Batches</p>
                <p className="text-2xl font-bold text-blue-600">{assignedToOtherBatch.length}</p>
              </div>
              <Users className="w-8 h-8 text-blue-600" />
            </div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name, email, college, skills..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Status Filter */}
            <div>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as any)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Mavericks</option>
                <option value="assigned">In This Batch</option>
                <option value="unassigned">Unassigned</option>
                <option value="other_batch">In Other Batches</option>
              </select>
            </div>

            {/* Batch Filter */}
            <div>
              <select
                value={selectedBatchFilter}
                onChange={(e) => setSelectedBatchFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Filter by Batch</option>
                {allBatches.map(b => (
                  <option key={b.id} value={b.id}>{b.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              Showing <span className="font-semibold">{filteredMavericks.length}</span> of <span className="font-semibold">{allMavericks.length}</span> mavericks
            </p>
            {(searchTerm || filterStatus !== 'all' || selectedBatchFilter) && (
              <button
                onClick={() => {
                  setSearchTerm('');
                  setFilterStatus('all');
                  setSelectedBatchFilter('');
                }}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Clear Filters
              </button>
            )}
          </div>
        </div>

        {/* Mavericks List */}
        {filteredMavericks.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Mavericks Found</h3>
            <p className="text-gray-600">
              {searchTerm || filterStatus !== 'all' || selectedBatchFilter
                ? 'Try adjusting your filters or search terms'
                : 'No approved mavericks available'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredMavericks.map((maverick) => {
              const isInThisBatch = maverick.current_batch_id === batchId;
              const isInOtherBatch = maverick.current_batch_id && maverick.current_batch_id !== batchId;
              const isAssigning = assigning === maverick.id;

              return (
                <div
                  key={maverick.id}
                  className={`bg-white rounded-lg shadow-sm border-2 p-4 transition-all ${
                    isInThisBatch
                      ? 'border-green-200 bg-green-50/30'
                      : isInOtherBatch
                      ? 'border-blue-200 bg-blue-50/30'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    {/* Maverick Info */}
                    <div className="flex-1">
                      <div className="flex items-start gap-4">
                        <div className="flex-shrink-0">
                          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                            {maverick.name.charAt(0).toUpperCase()}
                          </div>
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="text-lg font-semibold text-gray-900">
                              {maverick.name}
                            </h3>
                            {getStatusBadge(maverick)}
                          </div>

                          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-2">
                            <span className="flex items-center gap-1">
                              <Mail className="w-4 h-4" />
                              {maverick.email}
                            </span>
                            {maverick.college && (
                              <span className="flex items-center gap-1">
                                <GraduationCap className="w-4 h-4" />
                                {maverick.college}
                              </span>
                            )}
                            {maverick.cgpa && (
                              <span className="flex items-center gap-1">
                                <Award className="w-4 h-4" />
                                CGPA: {maverick.cgpa}
                              </span>
                            )}
                          </div>

                          {/* Skills */}
                          {maverick.skills && maverick.skills.length > 0 && (
                            <div className="flex flex-wrap gap-2 mt-2">
                              {maverick.skills.slice(0, 8).map((skill, idx) => (
                                <span
                                  key={idx}
                                  className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-md"
                                >
                                  {skill}
                                </span>
                              ))}
                              {maverick.skills.length > 8 && (
                                <span className="px-2 py-1 text-xs font-medium text-gray-500">
                                  +{maverick.skills.length - 8} more
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex-shrink-0">
                      {isInThisBatch ? (
                        <button
                          onClick={() => handleUnassignFromBatch(maverick.id, maverick.name)}
                          disabled={isAssigning}
                          className="inline-flex items-center px-4 py-2 text-sm font-medium text-red-700 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {isAssigning ? (
                            <>
                              <div className="animate-spin rounded-full h-4 w-4 border-2 border-red-700 border-t-transparent mr-2"></div>
                              Removing...
                            </>
                          ) : (
                            <>
                              <UserMinus className="w-4 h-4 mr-2" />
                              Remove from Batch
                            </>
                          )}
                        </button>
                      ) : isInOtherBatch ? (
                        <button
                          onClick={() => handleReassignToThisBatch(maverick.id, maverick.name, maverick.current_batch_name || 'other batch')}
                          disabled={isAssigning}
                          className="inline-flex items-center px-4 py-2 text-sm font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {isAssigning ? (
                            <>
                              <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-700 border-t-transparent mr-2"></div>
                              Moving...
                            </>
                          ) : (
                            <>
                              <RefreshCw className="w-4 h-4 mr-2" />
                              Move to This Batch
                            </>
                          )}
                        </button>
                      ) : (
                        <button
                          onClick={() => handleAssignToBatch(maverick.id, maverick.name)}
                          disabled={isAssigning}
                          className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {isAssigning ? (
                            <>
                              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                              Assigning...
                            </>
                          ) : (
                            <>
                              <UserPlus className="w-4 h-4 mr-2" />
                              Assign to Batch
                            </>
                          )}
                        </button>
                      )}
                    </div>
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
