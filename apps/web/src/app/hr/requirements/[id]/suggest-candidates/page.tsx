"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  ArrowLeft,
  Search,
  UserPlus,
  TrendingUp,
  Star,
  CheckCircle,
  Users,
  Briefcase,
  Building2,
  GraduationCap
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';

interface RequirementDetail {
  id: string;
  role_title: string;
  required_skills: string[];
  preferred_skills: string[];
  project_name?: string;
  vertical?: string;
  positions_count: number;
  filled_count: number;
  workflow_stage: string;
}

interface Maverick {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  skills?: string;
  cgpa?: number;
  degree?: string;
  branch?: string;
  graduation_year?: number;
  training_status?: string;
}

export default function SuggestCandidatesPage() {
  const params = useParams();
  const router = useRouter();
  const requirementId = params.id as string;

  const [requirement, setRequirement] = useState<RequirementDetail | null>(null);
  const [mavericks, setMavericks] = useState<Maverick[]>([]);
  const [selectedCandidates, setSelectedCandidates] = useState<Set<string>>(new Set());
  const [matchScores, setMatchScores] = useState<Record<string, number>>({});
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (requirementId) {
      fetchRequirement();
      fetchMavericks();
    }
  }, [requirementId]);

  const fetchRequirement = async () => {
    try {
      const response = await apiClient.get(`/deployments/requests/${requirementId}`);
      setRequirement(response.data);
    } catch (error) {
      console.error('Failed to fetch requirement:', error);
      toast.error('Failed to load requirement');
    }
  };

  const fetchMavericks = async () => {
    try {
      const response = await apiClient.get('/mavericks', {
        params: { page: 1, page_size: 100 }
      });
      setMavericks(response.data?.mavericks || []);
    } catch (error) {
      console.error('Failed to fetch mavericks:', error);
      toast.error('Failed to load mavericks');
    } finally {
      setLoading(false);
    }
  };

  const calculateMatchScore = (maverick: Maverick): number => {
    if (!requirement || !maverick.skills) return 0;

    const maverickSkills = JSON.parse(maverick.skills || '[]');
    const requiredSkills = requirement.required_skills || [];
    const preferredSkills = requirement.preferred_skills || [];

    let score = 0;
    let matchedRequired = 0;
    let matchedPreferred = 0;

    // Check required skills (70% weight)
    requiredSkills.forEach(reqSkill => {
      if (maverickSkills.some((ms: any) => 
        ms.skill?.toLowerCase().includes(reqSkill.toLowerCase()) ||
        reqSkill.toLowerCase().includes(ms.skill?.toLowerCase())
      )) {
        matchedRequired++;
      }
    });

    // Check preferred skills (30% weight)
    preferredSkills.forEach(prefSkill => {
      if (maverickSkills.some((ms: any) => 
        ms.skill?.toLowerCase().includes(prefSkill.toLowerCase()) ||
        prefSkill.toLowerCase().includes(ms.skill?.toLowerCase())
      )) {
        matchedPreferred++;
      }
    });

    const requiredScore = requiredSkills.length > 0 
      ? (matchedRequired / requiredSkills.length) * 70 
      : 70;

    const preferredScore = preferredSkills.length > 0 
      ? (matchedPreferred / preferredSkills.length) * 30 
      : 30;

    score = Math.round(requiredScore + preferredScore);

    return score;
  };

  const toggleCandidate = (maverickId: string, maverick: Maverick) => {
    const newSelected = new Set(selectedCandidates);
    if (newSelected.has(maverickId)) {
      newSelected.delete(maverickId);
    } else {
      newSelected.add(maverickId);
      // Auto-calculate match score if not set
      if (!matchScores[maverickId]) {
        const score = calculateMatchScore(maverick);
        setMatchScores({ ...matchScores, [maverickId]: score });
      }
    }
    setSelectedCandidates(newSelected);
  };

  const handleSubmit = async () => {
    if (selectedCandidates.size === 0) {
      toast.error('Please select at least one candidate');
      return;
    }

    setSubmitting(true);
    try {
      const candidates = Array.from(selectedCandidates).map(maverickId => ({
        maverick_id: maverickId,
        match_score: matchScores[maverickId] || 0,
        hr_notes: notes[maverickId] || ''
      }));

      await apiClient.post(`/workflow/requirements/${requirementId}/candidates/bulk`, {
        candidates
      });

      toast.success(`Successfully suggested ${candidates.length} candidate(s)`);
      router.push(`/deployments/${requirementId}/workflow`);
    } catch (error) {
      console.error('Failed to suggest candidates:', error);
      toast.error('Failed to suggest candidates');
    } finally {
      setSubmitting(false);
    }
  };

  const filteredMavericks = mavericks.filter(m => {
    const fullName = `${m.first_name} ${m.last_name}`.toLowerCase();
    const search = searchTerm.toLowerCase();
    return fullName.includes(search) || m.email.toLowerCase().includes(search);
  });

  // Sort by match score
  const sortedMavericks = filteredMavericks.sort((a, b) => {
    const scoreA = calculateMatchScore(a);
    const scoreB = calculateMatchScore(b);
    return scoreB - scoreA;
  });

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
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Suggest Candidates</h1>
            <p className="text-gray-600 mb-4">for {requirement.role_title}</p>

            <div className="flex flex-wrap items-center gap-4 text-sm">
              {requirement.project_name && (
                <div className="flex items-center gap-1 text-gray-600">
                  <Building2 className="w-4 h-4" />
                  {requirement.project_name}
                </div>
              )}
              {requirement.vertical && (
                <div className="flex items-center gap-1 text-gray-600">
                  <Briefcase className="w-4 h-4" />
                  {requirement.vertical}
                </div>
              )}
              <div className="flex items-center gap-1 text-gray-600">
                <Users className="w-4 h-4" />
                {requirement.positions_count} position(s) needed
              </div>
            </div>

            {/* Required Skills */}
            {requirement.required_skills && requirement.required_skills.length > 0 && (
              <div className="mt-4">
                <h3 className="text-xs font-semibold text-gray-700 mb-2">Required Skills</h3>
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

        {/* Search and Selection Summary */}
        <div className="mb-6 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div className="flex-1 mr-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search mavericks by name or email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-sm">
                <span className="font-semibold text-gray-900">{selectedCandidates.size}</span>
                <span className="text-gray-600"> selected</span>
              </div>
              <button
                onClick={handleSubmit}
                disabled={selectedCandidates.size === 0 || submitting}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {submitting ? 'Suggesting...' : `Suggest ${selectedCandidates.size || ''} Candidate(s)`}
              </button>
            </div>
          </div>
        </div>

        {/* Mavericks List */}
        <div className="space-y-4">
          {sortedMavericks.length === 0 ? (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
              <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No mavericks found</p>
            </div>
          ) : (
            sortedMavericks.map((maverick) => {
              const matchScore = calculateMatchScore(maverick);
              const isSelected = selectedCandidates.has(maverick.id);
              const maverickSkills = maverick.skills ? JSON.parse(maverick.skills) : [];

              return (
                <div
                  key={maverick.id}
                  className={`bg-white rounded-lg shadow-sm border-2 p-6 transition-all cursor-pointer ${
                    isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300'
                  }`}
                  onClick={() => toggleCandidate(maverick.id, maverick)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleCandidate(maverick.id, maverick)}
                          className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                          onClick={(e) => e.stopPropagation()}
                        />
                        <h3 className="text-lg font-semibold text-gray-900">
                          {maverick.first_name} {maverick.last_name}
                        </h3>
                        {isSelected && (
                          <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                            Selected
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 ml-8">{maverick.email}</p>

                      {/* Match Score */}
                      <div className="ml-8 mt-3 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-green-600" />
                        <span className={`text-lg font-bold ${
                          matchScore >= 70 ? 'text-green-700' :
                          matchScore >= 50 ? 'text-yellow-700' :
                          'text-red-700'
                        }`}>
                          {matchScore}% Match
                        </span>
                        <div className="flex-1 max-w-xs ml-2">
                          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${
                                matchScore >= 70 ? 'bg-green-500' :
                                matchScore >= 50 ? 'bg-yellow-500' :
                                'bg-red-500'
                              }`}
                              style={{ width: `${matchScore}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Details */}
                  <div className="ml-8 mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Skills */}
                    <div>
                      <h4 className="text-xs font-semibold text-gray-700 mb-2">Skills</h4>
                      <div className="flex flex-wrap gap-1">
                        {maverickSkills.slice(0, 4).map((s: any, idx: number) => (
                          <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                            {s.skill}
                          </span>
                        ))}
                        {maverickSkills.length > 4 && (
                          <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                            +{maverickSkills.length - 4}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Education */}
                    <div>
                      <h4 className="text-xs font-semibold text-gray-700 mb-2">Education</h4>
                      <div className="space-y-1 text-sm text-gray-600">
                        {maverick.degree && <div>{maverick.degree}</div>}
                        {maverick.branch && <div className="text-xs">{maverick.branch}</div>}
                        {maverick.cgpa && (
                          <div className="flex items-center gap-1">
                            <Star className="w-3 h-3 text-yellow-500" />
                            CGPA: {maverick.cgpa}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Training Status */}
                    <div>
                      <h4 className="text-xs font-semibold text-gray-700 mb-2">Status</h4>
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                        maverick.training_status === 'AVAILABLE_FOR_DEPLOYMENT' ? 'bg-green-100 text-green-700' :
                        maverick.training_status === 'IN_TRAINING' ? 'bg-blue-100 text-blue-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {maverick.training_status?.replace(/_/g, ' ')}
                      </span>
                    </div>
                  </div>

                  {/* Notes Input (shown when selected) */}
                  {isSelected && (
                    <div className="ml-8 mt-4 pt-4 border-t border-gray-200">
                      <label className="block text-xs font-semibold text-gray-700 mb-2">
                        HR Notes (Optional)
                      </label>
                      <textarea
                        value={notes[maverick.id] || ''}
                        onChange={(e) => {
                          e.stopPropagation();
                          setNotes({ ...notes, [maverick.id]: e.target.value });
                        }}
                        onClick={(e) => e.stopPropagation()}
                        placeholder="Add notes about why this candidate is a good match..."
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                        rows={2}
                      />
                      <div className="mt-2">
                        <label className="block text-xs font-semibold text-gray-700 mb-1">
                          Match Score
                        </label>
                        <input
                          type="number"
                          min="0"
                          max="100"
                          value={matchScores[maverick.id] || matchScore}
                          onChange={(e) => {
                            e.stopPropagation();
                            setMatchScores({ ...matchScores, [maverick.id]: parseInt(e.target.value) || 0 });
                          }}
                          onClick={(e) => e.stopPropagation()}
                          className="w-24 px-3 py-1 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                        />
                        <span className="ml-2 text-xs text-gray-600">%</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
