"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  ArrowLeft,
  Users,
  Calendar,
  CheckCircle,
  XCircle,
  Clock,
  UserPlus,
  Video,
  MapPin,
  Star,
  MessageSquare,
  AlertCircle,
  TrendingUp,
  Building2,
  Briefcase
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';
import ScheduleInterviewModal from '@/components/workflow/ScheduleInterviewModal';
import InterviewFeedbackModal from '@/components/workflow/InterviewFeedbackModal';

interface RequirementDetail {
  id: string;
  role_title: string;
  role_description?: string;
  required_skills: string[];
  preferred_skills: string[];
  project_name?: string;
  vertical?: string;
  competency?: string;
  positions_count: number;
  filled_count: number;
  workflow_stage: string;
  status: string;
  requested_by_name?: string;
  created_at: string;
}

interface Candidate {
  id: string;
  maverick_id: string;
  maverick_name?: string;
  maverick_email?: string;
  match_score?: number;
  status: string;
  hr_notes?: string;
  manager_notes?: string;
  shortlist_notes?: string;
  rejection_reason?: string;
  maverick_skills?: string[];
  maverick_cgpa?: number;
  maverick_degree?: string;
  maverick_branch?: string;
  suggestion_date: string;
}

interface Interview {
  id: string;
  maverick_name?: string;
  interview_type: string;
  interview_mode: string;
  interview_date: string;
  interview_time: string;
  location?: string;
  video_link?: string;
  status: string;
  rating?: number;
  technical_rating?: number;
  communication_rating?: number;
  cultural_fit_rating?: number;
  feedback?: string;
}

export default function RequirementWorkflowPage() {
  const params = useParams();
  const router = useRouter();
  const requirementId = params.id as string;

  const [requirement, setRequirement] = useState<RequirementDetail | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'candidates' | 'interviews' | 'details'>('candidates');
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState<{id: string; name: string} | null>(null);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [selectedInterview, setSelectedInterview] = useState<{id: string; candidateName: string} | null>(null);

  useEffect(() => {
    if (requirementId) {
      fetchRequirementDetails();
      fetchCandidates();
      fetchInterviews();
    }
  }, [requirementId]);

  const fetchRequirementDetails = async () => {
    try {
      const response = await apiClient.get(`/deployments/requests/${requirementId}`);
      setRequirement(response.data);
    } catch (error) {
      console.error('Failed to fetch requirement details:', error);
      toast.error('Failed to load requirement details');
    }
  };

  const fetchCandidates = async () => {
    try {
      const response = await apiClient.get(`/workflow/requirements/${requirementId}/candidates`);
      setCandidates(response.data.candidates || []);
    } catch (error) {
      console.error('Failed to fetch candidates:', error);
      // Don't show error toast - might be that workflow endpoints not yet available
      setCandidates([]);
    }
  };

  const fetchInterviews = async () => {
    try {
      const response = await apiClient.get(`/workflow/requirements/${requirementId}/interviews`);
      setInterviews(response.data.interviews || []);
    } catch (error) {
      console.error('Failed to fetch interviews:', error);
      setInterviews([]);
    } finally {
      setLoading(false);
    }
  };

  const handleShortlist = async (candidateId: string) => {
    try {
      await apiClient.post(`/workflow/requirements/${requirementId}/candidates/${candidateId}/shortlist`, {
        manager_notes: 'Shortlisted for interview'
      });
      toast.success('Candidate shortlisted successfully');
      fetchCandidates();
    } catch (error) {
      console.error('Failed to shortlist candidate:', error);
      toast.error('Failed to shortlist candidate');
    }
  };

  const handleReject = async (candidateId: string) => {
    const reason = prompt('Please provide a reason for rejection:');
    if (!reason) return;

    try {
      await apiClient.post(`/workflow/requirements/${requirementId}/candidates/${candidateId}/reject`, {
        rejection_reason: reason
      });
      toast.success('Candidate rejected');
      fetchCandidates();
    } catch (error) {
      console.error('Failed to reject candidate:', error);
      toast.error('Failed to reject candidate');
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { color: string; bgColor: string; label: string; icon: any }> = {
      SUGGESTED: { color: 'text-blue-700', bgColor: 'bg-blue-50 border-blue-200', label: 'Suggested', icon: UserPlus },
      SHORTLISTED: { color: 'text-green-700', bgColor: 'bg-green-50 border-green-200', label: 'Shortlisted', icon: CheckCircle },
      REJECTED: { color: 'text-red-700', bgColor: 'bg-red-50 border-red-200', label: 'Rejected', icon: XCircle },
      INTERVIEW_SCHEDULED: { color: 'text-purple-700', bgColor: 'bg-purple-50 border-purple-200', label: 'Interview Scheduled', icon: Calendar },
      INTERVIEWED: { color: 'text-indigo-700', bgColor: 'bg-indigo-50 border-indigo-200', label: 'Interviewed', icon: CheckCircle },
      SELECTED: { color: 'text-green-700', bgColor: 'bg-green-50 border-green-200', label: 'Selected', icon: Star },
    };

    const config = statusConfig[status] || { color: 'text-gray-700', bgColor: 'bg-gray-50 border-gray-200', label: status, icon: Clock };
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full border ${config.bgColor} ${config.color} text-xs font-medium`}>
        <Icon className="w-3 h-3" />
        {config.label}
      </span>
    );
  };

  const getWorkflowStageBadge = (stage: string) => {
    const stageConfig: Record<string, { color: string; label: string }> = {
      PENDING: { color: 'bg-gray-100 text-gray-800', label: 'Pending' },
      UNDER_REVIEW: { color: 'bg-yellow-100 text-yellow-800', label: 'Under Review' },
      CANDIDATES_SUGGESTED: { color: 'bg-blue-100 text-blue-800', label: 'Candidates Suggested' },
      INTERVIEW_SCHEDULING: { color: 'bg-purple-100 text-purple-800', label: 'Interview Scheduling' },
      INTERVIEWS_IN_PROGRESS: { color: 'bg-indigo-100 text-indigo-800', label: 'Interviews In Progress' },
      SELECTION_IN_PROGRESS: { color: 'bg-green-100 text-green-800', label: 'Selection In Progress' },
      AWAITING_APPROVAL: { color: 'bg-orange-100 text-orange-800', label: 'Awaiting Approval' },
      APPROVED: { color: 'bg-green-100 text-green-800', label: 'Approved' },
      COMPLETED: { color: 'bg-green-100 text-green-800', label: 'Completed' },
    };

    const config = stageConfig[stage] || { color: 'bg-gray-100 text-gray-800', label: stage };

    return (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${config.color}`}>
        {config.label}
      </span>
    );
  };

  if (loading || !requirement) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Requirements
          </button>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h1 className="text-2xl font-bold text-gray-900 mb-2">{requirement.role_title}</h1>
                <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600">
                  {requirement.project_name && (
                    <div className="flex items-center gap-1">
                      <Building2 className="w-4 h-4" />
                      {requirement.project_name}
                    </div>
                  )}
                  {requirement.vertical && (
                    <div className="flex items-center gap-1">
                      <Briefcase className="w-4 h-4" />
                      {requirement.vertical}
                    </div>
                  )}
                  <div className="flex items-center gap-1">
                    <Users className="w-4 h-4" />
                    {requirement.filled_count} / {requirement.positions_count} filled
                  </div>
                </div>
              </div>
              <div className="flex flex-col items-end gap-2">
                {getWorkflowStageBadge(requirement.workflow_stage)}
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  requirement.status === 'APPROVED' ? 'bg-green-100 text-green-800' :
                  requirement.status === 'REJECTED' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {requirement.status}
                </span>
              </div>
            </div>

            {/* Skills */}
            {requirement.required_skills && requirement.required_skills.length > 0 && (
              <div className="mt-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Required Skills</h3>
                <div className="flex flex-wrap gap-2">
                  {requirement.required_skills.map((skill, idx) => (
                    <span key={idx} className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-medium border border-blue-200">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('candidates')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'candidates'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  Candidates ({candidates.length})
                </div>
              </button>
              <button
                onClick={() => setActiveTab('interviews')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'interviews'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  Interviews ({interviews.length})
                </div>
              </button>
              <button
                onClick={() => setActiveTab('details')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'details'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  Details
                </div>
              </button>
            </nav>
          </div>

          {/* Candidates Tab */}
          {activeTab === 'candidates' && (
            <div className="p-6">
              {candidates.length === 0 ? (
                <div className="text-center py-12">
                  <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 mb-2">No candidates suggested yet</p>
                  <p className="text-sm text-gray-400">HR will suggest suitable candidates soon</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {candidates.map((candidate) => (
                    <div
                      key={candidate.id}
                      className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-all"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-lg font-semibold text-gray-900">{candidate.maverick_name || 'Unknown'}</h3>
                            {getStatusBadge(candidate.status)}
                          </div>
                          <p className="text-sm text-gray-600">{candidate.maverick_email}</p>
                          {candidate.match_score && (
                            <div className="mt-2 flex items-center gap-2">
                              <TrendingUp className="w-4 h-4 text-green-600" />
                              <span className="text-sm font-medium text-green-700">
                                Match Score: {candidate.match_score}%
                              </span>
                            </div>
                          )}
                        </div>
                        {candidate.status === 'SUGGESTED' && (
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleShortlist(candidate.id)}
                              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                            >
                              <CheckCircle className="w-4 h-4 inline mr-1" />
                              Shortlist
                            </button>
                            <button
                              onClick={() => handleReject(candidate.id)}
                              className="px-4 py-2 bg-red-50 text-red-700 border border-red-200 rounded-lg hover:bg-red-100 transition-colors text-sm font-medium"
                            >
                              <XCircle className="w-4 h-4 inline mr-1" />
                              Reject
                            </button>
                          </div>
                        )}
                        {candidate.status === 'SHORTLISTED' && (
                          <button
                            onClick={() => {
                              setSelectedCandidate({ id: candidate.id, name: candidate.maverick_name || 'Unknown' });
                              setShowScheduleModal(true);
                            }}
                            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
                          >
                            <Calendar className="w-4 h-4 inline mr-1" />
                            Schedule Interview
                          </button>
                        )}
                      </div>

                      {/* Candidate Details */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 pt-4 border-t border-gray-200">
                        {/* Skills */}
                        {candidate.maverick_skills && candidate.maverick_skills.length > 0 && (
                          <div>
                            <h4 className="text-xs font-semibold text-gray-700 mb-2">Skills</h4>
                            <div className="flex flex-wrap gap-1">
                              {candidate.maverick_skills.slice(0, 5).map((skill, idx) => (
                                <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                                  {skill}
                                </span>
                              ))}
                              {candidate.maverick_skills.length > 5 && (
                                <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                                  +{candidate.maverick_skills.length - 5} more
                                </span>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Education */}
                        <div>
                          <h4 className="text-xs font-semibold text-gray-700 mb-2">Education</h4>
                          <div className="space-y-1 text-sm text-gray-600">
                            {candidate.maverick_degree && <div>{candidate.maverick_degree}</div>}
                            {candidate.maverick_branch && <div>{candidate.maverick_branch}</div>}
                            {candidate.maverick_cgpa && (
                              <div className="flex items-center gap-1">
                                <Star className="w-3 h-3 text-yellow-500" />
                                CGPA: {candidate.maverick_cgpa}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Notes */}
                      {(candidate.hr_notes || candidate.manager_notes || candidate.rejection_reason) && (
                        <div className="mt-4 pt-4 border-t border-gray-200 space-y-2">
                          {candidate.hr_notes && (
                            <div className="flex gap-2">
                              <MessageSquare className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
                              <div>
                                <span className="text-xs font-semibold text-gray-700">HR Notes: </span>
                                <span className="text-sm text-gray-600">{candidate.hr_notes}</span>
                              </div>
                            </div>
                          )}
                          {candidate.manager_notes && (
                            <div className="flex gap-2">
                              <MessageSquare className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
                              <div>
                                <span className="text-xs font-semibold text-gray-700">Manager Notes: </span>
                                <span className="text-sm text-gray-600">{candidate.manager_notes}</span>
                              </div>
                            </div>
                          )}
                          {candidate.rejection_reason && (
                            <div className="flex gap-2">
                              <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
                              <div>
                                <span className="text-xs font-semibold text-gray-700">Rejection Reason: </span>
                                <span className="text-sm text-gray-600">{candidate.rejection_reason}</span>
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Interviews Tab */}
          {activeTab === 'interviews' && (
            <div className="p-6">
              {interviews.length === 0 ? (
                <div className="text-center py-12">
                  <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 mb-2">No interviews scheduled yet</p>
                  <p className="text-sm text-gray-400">Schedule interviews for shortlisted candidates</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {interviews.map((interview) => (
                    <div
                      key={interview.id}
                      className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-all"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900 mb-2">{interview.maverick_name || 'Unknown'}</h3>
                          <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600">
                            <div className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              {new Date(interview.interview_date).toLocaleDateString()}
                            </div>
                            <div className="flex items-center gap-1">
                              <Clock className="w-4 h-4" />
                              {interview.interview_time}
                            </div>
                            {interview.interview_type === 'ONLINE' ? (
                              <div className="flex items-center gap-1">
                                <Video className="w-4 h-4" />
                                Online
                              </div>
                            ) : (
                              <div className="flex items-center gap-1">
                                <MapPin className="w-4 h-4" />
                                Offline
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="flex flex-col items-end gap-2">
                          {getStatusBadge(interview.status)}
                          {interview.status === 'SCHEDULED' && (
                            <button
                              onClick={() => {
                                setSelectedInterview({ id: interview.id, candidateName: interview.maverick_name || 'Unknown' });
                                setShowFeedbackModal(true);
                              }}
                              className="px-3 py-1 bg-green-600 text-white text-xs rounded-lg hover:bg-green-700 transition-colors font-medium"
                            >
                              Submit Feedback
                            </button>
                          )}
                        </div>
                      </div>

                      {/* Interview Link/Location */}
                      {interview.video_link && (
                        <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                          <a
                            href={interview.video_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-blue-700 hover:text-blue-800 font-medium flex items-center gap-2"
                          >
                            <Video className="w-4 h-4" />
                            Join Video Call
                          </a>
                        </div>
                      )}
                      {interview.location && (
                        <div className="mt-3 p-3 bg-gray-50 border border-gray-200 rounded-lg">
                          <div className="text-sm text-gray-700 flex items-center gap-2">
                            <MapPin className="w-4 h-4" />
                            {interview.location}
                          </div>
                        </div>
                      )}

                      {/* Ratings */}
                      {interview.status === 'COMPLETED' && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                          <h4 className="text-sm font-semibold text-gray-700 mb-3">Interview Ratings</h4>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {interview.rating && (
                              <div className="text-center">
                                <div className="text-2xl font-bold text-gray-900 flex items-center justify-center gap-1">
                                  {interview.rating}
                                  <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
                                </div>
                                <div className="text-xs text-gray-600 mt-1">Overall</div>
                              </div>
                            )}
                            {interview.technical_rating && (
                              <div className="text-center">
                                <div className="text-2xl font-bold text-blue-900">{interview.technical_rating}</div>
                                <div className="text-xs text-gray-600 mt-1">Technical</div>
                              </div>
                            )}
                            {interview.communication_rating && (
                              <div className="text-center">
                                <div className="text-2xl font-bold text-green-900">{interview.communication_rating}</div>
                                <div className="text-xs text-gray-600 mt-1">Communication</div>
                              </div>
                            )}
                            {interview.cultural_fit_rating && (
                              <div className="text-center">
                                <div className="text-2xl font-bold text-purple-900">{interview.cultural_fit_rating}</div>
                                <div className="text-xs text-gray-600 mt-1">Cultural Fit</div>
                              </div>
                            )}
                          </div>
                          {interview.feedback && (
                            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                              <h5 className="text-xs font-semibold text-gray-700 mb-2">Feedback</h5>
                              <p className="text-sm text-gray-600">{interview.feedback}</p>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Details Tab */}
          {activeTab === 'details' && (
            <div className="p-6">
              <div className="space-y-6">
                {/* Role Description */}
                {requirement.role_description && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Role Description</h3>
                    <p className="text-sm text-gray-600 whitespace-pre-wrap">{requirement.role_description}</p>
                  </div>
                )}

                {/* Preferred Skills */}
                {requirement.preferred_skills && requirement.preferred_skills.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Preferred Skills</h3>
                    <div className="flex flex-wrap gap-2">
                      {requirement.preferred_skills.map((skill, idx) => (
                        <span key={idx} className="px-3 py-1 bg-gray-50 text-gray-700 rounded-full text-xs font-medium border border-gray-200">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Project Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {requirement.competency && (
                    <div>
                      <h3 className="text-sm font-semibold text-gray-700 mb-2">Competency</h3>
                      <p className="text-sm text-gray-600">{requirement.competency}</p>
                    </div>
                  )}
                  {requirement.requested_by_name && (
                    <div>
                      <h3 className="text-sm font-semibold text-gray-700 mb-2">Requested By</h3>
                      <p className="text-sm text-gray-600">{requirement.requested_by_name}</p>
                    </div>
                  )}
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Created At</h3>
                    <p className="text-sm text-gray-600">{new Date(requirement.created_at).toLocaleString()}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Schedule Interview Modal */}
        {showScheduleModal && selectedCandidate && (
          <ScheduleInterviewModal
            requirementId={requirementId}
            candidateId={selectedCandidate.id}
            candidateName={selectedCandidate.name}
            onClose={() => {
              setShowScheduleModal(false);
              setSelectedCandidate(null);
            }}
            onSuccess={() => {
              setShowScheduleModal(false);
              setSelectedCandidate(null);
              fetchInterviews();
              fetchCandidates();
            }}
          />
        )}

        {/* Interview Feedback Modal */}
        {showFeedbackModal && selectedInterview && (
          <InterviewFeedbackModal
            requirementId={requirementId}
            interviewId={selectedInterview.id}
            candidateName={selectedInterview.candidateName}
            onClose={() => {
              setShowFeedbackModal(false);
              setSelectedInterview(null);
            }}
            onSuccess={() => {
              setShowFeedbackModal(false);
              setSelectedInterview(null);
              fetchInterviews();
              fetchCandidates();
            }}
          />
        )}
      </div>
    </DashboardLayout>
  );
}
