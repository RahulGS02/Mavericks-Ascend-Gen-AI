"use client";

import { useState, useEffect } from 'react';
import { type MaverickResponse, hrAPI } from '@/lib/api/hr';
import {
  X,
  User,
  Mail,
  Phone,
  GraduationCap,
  Calendar,
  Award,
  Link as LinkIcon,
  FileText,
  Briefcase,
  Code,
  FolderGit2,
  CheckCircle,
  XCircle,
  Loader2,
  BookOpen,
} from 'lucide-react';

interface ProfileReviewModalProps {
  profile: MaverickResponse | null;
  isOpen: boolean;
  onClose: () => void;
  onReviewComplete: () => void;
}

export default function ProfileReviewModal({
  profile,
  isOpen,
  onClose,
  onReviewComplete,
}: ProfileReviewModalProps) {
  const [reviewNotes, setReviewNotes] = useState('');
  const [selectedBatch, setSelectedBatch] = useState('');
  const [processing, setProcessing] = useState(false);
  const [batches, setBatches] = useState<any[]>([]);
  const [loadingBatches, setLoadingBatches] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchBatches();
    }
  }, [isOpen]);

  const fetchBatches = async () => {
    try {
      setLoadingBatches(true);
      const response = await hrAPI.getAllBatches({ status: 'active' });
      setBatches(response.batches || []);
    } catch (error) {
      console.error('Failed to fetch batches:', error);
    } finally {
      setLoadingBatches(false);
    }
  };

  const handleApprove = async () => {
    if (!profile) return;

    try {
      setProcessing(true);
      
      // Approve the profile
      await hrAPI.approveMaverick(profile.id, reviewNotes || undefined);

      // Assign to batch if selected
      if (selectedBatch) {
        await hrAPI.assignToBatch(profile.id, selectedBatch);
      }

      alert('Profile approved successfully!');
      onReviewComplete();
      handleClose();
    } catch (error: any) {
      console.error('Failed to approve profile:', error);
      alert(error.response?.data?.detail || 'Failed to approve profile');
    } finally {
      setProcessing(false);
    }
  };

  const handleReject = async () => {
    if (!profile) return;
    
    if (!reviewNotes.trim()) {
      alert('Please provide a reason for rejection');
      return;
    }

    try {
      setProcessing(true);
      await hrAPI.rejectMaverick(profile.id, reviewNotes);

      alert('Profile rejected successfully!');
      onReviewComplete();
      handleClose();
    } catch (error: any) {
      console.error('Failed to reject profile:', error);
      alert(error.response?.data?.detail || 'Failed to reject profile');
    } finally {
      setProcessing(false);
    }
  };

  const handleClose = () => {
    setReviewNotes('');
    setSelectedBatch('');
    onClose();
  };

  if (!isOpen || !profile) {
    return null;
  }

  const aiData = profile.ai_resume_data;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-blue-900 text-white px-6 py-4 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold">{profile.name}</h2>
            <p className="text-blue-100 text-sm">{profile.email}</p>
          </div>
          <button
            onClick={handleClose}
            className="text-white hover:text-gray-200 transition"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Basic Information */}
          <div className="mb-6">
            <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
              <User className="w-5 h-5 text-blue-900" />
              Basic Information
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <InfoItem icon={<Mail />} label="Email" value={profile.email} />
              <InfoItem icon={<Phone />} label="Phone" value={profile.phone || '-'} />
              <InfoItem icon={<GraduationCap />} label="College" value={profile.college || '-'} />
              <InfoItem icon={<BookOpen />} label="Degree" value={`${profile.degree || '-'} (${profile.branch || '-'})`} />
              <InfoItem icon={<Calendar />} label="Graduation Year" value={profile.graduation_year || '-'} />
              <InfoItem icon={<Award />} label="CGPA" value={profile.cgpa ? profile.cgpa.toFixed(2) : '-'} />
            </div>
          </div>

          {/* Links */}
          {(profile.github_url || profile.linkedin_url || profile.resume_url) && (
            <div className="mb-6">
              <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                <LinkIcon className="w-5 h-5 text-blue-900" />
                Links & Resume
              </h3>
              <div className="space-y-2">
                {profile.github_url && (
                  <a
                    href={profile.github_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-blue-900 hover:underline"
                  >
                    <FolderGit2 className="w-4 h-4" />
                    GitHub Profile
                  </a>
                )}
                {profile.linkedin_url && (
                  <a
                    href={profile.linkedin_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-blue-900 hover:underline"
                  >
                    <LinkIcon className="w-4 h-4" />
                    LinkedIn Profile
                  </a>
                )}
                {profile.resume_url && (
                  <a
                    href={profile.resume_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-blue-900 hover:underline font-semibold"
                  >
                    <FileText className="w-4 h-4" />
                    View Resume
                  </a>
                )}
              </div>
            </div>
          )}

          {/* Skills */}
          <div className="mb-6">
            <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
              <Code className="w-5 h-5 text-blue-900" />
              Skills
            </h3>
            <div className="flex flex-wrap gap-2">
              {(profile.ai_extracted_skills || profile.skills || []).length > 0 ? (
                (profile.ai_extracted_skills || profile.skills || []).map((skill, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                  >
                    {skill}
                  </span>
                ))
              ) : (
                <p className="text-gray-500">No skills listed</p>
              )}
            </div>
          </div>

          {/* AI Summary */}
          {profile.ai_summary && (
            <div className="mb-6">
              <h3 className="text-lg font-bold text-gray-900 mb-3">AI-Generated Summary</h3>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-gray-700 whitespace-pre-wrap">{profile.ai_summary}</p>
              </div>
            </div>
          )}

          {/* AI Resume Data - Education */}
          {aiData?.education && aiData.education.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-bold text-gray-900 mb-3">Education (AI Extracted)</h3>
              <div className="space-y-3">
                {aiData.education.map((edu: any, idx: number) => (
                  <div key={idx} className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900">{edu.degree || edu.institution}</h4>
                    <p className="text-sm text-gray-600">{edu.institution}</p>
                    <p className="text-sm text-gray-500">
                      {edu.start_date} - {edu.end_date || 'Present'}
                      {edu.grade && <span> • Grade: {edu.grade}</span>}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Resume Data - Experience */}
          {aiData?.experience && aiData.experience.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-blue-900" />
                Experience (AI Extracted)
              </h3>
              <div className="space-y-3">
                {aiData.experience.map((exp: any, idx: number) => (
                  <div key={idx} className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900">{exp.position}</h4>
                    <p className="text-sm text-gray-600">{exp.company}</p>
                    <p className="text-sm text-gray-500">
                      {exp.start_date} - {exp.end_date || 'Present'}
                    </p>
                    {exp.description && (
                      <p className="text-sm text-gray-700 mt-2">{exp.description}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Resume Data - Projects */}
          {aiData?.projects && aiData.projects.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-bold text-gray-900 mb-3">Projects (AI Extracted)</h3>
              <div className="space-y-3">
                {aiData.projects.map((project: any, idx: number) => (
                  <div key={idx} className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900">{project.title}</h4>
                    {project.description && (
                      <p className="text-sm text-gray-700 mt-2">{project.description}</p>
                    )}
                    {project.technologies && project.technologies.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {project.technologies.map((tech: string, techIdx: number) => (
                          <span
                            key={techIdx}
                            className="text-xs bg-gray-200 text-gray-700 px-2 py-0.5 rounded"
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Review Actions */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Review Actions</h3>

            {/* Review Notes */}
            <div className="mb-4">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Review Notes / Comments
                <span className="text-red-500">*</span>
              </label>
              <textarea
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                placeholder="Add review notes or rejection reason..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-900 focus:border-transparent min-h-[100px]"
              />
              <p className="text-xs text-gray-500 mt-1">
                Required for rejection. Optional for approval.
              </p>
            </div>

            {/* Batch Assignment */}
            <div className="mb-6">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Assign to Batch (Optional)
              </label>
              <select
                value={selectedBatch}
                onChange={(e) => setSelectedBatch(e.target.value)}
                disabled={loadingBatches}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-900 focus:border-transparent"
              >
                <option value="">-- Select Batch (Optional) --</option>
                {batches.map((batch) => (
                  <option key={batch.id} value={batch.id}>
                    {batch.name} ({batch.status})
                  </option>
                ))}
              </select>
              {loadingBatches && (
                <p className="text-xs text-gray-500 mt-1">Loading batches...</p>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={handleApprove}
                disabled={processing}
                className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-bold uppercase text-sm tracking-wide transition"
              >
                {processing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    Approve
                  </>
                )}
              </button>

              <button
                onClick={handleReject}
                disabled={processing}
                className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed font-bold uppercase text-sm tracking-wide transition"
              >
                {processing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <XCircle className="w-5 h-5" />
                    Reject
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Helper component for info display
function InfoItem({ icon, label, value }: { icon: React.ReactNode; label: string; value: any }) {
  return (
    <div className="flex items-start gap-2">
      <div className="text-gray-400 mt-0.5">{icon}</div>
      <div>
        <p className="text-xs text-gray-500 uppercase font-semibold tracking-wide">{label}</p>
        <p className="text-sm text-gray-900 font-medium">{value}</p>
      </div>
    </div>
  );
}
