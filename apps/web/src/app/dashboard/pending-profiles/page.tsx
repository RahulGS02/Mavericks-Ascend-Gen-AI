"use client";

import { useEffect, useState, useRef } from 'react';
import { Search, UserCheck, UserX, Eye, Calendar, Mail, GraduationCap, Code } from 'lucide-react';
import { hrAPI } from '@/lib/api/hr';
import { batchAPI } from '@/lib/api/batch';
import ProfileReviewModal from '@/components/ProfileReviewModal';

interface Maverick {
  id: string;
  name: string;
  email: string;
  phone?: string;
  college?: string;
  degree?: string;
  branch?: string;
  graduation_year?: number;
  cgpa?: number;
  skills: string[];
  ai_extracted_skills?: string[];
  created_at: string;
}

interface Batch {
  id: string;
  name: string;
  current_enrollment: number;
  max_capacity: number;
}

export default function PendingProfilesPage() {
  const [mavericks, setMavericks] = useState<Maverick[]>([]);
  const [batches, setBatches] = useState<Batch[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMaverick, setSelectedMaverick] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  // Pie chart data
  const [chartData, setChartData] = useState<any>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    fetchData();
    fetchBatches();
  }, [currentPage, searchTerm]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await hrAPI.getPendingProfiles({
        page: currentPage,
        page_size: pageSize,
        search: searchTerm || undefined,
      });
      setMavericks(response.mavericks || []);
      setTotalCount(response.total || 0);
    } catch (error) {
      console.error('Failed to fetch pending profiles:', error);
      setMavericks([]);
      setTotalCount(0);
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

  const handleReviewSuccess = () => {
    fetchData();
    setSelectedMaverick(null);
  };

  // Draw pie chart for profile status distribution
  useEffect(() => {
    if (!canvasRef.current || !mavericks) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Calculate data (for demo, we'll show pending vs reviewed in last 7 days)
    const pending = mavericks?.length || 0;
    const data = {
      labels: ['Pending Review', 'Space'],
      values: [pending, Math.max(5 - pending, 0)],
      colors: ['#ef4444', '#e5e7eb']
    };

    const total = data.values.reduce((a, b) => a + b, 0);
    if (total === 0) return;

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(canvas.width, canvas.height) / 2 - 20;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    let currentAngle = -Math.PI / 2;

    data.values.forEach((value, index) => {
      const sliceAngle = (value / total) * 2 * Math.PI;
      
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
      ctx.closePath();
      ctx.fillStyle = data.colors[index];
      ctx.fill();

      currentAngle += sliceAngle;
    });

    // Draw center circle (donut)
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius * 0.6, 0, 2 * Math.PI);
    ctx.fillStyle = '#ffffff';
    ctx.fill();

    // Draw center text
    ctx.fillStyle = '#1e3a8a';
    ctx.font = 'bold 24px Montserrat';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(pending.toString(), centerX, centerY - 10);
    ctx.font = '12px Montserrat';
    ctx.fillStyle = '#64748b';
    ctx.fillText('Pending', centerX, centerY + 12);
  }, [mavericks]);

  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-blue-900 mb-2">Pending Profiles</h1>
          <p className="text-gray-600">Review and approve new maverick registrations</p>
        </div>

        {/* Analytics Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Pie Chart */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Profile Status</h3>
            <div className="flex justify-center">
              <canvas ref={canvasRef} width={180} height={180}></canvas>
            </div>
            <div className="mt-4 flex justify-center">
              <div className="flex items-center gap-2 text-sm">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <span className="text-gray-600">Pending Review</span>
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Quick Stats</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 text-sm">Total Pending</span>
                <span className="text-2xl font-bold text-blue-900">{totalCount}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 text-sm">This Page</span>
                <span className="text-lg font-semibold text-gray-700">{mavericks.length}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 text-sm">Active Batches</span>
                <span className="text-lg font-semibold text-gray-700">{batches.length}</span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow-sm border border-blue-200 p-6">
            <h3 className="text-sm font-semibold text-blue-900 mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full text-left px-3 py-2 bg-white rounded-md text-sm text-gray-700 hover:bg-blue-50 transition-colors">
                <UserCheck className="w-4 h-4 inline mr-2" />
                Approve All Eligible
              </button>
              <button className="w-full text-left px-3 py-2 bg-white rounded-md text-sm text-gray-700 hover:bg-blue-50 transition-colors">
                <Mail className="w-4 h-4 inline mr-2" />
                Send Reminder Emails
              </button>
            </div>
          </div>
        </div>

        {/* Search Bar */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search by name, email, or college..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Profiles Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
              <p className="mt-4 text-gray-600">Loading profiles...</p>
            </div>
          ) : mavericks.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <UserCheck className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium">No pending profiles found</p>
              <p className="text-sm mt-2">All caught up! 🎉</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Maverick</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Education</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Skills</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Registered</th>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {mavericks.map((maverick) => (
                    <tr key={maverick.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <span className="text-blue-600 font-semibold text-sm">
                              {maverick.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                            </span>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{maverick.name}</div>
                            <div className="text-sm text-gray-500 flex items-center gap-1">
                              <Mail className="w-3 h-3" />
                              {maverick.email}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">{maverick.college}</div>
                        <div className="text-xs text-gray-500 flex items-center gap-1">
                          <GraduationCap className="w-3 h-3" />
                          {maverick.degree} - {maverick.branch}
                        </div>
                        <div className="text-xs text-gray-500">
                          {maverick.graduation_year} • CGPA: {maverick.cgpa}
                        </div>
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
                              +{maverick.skills.length - 3} more
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
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => setSelectedMaverick(maverick.id)}
                          className="inline-flex items-center px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
                        >
                          <Eye className="w-4 h-4 mr-1" />
                          Review
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
              <div className="text-sm text-gray-600">
                Showing <span className="font-semibold">{(currentPage - 1) * pageSize + 1}</span> to{' '}
                <span className="font-semibold">{Math.min(currentPage * pageSize, totalCount)}</span> of{' '}
                <span className="font-semibold">{totalCount}</span> results
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Review Modal */}
      {selectedMaverick && (
        <ProfileReviewModal
          maverickId={selectedMaverick}
          onClose={() => setSelectedMaverick(null)}
          onSuccess={handleReviewSuccess}
          batches={batches}
        />
      )}
    </div>
  );
}
