"use client";

import { useEffect, useState } from 'react';
import { Search, Filter, Download, UserPlus, Eye, Edit, Trash2, Users, CheckCircle, XCircle, Clock } from 'lucide-react';
import { hrAPI } from '@/lib/api/hr';
import { toast } from 'sonner';
import Link from 'next/link';
import DashboardLayout from '@/components/DashboardLayout';

interface Maverick {
  id: string;
  name: string;
  email: string;
  phone?: string;
  college?: string;
  degree?: string;
  branch?: string;
  graduation_year?: number;
  cgpa?: number;
  skills: string[];
  profile_status: 'pending' | 'approved' | 'rejected';
  deployment_status?: string;
  current_batch_id?: string;
  current_batch_name?: string;
  created_at: string;
}

export default function MavericksPage() {
  const [mavericks, setMavericks] = useState<Maverick[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'approved' | 'rejected'>('all');
  const [deploymentFilter, setDeploymentFilter] = useState<'all' | 'assigned' | 'unassigned'>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 20;

  useEffect(() => {
    fetchMavericks();
  }, [currentPage, statusFilter, deploymentFilter, searchTerm]);

  const fetchMavericks = async () => {
    setLoading(true);
    try {
      const response = await hrAPI.getAllMavericks({
        page: currentPage,
        page_size: pageSize,
        profile_status: statusFilter === 'all' ? undefined : statusFilter,
        search: searchTerm || undefined,
      });
      
      let filteredMavericks = response.mavericks || [];
      
      // Apply deployment filter
      if (deploymentFilter === 'assigned') {
        filteredMavericks = filteredMavericks.filter((m: any) => m.current_batch_id);
      } else if (deploymentFilter === 'unassigned') {
        filteredMavericks = filteredMavericks.filter((m: any) => !m.current_batch_id);
      }
      
      setMavericks(filteredMavericks);
      setTotalCount(response.total || 0);
    } catch (error) {
      console.error('Failed to fetch mavericks:', error);
      toast.error('Failed to load mavericks');
      setMavericks([]);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    toast.success('Exporting mavericks data...');
    // TODO: Implement export to CSV/Excel
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <CheckCircle className="w-3 h-3 mr-1" />
            Approved
          </span>
        );
      case 'pending':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <Clock className="w-3 h-3 mr-1" />
            Pending
          </span>
        );
      case 'rejected':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <XCircle className="w-3 h-3 mr-1" />
            Rejected
          </span>
        );
      default:
        return null;
    }
  };

  const stats = {
    total: totalCount,
    approved: mavericks.filter(m => m.profile_status === 'approved').length,
    pending: mavericks.filter(m => m.profile_status === 'pending').length,
    assigned: mavericks.filter(m => m.current_batch_id).length,
  };

  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-blue-900 mb-2">Mavericks</h1>
          <p className="text-gray-600">Manage trainee profiles, assignments, and progress tracking</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Mavericks</p>
                <p className="text-2xl font-bold text-blue-900">{stats.total}</p>
              </div>
              <Users className="w-8 h-8 text-blue-500" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Approved</p>
                <p className="text-2xl font-bold text-green-600">{stats.approved}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Pending Review</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.pending}</p>
              </div>
              <Clock className="w-8 h-8 text-yellow-500" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Assigned to Batch</p>
                <p className="text-2xl font-bold text-purple-600">{stats.assigned}</p>
              </div>
              <Users className="w-8 h-8 text-purple-500" />
            </div>
          </div>
        </div>

        {/* Filters & Actions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by name, email, college..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value as any);
                setCurrentPage(1);
              }}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>

            {/* Deployment Filter */}
            <select
              value={deploymentFilter}
              onChange={(e) => {
                setDeploymentFilter(e.target.value as any);
                setCurrentPage(1);
              }}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Mavericks</option>
              <option value="assigned">Assigned to Batch</option>
              <option value="unassigned">Unassigned</option>
            </select>

            {/* Actions */}
            <button
              onClick={handleExport}
              className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              Export
            </button>
          </div>
        </div>

        {/* Mavericks Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
              <p className="mt-4 text-gray-600">Loading mavericks...</p>
            </div>
          ) : mavericks.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <Users className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium">No mavericks found</p>
              <p className="text-sm mt-2">Try adjusting your filters or search criteria</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Maverick</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Education</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Skills</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Batch</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {mavericks.map((maverick) => (
                      <tr key={maverick.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4">
                          <div className="flex items-center">
                            <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                              <span className="text-blue-600 font-semibold text-sm">
                                {maverick.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                              </span>
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">{maverick.name}</div>
                              <div className="text-sm text-gray-500">{maverick.email}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">{maverick.college}</div>
                          <div className="text-xs text-gray-500">
                            {maverick.degree} - {maverick.branch}
                          </div>
                          <div className="text-xs text-gray-500">
                            {maverick.graduation_year} • CGPA: {maverick.cgpa}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex flex-wrap gap-1">
                            {(maverick.skills || []).slice(0, 2).map((skill, idx) => (
                              <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                {skill}
                              </span>
                            ))}
                            {(maverick.skills?.length || 0) > 2 && (
                              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
                                +{maverick.skills.length - 2}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          {maverick.current_batch_name ? (
                            <span className="text-sm text-gray-900">{maverick.current_batch_name}</span>
                          ) : (
                            <span className="text-sm text-gray-400 italic">Not assigned</span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          {getStatusBadge(maverick.profile_status)}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex justify-end gap-2">
                            <Link
                              href={`/mavericks/${maverick.id}`}
                              className="inline-flex items-center px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
                            >
                              <Eye className="w-4 h-4 mr-1" />
                              View
                            </Link>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
                  <div className="text-sm text-gray-600">
                    Showing <span className="font-semibold">{(currentPage - 1) * pageSize + 1}</span> to{' '}
                    <span className="font-semibold">{Math.min(currentPage * pageSize, totalCount)}</span> of{' '}
                    <span className="font-semibold">{totalCount}</span> results
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Previous
                    </button>
                    <span className="px-4 py-2 text-sm">
                      Page {currentPage} of {totalPages}
                    </span>
                    <button
                      onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                      className="px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>

    </DashboardLayout>
  );
}