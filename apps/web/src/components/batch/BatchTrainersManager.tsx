"use client";

import { useState, useEffect } from 'react';
import { User, Plus, X, Trash2, UserPlus } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import { useAuthStore } from '@/store/authStore';

interface TrainerInfo {
  user_id: string;
  name: string;
  email: string;
  assigned_at: string;
}

interface AvailableTrainer {
  user_id: string;
  name: string;
  email: string;
}

interface BatchTrainersManagerProps {
  batchId: string;
  onUpdate?: () => void;
}

export default function BatchTrainersManager({ batchId, onUpdate }: BatchTrainersManagerProps) {
  const { user } = useAuthStore();
  const [trainers, setTrainers] = useState<TrainerInfo[]>([]);
  const [availableTrainers, setAvailableTrainers] = useState<AvailableTrainer[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedTrainerId, setSelectedTrainerId] = useState('');
  const [processing, setProcessing] = useState(false);

  // Check if user can manage trainers (HR or Super Admin only)
  const canManageTrainers = user?.role === 'hr' || user?.role === 'super_admin';

  useEffect(() => {
    fetchTrainers();
    fetchAvailableTrainers();
  }, [batchId]);

  const fetchTrainers = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/batches/${batchId}/trainers`);
      setTrainers(response.data || []);
    } catch (error: any) {
      console.error('Failed to fetch trainers:', error);
      toast.error('Failed to load trainers');
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableTrainers = async () => {
    try {
      const response = await apiClient.get('/trainers/', {
        params: { page: 1, page_size: 100, is_active: true }
      });
      setAvailableTrainers(response.data?.trainers || []);
    } catch (error) {
      console.error('Failed to fetch available trainers:', error);
    }
  };

  const handleAddTrainer = async () => {
    if (!selectedTrainerId) {
      toast.error('Please select a trainer');
      return;
    }

    setProcessing(true);
    try {
      await apiClient.post(`/batches/${batchId}/trainers/assign`, {
        trainer_id: selectedTrainerId,
        is_lead_trainer: false
      });

      toast.success('Trainer assigned successfully!');
      setShowAddModal(false);
      setSelectedTrainerId('');
      await fetchTrainers();
      onUpdate?.();
    } catch (error: any) {
      console.error('Failed to assign trainer:', error);
      toast.error(error.response?.data?.detail || 'Failed to assign trainer');
    } finally {
      setProcessing(false);
    }
  };

  const handleRemoveTrainer = async (trainerId: string, trainerName: string) => {
    if (!confirm(`Remove ${trainerName} from this batch?`)) {
      return;
    }

    setProcessing(true);
    try {
      await apiClient.delete(`/batches/${batchId}/trainers/${trainerId}`);
      toast.success('Trainer removed successfully!');
      await fetchTrainers();
      onUpdate?.();
    } catch (error: any) {
      console.error('Failed to remove trainer:', error);
      toast.error(error.response?.data?.detail || 'Failed to remove trainer');
    } finally {
      setProcessing(false);
    }
  };

  // Filter out already assigned trainers
  const unassignedTrainers = availableTrainers.filter(
    at => !trainers.some(t => t.user_id === at.user_id)
  );

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-2 border-blue-500 border-t-transparent"></div>
          <span className="ml-2 text-gray-600">Loading trainers...</span>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Compact Info Card - Matches other cards in grid */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <User className="w-5 h-5 text-blue-600" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs text-gray-600">Batch Trainers</div>
            <div className="text-sm font-semibold text-gray-900 truncate">
              {loading ? 'Loading...' : trainers.length === 0 ? 'No trainers' : `${trainers.length} trainer${trainers.length !== 1 ? 's' : ''}`}
            </div>
            {trainers.length > 0 && (
              <button
                onClick={() => setShowAddModal(true)}
                className="text-xs text-blue-600 hover:text-blue-700 font-medium mt-1"
              >
                {canManageTrainers ? 'View & manage →' : 'View →'}
              </button>
            )}
          </div>
          {trainers.length === 0 && canManageTrainers && (
            <button
              onClick={() => setShowAddModal(true)}
              disabled={processing}
              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              title="Add trainer"
            >
              <Plus className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {/* Manage Trainers Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Batch Trainers</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {trainers.length === 0 ? 'No trainers assigned' : `${trainers.length} trainer${trainers.length !== 1 ? 's' : ''} assigned`}
                  </p>
                </div>
                <button
                  onClick={() => {
                    setShowAddModal(false);
                    setSelectedTrainerId('');
                  }}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>
            </div>

            {/* Modal Body - Scrollable */}
            <div className="flex-1 overflow-y-auto">
              {/* Current Trainers */}
              {trainers.length > 0 && (
                <div className={`p-6 ${canManageTrainers ? 'border-b border-gray-200' : ''}`}>
                  <h4 className="text-sm font-semibold text-gray-900 mb-4">Assigned Trainers</h4>
                  <div className="space-y-3">
                    {trainers.map((trainer, index) => (
                      <div
                        key={trainer.user_id}
                        className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className={`w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold shadow-sm bg-gradient-to-br ${
                              index % 3 === 0 ? 'from-blue-500 to-purple-600' :
                              index % 3 === 1 ? 'from-green-500 to-teal-600' :
                              'from-pink-500 to-rose-600'
                            }`}
                          >
                            {trainer.name.charAt(0).toUpperCase()}
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">{trainer.name}</div>
                            <div className="text-sm text-gray-600">{trainer.email}</div>
                          </div>
                        </div>
                        {canManageTrainers && (
                          <button
                            onClick={() => handleRemoveTrainer(trainer.user_id, trainer.name)}
                            disabled={processing}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                            title="Remove trainer"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Add New Trainer Section - Only for HR/Super Admin */}
              {canManageTrainers && (
                <div className="p-6">
                  <h4 className="text-sm font-semibold text-gray-900 mb-4">Add Trainer</h4>
                  {unassignedTrainers.length === 0 ? (
                    <div className="text-center py-8 bg-gray-50 rounded-lg">
                      <User className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-600">All available trainers are already assigned!</p>
                    </div>
                  ) : (
                  <div className="space-y-4">
                    <select
                      value={selectedTrainerId}
                      onChange={(e) => setSelectedTrainerId(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">-- Select a trainer to add --</option>
                      {unassignedTrainers.map((trainer) => (
                        <option key={trainer.user_id} value={trainer.user_id}>
                          {trainer.name} ({trainer.email})
                        </option>
                      ))}
                    </select>
                    <button
                      onClick={handleAddTrainer}
                      disabled={!selectedTrainerId || processing}
                      className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      {processing ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                          Adding...
                        </>
                      ) : (
                        <>
                          <Plus className="w-4 h-4" />
                          Add Trainer
                        </>
                      )}
                    </button>
                  </div>
                )}
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-6 border-t border-gray-200">
              <button
                onClick={() => {
                  setShowAddModal(false);
                  setSelectedTrainerId('');
                }}
                className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
