"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import DashboardLayout from '@/components/DashboardLayout';
import { 
  Users, Plus, Search, Filter, Edit, Trash2, 
  UserPlus, Shield, Loader2, CheckCircle, XCircle 
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

export default function UserManagementPage() {
  const router = useRouter();
  const { user: currentUser, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState<User[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (currentUser?.role !== 'super_admin') {
      router.push('/dashboard');
      return;
    }

    fetchUsers();
  }, [isAuthenticated, currentUser, page, search, roleFilter, statusFilter]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const params: any = {
        page,
        page_size: pageSize,
      };
      
      if (search) params.search = search;
      if (roleFilter) params.role = roleFilter;
      if (statusFilter !== '') params.is_active = statusFilter === 'active';

      const response = await apiClient.get('/admin/users/', { params });
      setUsers(response.data.users);
      setTotal(response.data.total);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (!confirm('Are you sure you want to deactivate this user?')) {
      return;
    }

    try {
      await apiClient.delete(`/admin/users/${userId}`);
      fetchUsers();
    } catch (error) {
      console.error('Failed to delete user:', error);
      alert('Failed to delete user');
    }
  };

  const getRoleBadgeColor = (role: string) => {
    const colors: Record<string, string> = {
      super_admin: 'bg-red-100 text-red-800',
      hr: 'bg-blue-100 text-blue-800',
      trainer: 'bg-green-100 text-green-800',
      manager: 'bg-purple-100 text-purple-800',
      maverick: 'bg-gray-100 text-gray-800',
    };
    return colors[role] || 'bg-gray-100 text-gray-800';
  };

  if (loading && users.length === 0) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <Loader2 className="animate-spin h-12 w-12 text-blue-600 mx-auto" />
            <p className="mt-4 text-gray-600">Loading users...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
            <p className="mt-2 text-gray-600">Manage users across all roles</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <UserPlus className="w-4 h-4" />
            Create User
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by name or email..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Role Filter */}
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Roles</option>
              <option value="super_admin">Super Admin</option>
              <option value="hr">HR</option>
              <option value="trainer">Trainer</option>
              <option value="manager">Manager</option>
              <option value="maverick">Maverick</option>
            </select>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>

            {/* Total Count */}
            <div className="flex items-center justify-center bg-gray-50 rounded-lg px-4 py-2">
              <span className="text-sm text-gray-600">
                Total: <span className="font-bold text-gray-900">{total}</span> users
              </span>
            </div>
          </div>
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Login
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{user.name}</div>
                        <div className="text-sm text-gray-500">{user.email}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getRoleBadgeColor(user.role)}`}>
                        {user.role.replace('_', ' ').toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {user.is_active ? (
                        <span className="flex items-center gap-1 text-green-600">
                          <CheckCircle className="w-4 h-4" />
                          <span className="text-sm">Active</span>
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-red-600">
                          <XCircle className="w-4 h-4" />
                          <span className="text-sm">Inactive</span>
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => router.push(`/admin/users/${user.id}`)}
                          className="text-blue-600 hover:text-blue-900"
                          title="Edit User"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteUser(user.id)}
                          className="text-red-600 hover:text-red-900"
                          title="Deactivate User"
                          disabled={user.id === currentUser?.id}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="bg-gray-50 px-6 py-3 flex items-center justify-between border-t border-gray-200">
            <div className="text-sm text-gray-700">
              Showing <span className="font-medium">{(page - 1) * pageSize + 1}</span> to{' '}
              <span className="font-medium">{Math.min(page * pageSize, total)}</span> of{' '}
              <span className="font-medium">{total}</span> results
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page * pageSize >= total}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        </div>

        {/* Create User Modal - Placeholder */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full">
              <h2 className="text-xl font-bold mb-4">Create New User</h2>
              <p className="text-gray-600 mb-4">Create user form will be implemented here.</p>
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
