'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ArrowLeft, Upload, FileText } from 'lucide-react';
import MaverickRegistrationForm from '@/components/mavericks/MaverickRegistrationForm';
import ResumeUpload from '@/components/mavericks/ResumeUpload';
import Header from '@/components/common/Header';
import Footer from '@/components/common/Footer';
import { maverickAPI, MaverickProfile } from '@/lib/api/mavericks';

export default function MaverickRegisterPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [step, setStep] = useState<'form' | 'resume'>('form');
  const [loading, setLoading] = useState(false);
  const [profileData, setProfileData] = useState<Partial<MaverickProfile>>({});
  const [extractedData, setExtractedData] = useState<any>(null);
  const [profileId, setProfileId] = useState<string | null>(null);

  // Check if we're returning from registration (step=resume in URL)
  useEffect(() => {
    const stepParam = searchParams.get('step');
    const savedMaverickId = localStorage.getItem('maverick_id');
    const savedStep = localStorage.getItem('registration_step');

    if (stepParam === 'resume' && savedMaverickId) {
      console.log('📋 Resuming registration at step: resume');
      console.log('📋 Maverick ID:', savedMaverickId);
      setProfileId(savedMaverickId);
      setStep('resume');
    } else if (savedStep === 'resume' && savedMaverickId) {
      setProfileId(savedMaverickId);
      setStep('resume');
    }
  }, [searchParams]);

  // Handle form submission
  const handleFormSubmit = async (data: any) => {
    setLoading(true);
    try {
      // Validate password
      if (!data.password || data.password.length < 6) {
        alert('Password must be at least 6 characters');
        setLoading(false);
        return;
      }

      // Convert skills array to comma-separated string
      const skillsString = Array.isArray(data.skills)
        ? data.skills.join(', ')
        : data.skills || '';

      // Register with combined endpoint
      const registrationData = {
        name: data.name,
        email: data.email,
        password: data.password,
        phone: data.phone,
        college: data.college,
        degree: data.degree,
        branch: data.branch,
        graduation_year: data.graduation_year,
        cgpa: data.cgpa,
        skills: skillsString,
        github_url: data.github_url || '',
        linkedin_url: data.linkedin_url || ''
      };

      const result = await maverickAPI.registerMaverickWithProfile(registrationData);

      // Save token to localStorage
      localStorage.setItem('access_token', result.access_token);
      localStorage.setItem('user', JSON.stringify(result.user));
      localStorage.setItem('maverick_id', result.maverick_id);
      localStorage.setItem('registration_step', 'resume');

      console.log('✅ Registration successful!');
      console.log('✅ Token saved:', result.access_token.substring(0, 20) + '...');
      console.log('✅ Maverick ID:', result.maverick_id);

      // Show success message
      alert('Registration successful! Redirecting to resume upload...');

      // Reload page to ensure clean state and token is loaded
      window.location.href = '/mavericks/register?step=resume';
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to register. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle resume upload success
  const handleResumeUpload = (data: any) => {
    console.log('Resume uploaded:', data);
  };

  // Handle AI extracted data
  const handleExtractedData = async (data: any) => {
    setExtractedData(data);
    
    // Update profile with extracted data
    if (profileId && data) {
      try {
        await maverickAPI.updateProfile(profileId, {
          ai_extracted_skills: data,
          ai_summary: data.summary,
          skills: [...new Set([...(profileData.skills || []), ...(data.skills || [])])]
        });
      } catch (error) {
        console.error('Failed to update profile with AI data:', error);
      }
    }
  };

  // Submit profile for review
  const handleSubmitForReview = async () => {
    // Profile is already in PENDING status after resume upload
    // No need to call submit endpoint, just redirect

    // Clear registration state from localStorage
    localStorage.removeItem('registration_step');
    localStorage.removeItem('maverick_id');

    alert('Profile submitted for review successfully! Your profile is now PENDING HR approval. Please login to check status.');
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />

      <div className="flex-1 py-8">
        <div className="max-w-4xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8">
            <button
              onClick={() => step === 'resume' ? setStep('form') : router.back()}
              className="flex items-center text-gray-600 hover:text-blue-900 mb-4 font-semibold"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back
            </button>
            <h1 className="text-3xl font-black text-blue-900 uppercase tracking-tight">Maverick Registration</h1>
            <p className="text-gray-600 mt-2 font-medium">
              {step === 'form'
                ? 'Fill in your details to create your profile'
                : 'Upload your resume for AI-powered skill extraction'}
            </p>
          </div>

          {/* Progress Steps */}
          <div className="mb-8">
            <div className="flex items-center justify-center space-x-4">
            <div className={`flex items-center ${step === 'form' ? 'text-blue-600' : 'text-green-600'}`}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                step === 'form' ? 'bg-blue-600 text-white' : 'bg-green-600 text-white'
              }`}>
                {step === 'form' ? '1' : '✓'}
              </div>
              <span className="ml-2 font-medium">Profile Details</span>
            </div>
            <div className="w-16 h-1 bg-gray-300"></div>
            <div className={`flex items-center ${step === 'resume' ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                step === 'resume' ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
              }`}>
                2
              </div>
              <span className="ml-2 font-medium">Resume Upload</span>
            </div>
            </div>
          </div>

          {/* Content */}
          <div>
            {step === 'form' && (
              <MaverickRegistrationForm
                onSubmit={handleFormSubmit}
                initialData={profileData}
                loading={loading}
              />
            )}

            {step === 'resume' && (
            <div className="space-y-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                  <Upload className="w-6 h-6 mr-2 text-blue-600" />
                  Upload Resume
                </h2>
                <ResumeUpload
                  onUploadSuccess={handleResumeUpload}
                  onExtractedData={handleExtractedData}
                />
              </div>

              {/* Extracted Skills Display */}
              {extractedData && extractedData.skills && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <FileText className="w-5 h-5 mr-2 text-green-600" />
                    AI-Extracted Skills
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {extractedData.skills.map((skill: string, index: number) => (
                      <span key={index} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                        {skill}
                      </span>
                    ))}
                  </div>
                  {extractedData.summary && (
                    <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                      <h4 className="font-medium text-blue-900 mb-2">AI Summary</h4>
                      <p className="text-blue-800 text-sm">{extractedData.summary}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Submit Button */}
              <div className="flex justify-between">
                <button
                  onClick={() => setStep('form')}
                  className="px-6 py-3 border-2 border-blue-900 text-blue-900 rounded font-bold uppercase tracking-wide hover:bg-blue-50 transition"
                >
                  Back to Form
                </button>
                <button
                  onClick={handleSubmitForReview}
                  disabled={loading}
                  className="px-6 py-3 bg-blue-900 text-white rounded font-bold uppercase tracking-wide hover:bg-blue-800 disabled:bg-gray-400 transition"
                >
                  {loading ? 'Submitting...' : 'Submit for Review'}
                </button>
              </div>
            </div>
            )}
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
