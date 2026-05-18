"use client";

import { useState } from 'react';
import { X, Calendar, Clock, Link as LinkIcon, FileText } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';

interface ScheduleJobModalProps {
  batchId: string;
  job: {
    id: string;
    name: string;
    job_type: string;
    sequence_order: number;
    is_mandatory: boolean;
    duration_days: number | null;
    description: string | null;
  };
  onClose: () => void;
  onSuccess: () => void;
}

export default function ScheduleJobModal({ batchId, job, onClose, onSuccess }: ScheduleJobModalProps) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    start_date: '',
    end_date: '',
    deadline: '',
    meeting_link: '',
    attendance_required: job.job_type === 'TRAINING',
    notes: '',
    // Assessment-specific fields
    assessment_title: job.name,
    assessment_description: job.description || '',
    assessment_link: '',
    max_marks: 100,
    passing_marks: 50,
    duration_minutes: 60,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload: any = {
        pipeline_job_id: job.id,
        scheduled_start_date: formData.start_date,
        scheduled_end_date: formData.end_date,
        meeting_link: formData.meeting_link || null,
        attendance_required: formData.attendance_required,
        trainer_notes: formData.notes || null,
      };

      // Add assessment data if job type is ASSESSMENT
      if (job.job_type === 'ASSESSMENT') {
        payload.assessment_data = {
          title: formData.assessment_title,
          description: formData.assessment_description,
          assessment_link: formData.assessment_link,
          max_marks: formData.max_marks,
          passing_marks: formData.passing_marks,
          duration_minutes: formData.duration_minutes,
        };
      }

      await apiClient.post(`/batches/${batchId}/schedule`, payload);
      toast.success(`${job.name} scheduled successfully!`);
      onSuccess();
    } catch (error: any) {
      console.error('Failed to schedule job:', error);
      toast.error(error.response?.data?.detail || 'Failed to schedule job');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Schedule Job</h2>
            <p className="text-sm text-gray-600">{job.name}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Job Type Badge */}
          <div className="flex items-center gap-2">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              job.job_type === 'TRAINING' ? 'bg-purple-100 text-purple-800' :
              job.job_type === 'ASSESSMENT' ? 'bg-blue-100 text-blue-800' :
              'bg-green-100 text-green-800'
            }`}>
              {job.job_type}
            </span>
            {!job.is_mandatory && (
              <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium">
                Optional
              </span>
            )}
          </div>

          {/* Schedule Dates */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="w-4 h-4 inline mr-1" />
                Start Date *
              </label>
              <input
                type="date"
                required
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="w-4 h-4 inline mr-1" />
                End Date *
              </label>
              <input
                type="date"
                required
                value={formData.end_date}
                onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Meeting Link (for TRAINING) */}
          {job.job_type === 'TRAINING' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <LinkIcon className="w-4 h-4 inline mr-1" />
                  Meeting Link
                </label>
                <input
                  type="url"
                  placeholder="https://meet.google.com/..."
                  value={formData.meeting_link}
                  onChange={(e) => setFormData({ ...formData, meeting_link: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="attendance_required"
                  checked={formData.attendance_required}
                  onChange={(e) => setFormData({ ...formData, attendance_required: e.target.checked })}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="attendance_required" className="ml-2 text-sm text-gray-700">
                  Attendance Required
                </label>
              </div>
            </>
          )}

          {/* Assessment-specific fields */}
          {job.job_type === 'ASSESSMENT' && (
            <>
              <div className="border-t border-gray-200 pt-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Assessment Details
                </h3>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Title *
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.assessment_title}
                      onChange={(e) => setFormData({ ...formData, assessment_title: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description
                    </label>
                    <textarea
                      rows={3}
                      value={formData.assessment_description}
                      onChange={(e) => setFormData({ ...formData, assessment_description: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <LinkIcon className="w-4 h-4 inline mr-1" />
                      Assessment Link *
                    </label>
                    <input
                      type="url"
                      required
                      placeholder="https://forms.google.com/... or https://assessment-platform.com/..."
                      value={formData.assessment_link}
                      onChange={(e) => setFormData({ ...formData, assessment_link: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Link to Google Form, Typeform, or any assessment platform
                    </p>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Max Marks *
                      </label>
                      <input
                        type="number"
                        required
                        min="1"
                        value={formData.max_marks}
                        onChange={(e) => setFormData({ ...formData, max_marks: parseInt(e.target.value) })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Passing Marks *
                      </label>
                      <input
                        type="number"
                        required
                        min="1"
                        value={formData.passing_marks}
                        onChange={(e) => setFormData({ ...formData, passing_marks: parseInt(e.target.value) })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Duration (min) *
                      </label>
                      <input
                        type="number"
                        required
                        min="1"
                        value={formData.duration_minutes}
                        onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* Trainer Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notes (Optional)
            </label>
            <textarea
              rows={3}
              placeholder="Add any notes or instructions..."
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Scheduling...' : 'Schedule Job'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
