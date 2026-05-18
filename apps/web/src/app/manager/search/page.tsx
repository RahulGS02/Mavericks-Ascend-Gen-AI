"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Search,
  Filter,
  Award,
  TrendingUp,
  MapPin,
  Calendar,
  Star,
  GraduationCap,
  Mail,
  Target,
  Briefcase,
  ChevronDown,
  ChevronUp,
  Sparkles,
  ArrowRight,
  Building2
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import { useAuthStore } from '@/store/authStore';
import DashboardLayout from '@/components/DashboardLayout';

interface SearchResult {
  id: string;
  name: string;
  email: string;
  college: string;
  degree: string;
  branch: string;
  graduation_year: number;
  cgpa: number;

  // Training Status (NEW!)
  training_status: string;
  training_status_label: string;
  training_progress: number;
  current_batch_name: string | null;
  is_available_for_deployment: boolean;

  // Skills
  skills: Array<{
    name: string;
    proficiency: string;
    score: number;
    category: string;
  }>;
  total_skills: number;

  // Matching
  match_score: number;
  match_details: {
    required_matches: number;
    required_total: number;
    preferred_matches: number;
    preferred_total: number;
  };

  // Performance
  average_assessment_score: number;

  // Additional
  ai_summary: string;
  github_url: string;
  linkedin_url: string;
}

export default function ManagerTalentSearch() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [totalResults, setTotalResults] = useState(0);

  // Search & Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [requiredSkills, setRequiredSkills] = useState('');
  const [preferredSkills, setPreferredSkills] = useState('');
  const [trainingStatus, setTrainingStatus] = useState('AVAILABLE');
  const [minCGPA, setMinCGPA] = useState<number | null>(null);
  const [degree, setDegree] = useState('');
  const [branch, setBranch] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'manager') {
      router.push('/login');
      return;
    }
  }, [isAuthenticated, user]);

  const handleSearch = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();

      if (searchQuery) params.append('search_query', searchQuery);
      if (requiredSkills) params.append('required_skills', requiredSkills);
      if (preferredSkills) params.append('preferred_skills', preferredSkills);
      if (trainingStatus) params.append('training_status', trainingStatus);
      if (minCGPA) params.append('min_cgpa', minCGPA.toString());
      if (degree) params.append('degree', degree);
      if (branch) params.append('branch', branch);

      const response = await apiClient.get(`/manager/search/talent?${params.toString()}`);
      setResults(response.data.results || []);
      setTotalResults(response.data.total || 0);
      toast.success(`Found ${response.data.total || 0} candidate${response.data.total !== 1 ? 's' : ''}`);
    } catch (error) {
      console.error('Search failed:', error);
      toast.error('Search failed');
      setResults([]);
      setTotalResults(0);
    } finally {
      setLoading(false);
    }
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setRequiredSkills('');
    setPreferredSkills('');
    setTrainingStatus('AVAILABLE');
    setMinCGPA(null);
    setDegree('');
    setBranch('');
    setResults([]);
    setTotalResults(0);
  };

  const getTrainingStatusColor = (status: string) => {
    switch (status) {
      case 'NOT_STARTED': return 'bg-gray-100 text-gray-800 border-gray-300';
      case 'IN_TRAINING': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'TRAINING_COMPLETED': return 'bg-green-100 text-green-800 border-green-300';
      case 'AVAILABLE': return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'DEPLOYED': return 'bg-purple-100 text-purple-800 border-purple-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const handleRequestDeployment = (maverickId: string) => {
    // Navigate to create deployment request with pre-selected maverick
    router.push(`/deployments/requests?maverick_id=${maverickId}`);
  };

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Talent Search</h1>
          <p className="text-gray-600 mt-2">
            Find the perfect candidate for your project using AI-powered matching
          </p>
        </div>

        {/* Search Bar */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex gap-4 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name, college, email, or skills..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button
              onClick={handleSearch}
              disabled={loading}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium transition-colors"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                  Searching...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  Search
                </>
              )}
            </button>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`px-6 py-3 border-2 rounded-lg flex items-center gap-2 font-medium transition-all ${
                showFilters
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-300 hover:bg-gray-50 text-gray-700'
              }`}
            >
              <Filter className="w-5 h-5" />
              Filters
              {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="pt-4 border-t border-gray-200 animate-in fade-in duration-200">
              <h3 className="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Filter className="w-4 h-4" />
                Advanced Filters
              </h3>

              {/* Skills Section */}
              <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h4 className="text-sm font-semibold text-blue-900 mb-3">Skill Matching</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                      <Target className="w-4 h-4 text-red-600" />
                      Required Skills (Must-Have) <span className="text-red-600">*</span>
                    </label>
                    <input
                      type="text"
                      placeholder="e.g., React, Node.js, PostgreSQL"
                      value={requiredSkills}
                      onChange={(e) => setRequiredSkills(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="text-xs text-gray-600 mt-1">70% weight in match score</p>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                      <Star className="w-4 h-4 text-yellow-600" />
                      Preferred Skills (Nice-to-Have)
                    </label>
                    <input
                      type="text"
                      placeholder="e.g., AWS, Docker, TypeScript"
                      value={preferredSkills}
                      onChange={(e) => setPreferredSkills(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="text-xs text-gray-600 mt-1">30% weight in match score</p>
                  </div>
                </div>
              </div>

              {/* Training Status */}
              <div className="mb-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                  <GraduationCap className="w-4 h-4 text-blue-600" />
                  Training Status
                </label>
                <select
                  value={trainingStatus}
                  onChange={(e) => setTrainingStatus(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="ALL">All Mavericks</option>
                  <option value="NOT_STARTED">Not Started Training</option>
                  <option value="IN_TRAINING">In Training</option>
                  <option value="TRAINING_COMPLETED">Training Completed</option>
                  <option value="AVAILABLE">Available for Deployment</option>
                  <option value="DEPLOYED">Currently Deployed</option>
                </select>
              </div>

              {/* Education Filters */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                    <Star className="w-4 h-4 text-orange-600" />
                    Min. CGPA
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="10"
                    step="0.1"
                    placeholder="e.g., 7.5"
                    value={minCGPA || ''}
                    onChange={(e) => setMinCGPA(e.target.value ? Number(e.target.value) : null)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                    <Award className="w-4 h-4 text-indigo-600" />
                    Degree
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., BTech, BCA"
                    value={degree}
                    onChange={(e) => setDegree(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-pink-600" />
                    Branch
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., CSE, IT"
                    value={branch}
                    onChange={(e) => setBranch(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Clear Filters Button */}
              <div className="mt-4 flex justify-end">
                <button
                  onClick={handleClearFilters}
                  className="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors font-medium"
                >
                  Clear All Filters
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Results */}
        {loading ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent mb-4"></div>
            <p className="text-gray-600 font-medium">Searching for candidates...</p>
            <p className="text-sm text-gray-500 mt-2">This may take a few seconds</p>
          </div>
        ) : results.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <Search className="w-20 h-20 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No candidates found</h3>
            <p className="text-gray-500 mb-4">Try adjusting your search criteria or use different filters</p>
            <button
              onClick={() => {
                setSearchQuery('');
                setSkillsFilter('');
                setStatusFilter('AVAILABLE');
                setMinScore(null);
              }}
              className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
            >
              Clear All Filters
            </button>
          </div>
        ) : (
          <div>
            {/* Results Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  Search Results
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  Found <span className="font-semibold text-blue-600">{totalResults}</span> candidate{totalResults !== 1 ? 's' : ''}
                  {(requiredSkills || preferredSkills) && <span className="ml-1">matching your skills criteria</span>}
                </p>
              </div>
              {(requiredSkills || preferredSkills) && (
                <div className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                  <Sparkles className="w-5 h-5 text-purple-600" />
                  <span className="text-sm font-medium text-purple-900">Intelligent Match Scoring Active</span>
                </div>
              )}
            </div>

            {/* Results Grid */}
            <div className="space-y-6">

              {results.map((candidate) => (
                <div
                  key={candidate.id}
                  className="bg-white rounded-lg shadow-sm border-2 border-gray-200 p-6 hover:shadow-lg hover:border-blue-400 transition-all"
                >
                  {/* Match Score Badge & Training Status */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex flex-wrap gap-2">
                      {/* Match Score Badge */}
                      {(requiredSkills || preferredSkills) && candidate.match_score !== undefined && (
                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full shadow-md">
                          <TrendingUp className="w-5 h-5 text-white" />
                          <span className="text-sm font-bold text-white">
                            {candidate.match_score}% Match
                          </span>
                        </div>
                      )}

                      {/* Training Status Badge */}
                      <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border font-semibold text-sm ${getTrainingStatusColor(candidate.training_status)}`}>
                        <span>{candidate.training_status_label}</span>
                      </div>
                    </div>

                    {/* Available Badge */}
                    {candidate.is_available_for_deployment && (
                      <div className="px-3 py-1 bg-green-100 text-green-800 border border-green-300 rounded-full text-xs font-bold">
                        READY TO DEPLOY
                      </div>
                    )}
                  </div>

                  {/* Training Progress Bar (if in training) */}
                  {candidate.training_status === 'IN_TRAINING' && candidate.training_progress > 0 && (
                    <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-semibold text-blue-900">Training Progress</span>
                        <span className="text-sm font-bold text-blue-700">{Math.round(candidate.training_progress)}%</span>
                      </div>
                      <div className="w-full bg-blue-200 rounded-full h-2.5">
                        <div
                          className="bg-gradient-to-r from-blue-500 to-purple-500 h-2.5 rounded-full transition-all duration-500"
                          style={{ width: `${candidate.training_progress}%` }}
                        ></div>
                      </div>
                      {candidate.current_batch_name && (
                        <p className="text-xs text-blue-700 mt-2">
                          Batch: {candidate.current_batch_name}
                        </p>
                      )}
                    </div>
                  )}

                  {/* Match Details (if skills search) */}
                  {(requiredSkills || preferredSkills) && candidate.match_details && (
                    <div className="mb-4 p-3 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                      <h4 className="text-sm font-semibold text-purple-900 mb-2 flex items-center gap-2">
                        <Target className="w-4 h-4" />
                        Skill Match Breakdown
                      </h4>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        {candidate.match_details.required_total > 0 && (
                          <div className="flex items-center gap-2">
                            <span className="text-red-600 font-semibold">Required:</span>
                            <span className="text-gray-900">
                              {candidate.match_details.required_matches}/{candidate.match_details.required_total}
                            </span>
                            <span className="text-xs text-gray-600">
                              ({Math.round((candidate.match_details.required_matches / candidate.match_details.required_total) * 100)}%)
                            </span>
                          </div>
                        )}
                        {candidate.match_details.preferred_total > 0 && (
                          <div className="flex items-center gap-2">
                            <span className="text-yellow-600 font-semibold">Preferred:</span>
                            <span className="text-gray-900">
                              {candidate.match_details.preferred_matches}/{candidate.match_details.preferred_total}
                            </span>
                            <span className="text-xs text-gray-600">
                              ({Math.round((candidate.match_details.preferred_matches / candidate.match_details.preferred_total) * 100)}%)
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start gap-4">
                      {/* Avatar */}
                      <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-2xl flex-shrink-0">
                        {candidate.name.charAt(0)}
                      </div>
                      {/* Name & Email */}
                      <div>
                        <h3 className="text-xl font-bold text-gray-900 mb-1">{candidate.name}</h3>
                        <p className="text-sm text-gray-600 flex items-center gap-1">
                          <Mail className="w-4 h-4" />
                          {candidate.email}
                        </p>
                      </div>
                    </div>
                    <span
                      className={`px-3 py-1 text-sm font-semibold rounded-full ${
                        candidate.deployment_status === 'AVAILABLE'
                          ? 'bg-green-100 text-green-800 border border-green-300'
                          : candidate.deployment_status === 'DEPLOYED'
                          ? 'bg-blue-100 text-blue-800 border border-blue-300'
                          : 'bg-gray-100 text-gray-800 border border-gray-300'
                      }`}
                    >
                      {candidate.deployment_status}
                    </span>
                  </div>

                  {/* Education Info */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4 p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-2 text-sm text-gray-700">
                      <div className="p-2 bg-white rounded-lg">
                        <GraduationCap className="w-4 h-4 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-medium">{candidate.degree}</p>
                        <p className="text-xs text-gray-500">{candidate.branch}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-700">
                      <div className="p-2 bg-white rounded-lg">
                        <MapPin className="w-4 h-4 text-green-600" />
                      </div>
                      <div>
                        <p className="font-medium">{candidate.college}</p>
                        <p className="text-xs text-gray-500">Institution</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-700">
                      <div className="p-2 bg-white rounded-lg">
                        <Calendar className="w-4 h-4 text-purple-600" />
                      </div>
                      <div>
                        <p className="font-medium">{candidate.graduation_year}</p>
                        <p className="text-xs text-gray-500">Graduation Year</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-700">
                      <div className="p-2 bg-white rounded-lg">
                        <Star className="w-4 h-4 text-yellow-600" />
                      </div>
                      <div>
                        <p className="font-medium">CGPA: {candidate.cgpa?.toFixed(2) || 'N/A'}</p>
                        <p className="text-xs text-gray-500">Avg Score: {candidate.average_assessment_score?.toFixed(1) || 0}%</p>
                      </div>
                    </div>
                  </div>

                  {/* Skills */}
                  {candidate.skills && candidate.skills.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <Target className="w-4 h-4 text-blue-600" />
                        Technical Skills
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {candidate.skills.slice(0, 10).map((skill, idx) => (
                          <div
                            key={idx}
                            className="px-3 py-2 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 text-blue-700 rounded-lg text-sm font-medium hover:shadow-sm transition-shadow"
                          >
                            {skill.name}
                            <span className="ml-1.5 px-1.5 py-0.5 bg-blue-100 text-blue-600 text-xs rounded">
                              {skill.proficiency}
                            </span>
                          </div>
                        ))}
                        {candidate.skills.length > 10 && (
                          <div className="px-3 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm font-medium">
                            +{candidate.skills.length - 10} more skills
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* AI Summary */}
                  {candidate.ai_summary && (
                    <div className="mb-4 p-4 bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg">
                      <div className="flex items-start gap-2">
                        <Sparkles className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
                        <div>
                          <h4 className="text-sm font-semibold text-purple-900 mb-1">AI Profile Summary</h4>
                          <p className="text-sm text-gray-700 leading-relaxed">{candidate.ai_summary}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-3 pt-4 border-t border-gray-200">
                    <button
                      onClick={() => router.push(`/mavericks/${candidate.id}`)}
                      className="flex-1 px-4 py-2.5 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-all font-medium flex items-center justify-center gap-2"
                    >
                      View Full Profile
                      <ArrowRight className="w-4 h-4" />
                    </button>
                    {candidate.deployment_status === 'AVAILABLE' && (
                      <button
                        onClick={() => handleRequestDeployment(candidate.id)}
                        className="flex-1 px-4 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all font-medium shadow-sm hover:shadow-md flex items-center justify-center gap-2"
                      >
                        <Briefcase className="w-4 h-4" />
                        Request Deployment
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
