"use client";

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { ArrowLeft, Edit, Copy, GitBranch, Clock, CheckCircle } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';
import PipelineVisualEditor from '@/components/PipelineVisualEditor';

interface Job {
  id: string;
  name: string;
  description: string;
  job_type: string;
  sequence_order: number;
  duration_days: number;
  x: number;
  y: number;
}

interface Pipeline {
  id: string;
  name: string;
  description?: string;
  status: string;
  jobs: any[];
}

export default function ViewPipelinePage() {
  const router = useRouter();
  const params = useParams();
  const pipelineId = params.id as string;
  
  const [loading, setLoading] = useState(true);
  const [pipeline, setPipeline] = useState<Pipeline | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [connections, setConnections] = useState<any[]>([]);

  useEffect(() => {
    if (pipelineId) {
      fetchPipeline();
    }
  }, [pipelineId]);

  const fetchPipeline = async () => {
    try {
      const response = await apiClient.get(`/pipelines/${pipelineId}`);
      const pipelineData = response.data;
      
      setPipeline(pipelineData);
      
      // Convert backend jobs to visual format
      const visualJobs: Job[] = (pipelineData.jobs || []).map((job: any, index: number) => ({
        id: job.id,
        name: job.name,
        description: job.description || '',
        job_type: job.job_type,
        sequence_order: job.sequence_order,
        duration_days: job.duration_days || 7,
        x: 100 + (index * 250),
        y: 100 + (index % 3) * 150
      }));
      
      // Create connections based on sequence
      const visualConnections: any[] = [];
      for (let i = 0; i < visualJobs.length - 1; i++) {
        visualConnections.push({
          from: visualJobs[i].id,
          to: visualJobs[i + 1].id
        });
      }
      
      setJobs(visualJobs);
      setConnections(visualConnections);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch pipeline:', error);
      toast.error('Failed to load pipeline');
      router.push('/pipelines');
    }
  };

  const handleEdit = () => {
    router.push(`/pipelines/${pipelineId}/edit`);
  };

  const handleClone = async () => {
    try {
      const newName = `Copy of ${pipeline?.name}`;
      await apiClient.post(`/pipelines/${pipelineId}/clone`, null, {
        params: { new_name: newName, include_jobs: true }
      });
      toast.success(`Pipeline cloned as "${newName}"`);
      router.push('/pipelines');
    } catch (error) {
      console.error('Failed to clone pipeline:', error);
      toast.error('Failed to clone pipeline');
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (!pipeline) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="text-center text-gray-500">Pipeline not found</div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="flex flex-col h-screen">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.back()}
                className="p-2 hover:bg-gray-100 rounded-md"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-blue-900">{pipeline.name}</h1>
                <p className="text-gray-600 text-sm">{pipeline.description || 'Training pipeline'}</p>
              </div>
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={handleClone}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                <Copy className="w-4 h-4 mr-2" />
                Clone
              </button>
              <button
                onClick={handleEdit}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <Edit className="w-4 h-4 mr-2" />
                Edit
              </button>
            </div>
          </div>
        </div>

        {/* Visual View */}
        <div className="flex-1 overflow-hidden">
          <PipelineVisualEditor
            initialJobs={jobs}
            initialConnections={connections}
            onSave={() => {}}
            pipelineName={pipeline.name}
            readOnly={true}
          />
        </div>
      </div>
    </DashboardLayout>
  );
}
