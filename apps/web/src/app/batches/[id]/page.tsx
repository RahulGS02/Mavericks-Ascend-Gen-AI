"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Calendar, Users, BarChart3, Clock, GitBranch, User, UserPlus, Edit2, Trophy } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';
import BatchTimelineTab from '@/components/batch/BatchTimelineTab';
import BatchMavericksTab from '@/components/batch/BatchMavericksTab';
import BatchProgressTab from '@/components/batch/BatchProgressTab';
import BatchLeaderboardTab from '@/components/batch/BatchLeaderboardTab';
import BatchTrainersManager from '@/components/batch/BatchTrainersManager';

interface Batch {
  id: string;
  name: string;
  description?: string;
  pipeline_id: string;
  trainer_id?: string;
  start_date: string;
  end_date: string;
  max_capacity: number;
  current_enrollment: number;
  status: string;
  category?: string;
  created_at: string;
}

interface Trainer {
  user_id: string;
  name: string;
  email: string;
}

interface Pipeline {
  id: string;
  name: string;
  description?: string;
}

type TabType = 'timeline' | 'mavericks' | 'progress' | 'leaderboard';

export default function BatchDetailPage() {
  const params = useParams();
  const router = useRouter();
  const batchId = params?.id as string;

  const [activeTab, setActiveTab] = useState<TabType>('timeline');
  const [loading, setLoading] = useState(true);
  const [batch, setBatch] = useState<Batch | null>(null);
  const [pipeline, setPipeline] = useState<Pipeline | null>(null);
  const [trainer, setTrainer] = useState<Trainer | null>(null);
  const [trainers, setTrainers] = useState<Trainer[]>([]);
  const [showTrainerModal, setShowTrainerModal] = useState(false);
  const [selectedTrainerId, setSelectedTrainerId] = useState<string>('');

  useEffect(() => {
    if (batchId) {
      fetchBatchDetails();
      fetchTrainers();
    }
  }, [batchId]);

  const fetchBatchDetails = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get(`/batches/${batchId}`);
      setBatch(response.data);

      // Fetch pipeline details
      if (response.data.pipeline_id) {
        const pipelineResponse = await apiClient.get(`/pipelines/${response.data.pipeline_id}`);
        setPipeline(pipelineResponse.data);
      }

      // Fetch trainer details if assigned
      if (response.data.trainer_id) {
        const trainerResponse = await apiClient.get(`/trainers/${response.data.trainer_id}`);
        setTrainer(trainerResponse.data);
      } else {
        setTrainer(null);
      }
    } catch (error) {
      console.error('Failed to fetch batch details:', error);
      toast.error('Failed to load batch details');
    } finally {
      setLoading(false);
    }
  };

  const fetchTrainers = async () => {
    try {
      const response = await apiClient.get('/trainers/', {
        params: { page: 1, page_size: 100, is_active: true }
      });
      setTrainers(response.data?.trainers || []);
    } catch (error) {
      console.error('Failed to fetch trainers:', error);
    }
  };

  const handleAssignTrainer = async () => {
    if (!selectedTrainerId) {
      toast.error('Please select a trainer');
      return;
    }

    try {
      await apiClient.patch(`/batches/${batchId}`, {
        trainer_id: selectedTrainerId
      });
      toast.success('Trainer assigned successfully!');
      setShowTrainerModal(false);
      fetchBatchDetails(); // Refresh to get trainer details
    } catch (error: any) {
      console.error('Failed to assign trainer:', error);
      toast.error(error.response?.data?.detail || 'Failed to assign trainer');
    }
  };

  const handleRemoveTrainer = async () => {
    try {
      await apiClient.patch(`/batches/${batchId}`, {
        trainer_id: null
      });
      toast.success('Trainer removed successfully!');
      setShowTrainerModal(false);
      fetchBatchDetails();
    } catch (error: any) {
      console.error('Failed to remove trainer:', error);
      toast.error(error.response?.data?.detail || 'Failed to remove trainer');
    }
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

  if (!batch) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-red-500">Batch not found</div>
        </div>
      </DashboardLayout>
    );
  }

  const tabs = [
    { id: 'timeline' as TabType, label: 'Timeline', icon: <Clock className="w-4 h-4" /> },
    { id: 'mavericks' as TabType, label: 'Mavericks', icon: <Users className="w-4 h-4" /> },
    { id: 'progress' as TabType, label: 'Progress', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'leaderboard' as TabType, label: 'Leaderboard', icon: <Trophy className="w-4 h-4" /> },
  ];

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-4 mb-4">
            <button
              onClick={() => router.back()}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </button>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900">{batch.name}</h1>
              {batch.description && (
                <p className="text-gray-600 mt-1">{batch.description}</p>
              )}
            </div>
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${
              batch.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
              batch.status === 'COMPLETED' ? 'bg-purple-100 text-purple-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {batch.status}
            </div>
          </div>

          {/* Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <GitBranch className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <div className="text-xs text-gray-600">Pipeline</div>
                  <div className="text-sm font-semibold text-gray-900">
                    {pipeline?.name || 'Loading...'}
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Users className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <div className="text-xs text-gray-600">Enrollment</div>
                  <div className="text-sm font-semibold text-gray-900">
                    {batch.current_enrollment} / {batch.max_capacity}
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Calendar className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <div className="text-xs text-gray-600">Duration</div>
                  <div className="text-sm font-semibold text-gray-900">
                    {new Date(batch.start_date).toLocaleDateString()} - {new Date(batch.end_date).toLocaleDateString()}
                  </div>
                </div>
              </div>
            </div>

            {/* Multiple Trainers Manager */}
            <BatchTrainersManager
              batchId={batchId}
              onUpdate={fetchBatchDetails}
            />
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex gap-6">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors
                    ${activeTab === tab.id
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  {tab.icon}
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <div className="mt-6">
          {activeTab === 'timeline' && (
            <BatchTimelineTab batchId={batchId} batch={batch} pipeline={pipeline} />
          )}

          {activeTab === 'mavericks' && (
            <BatchMavericksTab
              batchId={batchId}
              mavericks={batch.mavericks || []}
              onUpdate={fetchBatchDetails}
            />
          )}

          {activeTab === 'progress' && (
            <BatchProgressTab
              batchId={batchId}
              batchName={batch.name}
            />
          )}

          {activeTab === 'leaderboard' && (
            <BatchLeaderboardTab
              batchId={batchId}
              batchName={batch.name}
            />
          )}
        </div>

        {/* Trainer Assignment Modal */}
        {showTrainerModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  {trainer ? 'Change Trainer' : 'Assign Trainer'}
                </h3>

                {trainer && (
                  <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="text-sm text-blue-900">
                      <strong>Current Trainer:</strong> {trainer.name}
                    </div>
                    <div className="text-xs text-blue-700">{trainer.email}</div>
                  </div>
                )}

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Trainer
                  </label>
                  <select
                    value={selectedTrainerId}
                    onChange={(e) => setSelectedTrainerId(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">-- Select a trainer --</option>
                    {trainers.map((t) => (
                      <option key={t.user_id} value={t.user_id}>
                        {t.name} ({t.email})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex gap-3">
                  {trainer && (
                    <button
                      onClick={handleRemoveTrainer}
                      className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                    >
                      Remove Trainer
                    </button>
                  )}
                  <button
                    onClick={() => {
                      setShowTrainerModal(false);
                      setSelectedTrainerId('');
                    }}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAssignTrainer}
                    disabled={!selectedTrainerId}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {trainer ? 'Update' : 'Assign'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
