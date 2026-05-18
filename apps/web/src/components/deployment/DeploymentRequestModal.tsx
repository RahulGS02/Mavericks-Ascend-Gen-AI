"use client";

import { useState } from 'react';
import { X, Rocket, Building2, Briefcase, FileText, Tag, Star } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';

interface DeploymentRequestModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export default function DeploymentRequestModal({
  onClose,
  onSuccess
}: DeploymentRequestModalProps) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    role_title: '',
    role_description: '',
    required_skills: [] as string[],
    preferred_skills: [] as string[],
    project_name: '',
    vertical: '',
    competency: ''
  });
  const [requiredSkillInput, setRequiredSkillInput] = useState('');
  const [preferredSkillInput, setPreferredSkillInput] = useState('');

  const verticals = [
    'Banking & Finance',
    'Healthcare',
    'E-Commerce',
    'Retail',
    'Manufacturing',
    'Insurance',
    'Government',
    'Telecom',
    'Education',
    'Other'
  ];

  const competencies = [
    'Full Stack Development',
    'Frontend Development',
    'Backend Development',
    'Mobile Development',
    'DevOps',
    'Data Science',
    'Machine Learning',
    'Cloud Architecture',
    'Cybersecurity',
    'QA/Testing',
    'UI/UX Design',
    'Other'
  ];

  const addRequiredSkill = () => {
    if (requiredSkillInput.trim() && !formData.required_skills.includes(requiredSkillInput.trim())) {
      setFormData({ ...formData, required_skills: [...formData.required_skills, requiredSkillInput.trim()] });
      setRequiredSkillInput('');
    }
  };

  const removeRequiredSkill = (skill: string) => {
    setFormData({ ...formData, required_skills: formData.required_skills.filter(s => s !== skill) });
  };

  const addPreferredSkill = () => {
    if (preferredSkillInput.trim() && !formData.preferred_skills.includes(preferredSkillInput.trim())) {
      setFormData({ ...formData, preferred_skills: [...formData.preferred_skills, preferredSkillInput.trim()] });
      setPreferredSkillInput('');
    }
  };

  const removePreferredSkill = (skill: string) => {
    setFormData({ ...formData, preferred_skills: formData.preferred_skills.filter(s => s !== skill) });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.role_title.trim()) {
      toast.error('Please enter a role title');
      return;
    }

    if (formData.required_skills.length === 0) {
      toast.error('Please add at least one required skill');
      return;
    }

    setLoading(true);
    try {
      await apiClient.post('/deployments/requests', formData);
      toast.success('Deployment requirement card created successfully!');
      onSuccess();
    } catch (error: any) {
      console.error('Failed to create deployment request:', error);
      toast.error(error.response?.data?.detail || 'Failed to create deployment request');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Rocket className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Create Deployment Requirement Card</h2>
              <p className="text-sm text-gray-500">Post role requirements - HR will find suitable mavericks</p>
            </div>
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
          {/* Role Title - REQUIRED */}
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">
              <Briefcase className="w-4 h-4 inline mr-1" />
              Role Title *
            </label>
            <input
              type="text"
              required
              value={formData.role_title}
              onChange={(e) => setFormData({ ...formData, role_title: e.target.value })}
              placeholder="e.g., Senior Full Stack Developer"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              The position you're hiring for
            </p>
          </div>

          {/* Required Skills - REQUIRED */}
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">
              <Tag className="w-4 h-4 inline mr-1 text-red-600" />
              Required Skills *
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={requiredSkillInput}
                onChange={(e) => setRequiredSkillInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addRequiredSkill())}
                placeholder="Type skill and press Enter (e.g., React, Node.js)"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="button"
                onClick={addRequiredSkill}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.required_skills.map((skill) => (
                <span
                  key={skill}
                  className="inline-flex items-center px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium"
                >
                  {skill}
                  <button
                    type="button"
                    onClick={() => removeRequiredSkill(skill)}
                    className="ml-2 text-red-600 hover:text-red-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            {formData.required_skills.length === 0 && (
              <p className="text-xs text-red-600 mt-1">
                ⚠️ Add at least one required skill
              </p>
            )}
          </div>

          {/* Preferred Skills */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Star className="w-4 h-4 inline mr-1" />
              Preferred Skills (Optional)
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={preferredSkillInput}
                onChange={(e) => setPreferredSkillInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addPreferredSkill())}
                placeholder="Nice-to-have skills"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="button"
                onClick={addPreferredSkill}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.preferred_skills.map((skill) => (
                <span
                  key={skill}
                  className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                >
                  {skill}
                  <button
                    type="button"
                    onClick={() => removePreferredSkill(skill)}
                    className="ml-2 text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Role Description */}
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">
              <FileText className="w-4 h-4 inline mr-1" />
              Role Description & Requirements *
            </label>
            <textarea
              rows={5}
              required
              value={formData.role_description}
              onChange={(e) => setFormData({ ...formData, role_description: e.target.value })}
              placeholder="Describe the role, responsibilities, and detailed requirements..."
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              Be specific about what the role entails
            </p>
          </div>

          {/* Project Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Building2 className="w-4 h-4 inline mr-1" />
              Project Name (Optional)
            </label>
            <input
              type="text"
              value={formData.project_name}
              onChange={(e) => setFormData({ ...formData, project_name: e.target.value })}
              placeholder="e.g., ABC Banking Portal"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Vertical */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Building2 className="w-4 h-4 inline mr-1" />
              Business Vertical (Optional)
            </label>
            <select
              value={formData.vertical}
              onChange={(e) => setFormData({ ...formData, vertical: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select vertical...</option>
              {verticals.map((v) => (
                <option key={v} value={v}>{v}</option>
              ))}
            </select>
          </div>

          {/* Competency */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Briefcase className="w-4 h-4 inline mr-1" />
              Competency Area (Optional)
            </label>
            <select
              value={formData.competency}
              onChange={(e) => setFormData({ ...formData, competency: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select competency...</option>
              {competencies.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !formData.role_title || formData.required_skills.length === 0}
              className="inline-flex items-center px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                  Creating Requirement Card...
                </>
              ) : (
                <>
                  <Rocket className="w-4 h-4 mr-2" />
                  Create Requirement Card
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
