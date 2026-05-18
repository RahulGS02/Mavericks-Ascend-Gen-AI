"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { 
  ArrowLeft, User, Mail, Phone, GraduationCap, Calendar, MapPin, 
  Github, Linkedin, FileText, CheckCircle, XCircle, Clock, 
  Briefcase, Code, Award, TrendingUp, AlertTriangle, BookOpen
} from 'lucide-react';
import DashboardLayout from '@/components/DashboardLayout';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';

interface MaverickProfile {
  id: string;
  user_id: string;
  name: string;
  email: string;
  phone?: string;
  college?: string;
  degree?: string;
  branch?: string;
  graduation_year?: number;
  cgpa?: number;
  skills: string[];
  ai_extracted_skills?: string[];
  ai_summary?: string;
  resume_url?: string;
  github_url?: string;
  linkedin_url?: string;
  profile_status: string;
  deployment_status?: string;
  current_batch_id?: string;
  review_notes?: string;
  reviewed_by?: string;
  created_at: string;
  updated_at: string;
}

interface Batch {
  id: string;
  name: string;
  pipeline_name?: string;
  start_date: string;
  end_date: string;
  status: string;
}

interface AssessmentAttempt {
  id: string;
  assessment_id: string;
  assessment_name: string;
  marks_obtained: number;
  max_marks: number;
  passed: boolean;
  percentage: number;
  evaluated_at: string;
  feedback?: string;
}

interface Deployment {
  id: string;
  project_name: string;
  vertical: string;
  competency: string;
  role?: string;
  manager_name?: string;
  location?: string;
  start_date: string;
  end_date?: string;
  status: string;
  notes?: string;
}

export default function HRMaverickProfilePage() {
  const params = useParams();
  const router = useRouter();
  const maverickId = params?.id as string;

  const [profile, setProfile] = useState<MaverickProfile | null>(null);
  const [batch, setBatch] = useState<Batch | null>(null);
  const [assessments, setAssessments] = useState<AssessmentAttempt[]>([]);
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'assessments' | 'deployments' | 'activity'>('overview');

  useEffect(() => {
    if (maverickId) {
      fetchMaverickData();
    }
  }, [maverickId]);

  const fetchMaverickData = async () => {
    setLoading(true);
    try {
      // Fetch maverick profile
      const profileResponse = await apiClient.get(`/mavericks/${maverickId}`);
      setProfile(profileResponse.data);

      // Fetch batch info if assigned
      if (profileResponse.data.current_batch_id) {
        try {
          const batchResponse = await apiClient.get(`/batches/${profileResponse.data.current_batch_id}`);
          setBatch(batchResponse.data);
        } catch (error) {
          console.error('Failed to fetch batch:', error);
        }
      }

      // Fetch assessment attempts - Note: This endpoint might not exist for all mavericks
      try {
        const assessmentsResponse = await apiClient.get(`/reattempts/maverick/${maverickId}/all-attempts`);
        setAssessments(assessmentsResponse.data?.attempts || []);
      } catch (error) {
        // Silently fail - maverick might not have any assessments yet
        console.log('No assessments found for this maverick');
        setAssessments([]);
      }

      // Fetch deployment history
      try {
        const deploymentsResponse = await apiClient.get(`/deployments/maverick/${maverickId}/history`);
        setDeployments(deploymentsResponse.data?.deployments || []);
      } catch (error) {
        // Silently fail - maverick might not have deployments yet
        console.log('No deployments found for this maverick');
        setDeployments([]);
      }
    } catch (error: any) {
      console.error('Failed to fetch maverick data:', error);
      toast.error(error.response?.data?.detail || 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!confirm('Approve this maverick profile?')) return;
    
    setProcessing(true);
    try {
      await apiClient.post(`/hr/approve-profile/${maverickId}`);
      toast.success('Profile approved successfully!');
      await fetchMaverickData();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to approve profile');
    } finally {
      setProcessing(false);
    }
  };

  const handleReject = async () => {
    const reason = prompt('Enter rejection reason:');
    if (!reason) return;

    setProcessing(true);
    try {
      await apiClient.post(`/hr/reject-profile/${maverickId}`, { reason });
      toast.success('Profile rejected');
      await fetchMaverickData();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to reject profile');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="p-6 flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading profile...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!profile) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
            <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Profile Not Found</h2>
            <p className="text-gray-600 mb-4">The maverick profile you're looking for doesn't exist.</p>
            <button
              onClick={() => router.back()}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Go Back
            </button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { color: string; icon: any; label: string }> = {
      'pending': { color: 'bg-yellow-100 text-yellow-800 border-yellow-300', icon: Clock, label: 'Pending' },
      'approved': { color: 'bg-green-100 text-green-800 border-green-300', icon: CheckCircle, label: 'Approved' },
      'rejected': { color: 'bg-red-100 text-red-800 border-red-300', icon: XCircle, label: 'Rejected' },
    };

    const config = statusConfig[status.toLowerCase()] || statusConfig['pending'];
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center gap-1.5 px-3 py-1 border rounded-full text-sm font-medium ${config.color}`}>
        <Icon className="w-4 h-4" />
        {config.label}
      </span>
    );
  };

  // Get active deployment
  const activeDeployment = deployments.find(d => d.status === 'ACTIVE');

  return (
    <DashboardLayout>
      <div className="p-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </button>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                  {profile.name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">{profile.name}</h1>
                  <div className="flex items-center gap-4 text-gray-600 mb-3">
                    <span className="inline-flex items-center gap-1">
                      <Mail className="w-4 h-4" />
                      {profile.email}
                    </span>
                    {profile.phone && (
                      <span className="inline-flex items-center gap-1">
                        <Phone className="w-4 h-4" />
                        {profile.phone}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(profile.profile_status)}
                    {profile.deployment_status && (
                      <span className={`inline-flex items-center gap-1.5 px-3 py-1 border border-green-300 rounded-full text-sm font-medium ${
                        profile.deployment_status === 'DEPLOYED' ? 'bg-purple-100 text-purple-800 border-purple-300' :
                        profile.deployment_status === 'ON_BENCH' ? 'bg-gray-100 text-gray-800 border-gray-300' :
                        'bg-green-100 text-green-800 border-green-300'
                      }`}>
                        <Briefcase className="w-4 h-4" />
                        {profile.deployment_status === 'AVAILABLE' ? 'Ready for Deployment' :
                         profile.deployment_status === 'DEPLOYED' ? 'Currently Deployed' :
                         profile.deployment_status === 'ON_BENCH' ? 'On Bench' :
                         profile.deployment_status}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2">
                {profile.profile_status.toLowerCase() === 'pending' && (
                  <>
                    <button
                      onClick={handleApprove}
                      disabled={processing}
                      className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                    >
                      <CheckCircle className="w-4 h-4" />
                      Approve
                    </button>
                    <button
                      onClick={handleReject}
                      disabled={processing}
                      className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
                    >
                      <XCircle className="w-4 h-4" />
                      Reject
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {/* Batch Info Card */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-blue-100 rounded-lg flex-shrink-0">
                <BookOpen className="w-5 h-5 text-blue-600" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-medium text-gray-600 mb-1">Current Batch</div>
                {batch ? (
                  <>
                    <button
                      onClick={() => router.push(`/batches/${batch.id}`)}
                      className="text-base font-bold text-blue-600 hover:text-blue-700 hover:underline truncate text-left block w-full"
                    >
                      {batch.name}
                    </button>
                    <div className="text-xs text-gray-600 mt-1">
                      {new Date(batch.start_date).toLocaleDateString()} - {new Date(batch.end_date).toLocaleDateString()}
                    </div>
                    <span className={`inline-block mt-2 px-2 py-1 rounded text-xs font-medium ${
                      batch.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
                      batch.status === 'COMPLETED' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {batch.status}
                    </span>
                  </>
                ) : (
                  <div className="text-gray-500 text-sm">Not assigned</div>
                )}
              </div>
            </div>
          </div>

          {/* Deployment Status Card */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-purple-100 rounded-lg flex-shrink-0">
                <Briefcase className="w-5 h-5 text-purple-600" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-medium text-gray-600 mb-1">Deployment Status</div>
                {activeDeployment ? (
                  <>
                    <div className="text-base font-bold text-gray-900 truncate">{activeDeployment.project_name}</div>
                    <div className="text-xs text-gray-600 mt-1 space-y-0.5">
                      <div><span className="font-medium">Vertical:</span> {activeDeployment.vertical}</div>
                      <div><span className="font-medium">Competency:</span> {activeDeployment.competency}</div>
                    </div>
                    <span className="inline-block mt-2 px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
                      Active
                    </span>
                  </>
                ) : (
                  <div>
                    <div className="text-base font-bold text-gray-700">
                      {profile.deployment_status === 'AVAILABLE' ? 'Ready for Deployment' :
                       profile.deployment_status === 'ON_BENCH' ? 'On Bench' :
                       profile.deployment_status || 'Not Deployed'}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {deployments.length > 0
                        ? `${deployments.length} past deployment${deployments.length > 1 ? 's' : ''}`
                        : profile.deployment_status === 'AVAILABLE'
                          ? 'Available for projects'
                          : 'No history'}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Assessments Card */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-green-100 rounded-lg flex-shrink-0">
                <Award className="w-5 h-5 text-green-600" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-medium text-gray-600 mb-1">Assessments</div>
                <div className="text-base font-bold text-gray-900">{assessments.length} Total</div>
                <div className="text-xs text-gray-600 mt-1">
                  <span className="text-green-600 font-medium">{assessments.filter(a => a.passed).length} Passed</span>
                  {' • '}
                  <span className="text-red-600 font-medium">{assessments.filter(a => a.passed === false).length} Failed</span>
                </div>
                {assessments.length > 0 && (
                  <div className="text-xs text-purple-600 font-medium mt-1">
                    Avg: {(assessments.reduce((sum, a) => sum + a.percentage, 0) / assessments.length).toFixed(1)}%
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex gap-6 px-6">
              {[
                { id: 'overview' as const, label: 'Overview', icon: User },
                { id: 'assessments' as const, label: 'Assessments', icon: Award },
                { id: 'deployments' as const, label: 'Deployments', icon: Briefcase },
                { id: 'activity' as const, label: 'Activity', icon: Calendar },
              ].map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                      activeTab === tab.id
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                );
              })}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Education */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <GraduationCap className="w-5 h-5 text-blue-600" />
                    Education
                  </h3>
                  <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm text-gray-600">College</div>
                        <div className="font-medium text-gray-900">{profile.college || 'N/A'}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Degree</div>
                        <div className="font-medium text-gray-900">{profile.degree || 'N/A'}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Branch</div>
                        <div className="font-medium text-gray-900">{profile.branch || 'N/A'}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Graduation Year</div>
                        <div className="font-medium text-gray-900">{profile.graduation_year || 'N/A'}</div>
                      </div>
                      {profile.cgpa && (
                        <div>
                          <div className="text-sm text-gray-600">CGPA</div>
                          <div className="font-medium text-gray-900">{profile.cgpa}</div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Skills */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <Code className="w-5 h-5 text-blue-600" />
                    Skills
                  </h3>
                  <div className="space-y-3">
                    {profile.skills && profile.skills.length > 0 && (
                      <div>
                        <div className="text-sm text-gray-600 mb-2">Manual Skills</div>
                        <div className="flex flex-wrap gap-2">
                          {profile.skills.map((skill, index) => (
                            <span
                              key={index}
                              className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {profile.ai_extracted_skills && profile.ai_extracted_skills.length > 0 && (
                      <div>
                        <div className="text-sm text-gray-600 mb-2">AI-Extracted Skills</div>
                        <div className="flex flex-wrap gap-2">
                          {profile.ai_extracted_skills.map((skill, index) => (
                            <span
                              key={index}
                              className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Batch Assignment */}
                {batch && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <Briefcase className="w-5 h-5 text-blue-600" />
                      Current Batch
                    </h3>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <div className="font-semibold text-gray-900 text-lg">{batch.name}</div>
                          {batch.pipeline_name && (
                            <div className="text-sm text-gray-600">Pipeline: {batch.pipeline_name}</div>
                          )}
                        </div>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          batch.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
                          batch.status === 'COMPLETED' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {batch.status}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <div className="text-gray-600">Start Date</div>
                          <div className="font-medium text-gray-900">
                            {new Date(batch.start_date).toLocaleDateString()}
                          </div>
                        </div>
                        <div>
                          <div className="text-gray-600">End Date</div>
                          <div className="font-medium text-gray-900">
                            {new Date(batch.end_date).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Documents & Links */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <FileText className="w-5 h-5 text-blue-600" />
                    Documents & Links
                  </h3>
                  {(!profile.resume_url && !profile.github_url && !profile.linkedin_url) ? (
                    <div className="text-center py-8 bg-gray-50 rounded-lg border border-gray-200">
                      <FileText className="w-12 h-12 text-gray-300 mx-auto mb-2" />
                      <p className="text-gray-500 text-sm">No documents or links uploaded yet</p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {profile.resume_url && (
                        <a
                          href={profile.resume_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-2 p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                          <FileText className="w-5 h-5 text-blue-600" />
                          <span className="text-gray-900 font-medium">View Resume</span>
                        </a>
                      )}
                      {profile.github_url && (
                        <a
                          href={profile.github_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-2 p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                          <Github className="w-5 h-5 text-gray-900" />
                          <span className="text-gray-900 font-medium">GitHub Profile</span>
                        </a>
                      )}
                      {profile.linkedin_url && (
                        <a
                          href={profile.linkedin_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-2 p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                          <Linkedin className="w-5 h-5 text-blue-600" />
                          <span className="text-gray-900 font-medium">LinkedIn Profile</span>
                        </a>
                      )}
                    </div>
                  )}
                </div>

                {/* AI Summary */}
                {profile.ai_summary && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Summary</h3>
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                      <p className="text-gray-700 whitespace-pre-wrap">{profile.ai_summary}</p>
                    </div>
                  </div>
                )}

                {/* Review Notes */}
                {profile.review_notes && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Review Notes</h3>
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <p className="text-gray-700">{profile.review_notes}</p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'assessments' && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Assessment History</h3>
                {assessments.length === 0 ? (
                  <div className="text-center py-12">
                    <Award className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-600">No assessments yet</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {assessments.map((assessment) => (
                      <div
                        key={assessment.id}
                        className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <div className="font-semibold text-gray-900">{assessment.assessment_name}</div>
                            <div className="text-sm text-gray-600">
                              {new Date(assessment.evaluated_at).toLocaleDateString()}
                            </div>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                            assessment.passed
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {assessment.passed ? 'Passed' : 'Failed'}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 mb-2">
                          <div>
                            <span className="text-2xl font-bold text-gray-900">
                              {assessment.marks_obtained}
                            </span>
                            <span className="text-gray-600">/{assessment.max_marks}</span>
                          </div>
                          <div className="text-lg font-semibold text-blue-600">
                            {assessment.percentage.toFixed(1)}%
                          </div>
                        </div>
                        {assessment.feedback && (
                          <div className="mt-3 text-sm text-gray-600 bg-gray-50 p-3 rounded">
                            <span className="font-medium">Feedback:</span> {assessment.feedback}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'deployments' && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Deployment History</h3>
                {deployments.length === 0 ? (
                  <div className="text-center py-12">
                    <Briefcase className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-600">No deployments yet</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {deployments.map((deployment) => (
                      <div
                        key={deployment.id}
                        className="border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <div className="font-semibold text-xl text-gray-900">{deployment.project_name}</div>
                            {deployment.role && (
                              <div className="text-sm text-gray-600 mt-1">{deployment.role}</div>
                            )}
                          </div>
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                            deployment.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
                            deployment.status === 'COMPLETED' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {deployment.status}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-3">
                          <div>
                            <div className="text-xs text-gray-500 uppercase">Vertical</div>
                            <div className="text-sm font-medium text-gray-900">{deployment.vertical}</div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500 uppercase">Competency</div>
                            <div className="text-sm font-medium text-gray-900">{deployment.competency}</div>
                          </div>
                          {deployment.location && (
                            <div>
                              <div className="text-xs text-gray-500 uppercase">Location</div>
                              <div className="text-sm font-medium text-gray-900">{deployment.location}</div>
                            </div>
                          )}
                        </div>

                        <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            <span>Start: {new Date(deployment.start_date).toLocaleDateString()}</span>
                          </div>
                          {deployment.end_date && (
                            <div className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              <span>End: {new Date(deployment.end_date).toLocaleDateString()}</span>
                            </div>
                          )}
                        </div>

                        {deployment.manager_name && (
                          <div className="text-sm">
                            <span className="text-gray-600">Manager:</span>{' '}
                            <span className="font-medium text-gray-900">{deployment.manager_name}</span>
                          </div>
                        )}

                        {deployment.notes && (
                          <div className="mt-3 text-sm text-gray-600 bg-gray-50 p-3 rounded">
                            <span className="font-medium">Notes:</span> {deployment.notes}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'activity' && (
              <div className="text-center py-12">
                <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-600">Activity timeline coming soon</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
