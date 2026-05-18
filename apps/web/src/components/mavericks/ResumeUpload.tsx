'use client';

import { useState, useCallback } from 'react';
import { Upload, FileText, X, Loader2, CheckCircle2 } from 'lucide-react';
import { maverickAPI } from '@/lib/api/mavericks';

interface ResumeUploadProps {
  onUploadSuccess?: (data: any) => void;
  onExtractedData?: (data: any) => void;
}

export default function ResumeUpload({ onUploadSuccess, onExtractedData }: ResumeUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [parsing, setParsing] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileSelect = (selectedFile: File) => {
    // Validate file type
    const allowedTypes = ['application/pdf', 'application/msword', 
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    
    if (!allowedTypes.includes(selectedFile.type)) {
      setError('Please upload a PDF or Word document');
      return;
    }

    // Validate file size (max 5MB)
    if (selectedFile.size > 5 * 1024 * 1024) {
      setError('File size must be less than 5MB');
      return;
    }

    setFile(selectedFile);
    setError(null);
    setUploadSuccess(false);
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      // Debug: Check if token exists
      const token = localStorage.getItem('access_token');
      console.log('🔍 Token exists:', !!token);
      console.log('🔍 Token preview:', token ? token.substring(0, 20) + '...' : 'NO TOKEN');

      if (!token) {
        setError('Authentication token not found. Please register again.');
        setUploading(false);
        return;
      }

      // Upload resume (backend handles AI parsing automatically)
      console.log('📤 Uploading resume...');
      const uploadResult = await maverickAPI.uploadResume(file);
      console.log('✅ Resume uploaded successfully:', uploadResult);

      // Backend already parsed the resume, check if AI extracted data
      if (uploadResult.ai_extracted_skills && uploadResult.ai_extracted_skills.length > 0) {
        console.log('✅ AI extracted skills:', uploadResult.ai_extracted_skills);
        // Pass the entire upload result as extracted data
        onExtractedData?.({
          skills: uploadResult.ai_extracted_skills,
          summary: uploadResult.ai_summary,
          resume_data: uploadResult.ai_resume_data
        });
      }

      setUploadSuccess(true);
      onUploadSuccess?.(uploadResult);

    } catch (err: any) {
      console.error('❌ Upload error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to upload resume');
      setUploadSuccess(false);
    } finally {
      setUploading(false);
      setParsing(false);
    }
  };

  const removeFile = () => {
    setFile(null);
    setUploadSuccess(false);
    setError(null);
  };

  return (
    <div className="w-full">
      {!file ? (
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <p className="text-lg font-medium text-gray-700 mb-2">
            Drop your resume here or click to browse
          </p>
          <p className="text-sm text-gray-500 mb-4">
            Supports PDF, DOC, DOCX (max 5MB)
          </p>
          <input
            type="file"
            id="resume-upload"
            className="hidden"
            accept=".pdf,.doc,.docx"
            onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
          />
          <label
            htmlFor="resume-upload"
            className="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer transition"
          >
            Choose File
          </label>
        </div>
      ) : (
        <div className="border rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <FileText className="w-10 h-10 text-blue-600" />
              <div>
                <p className="font-medium text-gray-900">{file.name}</p>
                <p className="text-sm text-gray-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            {!uploading && !uploadSuccess && (
              <button onClick={removeFile} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            )}
          </div>

          {uploadSuccess && (
            <div className="flex items-center space-x-2 text-green-600 mb-4">
              <CheckCircle2 className="w-5 h-5" />
              <span className="text-sm font-medium">Resume uploaded successfully!</span>
            </div>
          )}

          {parsing && (
            <div className="flex items-center space-x-2 text-blue-600 mb-4">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span className="text-sm">AI is parsing your resume...</span>
            </div>
          )}

          {error && (
            <div className="text-red-600 text-sm mb-4">{error}</div>
          )}

          {!uploadSuccess && !uploading && (
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
            >
              Upload & Parse with AI
            </button>
          )}
        </div>
      )}
    </div>
  );
}
