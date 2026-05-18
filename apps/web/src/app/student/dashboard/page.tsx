"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { 
  BookOpen, Clock, Award, Calendar, TrendingUp, CheckCircle, 
  SkipForward, AlertCircle, Users, GraduationCap
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';
import { useAuthStore } from '@/store/authStore';

interface DashboardData {
  welcome: {
    student_name: string;
    message: string;
    has_batch: boolean;
    batch?: {
      batch_name: string;
      pipeline_name: string;
      trainer_name: string;
      start_date: string;
      end_date: string;
      enrolled_count: number;
    };
  };
  progress: {
    overall_completion: number;
    completed_jobs: number;
    total_jobs: number;
    pipeline_name: string;
    steps: any[];
  };
  current_job: any;
  assessments: {
    average_score: number;
    total_taken: number;
    passed_count: number;
    scores: any[];
  };
  skills: any[];
  upcoming_sessions: any[];
}

export default function StudentDashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [skipping, setSkipping] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (user?.role !== 'maverick') {
      router.push('/dashboard');
      return;
    }

    fetchDashboardData();
  }, [isAuthenticated, user, router]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/maverick/dashboard/overview');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      toast.error('Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleSkipJob = async (jobId: string) => {
    if (!confirm('Are you sure you want to skip this optional job?')) {
      return;
    }

    try {
      setSkipping(true);
      await apiClient.post(`/maverick/dashboard/skip-job/${jobId}`);
      toast.success('Job skipped successfully!');
      fetchDashboardData(); // Refresh
    } catch (error: any) {
      console.error('Failed to skip job:', error);
      toast.error(error.response?.data?.detail || 'Failed to skip job');
    } finally {
      setSkipping(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-gray-500">Loading your dashboard...</div>
        </div>
      </DashboardLayout>
    );
  }

  if (!dashboardData || !dashboardData.welcome.has_batch) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
            <AlertCircle className="w-12 h-12 text-yellow-600 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No Batch Assigned</h2>
            <p className="text-gray-600">
              {dashboardData?.welcome.message || "You are not assigned to any batch yet. Please contact HR."}
            </p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const { welcome, progress, current_job, assessments, skills, upcoming_sessions } = dashboardData;

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        {/* Welcome Banner */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <h1 className="text-3xl font-bold mb-2">{welcome.student_name}</h1>
              <p className="text-blue-100 mt-1 mb-4">{welcome.message}</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <GraduationCap className="w-5 h-5" />
                  <div>
                    <div className="text-blue-100 text-xs">Batch</div>
                    <div className="font-semibold">{welcome.batch?.batch_name}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <BookOpen className="w-5 h-5" />
                  <div>
                    <div className="text-blue-100 text-xs">Pipeline</div>
                    <div className="font-semibold">{welcome.batch?.pipeline_name}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  <div>
                    <div className="text-blue-100 text-xs">Trainer</div>
                    <div className="font-semibold">{welcome.batch?.trainer_name}</div>
                  </div>
                </div>
              </div>
            </div>
            <div className="text-right ml-6">
              <div className="text-5xl font-bold mb-1">{progress.overall_completion}%</div>
              <div className="text-blue-100 text-sm">Overall Progress</div>
              <div className="mt-4 text-sm">
                <div className="text-blue-100">{progress.completed_jobs} of {progress.total_jobs} jobs completed</div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Completion</p>
                <p className="text-2xl font-bold text-blue-600">{progress.overall_completion}%</p>
              </div>
              <TrendingUp className="w-10 h-10 text-blue-600 opacity-20" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Jobs Completed</p>
                <p className="text-2xl font-bold text-green-600">{progress.completed_jobs}/{progress.total_jobs}</p>
              </div>
              <CheckCircle className="w-10 h-10 text-green-600 opacity-20" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Average Score</p>
                <p className="text-2xl font-bold text-yellow-600">{assessments.average_score}%</p>
              </div>
              <Award className="w-10 h-10 text-yellow-600 opacity-20" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Assessments Passed</p>
                <p className="text-2xl font-bold text-purple-600">{assessments.passed_count}/{assessments.total_taken}</p>
              </div>
              <Award className="w-10 h-10 text-purple-600 opacity-20" />
            </div>
          </div>
        </div>

        {/* Pipeline Progress Stepper */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-blue-600" />
            Learning Path Progress
          </h2>

          <div className="relative">
            {progress.steps.map((step, index) => (
              <div key={step.job_id} className="flex items-start gap-4 mb-6 last:mb-0">
                {/* Step Indicator */}
                <div className="flex flex-col items-center">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                    step.status === 'COMPLETED' ? 'bg-green-500 text-white' :
                    step.status === 'IN_PROGRESS' ? 'bg-blue-500 text-white' :
                    step.status === 'SKIPPED' ? 'bg-gray-400 text-white' :
                    'bg-gray-200 text-gray-600'
                  }`}>
                    {step.status === 'COMPLETED' ? <CheckCircle className="w-6 h-6" /> : step.order}
                  </div>
                  {index < progress.steps.length - 1 && (
                    <div className={`w-1 h-12 ${
                      step.status === 'COMPLETED' ? 'bg-green-300' : 'bg-gray-200'
                    }`} />
                  )}
                </div>

                {/* Step Content */}
                <div className={`flex-1 pb-4 ${step.is_current ? 'ring-2 ring-blue-500 rounded-lg p-4 bg-blue-50' : ''}`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900">{step.title}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          step.type === 'TRAINING' ? 'bg-blue-100 text-blue-700' :
                          step.type === 'ASSESSMENT' ? 'bg-purple-100 text-purple-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {step.type}
                        </span>
                        {step.is_optional && (
                          <span className="text-xs px-2 py-1 rounded-full bg-yellow-100 text-yellow-700">
                            Optional
                          </span>
                        )}
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          step.status === 'COMPLETED' ? 'bg-green-100 text-green-700' :
                          step.status === 'IN_PROGRESS' ? 'bg-blue-100 text-blue-700' :
                          step.status === 'SKIPPED' ? 'bg-gray-100 text-gray-600' :
                          'bg-gray-100 text-gray-600'
                        }`}>
                          {step.status}
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-gray-900">{step.completion_percentage}%</div>
                      {step.score && (
                        <div className="text-sm text-gray-600">Score: {step.score}%</div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Current Job Card */}
          {current_job && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Clock className="w-6 h-6 text-orange-600" />
                Current Job
              </h2>

              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-4">
                <h3 className="text-lg font-bold text-gray-900 mb-2">{current_job.title}</h3>
                <p className="text-gray-700 mb-3">{current_job.description}</p>

                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-gray-600">Type:</span>
                    <span className="ml-2 font-semibold">{current_job.type}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Duration:</span>
                    <span className="ml-2 font-semibold">{current_job.duration_hours}h</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Status:</span>
                    <span className="ml-2 font-semibold">{current_job.status}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Progress:</span>
                    <span className="ml-2 font-semibold">{current_job.completion_percentage}%</span>
                  </div>
                </div>
              </div>

              {current_job.can_skip && (
                <button
                  onClick={() => handleSkipJob(current_job.job_id)}
                  disabled={skipping}
                  className="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <SkipForward className="w-5 h-5" />
                  {skipping ? 'Skipping...' : 'Skip This Optional Job'}
                </button>
              )}
            </div>
          )}

          {/* Assessment Scores */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Award className="w-6 h-6 text-yellow-600" />
              Assessment Scores
            </h2>

            <div className="mb-4 grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">{assessments.average_score}%</div>
                <div className="text-sm text-gray-600">Average</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">{assessments.passed_count}</div>
                <div className="text-sm text-gray-600">Passed</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-600">{assessments.total_taken}</div>
                <div className="text-sm text-gray-600">Total</div>
              </div>
            </div>

            <div className="space-y-2">
              {assessments.scores.map((score, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900">{score.assessment_title}</div>
                    <div className="text-xs text-gray-600">Attempt #{score.attempt_number}</div>
                  </div>
                  <div className="text-right">
                    <div className={`text-lg font-bold ${score.passed ? 'text-green-600' : 'text-red-600'}`}>
                      {score.score_percentage}%
                    </div>
                    <div className="text-xs text-gray-600">{score.marks}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Upcoming Training Sessions */}
        {upcoming_sessions.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Calendar className="w-6 h-6 text-green-600" />
              Upcoming Training Sessions
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {upcoming_sessions.map((session) => (
                <div key={session.id} className="border border-gray-200 rounded-lg p-4 hover:border-blue-400 transition-colors">
                  <h3 className="font-semibold text-gray-900 mb-2">{session.title}</h3>
                  <div className="space-y-1 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      <span>{new Date(session.session_date).toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      <span>{session.duration_hours}h • {session.mode}</span>
                    </div>
                    {session.location && (
                      <div className="text-xs text-gray-500">{session.location}</div>
                    )}
                  </div>
                  {session.attendance_required && (
                    <div className="mt-2 text-xs px-2 py-1 bg-red-100 text-red-700 rounded inline-block">
                      Attendance Required
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
