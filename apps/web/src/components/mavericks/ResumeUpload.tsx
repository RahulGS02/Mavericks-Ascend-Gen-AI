'use client';

import { useState, useCallback } from 'react';
import { Upload, FileText, X, Loader2, CheckCircle2, Brain, Sparkles } from 'lucide-react';
import { maverickAPI } from '@/lib/api/mavericks';
import type { ResumeData } from './AISkillSummary';

export interface ExtractedResumeData {
  skills: string[];          // Flattened skill list
  summary?: string;          // AI professional summary
  resume_data?: ResumeData;  // Full structured parsed data
}

interface ResumeUploadProps {
  onUploadSuccess?: (data: any) => void;
  onExtractedData?: (data: ExtractedResumeData) => void;
}

type UploadStage = 'idle' | 'uploading' | 'parsing' | 'done' | 'error';

export default function ResumeUpload({ onUploadSuccess, onExtractedData }: ResumeUploadProps) {
  const [file, setFile]           = useState<File | null>(null);
  const [stage, setStage]         = useState<UploadStage>('idle');
  const [error, setError]         = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  // ── Drag handlers ──────────────────────────────────────────────────────────
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) handleFileSelect(e.dataTransfer.files[0]);
  }, []);

  // ── File validation ─────────────────────────────────────────────────────────
  const handleFileSelect = (selectedFile: File) => {
    const allowed = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ];
    if (!allowed.includes(selectedFile.type)) {
      setError('Please upload a PDF or Word document (.pdf, .doc, .docx)');
      return;
    }
    if (selectedFile.size > 5 * 1024 * 1024) {
      setError('File size must be less than 5 MB');
      return;
    }
    setFile(selectedFile);
    setError(null);
    setStage('idle');
  };

  // ── Upload + AI parse ───────────────────────────────────────────────────────
  const handleUpload = async () => {
    if (!file) return;

    const token = localStorage.getItem('access_token');
    if (!token) {
      setError('Authentication token not found. Please register again.');
      return;
    }

    try {
      // Step 1 — uploading to server
      setStage('uploading');
      setError(null);

      const uploadResult = await maverickAPI.uploadResume(file);

      // Step 2 — show that AI is processing (the backend already did it; we
      //           briefly show this state so the user sees the transition)
      setStage('parsing');
      await new Promise(r => setTimeout(r, 800)); // brief visual pause

      // Step 3 — done
      setStage('done');

      // Propagate full structured data to parent
      if (uploadResult) {
        const extracted: ExtractedResumeData = {
          skills:      uploadResult.ai_extracted_skills ?? [],
          summary:     uploadResult.ai_summary,
          resume_data: uploadResult.ai_resume_data,
        };
        onExtractedData?.(extracted);
      }
      onUploadSuccess?.(uploadResult);

    } catch (err: any) {
      console.error('Resume upload error:', err);
      setError(
        err.response?.data?.detail ??
        err.message ??
        'Failed to upload resume. Please try again.'
      );
      setStage('error');
    }
  };

  const removeFile = () => {
    setFile(null);
    setStage('idle');
    setError(null);
  };

  // ── Stage labels & colours ─────────────────────────────────────────────────
  const stageInfo: Record<UploadStage, { label: string; color: string }> = {
    idle:      { label: 'Upload & Parse with AI',         color: 'bg-blue-600 hover:bg-blue-700' },
    uploading: { label: 'Uploading…',                     color: 'bg-blue-400' },
    parsing:   { label: 'AI is analysing your resume…',  color: 'bg-indigo-500' },
    done:      { label: 'Uploaded & Parsed ✓',            color: 'bg-green-600' },
    error:     { label: 'Retry Upload',                   color: 'bg-red-600 hover:bg-red-700' },
  };

  const isProcessing = stage === 'uploading' || stage === 'parsing';

  return (
    <div className="w-full">
      {/* ── Drop zone (no file selected) ──────────────────────────────── */}
      {!file ? (
        <div
          className={`border-2 border-dashed rounded-xl p-10 text-center transition-colors ${
            dragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="flex flex-col items-center gap-3">
            <div className="w-14 h-14 rounded-full bg-blue-50 border border-blue-100 flex items-center justify-center">
              <Upload className="w-7 h-7 text-blue-500" />
            </div>
            <div>
              <p className="text-base font-semibold text-gray-700">
                Drop your resume here or{' '}
                <label
                  htmlFor="resume-upload"
                  className="text-blue-600 cursor-pointer hover:text-blue-700 underline underline-offset-2"
                >
                  browse
                </label>
              </p>
              <p className="text-sm text-gray-400 mt-1">
                PDF, DOC or DOCX · max 5 MB
              </p>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-indigo-600 mt-1">
              <Sparkles className="w-3.5 h-3.5" />
              <span>AI will automatically extract skills, experience & summary</span>
            </div>
          </div>

          <input
            type="file"
            id="resume-upload"
            className="hidden"
            accept=".pdf,.doc,.docx"
            onChange={e => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
          />
        </div>
      ) : (
        /* ── File selected ──────────────────────────────────────────── */
        <div className="border rounded-xl p-5 bg-white space-y-4">
          {/* File row */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center shrink-0">
                <FileText className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="font-medium text-gray-900 text-sm">{file.name}</p>
                <p className="text-xs text-gray-400">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            {!isProcessing && stage !== 'done' && (
              <button
                onClick={removeFile}
                className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                title="Remove file"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>

          {/* Status indicators */}
          {stage === 'uploading' && (
            <div className="flex items-center gap-2 text-blue-600 text-sm">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Uploading resume to secure storage…</span>
            </div>
          )}

          {stage === 'parsing' && (
            <div className="flex items-center gap-2 text-indigo-600 text-sm">
              <Brain className="w-4 h-4 animate-pulse" />
              <span>AI is analysing skills, experience & projects…</span>
            </div>
          )}

          {stage === 'done' && (
            <div className="flex items-center gap-2 text-green-600 text-sm">
              <CheckCircle2 className="w-4 h-4" />
              <span className="font-medium">Resume uploaded and AI analysis complete!</span>
            </div>
          )}

          {error && (
            <div className="text-red-600 text-sm bg-red-50 rounded-lg px-3 py-2">
              {error}
            </div>
          )}

          {/* Action button */}
          {stage !== 'done' && (
            <button
              onClick={handleUpload}
              disabled={isProcessing}
              className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg
                text-white font-medium transition-colors text-sm
                ${stageInfo[stage].color}
                disabled:opacity-70 disabled:cursor-not-allowed`}
            >
              {isProcessing ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Sparkles className="w-4 h-4" />
              )}
              {stageInfo[stage].label}
            </button>
          )}

          {/* Re-upload option after done */}
          {stage === 'done' && (
            <button
              onClick={removeFile}
              className="w-full text-sm text-gray-500 hover:text-gray-700 underline transition-colors"
            >
              Upload a different resume
            </button>
          )}
        </div>
      )}
    </div>
  );
}
