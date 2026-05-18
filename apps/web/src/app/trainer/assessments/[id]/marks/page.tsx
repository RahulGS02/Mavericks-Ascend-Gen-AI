"use client";

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  ArrowLeft,
  Save,
  Download,
  Upload,
  CheckCircle,
  XCircle,
  AlertCircle,
  Calendar,
  RotateCcw,
  Eye,
  FileSpreadsheet
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';

interface Assessment {
  id: string;
  title: string;
  description?: string;
  batch_id: string;
  batch_name?: string;
  max_marks: number;
  passing_marks: number;
  duration_minutes: number;
  scheduled_date?: string;
}

interface Maverick {
  id: string;
  name: string;
  email: string;
  maverick_id?: string;
}

interface AttemptData {
  maverick_id: string;
  maverick_name: string;
  maverick_email: string;
  marks_obtained?: number;
  feedback?: string;
  passed?: boolean;
  evaluated_at?: string;
  attempt_number?: number;
  has_attempt: boolean;
}

export default function MarksEntryPage() {
  const router = useRouter();
  const params = useParams();
  const assessmentId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [mavericks, setMavericks] = useState<Maverick[]>([]);
  const [marksData, setMarksData] = useState<Record<string, AttemptData>>({});
  const [editMode, setEditMode] = useState<Record<string, boolean>>({});
  const [showExcelUpload, setShowExcelUpload] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [showResultsModal, setShowResultsModal] = useState(false);
  const [resultsData, setResultsData] = useState<any>(null);
  const [showReattemptModal, setShowReattemptModal] = useState(false);
  const [selectedMaverick, setSelectedMaverick] = useState<string | null>(null);
  const [reattemptDate, setReattemptDate] = useState('');
  const [reattemptNotes, setReattemptNotes] = useState('');

  useEffect(() => {
    fetchAssessmentData();
  }, [assessmentId]);

  const fetchAssessmentData = async () => {
    try {
      setLoading(true);
      
      // Fetch assessment details
      const assessmentResponse = await apiClient.get(`/assessments/${assessmentId}`);
      setAssessment(assessmentResponse.data);

      // Fetch mavericks in batch
      const maverickResponse = await apiClient.get(`/batches/${assessmentResponse.data.batch_id}`);
      const batchMavericks = maverickResponse.data.mavericks || [];
      setMavericks(batchMavericks);

      // Fetch existing attempts
      const attemptsResponse = await apiClient.get(`/assessments/${assessmentId}/attempts`);
      const attempts = attemptsResponse.data.attempts || [];

      // Build marks data structure
      const marksMap: Record<string, AttemptData> = {};
      batchMavericks.forEach((mav: Maverick) => {
        const attempt = attempts.find((a: any) => a.maverick_id === mav.id);
        marksMap[mav.id] = {
          maverick_id: mav.id,
          maverick_name: mav.name,
          maverick_email: mav.email,
          marks_obtained: attempt?.marks_obtained,
          feedback: attempt?.feedback,
          passed: attempt?.passed,
          evaluated_at: attempt?.evaluated_at,
          attempt_number: attempt?.attempt_number || 0,
          has_attempt: !!attempt
        };
      });

      setMarksData(marksMap);
    } catch (error: any) {
      console.error('Failed to fetch data:', error);
      toast.error('Failed to load assessment data');
    } finally {
      setLoading(false);
    }
  };

  const handleMarksChange = (maverickId: string, marks: string) => {
    const marksValue = parseFloat(marks);
    if (isNaN(marksValue) || marksValue < 0) return;

    setMarksData(prev => ({
      ...prev,
      [maverickId]: {
        ...prev[maverickId],
        marks_obtained: marksValue,
        passed: marksValue >= (assessment?.passing_marks || 0)
      }
    }));
  };

  const handleFeedbackChange = (maverickId: string, feedback: string) => {
    setMarksData(prev => ({
      ...prev,
      [maverickId]: {
        ...prev[maverickId],
        feedback
      }
    }));
  };

  const handleSaveMarks = async (maverickId: string) => {
    const data = marksData[maverickId];
    
    if (data.marks_obtained === undefined || data.marks_obtained === null) {
      toast.error('Please enter marks');
      return;
    }

    if (data.marks_obtained > (assessment?.max_marks || 0)) {
      toast.error(`Marks cannot exceed ${assessment?.max_marks}`);
      return;
    }

    try {
      setSaving(true);
      
      const response = await apiClient.post(`/assessments/${assessmentId}/enter-marks`, {
        maverick_id: maverickId,
        marks_obtained: data.marks_obtained,
        feedback: data.feedback || null,
        auto_progress: true
      });

      toast.success(response.data.message);
      
      // Refresh data
      await fetchAssessmentData();
      
      // Exit edit mode
      setEditMode(prev => ({ ...prev, [maverickId]: false }));
    } catch (error: any) {
      console.error('Failed to save marks:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to save marks';
      toast.error(typeof errorMessage === 'string' ? errorMessage : 'Failed to save marks');
    } finally {
      setSaving(false);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await apiClient.get(`/assessments/${assessmentId}/template/excel`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `marks_template_${assessment?.title}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('Template downloaded successfully');
    } catch (error) {
      console.error('Failed to download template:', error);
      toast.error('Failed to download template');
    }
  };

  const handleExcelUpload = async () => {
    if (!uploadFile) {
      toast.error('Please select a file');
      return;
    }

    try {
      setSaving(true);
      const formData = new FormData();
      formData.append('file', uploadFile);

      const response = await apiClient.post(
        `/assessments/${assessmentId}/upload/excel?auto_progress=true`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      setResultsData(response.data);
      setShowResultsModal(true);
      setShowExcelUpload(false);
      setUploadFile(null);

      // Refresh data
      await fetchAssessmentData();

      toast.success(response.data.message);
    } catch (error: any) {
      console.error('Failed to upload marks:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to upload marks';
      toast.error(typeof errorMessage === 'string' ? errorMessage : 'Failed to upload marks');
    } finally {
      setSaving(false);
    }
  };

  const handleScheduleReattempt = async () => {
    if (!selectedMaverick) return;

    try {
      setSaving(true);
      const response = await apiClient.post(`/reattempts/${assessmentId}/schedule`, {
        maverick_id: selectedMaverick,
        scheduled_date: reattemptDate || null,
        notes: reattemptNotes || null
      });

      toast.success(response.data.message);
      setShowReattemptModal(false);
      setSelectedMaverick(null);
      setReattemptDate('');
      setReattemptNotes('');

      // Refresh data
      await fetchAssessmentData();
    } catch (error: any) {
      console.error('Failed to schedule reattempt:', error);
      toast.error(error.response?.data?.detail || 'Failed to schedule reattempt');
    } finally {
      setSaving(false);
    }
  };

  const getPassFailIndicator = (marks?: number, passed?: boolean) => {
    if (marks === undefined || marks === null) {
      return <span className="text-gray-400">-</span>;
    }

    if (passed) {
      return (
        <div className="flex items-center text-green-600">
          <CheckCircle className="w-4 h-4 mr-1" />
          <span className="font-medium">PASS</span>
        </div>
      );
    } else {
      return (
        <div className="flex items-center text-red-600">
          <XCircle className="w-4 h-4 mr-1" />
          <span className="font-medium">FAIL</span>
        </div>
      );
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
            <p className="mt-4 text-gray-600">Loading assessment data...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!assessment) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="text-center text-red-600">Assessment not found</div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to Assessments
          </button>

          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{assessment.title}</h1>
              <p className="text-gray-600">Batch: {assessment.batch_name || 'Unknown'}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleDownloadTemplate}
                className="inline-flex items-center px-4 py-2 text-sm font-medium text-blue-700 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <Download className="w-4 h-4 mr-2" />
                Download Template
              </button>
              <button
                onClick={() => setShowExcelUpload(true)}
                className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors"
              >
                <Upload className="w-4 h-4 mr-2" />
                Upload Excel
              </button>
            </div>
          </div>
        </div>

        {/* Assessment Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Max Marks:</span>
              <span className="ml-2 font-semibold text-gray-900">{assessment.max_marks}</span>
            </div>
            <div>
              <span className="text-gray-600">Passing Marks:</span>
              <span className="ml-2 font-semibold text-gray-900">{assessment.passing_marks}</span>
            </div>
            <div>
              <span className="text-gray-600">Duration:</span>
              <span className="ml-2 font-semibold text-gray-900">{assessment.duration_minutes} mins</span>
            </div>
            <div>
              <span className="text-gray-600">Students:</span>
              <span className="ml-2 font-semibold text-gray-900">{mavericks.length}</span>
            </div>
          </div>
        </div>

        {/* Statistics Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-600 mb-1">Evaluated</div>
            <div className="text-2xl font-bold text-green-600">
              {Object.values(marksData).filter(d => d.has_attempt).length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-600 mb-1">Pending</div>
            <div className="text-2xl font-bold text-amber-600">
              {Object.values(marksData).filter(d => !d.has_attempt).length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-600 mb-1">Passed</div>
            <div className="text-2xl font-bold text-green-600">
              {Object.values(marksData).filter(d => d.passed).length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-600 mb-1">Failed</div>
            <div className="text-2xl font-bold text-red-600">
              {Object.values(marksData).filter(d => d.has_attempt && !d.passed).length}
            </div>
          </div>
        </div>

        {/* Marks Entry Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Student
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Marks Obtained
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Result
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Feedback
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Evaluated
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {mavericks.map((maverick) => {
                  const data = marksData[maverick.id];
                  const isEditing = editMode[maverick.id];

                  return (
                    <tr key={maverick.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{data?.maverick_name}</div>
                          <div className="text-xs text-gray-500">{data?.maverick_email}</div>
                          {data?.attempt_number > 0 && (
                            <div className="text-xs text-blue-600 mt-1">
                              Attempt #{data.attempt_number + 1}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {isEditing ? (
                          <input
                            type="number"
                            min="0"
                            max={assessment.max_marks}
                            step="0.5"
                            value={data?.marks_obtained || ''}
                            onChange={(e) => handleMarksChange(maverick.id, e.target.value)}
                            className="w-24 px-3 py-1.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="0"
                          />
                        ) : (
                          <div className="text-sm">
                            {data?.marks_obtained !== undefined ? (
                              <span className="font-medium">
                                {data.marks_obtained} / {assessment.max_marks}
                              </span>
                            ) : (
                              <span className="text-gray-400">Not entered</span>
                            )}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {getPassFailIndicator(data?.marks_obtained, data?.passed)}
                      </td>
                      <td className="px-6 py-4">
                        {isEditing ? (
                          <textarea
                            value={data?.feedback || ''}
                            onChange={(e) => handleFeedbackChange(maverick.id, e.target.value)}
                            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="Optional feedback..."
                            rows={2}
                          />
                        ) : (
                          <div className="text-sm text-gray-600 max-w-xs">
                            {data?.feedback || '-'}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-600">
                          {formatDate(data?.evaluated_at)}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          {isEditing ? (
                            <>
                              <button
                                onClick={() => handleSaveMarks(maverick.id)}
                                disabled={saving}
                                className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                <Save className="w-4 h-4 mr-1" />
                                Save
                              </button>
                              <button
                                onClick={() => {
                                  setEditMode(prev => ({ ...prev, [maverick.id]: false }));
                                  fetchAssessmentData(); // Reset data
                                }}
                                className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                              >
                                Cancel
                              </button>
                            </>
                          ) : (
                            <>
                              <button
                                onClick={() => setEditMode(prev => ({ ...prev, [maverick.id]: true }))}
                                className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-blue-700 bg-blue-50 rounded-md hover:bg-blue-100"
                              >
                                {data?.has_attempt ? 'Edit' : 'Enter Marks'}
                              </button>
                              {data?.has_attempt && !data?.passed && (
                                <button
                                  onClick={() => {
                                    setSelectedMaverick(maverick.id);
                                    setShowReattemptModal(true);
                                  }}
                                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-amber-700 bg-amber-50 rounded-md hover:bg-amber-100"
                                >
                                  <RotateCcw className="w-4 h-4 mr-1" />
                                  Reattempt
                                </button>
                              )}
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Excel Upload Modal */}
        {showExcelUpload && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Upload Marks via Excel</h2>

              <div className="mb-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                  <div className="flex items-start">
                    <AlertCircle className="w-5 h-5 text-blue-600 mr-2 mt-0.5" />
                    <div className="text-sm text-blue-800">
                      <p className="font-medium mb-1">Instructions:</p>
                      <ol className="list-decimal list-inside space-y-1">
                        <li>Download the template first</li>
                        <li>Fill in marks for each student</li>
                        <li>Upload the completed file</li>
                      </ol>
                    </div>
                  </div>
                </div>

                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Excel File
                </label>
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
                {uploadFile && (
                  <p className="mt-2 text-sm text-gray-600">
                    Selected: {uploadFile.name}
                  </p>
                )}
              </div>

              <div className="flex justify-end gap-2">
                <button
                  onClick={() => {
                    setShowExcelUpload(false);
                    setUploadFile(null);
                  }}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  onClick={handleExcelUpload}
                  disabled={!uploadFile || saving}
                  className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? 'Uploading...' : 'Upload'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Results Summary Modal */}
        {showResultsModal && resultsData && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Upload Results</h2>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="text-sm text-green-600 mb-1">Success</div>
                  <div className="text-2xl font-bold text-green-700">{resultsData.success_count}</div>
                </div>
                <div className="bg-red-50 rounded-lg p-4">
                  <div className="text-sm text-red-600 mb-1">Failed</div>
                  <div className="text-2xl font-bold text-red-700">{resultsData.failed_count}</div>
                </div>
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="text-sm text-blue-600 mb-1">Passed</div>
                  <div className="text-2xl font-bold text-blue-700">{resultsData.passed_count}</div>
                </div>
                <div className="bg-purple-50 rounded-lg p-4">
                  <div className="text-sm text-purple-600 mb-1">Progressed</div>
                  <div className="text-2xl font-bold text-purple-700">{resultsData.progressed_count}</div>
                </div>
              </div>

              {resultsData.errors && resultsData.errors.length > 0 && (
                <div className="mb-4">
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Errors:</h3>
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 max-h-48 overflow-y-auto">
                    {resultsData.errors.map((error: any, index: number) => (
                      <div key={index} className="text-sm text-red-800 mb-2">
                        Row {error.row}: {error.error}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex justify-end">
                <button
                  onClick={() => setShowResultsModal(false)}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Reattempt Scheduling Modal */}
        {showReattemptModal && selectedMaverick && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Schedule Reattempt</h2>

              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-4">
                  Student: <span className="font-medium">{marksData[selectedMaverick]?.maverick_name}</span>
                </p>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Scheduled Date (Optional)
                  </label>
                  <input
                    type="datetime-local"
                    value={reattemptDate}
                    onChange={(e) => setReattemptDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Notes (Optional)
                  </label>
                  <textarea
                    value={reattemptNotes}
                    onChange={(e) => setReattemptNotes(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                    placeholder="Additional notes for reattempt..."
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2">
                <button
                  onClick={() => {
                    setShowReattemptModal(false);
                    setSelectedMaverick(null);
                    setReattemptDate('');
                    setReattemptNotes('');
                  }}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  onClick={handleScheduleReattempt}
                  disabled={saving}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? 'Scheduling...' : 'Schedule Reattempt'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
