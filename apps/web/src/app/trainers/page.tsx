"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { UserPlus, Search, Users, Mail, CheckCircle, XCircle, Edit } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';

interface Trainer {
  user_id: string;
  name: string;
  email: string;
  phone?: string;
  specialization?: string[];
  is_active: boolean;
  created_at: string;
  assigned_batches_count: number;
  is_idle: boolean;
}

export default function TrainersPage() {
  const router = useRouter();
  const [trainers, setTrainers] = useState<Trainer[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchTrainers();
  }, []);

  const fetchTrainers = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/trainers/', {
        params: { page: 1, page_size: 100 }
      });
      setTrainers(response.data?.trainers || []);
    } catch (error) {
      console.error('Failed to fetch trainers:', error);
      toast.error('Failed to load trainers');
    } finally {
      setLoading(false);
    }
  };

  const filteredTrainers = trainers.filter(trainer =>
    trainer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    trainer.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const trainersInBatch = filteredTrainers.filter(t => t.is_active && !t.is_idle && t.assigned_batches_count > 0);
  const trainersIdle = filteredTrainers.filter(t => t.is_active && (t.is_idle || t.assigned_batches_count === 0));

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Trainers</h1>
              <p className="text-gray-600 mt-1">Manage trainer accounts and assignments</p>
            </div>
            <button
              onClick={() => router.push('/trainers/create')}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <UserPlus className="w-5 h-5" />
              Add New Trainer
            </button>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search trainers by name or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Trainers</p>
                <p className="text-2xl font-bold text-gray-900">{trainers.length}</p>
              </div>
              <Users className="w-10 h-10 text-blue-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Trainers in Batch</p>
                <p className="text-2xl font-bold text-green-600">{trainersInBatch.length}</p>
              </div>
              <CheckCircle className="w-10 h-10 text-green-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Trainers Idle</p>
                <p className="text-2xl font-bold text-orange-600">{trainersIdle.length}</p>
              </div>
              <Users className="w-10 h-10 text-orange-600" />
            </div>
          </div>
        </div>

        {/* Trainers List */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
              <p className="mt-4 text-gray-600">Loading trainers...</p>
            </div>
          ) : filteredTrainers.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <Users className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium">No trainers found</p>
              <p className="text-sm mt-2">
                {searchTerm ? 'Try adjusting your search' : 'Click "Add New Trainer" to get started'}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Trainer
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Contact
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Specialization
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Assigned Batches
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredTrainers.map((trainer) => (
                    <tr key={trainer.user_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <span className="text-blue-700 font-bold text-lg">
                              {trainer.name.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{trainer.name}</div>
                            <div className="text-xs text-gray-500">
                              Joined {new Date(trainer.created_at).toLocaleDateString()}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-1 text-sm text-gray-600">
                          <Mail className="w-4 h-4" />
                          {trainer.email}
                        </div>
                        {trainer.phone && (
                          <div className="text-xs text-gray-500 mt-1">{trainer.phone}</div>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {trainer.specialization && trainer.specialization.length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {trainer.specialization.slice(0, 3).map((skill, idx) => (
                              <span
                                key={idx}
                                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                              >
                                {skill}
                              </span>
                            ))}
                            {trainer.specialization.length > 3 && (
                              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
                                +{trainer.specialization.length - 3}
                              </span>
                            )}
                          </div>
                        ) : (
                          <span className="text-sm text-gray-400">No specialization</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-purple-100 text-purple-700 font-semibold">
                          {trainer.assigned_batches_count}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {!trainer.is_active ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            <XCircle className="w-3 h-3 mr-1" />
                            Inactive
                          </span>
                        ) : trainer.is_idle || trainer.assigned_batches_count === 0 ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                            💤 Idle
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            In Batch
                          </span>
                        )}
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
