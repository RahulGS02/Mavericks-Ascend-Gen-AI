"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { UserPlus, Mail, Phone, User, BookOpen, ArrowLeft, Copy, Check } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';

export default function CreateTrainerPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [showCredentials, setShowCredentials] = useState(false);
  const [credentials, setCredentials] = useState<{ email: string; password: string } | null>(null);
  const [copied, setCopied] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    specialization: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate phone number (Indian standard: 10 digits)
    if (formData.phone && !/^[6-9]\d{9}$/.test(formData.phone)) {
      toast.error('Please enter a valid 10-digit Indian mobile number');
      return;
    }

    setLoading(true);

    try {
      // Parse specialization as array
      const specializationArray = formData.specialization
        .split(',')
        .map(s => s.trim())
        .filter(s => s.length > 0);

      const response = await apiClient.post('/trainers/', {
        name: formData.name,
        email: formData.email,
        phone: formData.phone || null,
        specialization: specializationArray.length > 0 ? specializationArray : null
      });

      // Show credentials
      setCredentials({
        email: response.data.email,
        password: response.data.temp_password
      });
      setShowCredentials(true);
      toast.success('Trainer account created successfully!');
    } catch (error: any) {
      console.error('Failed to create trainer:', error);
      toast.error(error.response?.data?.detail || 'Failed to create trainer account');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCredentials = () => {
    if (credentials) {
      const text = `Email: ${credentials.email}\nPassword: ${credentials.password}`;
      navigator.clipboard.writeText(text);
      setCopied(true);
      toast.success('Credentials copied to clipboard!');
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleCreateAnother = () => {
    setShowCredentials(false);
    setCredentials(null);
    setFormData({
      name: '',
      email: '',
      phone: '',
      specialization: ''
    });
  };

  if (showCredentials && credentials) {
    return (
      <DashboardLayout>
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Check className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Trainer Account Created!</h2>
              <p className="text-gray-600">Share these login credentials with the trainer</p>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
              <p className="text-sm text-yellow-800 mb-4 font-semibold">
                ⚠️ Important: Save these credentials now. They won't be shown again!
              </p>
              <div className="space-y-3">
                <div>
                  <label className="text-xs font-medium text-gray-700">Email (Username)</label>
                  <div className="mt-1 p-3 bg-white rounded border border-yellow-300 font-mono text-sm">
                    {credentials.email}
                  </div>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-700">Temporary Password</label>
                  <div className="mt-1 p-3 bg-white rounded border border-yellow-300 font-mono text-sm">
                    {credentials.password}
                  </div>
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleCopyCredentials}
                className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 bg-white rounded-lg hover:bg-gray-50 transition-colors"
              >
                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                {copied ? 'Copied!' : 'Copy Credentials'}
              </button>
              <button
                onClick={handleCreateAnother}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create Another Trainer
              </button>
              <button
                onClick={() => router.push('/trainers')}
                className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                View All Trainers
              </button>
            </div>

            <p className="text-xs text-gray-500 mt-4 text-center">
              Note: The trainer can change their password after first login
            </p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Create Trainer Account</h1>
          <p className="text-gray-600 mt-2">Add a new trainer to the platform</p>
        </div>

        {/* Form */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Name */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Full Name <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  id="name"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="pl-10 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="John Doe"
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  id="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="pl-10 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="john.doe@example.com"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">This will be used as the login username</p>
            </div>

            {/* Phone */}
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="tel"
                  id="phone"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="pl-10 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="9876543210"
                  pattern="[6-9]\d{9}"
                  maxLength={10}
                  required
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">Enter 10-digit Indian mobile number (starts with 6-9)</p>
            </div>

            {/* Specialization */}
            <div>
              <label htmlFor="specialization" className="block text-sm font-medium text-gray-700 mb-2">
                Specialization / Expertise
              </label>
              <div className="relative">
                <BookOpen className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  id="specialization"
                  value={formData.specialization}
                  onChange={(e) => setFormData({ ...formData, specialization: e.target.value })}
                  className="pl-10 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="React, Python, Data Science (comma-separated)"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">Enter skills separated by commas</p>
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-blue-900 mb-2">🔐 Automatic Credentials Generation</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• A temporary password will be generated automatically</li>
                <li>• You'll see the credentials after creating the account</li>
                <li>• Trainer can change their password after first login</li>
                <li>• Credentials will be shown only once - make sure to save them!</li>
              </ul>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={() => router.back()}
                className="flex-1 px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <UserPlus className="w-5 h-5" />
                    Create Trainer Account
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </DashboardLayout>
  );
}
