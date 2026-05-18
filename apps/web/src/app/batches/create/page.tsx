"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Save, Calendar, Users } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';

interface Pipeline {
  id: string;
  name: string;
  description?: string;
  status: string;
  jobs: any[];
}

interface Trainer {
  user_id: string;
  name: string;
  email: string;
  is_active: boolean;
}

export default function CreateBatchPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [trainers, setTrainers] = useState<Trainer[]>([]);
  const [loadingPipelines, setLoadingPipelines] = useState(true);
  const [loadingTrainers, setLoadingTrainers] = useState(true);

  // Form fields
  const [batchName, setBatchName] = useState('');
  const [description, setDescription] = useState('');
  const [pipelineId, setPipelineId] = useState('');
  const [trainerId, setTrainerId] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [maxCapacity, setMaxCapacity] = useState(20);
  const [category, setCategory] = useState('');

  useEffect(() => {
    fetchPipelines();
    fetchTrainers();
  }, []);

  const fetchPipelines = async () => {
    try {
      const response = await apiClient.get('/pipelines/', {
        params: { page: 1, page_size: 100 }
      });
      const activePipelines = (response.data?.pipelines || []).filter(
        (p: Pipeline) => p.status === 'ACTIVE' || p.status === 'DRAFT'
      );
      setPipelines(activePipelines);
    } catch (error) {
      console.error('Failed to fetch pipelines:', error);
      toast.error('Failed to load pipelines');
    } finally {
      setLoadingPipelines(false);
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
      toast.error('Failed to load trainers');
    } finally {
      setLoadingTrainers(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!batchName.trim()) {
      toast.error('Batch name is required');
      return;
    }

    if (!pipelineId) {
      toast.error('Please select a training pipeline');
      return;
    }

    if (!startDate || !endDate) {
      toast.error('Start and end dates are required');
      return;
    }

    setLoading(true);
    try {
      const payload = {
        name: batchName,
        description: description || null,
        pipeline_id: pipelineId,
        trainer_id: trainerId || null,
        start_date: startDate,
        end_date: endDate || null,
        max_capacity: maxCapacity,
        category: category || null
      };

      await apiClient.post('/batches/', payload);
      toast.success('Batch created successfully!');
      router.push('/batches');
    } catch (error: any) {
      console.error('Failed to create batch:', error);

      // Handle validation errors (array of error objects)
      let errorMessage = 'Failed to create batch';
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          // Pydantic validation errors
          const errors = error.response.data.detail.map((err: any) =>
            `${err.loc?.join('.') || 'Field'}: ${err.msg || err}`
          ).join(', ');
          errorMessage = errors;
        } else if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else {
          errorMessage = JSON.stringify(error.response.data.detail);
        }
      }

      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const selectedPipeline = pipelines.find(p => p.id === pipelineId);

  return (
    <DashboardLayout>
      <div className="p-6 max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6 flex items-center gap-4">
          <button
            onClick={() => router.back()}
            className="p-2 hover:bg-gray-100 rounded-md"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-blue-900">Create New Batch</h1>
            <p className="text-gray-600">Set up a new training batch with a pipeline</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Batch Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={batchName}
                  onChange={(e) => setBatchName(e.target.value)}
                  placeholder="e.g., Q1 2024 Full Stack Batch"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe this batch..."
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category
                  <span className="text-gray-500 text-xs ml-2">(Optional - for AI batch matching)</span>
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">-- Select Category (Optional) --</option>
                  <option value="TECH_DEVELOPMENT">Tech Development (Web, Mobile, Backend, Frontend)</option>
                  <option value="TECH_DEVOPS">Tech DevOps (Cloud, Infrastructure)</option>
                  <option value="TECH_TESTING">Tech Testing (QA, Automation)</option>
                  <option value="TECH_DATA_SCIENCE">Tech Data Science (ML, AI, Data Analysis)</option>
                  <option value="TECH_CYBER_SECURITY">Tech Cyber Security</option>
                  <option value="SOFT_SKILLS">Soft Skills (Communication, Leadership)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Pipeline Selection */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Training Pipeline & Trainer</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Pipeline <span className="text-red-500">*</span>
                </label>
                {loadingPipelines ? (
                  <div className="text-gray-500">Loading pipelines...</div>
                ) : pipelines.length === 0 ? (
                  <div className="text-amber-600 bg-amber-50 border border-amber-200 rounded-md p-4">
                    ⚠️ No pipelines available. Please create a pipeline first.
                  </div>
                ) : (
                  <select
                    value={pipelineId}
                    onChange={(e) => setPipelineId(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">-- Select a training pipeline --</option>
                    {pipelines.map((pipeline) => (
                      <option key={pipeline.id} value={pipeline.id}>
                        {pipeline.name} ({pipeline.jobs?.length || 0} jobs)
                      </option>
                    ))}
                  </select>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Assign Trainer (Optional)
                </label>
                {loadingTrainers ? (
                  <div className="text-gray-500">Loading trainers...</div>
                ) : (
                  <select
                    value={trainerId}
                    onChange={(e) => setTrainerId(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">-- No trainer assigned --</option>
                    {trainers.map((trainer) => (
                      <option key={trainer.user_id} value={trainer.user_id}>
                        {trainer.name} ({trainer.email})
                      </option>
                    ))}
                  </select>
                )}
                <p className="text-xs text-gray-500 mt-1">You can assign a trainer later if needed</p>
              </div>
            </div>

            {selectedPipeline && (
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mt-4">
                <div className="text-sm font-medium text-blue-900 mb-2">📋 Pipeline: {selectedPipeline.name}</div>
                {selectedPipeline.description && (
                  <p className="text-sm text-blue-700 mb-2">{selectedPipeline.description}</p>
                )}
                <div className="text-sm text-blue-700">
                  ✅ {selectedPipeline.jobs?.length || 0} jobs configured
                </div>
              </div>
            )}
          </div>

          {/* Schedule */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              <Calendar className="w-5 h-5 inline mr-2" />
              Schedule
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Date <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  End Date <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  min={startDate}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
            </div>
          </div>

          {/* Capacity */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              <Users className="w-5 h-5 inline mr-2" />
              Capacity
            </h2>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Maximum Capacity <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={maxCapacity}
                onChange={(e) => setMaxCapacity(parseInt(e.target.value) || 20)}
                min="1"
                max="100"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <p className="text-sm text-gray-500 mt-1">Maximum number of trainees in this batch</p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-4">
            <button
              type="button"
              onClick={() => router.back()}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || loadingPipelines}
              className="inline-flex items-center px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                  Creating...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Create Batch
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  );
}
