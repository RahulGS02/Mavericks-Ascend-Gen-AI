"use client";

import { useState } from 'react';
import { X, Star, MessageSquare } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';

interface InterviewFeedbackModalProps {
  requirementId: string;
  interviewId: string;
  candidateName: string;
  onClose: () => void;
  onSuccess: () => void;
}

export default function InterviewFeedbackModal({
  requirementId,
  interviewId,
  candidateName,
  onClose,
  onSuccess
}: InterviewFeedbackModalProps) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    feedback: '',
    rating: 3,
    technical_rating: 3,
    communication_rating: 3,
    cultural_fit_rating: 3
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await apiClient.post(
        `/workflow/requirements/${requirementId}/interviews/${interviewId}/feedback`,
        formData
      );
      toast.success('Interview feedback submitted successfully');
      onSuccess();
    } catch (error: any) {
      console.error('Failed to submit feedback:', error);
      toast.error(error.response?.data?.detail || 'Failed to submit feedback');
    } finally {
      setLoading(false);
    }
  };

  const RatingInput = ({ 
    label, 
    value, 
    onChange 
  }: { 
    label: string; 
    value: number; 
    onChange: (value: number) => void;
  }) => (
    <div>
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        {label}
      </label>
      <div className="flex items-center gap-2">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => onChange(star)}
            className="focus:outline-none transition-transform hover:scale-110"
          >
            <Star
              className={`w-8 h-8 ${
                star <= value
                  ? 'text-yellow-500 fill-yellow-500'
                  : 'text-gray-300'
              }`}
            />
          </button>
        ))}
        <span className="ml-2 text-lg font-semibold text-gray-700">
          {value}.0
        </span>
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Submit Interview Feedback</h2>
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
          {/* Overall Rating */}
          <RatingInput
            label="Overall Rating"
            value={formData.rating}
            onChange={(value) => setFormData({ ...formData, rating: value })}
          />

          {/* Technical Rating */}
          <RatingInput
            label="Technical Skills"
            value={formData.technical_rating}
            onChange={(value) => setFormData({ ...formData, technical_rating: value })}
          />

          {/* Communication Rating */}
          <RatingInput
            label="Communication Skills"
            value={formData.communication_rating}
            onChange={(value) => setFormData({ ...formData, communication_rating: value })}
          />

          {/* Cultural Fit Rating */}
          <RatingInput
            label="Cultural Fit"
            value={formData.cultural_fit_rating}
            onChange={(value) => setFormData({ ...formData, cultural_fit_rating: value })}
          />

          {/* Feedback Text */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Detailed Feedback
            </label>
            <textarea
              value={formData.feedback}
              onChange={(e) => setFormData({ ...formData, feedback: e.target.value })}
              placeholder="Provide detailed feedback about the candidate's performance, strengths, areas for improvement, and overall impression..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows={6}
              required
            />
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
              {loading ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
