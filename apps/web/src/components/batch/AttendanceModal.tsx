"use client";

import { useEffect, useState } from 'react';
import { X, Users, CheckCircle, XCircle, Search, Download } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';

interface AttendanceModalProps {
  scheduleId: string;
  jobName: string;
  batchId: string;
  onClose: () => void;
  onUpdate: () => void;
}

interface MaverickAttendance {
  id: string;
  name: string;
  email: string;
  is_present: boolean;
}

export default function AttendanceModal({ scheduleId, jobName, batchId, onClose, onUpdate }: AttendanceModalProps) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [mavericks, setMavericks] = useState<MaverickAttendance[]>([]);

  useEffect(() => {
    fetchAttendance();
  }, [scheduleId]);

  const fetchAttendance = async () => {
    setLoading(true);
    try {
      // Fetch all mavericks in the batch
      const batchResponse = await apiClient.get(`/batches/${batchId}`);
      const batchMavericks = batchResponse.data.mavericks || [];

      // Fetch existing attendance records
      let attendanceCount = 0;
      try {
        const attendanceResponse = await apiClient.get(`/batches/${batchId}/schedule/${scheduleId}/attendance`);
        attendanceCount = attendanceResponse.data.attendance_count || 0;
      } catch (error) {
        // No attendance records yet, that's okay
      }

      // Create attendance list
      const attendanceList: MaverickAttendance[] = batchMavericks.map((maverick: any) => ({
        id: maverick.id,
        name: maverick.name,
        email: maverick.email,
        is_present: false, // Will be set by user
      }));

      setMavericks(attendanceList);
    } catch (error) {
      console.error('Failed to fetch attendance:', error);
      toast.error('Failed to load attendance data');
    } finally {
      setLoading(false);
    }
  };

  const toggleAttendance = (maverickId: string) => {
    setMavericks(prev =>
      prev.map(m =>
        m.id === maverickId ? { ...m, is_present: !m.is_present } : m
      )
    );
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Get list of maverick IDs who were marked present
      const presentMaverickIds = mavericks
        .filter(m => m.is_present)
        .map(m => m.id);

      await apiClient.post(`/batches/${batchId}/schedule/${scheduleId}/attendance`, {
        maverick_ids: presentMaverickIds,
        notes: `Attendance marked on ${new Date().toLocaleDateString()}`
      });

      toast.success(`Attendance saved! ${presentMaverickIds.length} mavericks marked present.`);
      onUpdate();
      onClose();
    } catch (error) {
      console.error('Failed to save attendance:', error);
      toast.error('Failed to save attendance');
    } finally {
      setSaving(false);
    }
  };

  const handleMarkAll = (present: boolean) => {
    setMavericks(prev => prev.map(m => ({ ...m, is_present: present })));
  };

  const handleExport = () => {
    const csv = 'Name,Email,Status\n' + 
      mavericks.map(m => `"${m.name}","${m.email}",${m.is_present ? 'Present' : 'Absent'}`).join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${jobName}_attendance_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    toast.success('Attendance exported!');
  };

  const filteredMavericks = mavericks.filter(m =>
    m.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    m.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const presentCount = mavericks.filter(m => m.is_present).length;
  const absentCount = mavericks.length - presentCount;
  const attendancePercentage = mavericks.length > 0 
    ? Math.round((presentCount / mavericks.length) * 100) 
    : 0;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <Users className="w-5 h-5" />
              Attendance Tracking
            </h2>
            <p className="text-sm text-gray-600">{jobName}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Stats */}
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{mavericks.length}</div>
              <div className="text-xs text-gray-600">Total</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{presentCount}</div>
              <div className="text-xs text-gray-600">Present</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{absentCount}</div>
              <div className="text-xs text-gray-600">Absent</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{attendancePercentage}%</div>
              <div className="text-xs text-gray-600">Attendance</div>
            </div>
          </div>
        </div>

        {/* Actions Bar */}
        <div className="px-6 py-3 bg-white border-b border-gray-200 flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleMarkAll(true)}
              className="px-3 py-1.5 text-sm bg-green-100 text-green-700 rounded-md hover:bg-green-200 transition-colors"
            >
              Mark All Present
            </button>
            <button
              onClick={() => handleMarkAll(false)}
              className="px-3 py-1.5 text-sm bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors"
            >
              Mark All Absent
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleExport}
              className="inline-flex items-center px-3 py-1.5 text-sm border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
            >
              <Download className="w-4 h-4 mr-1" />
              Export
            </button>
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search mavericks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 pr-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Maverick List */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-gray-500">Loading attendance...</div>
            </div>
          ) : filteredMavericks.length === 0 ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-gray-500">No mavericks found</div>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredMavericks.map((maverick) => (
                <div
                  key={maverick.id}
                  className={`flex items-center justify-between p-3 rounded-lg border-2 transition-colors ${
                    maverick.is_present
                      ? 'border-green-300 bg-green-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                      maverick.is_present
                        ? 'bg-green-200 text-green-700'
                        : 'bg-gray-200 text-gray-600'
                    }`}>
                      {maverick.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">{maverick.name}</div>
                      <div className="text-sm text-gray-600">{maverick.email}</div>
                    </div>
                  </div>

                  <button
                    onClick={() => toggleAttendance(maverick.id)}
                    className={`px-4 py-2 rounded-md font-medium text-sm transition-colors ${
                      maverick.is_present
                        ? 'bg-green-600 text-white hover:bg-green-700'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    {maverick.is_present ? (
                      <span className="flex items-center gap-1">
                        <CheckCircle className="w-4 h-4" />
                        Present
                      </span>
                    ) : (
                      <span className="flex items-center gap-1">
                        <XCircle className="w-4 h-4" />
                        Absent
                      </span>
                    )}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            disabled={saving}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Attendance'}
          </button>
        </div>
      </div>
    </div>
  );
}
