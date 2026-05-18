"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Calendar, Clock, CheckCircle, PlayCircle, XCircle, GraduationCap, FileText, Rocket, Plus, Copy, ExternalLink, Users, Bell, Download, Edit, Check, ClipboardList, Info, Lock } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import ScheduleJobModal from './ScheduleJobModal';
import AttendanceModal from './AttendanceModal';
import EditScheduleModal from './EditScheduleModal';

interface BatchTimelineTabProps {
  batchId: string;
  batch: any;
  pipeline: any;
}

interface JobSchedule {
  id: string;
  batch_id: string;
  pipeline_job_id: string;
  job_name: string;
  job_type: string;
  job_sequence_order: number;
  job_is_mandatory: boolean;
  job_duration_days: number | null;
  scheduled_start_date: string | null;
  scheduled_end_date: string | null;
  actual_start_date: string | null;
  actual_end_date: string | null;
  meeting_link: string | null;
  attendance_required: boolean;
  attendance_count: number;
  assessment_id: string | null;
  status: string;
  completion_percentage: number;
  is_overdue: boolean;
  trainer_notes: string | null;
  is_published: boolean;
  created_at: string;
}

interface UnscheduledJob {
  id: string;
  name: string;
  job_type: string;
  sequence_order: number;
  is_mandatory: boolean;
  duration_days: number | null;
  description: string | null;
}

interface TimelineData {
  batch_id: string;
  batch_name: string;
  pipeline_id: string;
  pipeline_name: string;
  total_jobs: number;
  scheduled_jobs: number;
  completed_jobs: number;
  in_progress_jobs: number;
  overdue_jobs: number;
  schedules: JobSchedule[];
  unscheduled_jobs: UnscheduledJob[];
}

// Deployment Readiness Display Component
function DeploymentReadinessDisplay({ batchId }: { batchId: string }) {
  const [readiness, setReadiness] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReadiness();
  }, [batchId]);

  const fetchReadiness = async () => {
    try {
      const response = await apiClient.get(`/deployments/batch/${batchId}/readiness`);
      setReadiness(response.data);
    } catch (error) {
      console.error('Failed to fetch deployment readiness:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="mt-3 p-3 bg-purple-50 border border-purple-200 rounded-md">
        <p className="text-sm text-purple-700">Loading deployment readiness...</p>
      </div>
    );
  }

  if (!readiness) return null;

  return (
    <div className="mt-3 p-4 bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-purple-300 rounded-lg">
      <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
        <Rocket className="w-4 h-4 text-purple-600" />
        Deployment Readiness
      </h4>
      <div className="grid grid-cols-3 gap-3">
        {/* Ready Count */}
        <div className="bg-white rounded-md p-3 border border-green-200">
          <div className="flex items-center gap-2 mb-1">
            <CheckCircle className="w-4 h-4 text-green-600" />
            <span className="text-xs text-gray-600">Ready</span>
          </div>
          <div className="text-2xl font-bold text-green-600">
            {readiness.deployment_ready_count}
          </div>
        </div>

        {/* Not Ready Count */}
        <div className="bg-white rounded-md p-3 border border-orange-200">
          <div className="flex items-center gap-2 mb-1">
            <XCircle className="w-4 h-4 text-orange-600" />
            <span className="text-xs text-gray-600">Not Ready</span>
          </div>
          <div className="text-2xl font-bold text-orange-600">
            {readiness.not_ready_count}
          </div>
        </div>

        {/* Deployed Count */}
        <div className="bg-white rounded-md p-3 border border-blue-200">
          <div className="flex items-center gap-2 mb-1">
            <GraduationCap className="w-4 h-4 text-blue-600" />
            <span className="text-xs text-gray-600">Deployed</span>
          </div>
          <div className="text-2xl font-bold text-blue-600">
            {readiness.deployed_count}
          </div>
        </div>
      </div>

      <div className="mt-3 text-xs text-gray-600 flex items-start gap-2">
        <Info className="w-3 h-3 mt-0.5 flex-shrink-0" />
        <p>
          Students are deployment-ready when they've attended all training sessions and passed all assessments.
        </p>
      </div>
    </div>
  );
}

export default function BatchTimelineTab({ batchId, batch, pipeline }: BatchTimelineTabProps) {
  const router = useRouter();
  const [timeline, setTimeline] = useState<TimelineData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState<UnscheduledJob | null>(null);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [showAttendanceModal, setShowAttendanceModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedSchedule, setSelectedSchedule] = useState<JobSchedule | null>(null);
  const [completingJob, setCompletingJob] = useState<string | null>(null);

  useEffect(() => {
    fetchTimeline();
  }, [batchId]);

  const fetchTimeline = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get(`/batches/${batchId}/timeline`);
      setTimeline(response.data);
    } catch (error) {
      console.error('Failed to fetch timeline:', error);
      toast.error('Failed to load batch timeline');
    } finally {
      setLoading(false);
    }
  };

  const handleScheduleClick = (job: UnscheduledJob) => {
    setSelectedJob(job);
    setShowScheduleModal(true);
  };

  const handleScheduleSuccess = () => {
    setShowScheduleModal(false);
    setSelectedJob(null);
    fetchTimeline(); // Refresh timeline
    toast.success('Job scheduled successfully!');
  };

  const handleCopyMeetingLink = (link: string, jobName: string) => {
    navigator.clipboard.writeText(link);
    toast.success(`Meeting link copied for ${jobName}!`);
  };

  const handleAttendanceClick = (schedule: JobSchedule) => {
    setSelectedSchedule(schedule);
    setShowAttendanceModal(true);
  };

  const handleAttendanceUpdate = () => {
    setShowAttendanceModal(false);
    setSelectedSchedule(null);
    fetchTimeline(); // Refresh to update attendance count
  };

  const handleEditClick = (schedule: JobSchedule) => {
    setSelectedSchedule(schedule);
    setShowEditModal(true);
  };

  const handleEditSuccess = () => {
    setShowEditModal(false);
    setSelectedSchedule(null);
    fetchTimeline();
    toast.success('Schedule updated successfully!');
  };

  const handleMarkComplete = async (schedule: JobSchedule) => {
    if (!confirm(`Are you sure you want to mark "${schedule.job_name}" as completed?`)) {
      return;
    }

    setCompletingJob(schedule.id);
    try {
      await apiClient.put(`/batches/${batchId}/schedule/${schedule.id}`, {
        status: 'COMPLETED',
        completion_percentage: 100,
        actual_end_date: new Date().toISOString(),
      });

      toast.success(`${schedule.job_name} marked as completed!`);
      fetchTimeline();
    } catch (error: any) {
      console.error('Failed to mark job as complete:', error);
      toast.error(error.response?.data?.detail || 'Failed to mark job as complete');
    } finally {
      setCompletingJob(null);
    }
  };

  const getDeadlineWarning = (endDate: string | null) => {
    if (!endDate) return null;

    const now = new Date();
    const deadline = new Date(endDate);
    const diffTime = deadline.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays < 0) {
      return { type: 'overdue', message: `${Math.abs(diffDays)} days overdue`, color: 'text-red-600' };
    } else if (diffDays === 0) {
      return { type: 'today', message: 'Due today!', color: 'text-orange-600' };
    } else if (diffDays === 1) {
      return { type: 'tomorrow', message: 'Due tomorrow', color: 'text-orange-500' };
    } else if (diffDays <= 3) {
      return { type: 'soon', message: `${diffDays} days left`, color: 'text-yellow-600' };
    } else if (diffDays <= 7) {
      return { type: 'upcoming', message: `${diffDays} days left`, color: 'text-blue-600' };
    }
    return null;
  };

  const canScheduleJob = (job: UnscheduledJob) => {
    // Allow scheduling any job at any time - no restrictions
    return true;
  };

  const getPrerequisiteMessage = (job: UnscheduledJob) => {
    if (!timeline) return null;

    const incompletePrevious = timeline.schedules.filter(
      s => s.job_sequence_order < job.sequence_order &&
           s.job_is_mandatory &&
           s.status !== 'COMPLETED'
    );

    if (incompletePrevious.length > 0) {
      return `Complete "${incompletePrevious[0].job_name}" first`;
    }
    return null;
  };

  const handleExportTimeline = async () => {
    try {
      toast.info('Exporting timeline...');

      // Create CSV content
      let csv = 'Job Name,Type,Status,Start Date,End Date,Progress,Mandatory,Meeting Link\n';

      timeline?.schedules.forEach(schedule => {
        csv += `"${schedule.job_name}",${schedule.job_type},${schedule.status},`;
        csv += `${schedule.scheduled_start_date || 'N/A'},${schedule.scheduled_end_date || 'N/A'},`;
        csv += `${schedule.completion_percentage}%,${schedule.job_is_mandatory ? 'Yes' : 'No'},`;
        csv += `${schedule.meeting_link || 'N/A'}\n`;
      });

      timeline?.unscheduled_jobs.forEach(job => {
        csv += `"${job.name}",${job.job_type},NOT_SCHEDULED,N/A,N/A,0%,`;
        csv += `${job.is_mandatory ? 'Yes' : 'No'},N/A\n`;
      });

      // Download CSV
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${timeline?.batch_name}_timeline_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);

      toast.success('Timeline exported successfully!');
    } catch (error) {
      console.error('Export failed:', error);
      toast.error('Failed to export timeline');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'IN_PROGRESS':
        return <PlayCircle className="w-5 h-5 text-blue-600" />;
      case 'OVERDUE':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      case 'CANCELLED':
        return <XCircle className="w-5 h-5 text-gray-600" />;
      default:
        return <Clock className="w-5 h-5 text-yellow-600" />;
    }
  };

  const getJobTypeIcon = (type: string) => {
    switch (type) {
      case 'TRAINING':
        return <GraduationCap className="w-5 h-5 text-purple-600" />;
      case 'ASSESSMENT':
        return <FileText className="w-5 h-5 text-blue-600" />;
      case 'DEPLOYMENT':
        return <Rocket className="w-5 h-5 text-green-600" />;
      default:
        return <Clock className="w-5 h-5 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string, isOverdue: boolean) => {
    if (isOverdue) return 'border-red-300 bg-red-50';
    switch (status) {
      case 'COMPLETED':
        return 'border-green-300 bg-green-50';
      case 'IN_PROGRESS':
        return 'border-blue-300 bg-blue-50';
      case 'SCHEDULED':
        return 'border-yellow-300 bg-yellow-50';
      default:
        return 'border-gray-300 bg-white';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-500">Loading timeline...</div>
      </div>
    );
  }

  if (!timeline) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
        <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No Timeline Data</h3>
        <p className="text-gray-600">Unable to load timeline information</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Export */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Batch Timeline</h2>
          <p className="text-sm text-gray-600">Manage and track all pipeline jobs for this batch</p>
        </div>
        <button
          onClick={handleExportTimeline}
          className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors"
        >
          <Download className="w-4 h-4 mr-2" />
          Export Timeline
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="text-xs text-gray-600 mb-1">Total Jobs</div>
          <div className="text-2xl font-bold text-gray-900">{timeline.total_jobs}</div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="text-xs text-gray-600 mb-1">Scheduled</div>
          <div className="text-2xl font-bold text-yellow-600">{timeline.scheduled_jobs}</div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="text-xs text-gray-600 mb-1">In Progress</div>
          <div className="text-2xl font-bold text-blue-600">{timeline.in_progress_jobs}</div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="text-xs text-gray-600 mb-1">Completed</div>
          <div className="text-2xl font-bold text-green-600">{timeline.completed_jobs}</div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="text-xs text-gray-600 mb-1">Overdue</div>
          <div className="text-2xl font-bold text-red-600">{timeline.overdue_jobs}</div>
        </div>
      </div>

      {/* Scheduled Jobs */}
      {timeline.schedules && timeline.schedules.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Scheduled Jobs</h2>
          <div className="space-y-3">
            {timeline.schedules.map((schedule) => (
              <div
                key={schedule.id}
                className={`rounded-lg border-2 p-4 ${getStatusColor(schedule.status, schedule.is_overdue)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    <div className="mt-1">{getJobTypeIcon(schedule.job_type)}</div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-gray-900">{schedule.job_name}</h3>
                        {!schedule.job_is_mandatory && (
                          <span className="px-2 py-0.5 bg-gray-200 text-gray-700 text-xs rounded-full">
                            Optional
                          </span>
                        )}
                      </div>
                      <div className="space-y-2">
                        {/* Dates and Deadline Warning */}
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            <span>
                              {schedule.scheduled_start_date
                                ? new Date(schedule.scheduled_start_date).toLocaleDateString()
                                : 'Not set'}
                              {' - '}
                              {schedule.scheduled_end_date
                                ? new Date(schedule.scheduled_end_date).toLocaleDateString()
                                : 'Not set'}
                            </span>
                          </div>
                          {(() => {
                            const warning = getDeadlineWarning(schedule.scheduled_end_date);
                            return warning && (
                              <div className={`flex items-center gap-1 ${warning.color} font-medium`}>
                                <Bell className="w-4 h-4" />
                                <span>{warning.message}</span>
                              </div>
                            );
                          })()}
                        </div>

                        {/* Deployment Readiness Stats (for DEPLOYMENT jobs only) */}
                        {schedule.job_type === 'DEPLOYMENT' && (
                          <DeploymentReadinessDisplay batchId={batchId} />
                        )}

                        {/* Meeting Link with Actions */}
                        {schedule.meeting_link && (
                          <div className="flex items-center gap-2">
                            <a
                              href={schedule.meeting_link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 px-3 py-1 bg-blue-50 text-blue-700 text-sm rounded-md hover:bg-blue-100 transition-colors"
                            >
                              <ExternalLink className="w-3 h-3" />
                              Join Meeting
                            </a>
                            <button
                              onClick={() => handleCopyMeetingLink(schedule.meeting_link!, schedule.job_name)}
                              className="inline-flex items-center gap-1 px-3 py-1 bg-gray-50 text-gray-700 text-sm rounded-md hover:bg-gray-100 transition-colors"
                            >
                              <Copy className="w-3 h-3" />
                              Copy Link
                            </button>
                          </div>
                        )}

                        {/* Action Buttons */}
                        <div className="flex items-center flex-wrap gap-2">
                          {/* Enter Marks Button (for ASSESSMENT only) */}
                          {schedule.job_type === 'ASSESSMENT' && schedule.assessment_id && (
                            <button
                              onClick={() => router.push(`/trainer/assessments/${schedule.assessment_id}/marks`)}
                              className="inline-flex items-center gap-1 px-3 py-1 bg-amber-50 text-amber-700 text-sm rounded-md hover:bg-amber-100 transition-colors"
                            >
                              <ClipboardList className="w-3 h-3" />
                              Enter Marks
                            </button>
                          )}

                          {/* Attendance Tracking (for TRAINING and ASSESSMENT) */}
                          {((schedule.job_type === 'TRAINING' && schedule.attendance_required) ||
                            schedule.job_type === 'ASSESSMENT') && (
                            <button
                              onClick={() => handleAttendanceClick(schedule)}
                              className="inline-flex items-center gap-1 px-3 py-1 bg-purple-50 text-purple-700 text-sm rounded-md hover:bg-purple-100 transition-colors"
                            >
                              <Users className="w-3 h-3" />
                              {schedule.job_type === 'ASSESSMENT' ? 'Track Participants' : 'Track Attendance'} ({schedule.attendance_count})
                            </button>
                          )}

                          {/* Edit Schedule Button */}
                          {schedule.status !== 'COMPLETED' && (
                            <button
                              onClick={() => handleEditClick(schedule)}
                              className="inline-flex items-center gap-1 px-3 py-1 bg-blue-50 text-blue-700 text-sm rounded-md hover:bg-blue-100 transition-colors"
                            >
                              <Edit className="w-3 h-3" />
                              Edit Schedule
                            </button>
                          )}

                          {/* Mark as Complete Button */}
                          {schedule.status !== 'COMPLETED' && (
                            <button
                              onClick={() => handleMarkComplete(schedule)}
                              disabled={completingJob === schedule.id}
                              className="inline-flex items-center gap-1 px-3 py-1 bg-green-50 text-green-700 text-sm rounded-md hover:bg-green-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              <Check className="w-3 h-3" />
                              {completingJob === schedule.id ? 'Completing...' : 'Mark Complete'}
                            </button>
                          )}
                        </div>
                      </div>
                      {/* Progress Bar */}
                      <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                        <div
                          className={`h-2 rounded-full ${
                            schedule.status === 'COMPLETED' ? 'bg-green-600' :
                            schedule.status === 'IN_PROGRESS' ? 'bg-blue-600' :
                            schedule.is_overdue ? 'bg-red-600' :
                            'bg-yellow-600'
                          }`}
                          style={{ width: `${schedule.completion_percentage}%` }}
                        />
                      </div>
                      <div className="text-xs text-gray-500">
                        {schedule.completion_percentage}% Complete
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(schedule.status)}
                    <div className="text-right">
                      <div className={`text-sm font-medium ${
                        schedule.is_overdue ? 'text-red-600' :
                        schedule.status === 'COMPLETED' ? 'text-green-600' :
                        schedule.status === 'IN_PROGRESS' ? 'text-blue-600' :
                        'text-yellow-600'
                      }`}>
                        {schedule.is_overdue ? 'OVERDUE' : schedule.status}
                      </div>
                      {schedule.is_overdue && (
                        <div className="text-xs text-red-500">Action needed!</div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Unscheduled Jobs */}
      {timeline.unscheduled_jobs && timeline.unscheduled_jobs.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Unscheduled Jobs</h2>
          <div className="space-y-3">
            {timeline.unscheduled_jobs.map((job) => {
              const canSchedule = canScheduleJob(job);
              const prerequisiteMsg = getPrerequisiteMessage(job);
              const isDeployment = job.job_type === 'DEPLOYMENT';

              return (
                <div
                  key={job.id}
                  className={`rounded-lg border-2 p-4 transition-colors ${
                    isDeployment
                      ? 'bg-gradient-to-r from-purple-50 to-blue-50 border-purple-300'
                      : canSchedule
                      ? 'bg-white border-dashed border-gray-300 hover:border-blue-400'
                      : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      <div className="mt-1">
                        {canSchedule || isDeployment ? (
                          getJobTypeIcon(job.job_type)
                        ) : (
                          <Lock className="w-5 h-5 text-gray-400" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-gray-900">
                            {job.name}
                          </h3>
                          {!job.is_mandatory && (
                            <span className="px-2 py-0.5 bg-gray-200 text-gray-700 text-xs rounded-full">
                              Optional
                            </span>
                          )}
                          {isDeployment && (
                            <span className="px-2 py-0.5 bg-purple-100 text-purple-700 text-xs rounded-full font-medium">
                              Auto-Activates
                            </span>
                          )}
                        </div>
                        {job.description && (
                          <p className="text-sm mb-2 text-gray-600">
                            {job.description}
                          </p>
                        )}
                        <div className="text-xs text-gray-500 mt-2">
                          Sequence: {job.sequence_order}
                          {job.duration_days && ` • Duration: ${job.duration_days} days`}
                        </div>
                      </div>
                    </div>
                    {!isDeployment && (
                      <button
                        onClick={() => handleScheduleClick(job)}
                        className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors bg-blue-600 text-white hover:bg-blue-700"
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Schedule Now
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Empty State */}
      {timeline.schedules.length === 0 && timeline.unscheduled_jobs.length === 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
          <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Jobs in Pipeline</h3>
          <p className="text-gray-600">This batch's pipeline doesn't have any jobs yet.</p>
        </div>
      )}

      {/* Schedule Job Modal */}
      {showScheduleModal && selectedJob && (
        <ScheduleJobModal
          batchId={batchId}
          job={selectedJob}
          onClose={() => {
            setShowScheduleModal(false);
            setSelectedJob(null);
          }}
          onSuccess={handleScheduleSuccess}
        />
      )}

      {/* Attendance Modal */}
      {showAttendanceModal && selectedSchedule && (
        <AttendanceModal
          scheduleId={selectedSchedule.id}
          jobName={selectedSchedule.job_name}
          batchId={batchId}
          onClose={() => {
            setShowAttendanceModal(false);
            setSelectedSchedule(null);
          }}
          onUpdate={handleAttendanceUpdate}
        />
      )}

      {/* Edit Schedule Modal */}
      {showEditModal && selectedSchedule && (
        <EditScheduleModal
          batchId={batchId}
          schedule={selectedSchedule}
          onClose={() => {
            setShowEditModal(false);
            setSelectedSchedule(null);
          }}
          onSuccess={handleEditSuccess}
        />
      )}
    </div>
  );
}
