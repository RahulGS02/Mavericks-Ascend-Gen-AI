"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import DashboardLayout from '@/components/DashboardLayout';
import ProfileReviewModal from '@/components/ProfileReviewModal';
import { hrAPI, type MaverickResponse } from '@/lib/api/hr';
import { Search, Eye, UserCheck, UserX, Filter, Loader2 } from 'lucide-react';

export default function PendingProfilesPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  
  const [profiles, setProfiles] = useState<MaverickResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProfile, setSelectedProfile] = useState<MaverickResponse | null>(null);
  const [showReviewModal, setShowReviewModal] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    
    if (user?.role !== 'hr' && user?.role !== 'super_admin') {
      router.push('/dashboard');
      return;
    }

    fetchPendingProfiles();
  }, [isAuthenticated, user, page, router]);

  const fetchPendingProfiles = async () => {
    try {
      setLoading(true);
      const response = await hrAPI.getPendingProfiles({
        page,
        page_size: pageSize,
        search: searchQuery || undefined
      });
      
      setProfiles(response.mavericks);
      setTotal(response.total);
    } catch (error) {
      console.error('Failed to fetch pending profiles:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1); // Reset to first page
    fetchPendingProfiles();
  };

  const handleViewProfile = (profile: MaverickResponse) => {
    setSelectedProfile(profile);
    setShowReviewModal(true);
  };

  const totalPages = Math.ceil(total / pageSize);

  if (!user) {
    return null;
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Pending Profiles</h1>
          <p className="mt-2 text-gray-600">
            Review and approve maverick registrations
          </p>
        </div>

        {/* Search and Filters */}
        <div className="mb-6 bg-white rounded-lg shadow p-4">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by name, email, or college..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-900 focus:border-transparent"
              />
            </div>
            <button
              onClick={handleSearch}
              className="px-6 py-2 bg-blue-900 text-white rounded-lg hover:bg-blue-800 transition font-semibold uppercase text-sm tracking-wide"
            >
              Search
            </button>
          </div>
        </div>

        {/* Profiles Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-900" />
            </div>
          ) : profiles.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">No pending profiles found</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                        Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                        Email
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                        College
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                        Degree
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                        CGPA
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                        Skills
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {profiles.map((profile) => (
                      <tr key={profile.id} className="hover:bg-gray-50 transition">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{profile.name}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-600">{profile.email}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">{profile.college || '-'}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-600">{profile.degree || '-'}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900 font-medium">
                            {profile.cgpa ? profile.cgpa.toFixed(2) : '-'}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex flex-wrap gap-1">
                            {(profile.ai_extracted_skills || profile.skills || []).slice(0, 3).map((skill, idx) => (
                              <span
                                key={idx}
                                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                              >
                                {skill}
                              </span>
                            ))}
                            {(profile.ai_extracted_skills || profile.skills || []).length > 3 && (
                              <span className="text-xs text-gray-500">
                                +{(profile.ai_extracted_skills || profile.skills || []).length - 3} more
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => handleViewProfile(profile)}
                            className="text-blue-900 hover:text-blue-700 font-semibold uppercase text-xs tracking-wide"
                          >
                            <Eye className="w-5 h-5 inline mr-1" />
                            Review
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Showing <span className="font-medium">{(page - 1) * pageSize + 1}</span> to{' '}
                  <span className="font-medium">{Math.min(page * pageSize, total)}</span> of{' '}
                  <span className="font-medium">{total}</span> results
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage(page - 1)}
                    disabled={page === 1}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage(page + 1)}
                    disabled={page >= totalPages}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Profile Review Modal */}
      <ProfileReviewModal
        profile={selectedProfile}
        isOpen={showReviewModal}
        onClose={() => setShowReviewModal(false)}
        onReviewComplete={() => {
          fetchPendingProfiles(); // Refresh the list
        }}
      />
    </DashboardLayout>
  );
}
