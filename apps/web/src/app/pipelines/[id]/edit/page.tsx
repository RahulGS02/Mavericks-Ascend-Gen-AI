"use client";

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
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

export default function EditPipelinePage() {
  const router = useRouter();
  const params = useParams();
  const pipelineId = params.id as string;
  
  const [loading, setLoading] = useState(true);
  const [pipelineName, setPipelineName] = useState('');
  const [description, setDescription] = useState('');
  const [initialJobs, setInitialJobs] = useState<Job[]>([]);
  const [initialConnections, setInitialConnections] = useState<Connection[]>([]);

  useEffect(() => {
    if (pipelineId) {
      fetchPipeline();
    }
  }, [pipelineId]);

  const fetchPipeline = async () => {
    try {
      const response = await apiClient.get(`/pipelines/${pipelineId}`);
      const pipeline = response.data;
      
      setPipelineName(pipeline.name);
      setDescription(pipeline.description || '');
      
      // Convert backend jobs to visual editor format
      const jobs: Job[] = (pipeline.jobs || []).map((job: any, index: number) => ({
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
      const connections: Connection[] = [];
      for (let i = 0; i < jobs.length - 1; i++) {
        connections.push({
          from: jobs[i].id,
          to: jobs[i + 1].id
        });
      }
      
      setInitialJobs(jobs);
      setInitialConnections(connections);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch pipeline:', error);
      toast.error('Failed to load pipeline');
      router.push('/pipelines');
    }
  };

  const handleSave = async (jobs: Job[], connections: Connection[]) => {
    try {
      // Delete all existing jobs
      for (const job of initialJobs) {
        try {
          await apiClient.delete(`/pipelines/${pipelineId}/jobs/${job.id}`);
        } catch (e) {
          console.log('Job already deleted or not found');
        }
      }

      // Add new jobs
      const orderedJobs = jobs.map((job, index) => ({
        name: job.name,
        description: job.description || null,
        job_type: job.job_type,
        sequence_order: index + 1,
        duration_days: job.duration_days
      }));

      for (const job of orderedJobs) {
        await apiClient.post(`/pipelines/${pipelineId}/jobs`, job);
      }

      // Update pipeline name and description
      await apiClient.patch(`/pipelines/${pipelineId}`, {
        name: pipelineName,
        description: description || null
      });

      toast.success('Pipeline updated successfully!');
      router.push('/pipelines');
    } catch (error: any) {
      console.error('Failed to update pipeline:', error);
      toast.error(error.response?.data?.detail || 'Failed to update pipeline');
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
              />
              <p className="text-gray-600 text-sm">Edit pipeline - modify jobs and connections</p>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-hidden">
          <PipelineVisualEditor
            initialJobs={initialJobs}
            initialConnections={initialConnections}
            onSave={handleSave}
            pipelineName={pipelineName}
            readOnly={false}
          />
        </div>
      </div>
    </DashboardLayout>
  );
}
