"use client";

import { useEffect, useState, useRef } from 'react';
import { Search, Users, Calendar, TrendingUp, User, BookOpen, CheckCircle2 } from 'lucide-react';
import { batchAPI } from '@/lib/api/batch';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import Link from 'next/link';

interface Batch {
  id: string;
  name: string;
  description?: string;
  category?: string;
  start_date: string;
  end_date: string;
  max_capacity: number;
  current_enrollment: number;
  trainer_id?: string;
  status: 'ACTIVE' | 'COMPLETED' | 'DRAFT';
  created_at: string;
  focus_areas?: string[];
}

interface BatchProgress {
  [batchId: string]: number;
}

export default function ActiveBatchesPage() {
  const [batches, setBatches] = useState<Batch[]>([]);
  const [batchProgress, setBatchProgress] = useState<BatchProgress>({});
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const progressCanvasRef = useRef<HTMLCanvasElement>(null);
  const capacityCanvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    fetchBatches();
  }, []);

  const fetchBatches = async () => {
    setLoading(true);
    try {
      const response = await batchAPI.getAllBatches({
        status: 'ACTIVE',
        page: 1,
        page_size: 100,
      });
      const batchesData = response?.batches || [];
      setBatches(batchesData);

      // Fetch job progress for each batch
      const progressMap: BatchProgress = {};
      await Promise.all(
        batchesData.map(async (batch) => {
          try {
            const progressResponse = await apiClient.get(`/job-progress/batch/${batch.id}`);
            progressMap[batch.id] = progressResponse.data.overall_completion || 0;
          } catch (err) {
            // If no progress data, default to 0
            progressMap[batch.id] = 0;
          }
        })
      );

      setBatchProgress(progressMap);
    } catch (error) {
      console.error('Failed to fetch batches:', error);
      toast.error('Failed to load batches');
      setBatches([]);
    } finally {
      setLoading(false);
    }
  };

  const getProgress = (batchId: string) => {
    return Math.round(batchProgress[batchId] || 0);
  };

  // Draw batch progress line chart
  useEffect(() => {
    if (!progressCanvasRef.current || batches.length === 0) return;

    const canvas = progressCanvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const padding = 40;
    const chartWidth = canvas.width - padding * 2;
    const chartHeight = canvas.height - padding * 2;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw grid
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
      const y = padding + (chartHeight / 5) * i;
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(canvas.width - padding, y);
      ctx.stroke();
    }

    // Draw progress for each batch (show top 5)
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
    batches.slice(0, 5).forEach((batch, index) => {
      const progress = getProgress(batch.id);
      const y = padding + (index * (chartHeight / 6)) + 20;
      
      // Background bar
      ctx.fillStyle = '#e5e7eb';
      ctx.fillRect(padding, y, chartWidth, 15);
      
      // Progress bar
      ctx.fillStyle = colors[index];
      ctx.fillRect(padding, y, (progress / 100) * chartWidth, 15);
      
      // Label
      ctx.fillStyle = '#374151';
      ctx.font = '11px Montserrat';
      ctx.textAlign = 'left';
      ctx.fillText(batch.name.slice(0, 20), padding, y - 5);
      
      // Percentage
      ctx.textAlign = 'right';
      ctx.fillText(`${progress}%`, canvas.width - padding, y + 11);
    });
  }, [batches]);

  // Draw capacity vs enrollment bar chart
  useEffect(() => {
    if (!capacityCanvasRef.current || batches.length === 0) return;

    const canvas = capacityCanvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const padding = 40;
    const chartWidth = canvas.width - padding * 2;
    const chartHeight = canvas.height - padding * 2;
    const barWidth = chartWidth / (batches.length * 2);
    const maxCapacity = Math.max(...batches.map(b => b.max_capacity), 1);

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    batches.forEach((batch, index) => {
      const x = padding + (index * barWidth * 2);
      
      // Capacity bar (gray)
      const capacityHeight = (batch.max_capacity / maxCapacity) * chartHeight;
      ctx.fillStyle = '#e5e7eb';
      ctx.fillRect(x, canvas.height - padding - capacityHeight, barWidth * 0.8, capacityHeight);
      
      // Enrollment bar (blue)
      const enrollmentHeight = (batch.current_enrollment / maxCapacity) * chartHeight;
      ctx.fillStyle = '#3b82f6';
      ctx.fillRect(x + barWidth, canvas.height - padding - enrollmentHeight, barWidth * 0.8, enrollmentHeight);
    });

    // Legend
    ctx.fillStyle = '#e5e7eb';
    ctx.fillRect(padding, 10, 15, 15);
    ctx.fillStyle = '#374151';
    ctx.font = '11px Montserrat';
    ctx.fillText('Capacity', padding + 20, 21);

    ctx.fillStyle = '#3b82f6';
    ctx.fillRect(padding + 100, 10, 15, 15);
    ctx.fillStyle = '#374151';
    ctx.fillText('Enrolled', padding + 120, 21);
  }, [batches]);

  const filteredBatches = batches.filter(batch =>
    batch.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    batch.category?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalEnrollment = batches.reduce((sum, b) => sum + b.current_enrollment, 0);
  const totalCapacity = batches.reduce((sum, b) => sum + b.max_capacity, 0);
  const avgUtilization = totalCapacity > 0 ? Math.round((totalEnrollment / totalCapacity) * 100) : 0;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-blue-900 mb-2">Active Batches</h1>
          <p className="text-gray-600">Monitor ongoing training batches and enrollment</p>
        </div>

        {/* Analytics Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Progress Chart */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Batch Progress Timeline</h3>
            <canvas ref={progressCanvasRef} width={500} height={200}></canvas>
          </div>

          {/* Capacity Chart */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Capacity vs Enrollment</h3>
            <canvas ref={capacityCanvasRef} width={500} height={200}></canvas>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Batches</p>
                <p className="text-3xl font-bold text-blue-600">{batches.length}</p>
              </div>
              <BookOpen className="w-10 h-10 text-blue-400" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Enrolled</p>
                <p className="text-3xl font-bold text-green-600">{totalEnrollment}</p>
              </div>
              <Users className="w-10 h-10 text-green-400" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Capacity</p>
                <p className="text-3xl font-bold text-purple-600">{totalCapacity}</p>
              </div>
              <TrendingUp className="w-10 h-10 text-purple-400" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Utilization</p>
                <p className="text-3xl font-bold text-orange-600">{avgUtilization}%</p>
              </div>
              <CheckCircle2 className="w-10 h-10 text-orange-400" />
            </div>
          </div>
        </div>

        {/* Search Bar */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search by batch name or category..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Batches Grid */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
              <p className="mt-4 text-gray-600">Loading batches...</p>
            </div>
          ) : filteredBatches.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <BookOpen className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium">No active batches found</p>
              <p className="text-sm mt-2">Try adjusting your search</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
              {filteredBatches.map((batch) => {
                const progress = getProgress(batch.id);
                const utilization = Math.round((batch.current_enrollment / batch.max_capacity) * 100);

                return (
                  <div key={batch.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                    <div className="mb-4">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">{batch.name}</h3>
                      {batch.category && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                          {batch.category}
                        </span>
                      )}
                    </div>

                    {batch.description && (
                      <p className="text-sm text-gray-600 mb-4 line-clamp-2">{batch.description}</p>
                    )}

                    {/* Progress Bar */}
                    <div className="mb-4">
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">Progress</span>
                        <span className="font-semibold text-blue-600">{progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{ width: `${progress}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Enrollment */}
                    <div className="mb-4">
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">Enrollment</span>
                        <span className="font-semibold text-green-600">{utilization}%</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-gray-400" />
                        <span className="text-sm font-medium">
                          {batch.current_enrollment} / {batch.max_capacity} Mavericks
                        </span>
                      </div>
                    </div>

                    {/* Dates */}
                    <div className="border-t border-gray-200 pt-4 space-y-2">
                      <div className="flex items-center gap-2 text-sm">
                        <Calendar className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-600">
                          {new Date(batch.start_date).toLocaleDateString()} - {new Date(batch.end_date).toLocaleDateString()}
                        </span>
                      </div>
                      {batch.focus_areas && batch.focus_areas.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {batch.focus_areas.slice(0, 3).map((area, idx) => (
                            <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-700">
                              {area}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* View Details Button */}
                    <Link
                      href={`/dashboard/batches/${batch.id}`}
                      className="mt-4 block w-full text-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
                    >
                      View Details
                    </Link>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
