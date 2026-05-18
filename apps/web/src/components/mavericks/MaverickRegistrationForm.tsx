'use client';

import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { MaverickProfile } from '@/lib/api/mavericks';

interface MaverickRegistrationFormProps {
  onSubmit: (data: Partial<MaverickProfile>) => void;
  initialData?: Partial<MaverickProfile>;
  loading?: boolean;
}

export default function MaverickRegistrationForm({
  onSubmit,
  initialData,
  loading = false
}: MaverickRegistrationFormProps) {
  const [formData, setFormData] = useState<any>({
    name: initialData?.name || '',
    email: initialData?.email || '',
    password: '',
    phone: initialData?.phone || '',
    college: initialData?.college || '',
    degree: initialData?.degree || '',
    branch: initialData?.branch || '',
    graduation_year: initialData?.graduation_year || new Date().getFullYear(),
    cgpa: initialData?.cgpa || 0,
    github_url: initialData?.github_url || '',
    linkedin_url: initialData?.linkedin_url || '',
    skills: initialData?.skills || [],
  });

  const [skillInput, setSkillInput] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value
    }));
  };

  const addSkill = () => {
    if (skillInput.trim() && !formData.skills?.includes(skillInput.trim())) {
      setFormData(prev => ({
        ...prev,
        skills: [...(prev.skills || []), skillInput.trim()]
      }));
      setSkillInput('');
    }
  };

  const removeSkill = (skill: string) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills?.filter(s => s !== skill)
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Personal Information */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Full Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="John Doe"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email <span className="text-red-500">*</span>
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="john@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Phone <span className="text-red-500">*</span>
            </label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="+91 9876543210"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password <span className="text-red-500">*</span>
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={6}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Min. 6 characters"
            />
            <p className="text-xs text-gray-500 mt-1">Use a strong password (min. 6 characters)</p>
          </div>
        </div>
      </div>

      {/* Education Details */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Education Details</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              College/University <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="college"
              value={formData.college}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="IIT Delhi"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Degree <span className="text-red-500">*</span>
            </label>
            <select
              name="degree"
              value={formData.degree}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select Degree</option>
              <option value="B.Tech">B.Tech</option>
              <option value="B.E">B.E</option>
              <option value="M.Tech">M.Tech</option>
              <option value="M.Sc">M.Sc</option>
              <option value="BCA">BCA</option>
              <option value="MCA">MCA</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Branch/Specialization <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="branch"
              value={formData.branch}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Computer Science"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Graduation Year <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              name="graduation_year"
              value={formData.graduation_year}
              onChange={handleChange}
              required
              min="2000"
              max="2030"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              CGPA/Percentage <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              name="cgpa"
              value={formData.cgpa}
              onChange={handleChange}
              required
              step="0.01"
              min="0"
              max="10"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="8.5"
            />
          </div>
        </div>
      </div>

      {/* Social Links */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Social Links</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              GitHub URL
            </label>
            <input
              type="url"
              name="github_url"
              value={formData.github_url}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="https://github.com/username"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              LinkedIn URL
            </label>
            <input
              type="url"
              name="linkedin_url"
              value={formData.linkedin_url}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="https://linkedin.com/in/username"
            />
          </div>
        </div>
      </div>

      {/* Skills */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Skills</h3>

        <div className="flex gap-2 mb-4">
          <input
            type="text"
            value={skillInput}
            onChange={(e) => setSkillInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Add a skill (e.g., Python, React, SQL)"
          />
          <button
            type="button"
            onClick={addSkill}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Add
          </button>
        </div>

        <div className="flex flex-wrap gap-2">
          {formData.skills?.map((skill, index) => (
            <span
              key={index}
              className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
            >
              {skill}
              <button
                type="button"
                onClick={() => removeSkill(skill)}
                className="text-blue-600 hover:text-blue-800"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

      {/* Submit Button */}
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="px-8 py-3 bg-blue-900 text-white rounded font-bold uppercase tracking-wide hover:bg-blue-800 disabled:bg-gray-400 transition flex items-center gap-2"
        >
          {loading && <Loader2 className="w-5 h-5 animate-spin" />}
          {loading ? 'Saving...' : 'Save Profile'}
        </button>
      </div>
    </form>
  );
}
