"use client";

import { useEffect, useState, useRef } from 'react';
import { Search, CheckCircle, XCircle, Clock, Building2, User, Calendar, FileText } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';

interface DeploymentRequest {
  id: string;
  maverick_id: string;
  maverick_name?: string;
  requested_by: string;
  project_name: string;
  vertical: string;
  competency: string;
  justification: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  created_at: string;
  approved_by?: string;
  approved_at?: string;
  rejection_reason?: string;
}

interface TimelineData {
  date: string;
  count: number;
}

export default function PendingRequestsPage() {
  const [requests, setRequests] = useState<DeploymentRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'PENDING' | 'APPROVED' | 'REJECTED'>('PENDING');
  const [selectedRequest, setSelectedRequest] = useState<string | null>(null);
  const [actionInProgress, setActionInProgress] = useState(false);
  const timelineCanvasRef = useRef<HTMLCanvasElement>(null);
  const verticalPieRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    fetchRequests();
  }, [statusFilter]);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/deployments/requests', {
        params: {
          status_filter: statusFilter === 'all' ? undefined : statusFilter,
          page: 1,
          page_size: 100,
        }
      });
      setRequests(response.data?.requests || []);
    } catch (error) {
      console.error('Failed to fetch deployment requests:', error);
      toast.error('Failed to load deployment requests');
      setRequests([]);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (requestId: string) => {
    if (!confirm('Approve this deployment request?')) return;
    
    setActionInProgress(true);
    try {
      await apiClient.post(`/deployments/requests/${requestId}/approve`);
      toast.success('Deployment request approved');
      fetchRequests();
    } catch (error: any) {
      console.error('Failed to approve request:', error);
      toast.error(error.response?.data?.detail || 'Failed to approve request');
    } finally {
      setActionInProgress(false);
    }
  };

  const handleReject = async (requestId: string) => {
    const reason = prompt('Enter rejection reason:');
    if (!reason) return;

    setActionInProgress(true);
    try {
      await apiClient.post(`/deployments/requests/${requestId}/reject`, { reason });
      toast.success('Deployment request rejected');
      fetchRequests();
    } catch (error: any) {
      console.error('Failed to reject request:', error);
      toast.error(error.response?.data?.detail || 'Failed to reject request');
    } finally {
      setActionInProgress(false);
    }
  };

  // Draw timeline chart
  useEffect(() => {
    if (!timelineCanvasRef.current || requests.length === 0) return;

    const canvas = timelineCanvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Group by week
    const weekCounts: Record<string, number> = {};
    const now = new Date();
    
    for (let i = 0; i < 8; i++) {
      const weekDate = new Date(now);
      weekDate.setDate(weekDate.getDate() - (i * 7));
      const weekKey = weekDate.toISOString().split('T')[0].slice(0, 10);
      weekCounts[weekKey] = 0;
    }

    requests.forEach(req => {
      const reqDate = new Date(req.created_at);
      const weekStart = new Date(reqDate);
      weekStart.setDate(weekStart.getDate() - weekStart.getDay());
      const weekKey = weekStart.toISOString().split('T')[0];
      if (weekKey in weekCounts) {
        weekCounts[weekKey]++;
      }
    });

    const weeks = Object.keys(weekCounts).sort().reverse().slice(0, 8);
    const counts = weeks.map(w => weekCounts[w]);
    const maxCount = Math.max(...counts, 1);

    const padding = 40;
    const chartWidth = canvas.width - padding * 2;
    const chartHeight = canvas.height - padding * 2;
    const barWidth = chartWidth / weeks.length;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw grid lines
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
      const y = padding + (chartHeight / 5) * i;
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(canvas.width - padding, y);
      ctx.stroke();
    }

    // Draw line chart
    ctx.beginPath();
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 3;
    
    counts.forEach((count, index) => {
      const x = padding + (index * barWidth) + barWidth / 2;
      const y = padding + chartHeight - (count / maxCount) * chartHeight;
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();

    // Draw points
    counts.forEach((count, index) => {
      const x = padding + (index * barWidth) + barWidth / 2;
      const y = padding + chartHeight - (count / maxCount) * chartHeight;
      
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, 2 * Math.PI);
      ctx.fillStyle = '#3b82f6';
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();
    });

    // Draw labels
    ctx.fillStyle = '#6b7280';
    ctx.font = '10px Montserrat';
    ctx.textAlign = 'center';
    weeks.forEach((week, index) => {
      const x = padding + (index * barWidth) + barWidth / 2;
      const label = new Date(week).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      ctx.fillText(label, x, canvas.height - 10);
    });
  }, [requests]);

  // Draw vertical distribution pie chart
  useEffect(() => {
    if (!verticalPieRef.current || requests.length === 0) return;

    const canvas = verticalPieRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const verticalCounts: Record<string, number> = {};
    requests.forEach(req => {
      verticalCounts[req.vertical] = (verticalCounts[req.vertical] || 0) + 1;
    });

    const verticals = Object.keys(verticalCounts);
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
    
    const total = requests.length;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(canvas.width, canvas.height) / 2 - 20;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    let currentAngle = -Math.PI / 2;
    verticals.forEach((vertical, index) => {
      const count = verticalCounts[vertical];
      const sliceAngle = (count / total) * 2 * Math.PI;

      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
      ctx.closePath();
      ctx.fillStyle = colors[index % colors.length];
      ctx.fill();

      currentAngle += sliceAngle;
    });

    // Draw center circle (donut)
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius * 0.6, 0, 2 * Math.PI);
    ctx.fillStyle = '#ffffff';
    ctx.fill();
  }, [requests]);

  const filteredRequests = requests.filter(req =>
    req.project_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    req.vertical.toLowerCase().includes(searchTerm.toLowerCase()) ||
    req.competency.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const pendingCount = requests.filter(r => r.status === 'PENDING').length;
  const approvedCount = requests.filter(r => r.status === 'APPROVED').length;
  const rejectedCount = requests.filter(r => r.status === 'REJECTED').length;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-blue-900 mb-2">Deployment Requests</h1>
          <p className="text-gray-600">Review and approve maverick deployment requests</p>
        </div>

        {/* Analytics Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Timeline Chart */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Request Volume (Last 8 Weeks)</h3>
            <canvas ref={timelineCanvasRef} width={600} height={200}></canvas>
          </div>

          {/* Vertical Distribution */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Vertical Distribution</h3>
            <div className="flex justify-center">
              <canvas ref={verticalPieRef} width={180} height={180}></canvas>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Pending</p>
                <p className="text-3xl font-bold text-orange-600">{pendingCount}</p>
              </div>
              <Clock className="w-10 h-10 text-orange-400" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Approved</p>
                <p className="text-3xl font-bold text-green-600">{approvedCount}</p>
              </div>
              <CheckCircle className="w-10 h-10 text-green-400" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Rejected</p>
                <p className="text-3xl font-bold text-red-600">{rejectedCount}</p>
              </div>
              <XCircle className="w-10 h-10 text-red-400" />
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by project, vertical, or competency..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as any)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="PENDING">Pending Only</option>
              <option value="all">All Requests</option>
              <option value="APPROVED">Approved</option>
              <option value="REJECTED">Rejected</option>
            </select>
          </div>
        </div>

        {/* Requests Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
              <p className="mt-4 text-gray-600">Loading requests...</p>
            </div>
          ) : filteredRequests.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium">No deployment requests found</p>
              <p className="text-sm mt-2">Try adjusting your filters</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Project</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Maverick</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Vertical/Competency</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Requested</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredRequests.map((request) => (
                    <tr key={request.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <Building2 className="w-5 h-5 text-blue-500 mr-2" />
                          <div>
                            <div className="text-sm font-medium text-gray-900">{request.project_name}</div>
                            <div className="text-xs text-gray-500 mt-1">{request.justification.slice(0, 60)}...</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <User className="w-4 h-4 text-gray-400 mr-2" />
                          <span className="text-sm text-gray-900">{request.maverick_name || 'N/A'}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">{request.vertical}</div>
                        <div className="text-xs text-gray-500">{request.competency}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-500 flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {new Date(request.created_at).toLocaleDateString()}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {request.status === 'PENDING' && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                            <Clock className="w-3 h-3 mr-1" />
                            Pending
                          </span>
                        )}
                        {request.status === 'APPROVED' && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Approved
                          </span>
                        )}
                        {request.status === 'REJECTED' && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            <XCircle className="w-3 h-3 mr-1" />
                            Rejected
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right">
                        {request.status === 'PENDING' && (
                          <div className="flex justify-end gap-2">
                            <button
                              onClick={() => handleApprove(request.id)}
                              disabled={actionInProgress}
                              className="inline-flex items-center px-3 py-1.5 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              <CheckCircle className="w-4 h-4 mr-1" />
                              Approve
                            </button>
                            <button
                              onClick={() => handleReject(request.id)}
                              disabled={actionInProgress}
                              className="inline-flex items-center px-3 py-1.5 bg-red-600 text-white text-sm font-medium rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              <XCircle className="w-4 h-4 mr-1" />
                              Reject
                            </button>
                          </div>
                        )}
                        {request.status === 'APPROVED' && (
                          <span className="text-sm text-gray-500">
                            {request.approved_at && new Date(request.approved_at).toLocaleDateString()}
                          </span>
                        )}
                        {request.status === 'REJECTED' && (
                          <span className="text-sm text-gray-500" title={request.rejection_reason}>
                            See reason
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
    </div>
  );
}
