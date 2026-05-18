"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { User, Mail, Phone, GraduationCap, BookOpen, Calendar, Award, Github, Linkedin, Edit } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';
import { useAuthStore } from '@/store/authStore';

interface ProfileData {
  id: string;
  user_id: string;
  name: string;
  email: string;
  phone: string;
  college: string;
  degree: string;
  branch: string;
  graduation_year: number;
  cgpa: number;
  skills: string[];
  github_url?: string;
  linkedin_url?: string;
  resume_url?: string;
  profile_status: string;
  deployment_status: string;
  current_batch_id?: string;
}

export default function StudentProfilePage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<ProfileData | null>(null);

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'maverick') {
      router.push('/login');
      return;
    }
    fetchProfile();
  }, [isAuthenticated, user, router]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/mavericks/my-profile');
      setProfile(response.data);
    } catch (error: any) {
      console.error('Failed to fetch profile:', error);
      if (error.response?.status === 404) {
        toast.error('Profile not found. Please contact HR.');
      } else {
        toast.error('Failed to load profile');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading profile...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!profile) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Profile Not Found</h2>
            <p className="text-gray-600 mb-4">Your maverick profile could not be found. Please contact HR for assistance.</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'approved': return 'bg-green-100 text-green-700';
      case 'pending': return 'bg-yellow-100 text-yellow-700';
      case 'rejected': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <DashboardLayout>
      <div className="p-6 max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{profile.name}</h1>
              <div className="flex items-center gap-3">
                <span className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(profile.profile_status)}`}>
                  {profile.profile_status}
                </span>
                <span className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(profile.deployment_status)}`}>
                  {profile.deployment_status}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <User className="w-6 h-6 text-blue-600" />
            Contact Information
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-3">
              <Mail className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="font-medium text-gray-900">{profile.email}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Phone className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-600">Phone</p>
                <p className="font-medium text-gray-900">{profile.phone || 'Not provided'}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Education */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <GraduationCap className="w-6 h-6 text-blue-600" />
            Education
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">College</p>
              <p className="font-medium text-gray-900">{profile.college}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Degree</p>
              <p className="font-medium text-gray-900">{profile.degree}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Branch</p>
              <p className="font-medium text-gray-900">{profile.branch}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Graduation Year</p>
              <p className="font-medium text-gray-900">{profile.graduation_year}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">CGPA</p>
              <p className="font-medium text-gray-900">{profile.cgpa}/10</p>
            </div>
          </div>
        </div>

        {/* Skills */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Award className="w-6 h-6 text-blue-600" />
            Skills
          </h2>
          <div className="flex flex-wrap gap-2">
            {profile.skills && profile.skills.length > 0 ? (
              profile.skills.map((skill, index) => (
                <span key={index} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                  {skill}
                </span>
              ))
            ) : (
              <p className="text-gray-500">No skills listed</p>
            )}
          </div>
        </div>

        {/* Links */}
        {(profile.github_url || profile.linkedin_url) && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Professional Links</h2>
            <div className="space-y-3">
              {profile.github_url && (
                <a href={profile.github_url} target="_blank" rel="noopener noreferrer" 
                   className="flex items-center gap-3 text-blue-600 hover:text-blue-700">
                  <Github className="w-5 h-5" />
                  <span>GitHub Profile</span>
                </a>
              )}
              {profile.linkedin_url && (
                <a href={profile.linkedin_url} target="_blank" rel="noopener noreferrer"
                   className="flex items-center gap-3 text-blue-600 hover:text-blue-700">
                  <Linkedin className="w-5 h-5" />
                  <span>LinkedIn Profile</span>
                </a>
              )}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
