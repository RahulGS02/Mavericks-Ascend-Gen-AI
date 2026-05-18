"use client";

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Search, AlertTriangle, User, Calendar, TrendingDown, BookOpen, Mail, Phone, Eye } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';

interface AtRiskMaverick {
  id: string;
  name: string;
  email: string;
  phone?: string;
  current_batch_id?: string;
  batch_name?: string;
  failed_assessments: number;
  total_assessments: number;
  recent_failures: Array<{
    assessment_name: string;
    marks_obtained: number;
    max_marks: number;
    evaluated_at: string;
    feedback?: string;
  }>;
  risk_level: 'HIGH' | 'MEDIUM' | 'LOW';
}

interface FailureReason {
  category: string;
  count: number;
}

export default function AtRiskMavericksPage() {
  const router = useRouter();
  const [mavericks, setMavericks] = useState<AtRiskMaverick[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState<'all' | 'HIGH' | 'MEDIUM' | 'LOW'>('all');
  const failureBarRef = useRef<HTMLCanvasElement>(null);
  const riskPieRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    fetchAtRiskMavericks();
  }, []);

  const fetchAtRiskMavericks = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/hr/dashboard/at-risk-mavericks');
      setMavericks(response.data?.at_risk_mavericks || []);
    } catch (error) {
      console.error('Failed to fetch at-risk mavericks:', error);
      toast.error('Failed to load at-risk mavericks');
      setMavericks([]);
    } finally {
      setLoading(false);
    }
  };

  // Draw failure reasons bar chart
  useEffect(() => {
    if (!failureBarRef.current || mavericks.length === 0) return;

    const canvas = failureBarRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Categorize failures (simplified - in production, get from API)
    const reasons: FailureReason[] = [
      { category: 'Low Marks (<50%)', count: 0 },
      { category: 'Moderate (50-60%)', count: 0 },
      { category: 'Near Pass (60-70%)', count: 0 },
      { category: 'Time Management', count: 0 },
      { category: 'Conceptual Gaps', count: 0 },
    ];

    mavericks.forEach(m => {
      m.recent_failures.forEach(f => {
        const percentage = (f.marks_obtained / f.max_marks) * 100;
        if (percentage < 50) reasons[0].count++;
        else if (percentage < 60) reasons[1].count++;
        else reasons[2].count++;
      });
    });

    // Remove zero counts
    const filteredReasons = reasons.filter(r => r.count > 0).slice(0, 5);
    const maxCount = Math.max(...filteredReasons.map(r => r.count), 1);

    const barHeight = 30;
    const barSpacing = 15;
    const leftMargin = 150;
    const chartWidth = canvas.width - leftMargin - 40;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    filteredReasons.forEach((reason, index) => {
      const y = index * (barHeight + barSpacing) + 20;
      const barWidth = (reason.count / maxCount) * chartWidth;

      // Draw bar
      ctx.fillStyle = '#ef4444';
      ctx.fillRect(leftMargin, y, barWidth, barHeight);

      // Draw category name
      ctx.fillStyle = '#374151';
      ctx.font = '12px Montserrat';
      ctx.textAlign = 'right';
      ctx.fillText(reason.category, leftMargin - 10, y + barHeight / 2 + 4);

      // Draw count
      ctx.fillStyle = '#ffffff';
      ctx.textAlign = 'left';
      ctx.fillText(reason.count.toString(), leftMargin + 8, y + barHeight / 2 + 4);
    });
  }, [mavericks]);

  // Draw risk level pie chart
  useEffect(() => {
    if (!riskPieRef.current || mavericks.length === 0) return;

    const canvas = riskPieRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const riskCounts = {
      HIGH: mavericks.filter(m => m.risk_level === 'HIGH').length,
      MEDIUM: mavericks.filter(m => m.risk_level === 'MEDIUM').length,
      LOW: mavericks.filter(m => m.risk_level === 'LOW').length,
    };

    const data = [
      { label: 'High Risk', count: riskCounts.HIGH, color: '#ef4444' },
      { label: 'Medium Risk', count: riskCounts.MEDIUM, color: '#f59e0b' },
      { label: 'Low Risk', count: riskCounts.LOW, color: '#fbbf24' },
    ].filter(d => d.count > 0);

    const total = data.reduce((sum, d) => sum + d.count, 0);
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(canvas.width, canvas.height) / 2 - 20;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    let currentAngle = -Math.PI / 2;
    data.forEach((item) => {
      const sliceAngle = (item.count / total) * 2 * Math.PI;

      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
      ctx.closePath();
      ctx.fillStyle = item.color;
      ctx.fill();

      currentAngle += sliceAngle;
    });

    // Draw center circle (donut)
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius * 0.6, 0, 2 * Math.PI);
    ctx.fillStyle = '#ffffff';
    ctx.fill();

    // Draw total count
    ctx.fillStyle = '#374151';
    ctx.font = 'bold 24px Montserrat';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(total.toString(), centerX, centerY - 10);
    ctx.font = '12px Montserrat';
    ctx.fillStyle = '#64748b';
    ctx.fillText('At Risk', centerX, centerY + 12);
  }, [mavericks]);

  const filteredMavericks = mavericks.filter(m => {
    const matchesSearch = m.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          m.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRisk = riskFilter === 'all' || m.risk_level === riskFilter;
    return matchesSearch && matchesRisk;
  });

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-blue-900 mb-2">At Risk Mavericks</h1>
          <p className="text-gray-600">Mavericks who need additional support and intervention</p>
        </div>

        {/* Analytics Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Failure Reasons Bar Chart */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Failure Categories</h3>
            <canvas ref={failureBarRef} width={600} height={210}></canvas>
          </div>

          {/* Risk Level Pie Chart */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Risk Distribution</h3>
            <div className="flex justify-center">
              <canvas ref={riskPieRef} width={180} height={180}></canvas>
            </div>
            <div className="mt-4 space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <span className="text-gray-600">High Risk</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <div className="w-3 h-3 rounded-full bg-orange-500"></div>
                <span className="text-gray-600">Medium Risk</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <span className="text-gray-600">Low Risk</span>
              </div>
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
                placeholder="Search by name or email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value as any)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Risk Levels</option>
              <option value="HIGH">High Risk</option>
              <option value="MEDIUM">Medium Risk</option>
              <option value="LOW">Low Risk</option>
            </select>
          </div>
        </div>

        {/* At Risk Mavericks List */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
              <p className="mt-4 text-gray-600">Loading at-risk mavericks...</p>
            </div>
          ) : filteredMavericks.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <AlertTriangle className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium">No at-risk mavericks found</p>
              <p className="text-sm mt-2">Great news! Everyone is performing well 🎉</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Maverick</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Risk Level</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Failures</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Recent Failure</th>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredMavericks.map((maverick) => {
                    const failureRate = maverick.total_assessments > 0
                      ? Math.round((maverick.failed_assessments / maverick.total_assessments) * 100)
                      : 0;
                    const recentFailure = maverick.recent_failures[0];

                    return (
                      <tr key={maverick.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4">
                          <div className="flex items-center">
                            <div className="flex-shrink-0 h-10 w-10 rounded-full bg-red-100 flex items-center justify-center">
                              <AlertTriangle className="w-5 h-5 text-red-600" />
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">{maverick.name}</div>
                              <div className="text-sm text-gray-500 flex items-center gap-2">
                                <Mail className="w-3 h-3" />
                                {maverick.email}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          {maverick.risk_level === 'HIGH' && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                              <AlertTriangle className="w-3 h-3 mr-1" />
                              High Risk
                            </span>
                          )}
                          {maverick.risk_level === 'MEDIUM' && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                              <TrendingDown className="w-3 h-3 mr-1" />
                              Medium Risk
                            </span>
                          )}
                          {maverick.risk_level === 'LOW' && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                              Low Risk
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">
                            <span className="font-semibold text-red-600">{maverick.failed_assessments}</span>
                            {' / '}
                            {maverick.total_assessments} assessments
                          </div>
                          <div className="text-xs text-gray-500">
                            {failureRate}% failure rate
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          {recentFailure && (
                            <div>
                              <div className="text-sm text-gray-900">{recentFailure.assessment_name}</div>
                              <div className="text-xs text-gray-500">
                                Score: {recentFailure.marks_obtained}/{recentFailure.max_marks} ({Math.round((recentFailure.marks_obtained / recentFailure.max_marks) * 100)}%)
                              </div>
                              <div className="text-xs text-gray-400 flex items-center gap-1 mt-1">
                                <Calendar className="w-3 h-3" />
                                {new Date(recentFailure.evaluated_at).toLocaleDateString()}
                              </div>
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex justify-end gap-2">
                            <button
                              onClick={() => {
                                router.push(`/hr/mavericks/${maverick.id}`);
                              }}
                              className="inline-flex items-center px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
                              title="View full profile"
                            >
                              <Eye className="w-4 h-4 mr-1" />
                              View Profile
                            </button>
                            <button
                              onClick={() => {
                                window.location.href = `mailto:${maverick.email}`;
                              }}
                              className="inline-flex items-center px-3 py-1.5 bg-gray-600 text-white text-sm font-medium rounded-md hover:bg-gray-700 transition-colors"
                              title="Send email"
                            >
                              <Mail className="w-4 h-4 mr-1" />
                              Contact
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
