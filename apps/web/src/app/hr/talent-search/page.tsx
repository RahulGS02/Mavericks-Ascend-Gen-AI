"use client";

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import DashboardLayout from '@/components/DashboardLayout';
import { Search, Loader2, User, X, Plus } from 'lucide-react';
import { talentSearchAPI, apiClient } from '@/lib/api';
import { toast } from 'sonner';
import Link from 'next/link';

// Types
interface Candidate {
  id: string;
  name: string;
  email: string;
  cgpa: number;
  deployment_status: string;
  profile_status: string;
  final_score: number;
  tier: string;
  exact_matches: Array<{ skill: string; proficiency_score: number }>;
  similar_matches: Array<{ skill: string; proficiency_score: number }>;
  transferable_matches: Array<{ skill: string; proficiency_score: number }>;
  adaptability_score: number;
  deployment_readiness: string;
  learning_weeks_required: number;
}

interface SearchResult {
  query: string;
  parsed_requirements: any;
  total_found: number;
  results: Candidate[];
}

// Requirement interface
interface Requirement {
  id: string;
  role_title: string;
  required_skills: string[];
  preferred_skills: string[];
  project_name?: string;
  status: string;
  positions_count: number;
  filled_count: number;
}

export default function TalentSearchPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState('');
  const [searchResult, setSearchResult] = useState<SearchResult | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<string>('all');

  // Add to Requirement Modal
  const [showRequirementModal, setShowRequirementModal] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [loadingRequirements, setLoadingRequirements] = useState(false);
  const [addingToRequirement, setAddingToRequirement] = useState(false);

  // Auth check
  useEffect(() => {
    if (!isAuthenticated || !user) {
      router.push('/login');
      return;
    }
    if (!['hr', 'manager', 'super_admin'].includes(user.role)) {
      router.push('/dashboard');
      toast.error('Access denied. HR/Manager role required.');
      return;
    }
  }, [isAuthenticated, user, router]);

  // Restore search state from URL params
  useEffect(() => {
    const savedQuery = searchParams?.get('q');
    const savedFilter = searchParams?.get('filter');

    if (savedQuery) {
      setQuery(savedQuery);
      // Automatically re-run search
      handleSearchWithQuery(savedQuery);
    }

    if (savedFilter) {
      setSelectedFilter(savedFilter);
    }
  }, []);

  // Save search state to URL
  const updateURL = (searchQuery: string, filter: string) => {
    const params = new URLSearchParams();
    if (searchQuery) params.set('q', searchQuery);
    if (filter !== 'all') params.set('filter', filter);

    const queryString = params.toString();
    const newURL = queryString ? `?${queryString}` : window.location.pathname;
    window.history.replaceState({}, '', newURL);
  };

  const handleSearchWithQuery = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    try {
      setLoading(true);
      setSelectedFilter('all');
      const response = await talentSearchAPI.search({
        query: searchQuery.trim(),
        max_results: 100,
        include_similar: true,
        urgency: 'flexible',
      });

      setSearchResult(response.data);
      toast.success(`Found ${response.data.total_found} candidates`);

      // Update URL to preserve state
      updateURL(searchQuery.trim(), 'all');
    } catch (error: any) {
      console.error('Search failed:', error);
      toast.error(error.response?.data?.detail || 'Search failed');
      setSearchResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    await handleSearchWithQuery(query);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !loading) {
      handleSearch();
    }
  };

  // Fetch requirements when modal opens
  const handleOpenRequirementModal = async (candidate: Candidate) => {
    setSelectedCandidate(candidate);
    setShowRequirementModal(true);
    setLoadingRequirements(true);

    try {
      const response = await apiClient.get('/deployment-requests', {
        params: { status: 'PENDING,APPROVED', limit: 50 }
      });
      setRequirements(response.data.requirements || response.data || []);
    } catch (error: any) {
      console.error('Failed to fetch requirements:', error);
      toast.error('Failed to load requirements');
      setRequirements([]);
    } finally {
      setLoadingRequirements(false);
    }
  };

  // Add candidate to requirement
  const handleAddToRequirement = async (requirementId: string) => {
    if (!selectedCandidate) return;

    setAddingToRequirement(true);
    try {
      await apiClient.post(`/requirement-workflow/${requirementId}/suggest`, {
        maverick_id: selectedCandidate.id,
        match_score: selectedCandidate.final_score,
        hr_notes: `AI Talent Search: ${selectedCandidate.tier} match with ${selectedCandidate.final_score.toFixed(1)}% score`
      });

      toast.success(`${selectedCandidate.name} added to requirement!`);
      setShowRequirementModal(false);
      setSelectedCandidate(null);
    } catch (error: any) {
      console.error('Failed to add to requirement:', error);
      toast.error(error.response?.data?.detail || 'Failed to add candidate');
    } finally {
      setAddingToRequirement(false);
    }
  };

  // Filter logic - All candidates from backend are AVAILABLE only
  const getFilteredCandidates = () => {
    if (!searchResult) return [];

    const candidates = searchResult.results;

    switch (selectedFilter) {
      case 'exact':
        // Perfect match - ready for immediate deployment
        return candidates.filter(c => c.tier === 'TIER_1_EXACT');
      case 'similar':
        // Has similar skills - needs short training
        return candidates.filter(c => c.tier === 'TIER_2_SIMILAR');
      case 'trainable':
        // Has transferable skills - can be trained
        return candidates.filter(c => c.tier === 'TIER_3_TRANSFERABLE');
      default:
        return candidates;
    }
  };

  const getStatusBadge = (status: string) => {
    const badges: any = {
      AVAILABLE: { label: 'Available', color: 'bg-green-100 text-green-800 border-green-300' },
      IN_TRAINING: { label: 'In Training', color: 'bg-blue-100 text-blue-800 border-blue-300' },
      DEPLOYED: { label: 'Deployed', color: 'bg-gray-100 text-gray-800 border-gray-300' },
    };
    return badges[status] || badges.AVAILABLE;
  };

  const getReadinessLabel = (readiness: string) => {
    const labels: any = {
      immediate: 'Ready Now',
      short_term: '1-4 weeks',
      medium_term: '1-3 months',
      long_term: '3+ months',
    };
    return labels[readiness] || readiness;
  };

  const filteredCandidates = getFilteredCandidates();
  const exactCount = searchResult?.results.filter(c => c.tier === 'TIER_1_EXACT').length || 0;
  const similarCount = searchResult?.results.filter(c => c.tier === 'TIER_2_SIMILAR').length || 0;
  const trainableCount = searchResult?.results.filter(c => c.tier === 'TIER_3_TRANSFERABLE').length || 0;

  if (!user) return null;

  return (
    <DashboardLayout user={user}>
      <div className="p-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">AI Talent Search</h1>
          <p className="text-gray-600">Find candidates with natural language queries</p>
        </div>

        {/* Search Box */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="e.g., Python developer with Django and React, CGPA > 8"
              className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={loading}
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={loading || !query.trim()}
            className="mt-4 w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Searching...
              </>
            ) : (
              <>
                <Search className="w-5 h-5" />
                Search
              </>
            )}
          </button>
        </div>

        {/* Results */}
        {searchResult && (
          <div className="space-y-6">
            {/* Filter Tabs */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setSelectedFilter('all')}
                  className={`px-4 py-2 rounded-lg font-medium transition ${
                    selectedFilter === 'all'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  All Results ({searchResult.total_found})
                </button>
                <button
                  onClick={() => setSelectedFilter('exact')}
                  className={`px-4 py-2 rounded-lg font-medium transition ${
                    selectedFilter === 'exact'
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Ready Now - Exact Match ({exactCount})
                </button>
                <button
                  onClick={() => setSelectedFilter('similar')}
                  className={`px-4 py-2 rounded-lg font-medium transition ${
                    selectedFilter === 'similar'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Short Training - Similar Skills ({similarCount})
                </button>
                <button
                  onClick={() => setSelectedFilter('trainable')}
                  className={`px-4 py-2 rounded-lg font-medium transition ${
                    selectedFilter === 'trainable'
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Can Be Trained ({trainableCount})
                </button>
              </div>
            </div>

            {/* Candidate Cards */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-gray-900">
                {filteredCandidates.length} Candidate{filteredCandidates.length !== 1 ? 's' : ''}
              </h2>

              {filteredCandidates.map((candidate) => {
                const statusBadge = getStatusBadge(candidate.deployment_status);

                // Determine tier badge color
                const getTierBadge = (tier: string) => {
                  const badges: any = {
                    TIER_1_EXACT: { label: 'Exact Match', color: 'bg-green-100 text-green-800 border-green-300' },
                    TIER_2_SIMILAR: { label: 'Similar Skills', color: 'bg-blue-100 text-blue-800 border-blue-300' },
                    TIER_3_TRANSFERABLE: { label: 'Trainable', color: 'bg-purple-100 text-purple-800 border-purple-300' },
                  };
                  return badges[tier] || badges.TIER_1_EXACT;
                };

                const tierBadge = getTierBadge(candidate.tier);

                return (
                  <div
                    key={candidate.id}
                    className="bg-white rounded-lg shadow-sm border-2 hover:shadow-md transition"
                    style={{
                      borderColor: candidate.tier === 'TIER_1_EXACT' ? '#10b981' :
                                   candidate.tier === 'TIER_2_SIMILAR' ? '#3b82f6' : '#a855f7'
                    }}
                  >
                    {/* Header Row */}
                    <div className="flex items-start justify-between p-4 pb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-base font-bold text-gray-900">{candidate.name}</h3>
                          <span className={`px-2 py-0.5 text-xs font-semibold rounded-full border ${tierBadge.color}`}>
                            {tierBadge.label}
                          </span>
                          <span className={`px-2 py-0.5 text-xs font-semibold rounded-full border ${statusBadge.color}`}>
                            {statusBadge.label}
                          </span>
                        </div>
                        <p className="text-xs text-gray-600">{candidate.email}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-xl font-bold text-blue-600">{candidate.final_score.toFixed(1)}</div>
                        <p className="text-xs text-gray-500">Score</p>
                      </div>
                    </div>

                    {/* Skills Section - Compact */}
                    <div className="px-4 pb-2">
                      {/* Exact Match Skills */}
                      {candidate.exact_matches.length > 0 && (
                        <div className="mb-2">
                          <p className="text-xs font-semibold text-green-700 mb-1">Exact ({candidate.exact_matches.length})</p>
                          <div className="flex flex-wrap gap-1.5">
                            {candidate.exact_matches.slice(0, 5).map((match: any, idx: number) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 bg-green-50 text-green-800 text-xs font-medium rounded-md border border-green-200"
                              >
                                {match.skill}
                              </span>
                            ))}
                            {candidate.exact_matches.length > 5 && (
                              <span className="px-2 py-0.5 text-xs text-gray-500">
                                +{candidate.exact_matches.length - 5} more
                              </span>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Similar Skills */}
                      {candidate.similar_matches.length > 0 && (
                        <div className="mb-2">
                          <p className="text-xs font-semibold text-blue-700 mb-1">Similar ({candidate.similar_matches.length})</p>
                          <div className="flex flex-wrap gap-1.5">
                            {candidate.similar_matches.slice(0, 3).map((match: any, idx: number) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 bg-blue-50 text-blue-800 text-xs font-medium rounded-md border border-blue-200"
                              >
                                {match.candidate_has}
                              </span>
                            ))}
                            {candidate.similar_matches.length > 3 && (
                              <span className="px-2 py-0.5 text-xs text-gray-500">
                                +{candidate.similar_matches.length - 3} more
                              </span>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Transferable Skills */}
                      {candidate.transferable_matches.length > 0 && (
                        <div className="mb-2">
                          <p className="text-xs font-semibold text-purple-700 mb-1">Transferable ({candidate.transferable_matches.length})</p>
                          <div className="flex flex-wrap gap-1.5">
                            {candidate.transferable_matches.slice(0, 3).map((match: any, idx: number) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 bg-purple-50 text-purple-800 text-xs font-medium rounded-md border border-purple-200"
                              >
                                {match.candidate_has}
                              </span>
                            ))}
                            {candidate.transferable_matches.length > 3 && (
                              <span className="px-2 py-0.5 text-xs text-gray-500">
                                +{candidate.transferable_matches.length - 3} more
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Details Grid - Compact */}
                    <div className="grid grid-cols-4 gap-2 px-4 py-2 bg-gray-50 border-t border-gray-200">
                      <div>
                        <p className="text-xs text-gray-500">CGPA</p>
                        <p className="text-sm font-semibold text-gray-900">{candidate.cgpa.toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Adaptability</p>
                        <p className="text-sm font-semibold text-gray-900">
                          {candidate.adaptability_score.toFixed(0)}/100
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Ready</p>
                        <p className="text-sm font-semibold text-gray-900">{getReadinessLabel(candidate.deployment_readiness)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Training</p>
                        <p className="text-sm font-semibold text-gray-900">
                          {candidate.learning_weeks_required > 0 ? `${candidate.learning_weeks_required}w` : 'Now'}
                        </p>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex justify-end gap-2 px-4 py-3 border-t border-gray-100">
                      <button
                        onClick={() => handleOpenRequirementModal(candidate)}
                        className="px-3 py-1.5 bg-green-600 text-white text-xs font-medium rounded-lg hover:bg-green-700 transition"
                      >
                        Add to Requirement
                      </button>
                      <Link
                        href={`/hr/mavericks/${candidate.id}`}
                        className="px-3 py-1.5 bg-blue-600 text-white text-xs font-medium rounded-lg hover:bg-blue-700 transition"
                      >
                        View Profile
                      </Link>
                    </div>
                  </div>
                );
              })}

              {filteredCandidates.length === 0 && (
                <div className="bg-gray-50 rounded-lg p-8 text-center">
                  <p className="text-gray-600">No candidates found for this filter</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Add to Requirement Modal */}
        {showRequirementModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
              {/* Modal Header */}
              <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Add to Requirement</h2>
                  {selectedCandidate && (
                    <p className="text-sm text-gray-600 mt-1">
                      Adding: <span className="font-semibold">{selectedCandidate.name}</span>
                    </p>
                  )}
                </div>
                <button
                  onClick={() => {
                    setShowRequirementModal(false);
                    setSelectedCandidate(null);
                  }}
                  className="text-gray-400 hover:text-gray-600 transition"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Modal Content */}
              <div className="flex-1 overflow-y-auto p-6">
                {loadingRequirements ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                    <span className="ml-3 text-gray-600">Loading requirements...</span>
                  </div>
                ) : requirements.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-gray-600 mb-4">No open requirements found</p>
                    <Link
                      href="/deployments/create"
                      className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Create New Requirement
                    </Link>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {requirements.map((requirement) => (
                      <div
                        key={requirement.id}
                        className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-sm transition cursor-pointer"
                        onClick={() => handleAddToRequirement(requirement.id)}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900 mb-1">
                              {requirement.role_title}
                            </h3>
                            {requirement.project_name && (
                              <p className="text-sm text-gray-600">
                                Project: {requirement.project_name}
                              </p>
                            )}
                          </div>
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                            requirement.status === 'PENDING'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-green-100 text-green-800'
                          }`}>
                            {requirement.status}
                          </span>
                        </div>

                        <div className="flex items-center gap-4 text-sm text-gray-600 mb-2">
                          <span>Positions: {requirement.filled_count}/{requirement.positions_count}</span>
                        </div>

                        {requirement.required_skills && requirement.required_skills.length > 0 && (
                          <div className="flex flex-wrap gap-1.5 mt-2">
                            {requirement.required_skills.slice(0, 5).map((skill, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded-md"
                              >
                                {skill}
                              </span>
                            ))}
                            {requirement.required_skills.length > 5 && (
                              <span className="px-2 py-0.5 text-xs text-gray-500">
                                +{requirement.required_skills.length - 5} more
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Modal Footer */}
              <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
                <Link
                  href="/deployments/create"
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Create New Requirement
                </Link>
                <button
                  onClick={() => {
                    setShowRequirementModal(false);
                    setSelectedCandidate(null);
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
