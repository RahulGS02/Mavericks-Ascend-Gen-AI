'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { User, Mail, Phone, GraduationCap, Github, Linkedin, FileText, Edit } from 'lucide-react';
import ProfileStatusBadge from '@/components/mavericks/ProfileStatusBadge';
import LoadingScreen from '@/components/common/LoadingScreen';
import Header from '@/components/common/Header';
import Footer from '@/components/common/Footer';
import { maverickAPI, MaverickProfile } from '@/lib/api/mavericks';

export default function MaverickProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<MaverickProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const data = await maverickAPI.getMyProfile();
      setProfile(data);
    } catch (error) {
      console.error('Failed to fetch profile:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingScreen message="Loading your Maverick profile..." />;
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">No profile found</p>
          <button
            onClick={() => router.push('/mavericks/register')}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Create Profile
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />

      <div className="flex-1 py-8">
        <div className="max-w-5xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{profile.name}</h1>
              <div className="flex items-center gap-2 mb-4">
                <ProfileStatusBadge status={profile.profile_status} />
              </div>
            </div>
            <button
              onClick={() => router.push(`/mavericks/edit/${profile.id}`)}
              className="flex items-center gap-2 px-4 py-2 border-2 border-blue-900 text-blue-900 rounded font-bold uppercase text-sm tracking-wide hover:bg-blue-50 transition"
            >
              <Edit className="w-4 h-4" />
              Edit Profile
            </button>
          </div>
        </div>

        {/* Contact Information */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <User className="w-5 h-5 mr-2 text-blue-600" />
            Contact Information
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center">
              <Mail className="w-5 h-5 text-gray-400 mr-3" />
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p className="text-gray-900">{profile.email}</p>
              </div>
            </div>
            <div className="flex items-center">
              <Phone className="w-5 h-5 text-gray-400 mr-3" />
              <div>
                <p className="text-sm text-gray-500">Phone</p>
                <p className="text-gray-900">{profile.phone}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Education */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <GraduationCap className="w-5 h-5 mr-2 text-blue-600" />
            Education
          </h2>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">College/University</p>
                <p className="text-gray-900 font-medium">{profile.college}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Degree</p>
                <p className="text-gray-900 font-medium">{profile.degree}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Branch</p>
                <p className="text-gray-900 font-medium">{profile.branch}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Graduation Year</p>
                <p className="text-gray-900 font-medium">{profile.graduation_year}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">CGPA</p>
                <p className="text-gray-900 font-medium">{profile.cgpa}/10</p>
              </div>
            </div>
          </div>
        </div>

        {/* Social Links */}
        {(profile.github_url || profile.linkedin_url) && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Social Links</h2>
            <div className="space-y-3">
              {profile.github_url && (
                <a
                  href={profile.github_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-blue-600 hover:text-blue-800"
                >
                  <Github className="w-5 h-5 mr-2" />
                  {profile.github_url}
                </a>
              )}
              {profile.linkedin_url && (
                <a
                  href={profile.linkedin_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-blue-600 hover:text-blue-800"
                >
                  <Linkedin className="w-5 h-5 mr-2" />
                  {profile.linkedin_url}
                </a>
              )}
            </div>
          </div>
        )}

        {/* Skills */}
        {profile.skills && profile.skills.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Skills</h2>
            <div className="flex flex-wrap gap-2">
              {profile.skills.map((skill, index) => (
                <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* AI Summary */}
        {profile.ai_summary && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <FileText className="w-5 h-5 mr-2 text-green-600" />
              AI-Generated Summary
            </h2>
            <p className="text-gray-700">{profile.ai_summary}</p>
          </div>
        )}

        {/* Review Notes (if rejected) */}
        {profile.profile_status === 'REJECTED' && profile.review_notes && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-red-900 mb-4">Review Feedback</h2>
            <p className="text-red-800">{profile.review_notes}</p>
          </div>
        )}
        </div>
      </div>

      <Footer />
    </div>
  );
}
