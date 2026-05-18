"use client";

import { useEffect, useState, useRef } from 'react';
import { Search, Users, UserPlus, Calendar, Code, AlertCircle, CheckCircle } from 'lucide-react';
import { hrAPI } from '@/lib/api/hr';
import { batchAPI } from '@/lib/api/batch';
import { toast } from 'sonner';

interface Maverick {
  id: string;
  name: string;
  email: string;
  skills: string[];
  ai_extracted_skills?: string[];
  college?: string;
  degree?: string;
  created_at: string;
}

interface Batch {
  id: string;
  name: string;
  current_enrollment: number;
  max_capacity: number;
  focus_areas?: string[];
}

export default function UnassignedMavericksPage() {
  const [mavericks, setMavericks] = useState<Maverick[]>([]);
  const [batches, setBatches] = useState<Batch[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMavericks, setSelectedMavericks] = useState<Set<string>>(new Set());
  const [selectedBatch, setSelectedBatch] = useState<string>('');
  const [assigning, setAssigning] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    fetchData();
    fetchBatches();
  }, [searchTerm]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await hrAPI.getAllMavericks({
        profile_status: 'approved',
        page: 1,
        page_size: 100,
        search: searchTerm || undefined,
      });

      // Filter unassigned (no current_batch_id)
      const unassigned = (response.mavericks || []).filter((m: any) => !m.current_batch_id);
      setMavericks(unassigned);
    } catch (error) {
      console.error('Failed to fetch mavericks:', error);
      toast.error('Failed to load unassigned mavericks');
      setMavericks([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchBatches = async () => {
    try {
      const response = await batchAPI.getActiveBatches();
      setBatches(response.batches || []);
    } catch (error) {
      console.error('Failed to fetch batches:', error);
      setBatches([]);
    }
  };

  const handleBulkAssign = async () => {
    if (!selectedBatch || selectedMavericks.size === 0) {
      toast.error('Please select a batch and at least one maverick');
      return;
    }

    setAssigning(true);
    try {
      await batchAPI.bulkAssignMavericks(selectedBatch, Array.from(selectedMavericks));
      toast.success(`Successfully assigned ${selectedMavericks.size} maverick(s) to batch`);
      setSelectedMavericks(new Set());
      setSelectedBatch('');
      fetchData();
    } catch (error: any) {
      console.error('Failed to assign mavericks:', error);
      toast.error(error.response?.data?.detail || 'Failed to assign mavericks');
    } finally {
      setAssigning(false);
    }
  };

  const toggleMaverickSelection = (id: string) => {
    const newSelection = new Set(selectedMavericks);
    if (newSelection.has(id)) {
      newSelection.delete(id);
    } else {
      newSelection.add(id);
    }
    setSelectedMavericks(newSelection);
  };

  const toggleSelectAll = () => {
    if (selectedMavericks.size === mavericks.length) {
      setSelectedMavericks(new Set());
    } else {
      setSelectedMavericks(new Set(mavericks.map(m => m.id)));
    }
  };

  // Draw skills distribution bar chart
  useEffect(() => {
    if (!canvasRef.current || mavericks.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Count skills
    const skillCounts: Record<string, number> = {};
    mavericks.forEach(m => {
      (m.skills || []).forEach(skill => {
        skillCounts[skill] = (skillCounts[skill] || 0) + 1;
      });
    });

    // Get top 5 skills
    const topSkills = Object.entries(skillCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);

    if (topSkills.length === 0) return;

    const maxCount = topSkills[0][1];
    const barHeight = 25;
    const barSpacing = 10;
    const leftMargin = 100;
    const chartWidth = canvas.width - leftMargin - 40;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    topSkills.forEach(([skill, count], index) => {
      const y = index * (barHeight + barSpacing) + 10;
      const barWidth = (count / maxCount) * chartWidth;

      // Draw bar
      ctx.fillStyle = '#3b82f6';
      ctx.fillRect(leftMargin, y, barWidth, barHeight);

      // Draw skill name
      ctx.fillStyle = '#374151';
      ctx.font = '12px Montserrat';
      ctx.textAlign = 'right';
      ctx.fillText(skill, leftMargin - 10, y + barHeight / 2 + 4);

      // Draw count
      ctx.fillStyle = '#ffffff';
      ctx.textAlign = 'left';
      ctx.fillText(count.toString(), leftMargin + 8, y + barHeight / 2 + 4);
    });
  }, [mavericks]);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-blue-900 mb-2">Unassigned Mavericks</h1>
          <p className="text-gray-600">Approved mavericks waiting for batch assignment</p>
        </div>

        {/* Analytics Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Skills Bar Chart */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Top Skills Distribution</h3>
            <canvas ref={canvasRef} width={600} height={185}></canvas>
          </div>

          {/* Quick Stats */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Quick Stats</h3>
            <div className="space-y-4">
              <div>
                <div className="text-3xl font-bold text-orange-600">{mavericks.length}</div>
                <div className="text-sm text-gray-500">Unassigned Mavericks</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-600">{batches.length}</div>
                <div className="text-sm text-gray-500">Active Batches</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">{selectedMavericks.size}</div>
                <div className="text-sm text-gray-500">Selected for Assignment</div>
              </div>
            </div>
          </div>
        </div>

        {/* Bulk Assignment Section */}
        {selectedMavericks.size > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <AlertCircle className="w-5 h-5 text-blue-600" />
                <span className="font-medium text-blue-900">
                  {selectedMavericks.size} maverick(s) selected
                </span>
                <select
                  value={selectedBatch}
                  onChange={(e) => setSelectedBatch(e.target.value)}
                  className="px-3 py-2 border border-blue-300 rounded-md focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select a batch...</option>
                  {batches.map(batch => (
                    <option key={batch.id} value={batch.id}>
                      {batch.name} ({batch.current_enrollment}/{batch.max_capacity})
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setSelectedMavericks(new Set())}
                  className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleBulkAssign}
                  disabled={!selectedBatch || assigning}
                  className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {assigning ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                      Assigning...
                    </>
                  ) : (
                    <>
                      <UserPlus className="w-4 h-4" />
                      Assign to Batch
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Search Bar */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search by name, email, or skills..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
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
              <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-300" />
              <p className="text-lg font-medium">No unassigned mavericks</p>
              <p className="text-sm mt-2">All approved mavericks are assigned to batches! 🎉</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left">
                      <input
                        type="checkbox"
                        checked={selectedMavericks.size === mavericks.length && mavericks.length > 0}
                        onChange={toggleSelectAll}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Maverick</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Education</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Skills</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Approved On</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {mavericks.map((maverick) => (
                    <tr key={maverick.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <input
                          type="checkbox"
                          checked={selectedMavericks.has(maverick.id)}
                          onChange={() => toggleMaverickSelection(maverick.id)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10 rounded-full bg-orange-100 flex items-center justify-center">
                            <span className="text-orange-600 font-semibold text-sm">
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
                        <div className="text-xs text-gray-500">{maverick.degree}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1">
                          {(maverick.skills || []).slice(0, 3).map((skill, idx) => (
                            <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                              <Code className="w-3 h-3 mr-1" />
                              {skill}
                            </span>
                          ))}
                          {(maverick.skills?.length || 0) > 3 && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
                              +{maverick.skills.length - 3}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-500 flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {new Date(maverick.created_at).toLocaleDateString()}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
