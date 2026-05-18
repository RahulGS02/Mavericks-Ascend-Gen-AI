"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';
import PipelineVisualEditor from '@/components/PipelineVisualEditor';

interface Job {
  id: string;
  name: string;
  description: string;
  job_type: 'TRAINING' | 'ASSESSMENT' | 'DEPLOYMENT';
  sequence_order: number;
  duration_days: number;
  x: number;
  y: number;
}

interface Connection {
  from: string;
  to: string;
}

export default function CreatePipelinePage() {
  const router = useRouter();
  const [pipelineName, setPipelineName] = useState('New Training Pipeline');
  const [description, setDescription] = useState('');
  const [showNameDialog, setShowNameDialog] = useState(true);

  const handleSave = async (jobs: Job[], connections: Connection[]) => {
    if (!pipelineName.trim()) {
      toast.error('Pipeline name is required');
      return;
    }

    if (jobs.length === 0) {
      toast.error('Add at least one job to the pipeline');
      return;
    }

    try {
      const orderedJobs = jobs.map((job, index) => ({
        name: job.name,
        description: job.description || null,
        job_type: job.job_type,
        sequence_order: index + 1,
        duration_days: job.duration_days
      }));

      const payload = {
        name: pipelineName,
        description: description || null,
        status: 'DRAFT',
        jobs: orderedJobs
      };

      await apiClient.post('/pipelines/', payload);
      toast.success('Pipeline created successfully!');
      router.push('/pipelines');
    } catch (error: any) {
      console.error('Failed to create pipeline:', error);
      toast.error(error.response?.data?.detail || 'Failed to create pipeline');
    }
  };

  return (
    <DashboardLayout>
      <div className="flex flex-col h-screen">
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button onClick={() => router.back()} className="p-2 hover:bg-gray-100 rounded-md">
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </button>
            <div>
              <input
                type="text"
                value={pipelineName}
                onChange={(e) => setPipelineName(e.target.value)}
                className="text-2xl font-bold text-blue-900 bg-transparent border-none focus:outline-none"
                placeholder="Pipeline Name"
              />
              <p className="text-gray-600 text-sm">Visual pipeline builder</p>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-hidden">
          <PipelineVisualEditor
            initialJobs={[]}
            initialConnections={[]}
            onSave={handleSave}
            pipelineName={pipelineName}
            readOnly={false}
          />
        </div>

        {showNameDialog && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Name Your Pipeline</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Pipeline Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={pipelineName}
                    onChange={(e) => setPipelineName(e.target.value)}
                    placeholder="e.g., Full Stack Development Program"
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe this training program..."
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="flex justify-end gap-3">
                  <button onClick={() => router.back()} className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50">
                    Cancel
                  </button>
                  <button onClick={() => setShowNameDialog(false)} className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                    Start Building
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
