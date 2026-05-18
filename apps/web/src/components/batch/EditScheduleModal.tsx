"use client";

import { useState, useEffect } from 'react';
import { X, Calendar, Clock, Link as LinkIcon, FileText, Check } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';

interface EditScheduleModalProps {
  batchId: string;
  schedule: {
    id: string;
    job_name: string;
    job_type: string;
    scheduled_start_date: string | null;
    scheduled_end_date: string | null;
    meeting_link: string | null;
    attendance_required: boolean;
    trainer_notes: string | null;
    assessment_id: string | null;
  };
  onClose: () => void;
  onSuccess: () => void;
}

export default function EditScheduleModal({ batchId, schedule, onClose, onSuccess }: EditScheduleModalProps) {
  const [loading, setLoading] = useState(false);
  const [assessmentDetails, setAssessmentDetails] = useState<any>(null);
  const [loadingAssessment, setLoadingAssessment] = useState(false);
  
  const [formData, setFormData] = useState({
    start_date: schedule.scheduled_start_date 
      ? new Date(schedule.scheduled_start_date).toISOString().slice(0, 16)
      : '',
    end_date: schedule.scheduled_end_date
      ? new Date(schedule.scheduled_end_date).toISOString().slice(0, 16)
      : '',
    meeting_link: schedule.meeting_link || '',
    attendance_required: schedule.attendance_required,
    notes: schedule.trainer_notes || '',
    // Assessment fields
    assessment_link: '',
    max_marks: 100,
    passing_marks: 50,
    duration_minutes: 60,
  });

  // Load assessment details if it's an assessment job
  useEffect(() => {
    if (schedule.job_type === 'ASSESSMENT' && schedule.assessment_id) {
      fetchAssessmentDetails();
    }
  }, [schedule.assessment_id]);

  const fetchAssessmentDetails = async () => {
    if (!schedule.assessment_id) return;
    
    setLoadingAssessment(true);
    try {
      const response = await apiClient.get(`/assessments/${schedule.assessment_id}`);
      setAssessmentDetails(response.data);
      setFormData(prev => ({
        ...prev,
        assessment_link: response.data.assessment_link || '',
        max_marks: response.data.max_marks || 100,
        passing_marks: response.data.passing_marks || 50,
        duration_minutes: response.data.duration_minutes || 60,
      }));
    } catch (error) {
      console.error('Failed to fetch assessment:', error);
    } finally {
      setLoadingAssessment(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Update schedule
      const schedulePayload: any = {
        scheduled_start_date: formData.start_date || null,
        scheduled_end_date: formData.end_date || null,
        meeting_link: formData.meeting_link || null,
        attendance_required: formData.attendance_required,
        trainer_notes: formData.notes || null,
      };

      await apiClient.put(`/batches/${batchId}/schedule/${schedule.id}`, schedulePayload);

      // If assessment, update assessment details
      if (schedule.job_type === 'ASSESSMENT' && schedule.assessment_id) {
        const assessmentPayload = {
          assessment_link: formData.assessment_link || null,
          max_marks: formData.max_marks,
          passing_marks: formData.passing_marks,
          duration_minutes: formData.duration_minutes,
        };
        
        await apiClient.patch(`/assessments/${schedule.assessment_id}`, assessmentPayload);
      }

      toast.success('Schedule updated successfully!');
      onSuccess();
    } catch (error: any) {
      console.error('Failed to update schedule:', error);
      toast.error(error.response?.data?.detail || 'Failed to update schedule');
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
            <h2 className="text-xl font-bold text-gray-900">Edit Schedule</h2>
            <p className="text-sm text-gray-600">{schedule.job_name}</p>
            <span className="inline-block mt-1 px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-800">
              {schedule.job_type}
            </span>
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
          {/* Date & Time Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="w-4 h-4 inline mr-1" />
                Start Date & Time
              </label>
              <input
                type="datetime-local"
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Clock className="w-4 h-4 inline mr-1" />
                End Date & Time
              </label>
              <input
                type="datetime-local"
                value={formData.end_date}
                onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Meeting Link (for all job types) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <LinkIcon className="w-4 h-4 inline mr-1" />
              Meeting Link {schedule.job_type === 'TRAINING' && '(Required for Training)'}
            </label>
            <input
              type="url"
              value={formData.meeting_link}
              onChange={(e) => setFormData({ ...formData, meeting_link: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="https://meet.google.com/..."
            />
          </div>

          {/* Training-specific fields */}
          {schedule.job_type === 'TRAINING' && (
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
          )}

          {/* Assessment-specific fields */}
          {schedule.job_type === 'ASSESSMENT' && (
            <>
              <div className="border-t border-gray-200 pt-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Assessment Details
                </h3>

                {loadingAssessment ? (
                  <div className="text-center py-4 text-gray-500">Loading assessment...</div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Assessment Link
                      </label>
                      <input
                        type="url"
                        value={formData.assessment_link}
                        onChange={(e) => setFormData({ ...formData, assessment_link: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="https://forms.google.com/..."
                      />
                      <p className="text-xs text-gray-500 mt-1">Link to the assessment platform</p>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Max Marks</label>
                        <input
                          type="number"
                          value={formData.max_marks}
                          onChange={(e) => setFormData({ ...formData, max_marks: parseInt(e.target.value) || 0 })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          min="1"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Passing Marks</label>
                        <input
                          type="number"
                          value={formData.passing_marks}
                          onChange={(e) => setFormData({ ...formData, passing_marks: parseInt(e.target.value) || 0 })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          min="1"
                          max={formData.max_marks}
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Duration (min)</label>
                        <input
                          type="number"
                          value={formData.duration_minutes}
                          onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) || 0 })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          min="1"
                        />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Trainer Notes (Optional)
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Any additional notes for trainers..."
            />
          </div>

          {/* Footer */}
          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || loadingAssessment}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
