"use client";

import { useState } from 'react';
import { Users, Mail, GraduationCap, Award, TrendingUp, TrendingDown, Minus, ExternalLink, UserX, Search } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import { useAuthStore } from '@/store/authStore';

interface MaverickInBatch {
  id: string;
  name: string;
  email: string;
  college: string;
  skills: string[];
  profile_status?: string;
  deployment_status?: string;
}

interface BatchMavericksTabProps {
  batchId: string;
  mavericks: MaverickInBatch[];
  onUpdate: () => void;
}

export default function BatchMavericksTab({ batchId, mavericks, onUpdate }: BatchMavericksTabProps) {
  const { user } = useAuthStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [removing, setRemoving] = useState<string | null>(null);

  // Check if user can manage mavericks (HR or Super Admin only)
  const canManageMavericks = user?.role === 'hr' || user?.role === 'super_admin';

  const filteredMavericks = mavericks.filter(m =>
    m.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    m.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    m.college?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleRemoveFromBatch = async (maverickId: string, maverickName: string) => {
    if (!confirm(`Are you sure you want to remove ${maverickName} from this batch?`)) {
      return;
    }

    setRemoving(maverickId);
    try {
      await apiClient.patch(`/mavericks/${maverickId}`, {
        current_batch_id: null
      });

      toast.success(`${maverickName} removed from batch`);
      onUpdate(); // Refresh batch data
    } catch (error) {
      console.error('Failed to remove maverick:', error);
      toast.error('Failed to remove maverick from batch');
    } finally {
      setRemoving(null);
    }
  };

  if (mavericks.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
        <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">No Mavericks Enrolled</h3>
        <p className="text-gray-600 mb-6">
          This batch doesn't have any mavericks assigned yet.
        </p>
        <a
          href={`/batches/${batchId}/assign`}
          className="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Assign Mavericks
        </a>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Users className="w-6 h-6 text-blue-600" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Enrolled Mavericks</h3>
              <p className="text-sm text-gray-600">{mavericks.length} total</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Manage Assignments Button */}
            <a
              href={`/batches/${batchId}/assign`}
              className="px-4 py-2 text-sm font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
            >
              Manage Assignments
            </a>

            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search mavericks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Mavericks Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredMavericks.map((maverick) => (
          <div
            key={maverick.id}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-blue-700 font-bold text-lg">
                    {maverick.name.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold text-gray-900 truncate">{maverick.name}</h4>
                  <div className="flex items-center gap-1 text-sm text-gray-600">
                    <Mail className="w-3 h-3" />
                    <span className="truncate">{maverick.email}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* College */}
            {maverick.college && (
              <div className="flex items-center gap-2 text-sm text-gray-600 mb-3">
                <GraduationCap className="w-4 h-4" />
                <span className="truncate">{maverick.college}</span>
              </div>
            )}

            {/* Skills */}
            {maverick.skills && maverick.skills.length > 0 && (
              <div className="mb-4">
                <p className="text-xs font-medium text-gray-700 mb-2">Skills:</p>
                <div className="flex flex-wrap gap-1">
                  {maverick.skills.slice(0, 4).map((skill, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                    >
                      {skill}
                    </span>
                  ))}
                  {maverick.skills.length > 4 && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
                      +{maverick.skills.length - 4} more
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-2 pt-3 border-t border-gray-200">
              <button
                onClick={() => window.location.href = `/hr/mavericks/${maverick.id}`}
                className={`${canManageMavericks ? 'flex-1' : 'w-full'} flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded hover:bg-blue-100 transition-colors`}
              >
                <ExternalLink className="w-4 h-4" />
                View Profile
              </button>
              {canManageMavericks && (
                <button
                  onClick={() => handleRemoveFromBatch(maverick.id, maverick.name)}
                  disabled={removing === maverick.id}
                  className="px-3 py-2 text-sm font-medium text-red-600 bg-red-50 rounded hover:bg-red-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Remove from batch"
                >
                  <UserX className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredMavericks.length === 0 && searchTerm && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
          <p className="text-gray-600">No mavericks found matching "{searchTerm}"</p>
        </div>
      )}
    </div>
  );
}
