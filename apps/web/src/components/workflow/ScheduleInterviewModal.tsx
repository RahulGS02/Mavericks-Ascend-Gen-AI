"use client";

import { useState } from 'react';
import { X, Calendar, Clock, Video, MapPin, Users } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';

interface ScheduleInterviewModalProps {
  requirementId: string;
  candidateId: string;
  candidateName: string;
  onClose: () => void;
  onSuccess: () => void;
}

export default function ScheduleInterviewModal({
  requirementId,
  candidateId,
  candidateName,
  onClose,
  onSuccess
}: ScheduleInterviewModalProps) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    interview_type: 'ONLINE',
    interview_mode: 'VIDEO_CALL',
    interview_date: '',
    interview_time: '',
    duration_minutes: 60,
    location: '',
    video_link: '',
    interviewer_panel: [] as string[]
  });
  const [interviewerInput, setInterviewerInput] = useState('');

  const interviewModes = {
    ONLINE: ['VIDEO_CALL', 'PHONE_CALL'],
    OFFLINE: ['IN_PERSON', 'PANEL_INTERVIEW', 'TECHNICAL_ROUND', 'HR_ROUND', 'MANAGERIAL_ROUND']
  };

  const handleAddInterviewer = () => {
    if (interviewerInput.trim()) {
      setFormData({
        ...formData,
        interviewer_panel: [...formData.interviewer_panel, interviewerInput.trim()]
      });
      setInterviewerInput('');
    }
  };

  const handleRemoveInterviewer = (index: number) => {
    setFormData({
      ...formData,
      interviewer_panel: formData.interviewer_panel.filter((_, i) => i !== index)
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await apiClient.post(`/workflow/requirements/${requirementId}/candidates/${candidateId}/interviews`, formData);
      toast.success('Interview scheduled successfully');
      onSuccess();
    } catch (error: any) {
      console.error('Failed to schedule interview:', error);
      toast.error(error.response?.data?.detail || 'Failed to schedule interview');
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
            <h2 className="text-xl font-bold text-gray-900">Schedule Interview</h2>
            <p className="text-sm text-gray-600 mt-1">for {candidateName}</p>
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
          {/* Interview Type */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Interview Type
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setFormData({ 
                  ...formData, 
                  interview_type: 'ONLINE',
                  interview_mode: 'VIDEO_CALL'
                })}
                className={`p-4 border-2 rounded-lg flex items-center gap-3 transition-all ${
                  formData.interview_type === 'ONLINE'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-blue-300'
                }`}
              >
                <Video className="w-5 h-5" />
                <span className="font-medium">Online</span>
              </button>
              <button
                type="button"
                onClick={() => setFormData({ 
                  ...formData, 
                  interview_type: 'OFFLINE',
                  interview_mode: 'IN_PERSON'
                })}
                className={`p-4 border-2 rounded-lg flex items-center gap-3 transition-all ${
                  formData.interview_type === 'OFFLINE'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-blue-300'
                }`}
              >
                <MapPin className="w-5 h-5" />
                <span className="font-medium">Offline</span>
              </button>
            </div>
          </div>

          {/* Interview Mode */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Interview Mode
            </label>
            <select
              value={formData.interview_mode}
              onChange={(e) => setFormData({ ...formData, interview_mode: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
              {interviewModes[formData.interview_type as 'ONLINE' | 'OFFLINE'].map(mode => (
                <option key={mode} value={mode}>
                  {mode.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>

          {/* Date and Time */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Interview Date
              </label>
              <input
                type="date"
                value={formData.interview_date}
                onChange={(e) => setFormData({ ...formData, interview_date: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
                min={new Date().toISOString().split('T')[0]}
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Interview Time
              </label>
              <input
                type="time"
                value={formData.interview_time}
                onChange={(e) => setFormData({ ...formData, interview_time: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>
          </div>

          {/* Duration */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Duration (minutes)
            </label>
            <input
              type="number"
              value={formData.duration_minutes}
              onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              min="15"
              step="15"
              required
            />
          </div>

          {/* Video Link (for online) or Location (for offline) */}
          {formData.interview_type === 'ONLINE' ? (
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <Video className="w-4 h-4" />
                Video Call Link
              </label>
              <input
                type="url"
                value={formData.video_link}
                onChange={(e) => setFormData({ ...formData, video_link: e.target.value })}
                placeholder="https://meet.google.com/xxx-yyyy-zzz"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                Google Meet, Zoom, Teams, or any other video conferencing link
              </p>
            </div>
          ) : (
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <MapPin className="w-4 h-4" />
                Location
              </label>
              <input
                type="text"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                placeholder="Office address or meeting room"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          )}

          {/* Interviewer Panel */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <Users className="w-4 h-4" />
              Interviewer Panel
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={interviewerInput}
                onChange={(e) => setInterviewerInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddInterviewer())}
                placeholder="Enter interviewer name and press Enter"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                type="button"
                onClick={handleAddInterviewer}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Add
              </button>
            </div>
            {formData.interviewer_panel.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {formData.interviewer_panel.map((interviewer, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-2 px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                  >
                    {interviewer}
                    <button
                      type="button"
                      onClick={() => handleRemoveInterviewer(index)}
                      className="text-gray-500 hover:text-red-600"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? 'Scheduling...' : 'Schedule Interview'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
