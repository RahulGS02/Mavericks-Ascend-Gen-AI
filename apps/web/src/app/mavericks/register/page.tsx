'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ArrowLeft, Upload, Brain } from 'lucide-react';
import MaverickRegistrationForm from '@/components/mavericks/MaverickRegistrationForm';
import ResumeUpload, { type ExtractedResumeData } from '@/components/mavericks/ResumeUpload';
import AISkillSummary from '@/components/mavericks/AISkillSummary';
import Header from '@/components/common/Header';
import Footer from '@/components/common/Footer';
import { maverickAPI, MaverickProfile } from '@/lib/api/mavericks';

export default function MaverickRegisterPage() {
  const router       = useRouter();
  const searchParams = useSearchParams();

  const [step, setStep]               = useState<'form' | 'resume'>('form');
  const [loading, setLoading]         = useState(false);
  const [profileData, setProfileData] = useState<Partial<MaverickProfile>>({});
  const [extractedData, setExtractedData] = useState<ExtractedResumeData | null>(null);
  const [profileId, setProfileId]     = useState<string | null>(null);

  // ── Restore step from URL / localStorage ─────────────────────────────────
  useEffect(() => {
    const stepParam      = searchParams.get('step');
    const savedId        = localStorage.getItem('maverick_id');
    const savedStep      = localStorage.getItem('registration_step');

    if (stepParam === 'resume' && savedId) {
      setProfileId(savedId);
      setStep('resume');
    } else if (savedStep === 'resume' && savedId) {
      setProfileId(savedId);
      setStep('resume');
    }
  }, [searchParams]);

  // ── Step 1 — Profile form submission ─────────────────────────────────────
  const handleFormSubmit = async (data: any) => {
    setLoading(true);
    try {
      if (!data.password || data.password.length < 6) {
        alert('Password must be at least 6 characters');
        return;
      }

      const skillsString = Array.isArray(data.skills)
        ? data.skills.join(', ')
        : data.skills || '';

      const result = await maverickAPI.registerMaverickWithProfile({
        name:            data.name,
        email:           data.email,
        password:        data.password,
        phone:           data.phone,
        college:         data.college,
        degree:          data.degree,
        branch:          data.branch,
        graduation_year: data.graduation_year,
        cgpa:            data.cgpa,
        skills:          skillsString,
        github_url:      data.github_url  || '',
        linkedin_url:    data.linkedin_url || '',
      });

      // Persist token + navigation state
      localStorage.setItem('access_token',      result.access_token);
      localStorage.setItem('user',              JSON.stringify(result.user));
      localStorage.setItem('maverick_id',       result.maverick_id);
      localStorage.setItem('registration_step', 'resume');

      // Reload cleanly so the API client picks up the new token
      window.location.href = '/mavericks/register?step=resume';
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // ── Step 2 — AI extracted data callback ──────────────────────────────────
  const handleExtractedData = (data: ExtractedResumeData) => {
    setExtractedData(data);
  };

  // ── Step 2 — Submit profile for HR review ────────────────────────────────
  const handleSubmitForReview = async () => {
    localStorage.removeItem('registration_step');
    localStorage.removeItem('maverick_id');
    alert(
      'Profile submitted for review! Your profile is now PENDING HR approval.\n\nPlease login to check your status.'
    );
    router.push('/login');
  };

  // ─────────────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />

      <div className="flex-1 py-8">
        <div className="max-w-4xl mx-auto px-4">

          {/* ── Page header ─────────────────────────────────────────────── */}
          <div className="mb-8">
            <button
              onClick={() => step === 'resume' ? setStep('form') : router.back()}
              className="flex items-center text-gray-600 hover:text-blue-900 mb-4 font-semibold transition-colors"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back
            </button>
            <h1 className="text-3xl font-black text-blue-900 uppercase tracking-tight">
              Maverick Registration
            </h1>
            <p className="text-gray-600 mt-2 font-medium">
              {step === 'form'
                ? 'Fill in your details to create your profile'
                : 'Upload your resume — AI will extract your skills automatically'}
            </p>
          </div>

          {/* ── Progress indicator ──────────────────────────────────────── */}
          <div className="mb-8">
            <div className="flex items-center justify-center space-x-4">
              <div className={`flex items-center ${step === 'form' ? 'text-blue-600' : 'text-green-600'}`}>
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                  step === 'form' ? 'bg-blue-600 text-white' : 'bg-green-600 text-white'
                }`}>
                  {step === 'form' ? '1' : '✓'}
                </div>
                <span className="ml-2 font-medium">Profile Details</span>
              </div>
              <div className="w-16 h-1 bg-gray-300 rounded" />
              <div className={`flex items-center ${step === 'resume' ? 'text-blue-600' : 'text-gray-400'}`}>
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                  step === 'resume' ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
                }`}>
                  2
                </div>
                <span className="ml-2 font-medium">Resume & AI Analysis</span>
              </div>
            </div>
          </div>

          {/* ── Step content ─────────────────────────────────────────────── */}

          {/* STEP 1 — Registration Form */}
          {step === 'form' && (
            <MaverickRegistrationForm
              onSubmit={handleFormSubmit}
              initialData={profileData}
              loading={loading}
            />
          )}

          {/* STEP 2 — Resume Upload + AI Summary */}
          {step === 'resume' && (
            <div className="space-y-6">

              {/* Upload card */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-1 flex items-center gap-2">
                  <Upload className="w-5 h-5 text-blue-600" />
                  Upload Your Resume
                </h2>
                <p className="text-sm text-gray-500 mb-5">
                  Our AI will parse your resume and build a detailed skill profile for you automatically.
                </p>
                <ResumeUpload
                  onUploadSuccess={() => {}}
                  onExtractedData={handleExtractedData}
                />
              </div>

              {/* AI Skill Proficiency Summary — shown after upload */}
              {extractedData && (
                <div>
                  <div className="flex items-center gap-2 mb-3 px-1">
                    <Brain className="w-5 h-5 text-indigo-600" />
                    <h2 className="text-lg font-bold text-gray-900">AI Analysis Results</h2>
                  </div>
                  <AISkillSummary
                    summary={extractedData.summary}
                    resumeData={extractedData.resume_data}
                  />
                </div>
              )}

              {/* Placeholder while waiting */}
              {!extractedData && (
                <div className="bg-white rounded-xl border border-dashed border-gray-300 p-8 text-center">
                  <Brain className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-400 text-sm">
                    Upload your resume above — AI analysis results will appear here
                  </p>
                </div>
              )}

              {/* Action buttons */}
              <div className="flex items-center justify-between pt-2">
                <button
                  onClick={() => setStep('form')}
                  className="px-6 py-3 border-2 border-blue-900 text-blue-900 rounded font-bold uppercase tracking-wide hover:bg-blue-50 transition-colors"
                >
                  Back to Form
                </button>
                <button
                  onClick={handleSubmitForReview}
                  disabled={loading}
                  className="px-6 py-3 bg-blue-900 text-white rounded font-bold uppercase tracking-wide hover:bg-blue-800 disabled:bg-gray-400 transition-colors"
                >
                  {loading ? 'Submitting…' : 'Submit for Review'}
                </button>
              </div>
            </div>
          )}

        </div>
      </div>

      <Footer />
    </div>
  );
}
