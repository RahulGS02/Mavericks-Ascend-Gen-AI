"use client";

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import DashboardLayout from '@/components/DashboardLayout';
import { Search, Download, Sparkles, TrendingUp, Database, AlertCircle, Loader2, CheckCircle } from 'lucide-react';
import { nlQueryAPI } from '@/lib/api';

interface QueryResult {
  data: Array<Record<string, any>>;
  statistics: {
    total_rows: number;
    columns: string[];
    column_types: Record<string, string>;
    execution_time_ms: number;
    executed_at: string;
    aggregations?: {
      numeric?: Record<string, { count: number; min: number; max: number; avg: number; sum: number }>;
      string?: Record<string, { count: number; unique_count: number; unique_values: string[] }>;
    };
  };
  query_info: {
    natural_query: string;
    sql: string;
    explanation: string;
    tables_used: string[];
  };
}

export default function AISearchPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [results, setResults] = useState<QueryResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const tableRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);

  // Check if user is SuperAdmin
  if (user?.role !== 'super_admin') {
    router.push('/dashboard');
    return null;
  }

  // Mouse drag scroll functionality
  const handleMouseDown = (e: React.MouseEvent) => {
    if (!tableRef.current) return;
    setIsDragging(true);
    setStartX(e.pageX - tableRef.current.offsetLeft);
    setScrollLeft(tableRef.current.scrollLeft);
    tableRef.current.style.scrollBehavior = 'auto';
  };

  const handleMouseLeave = () => {
    setIsDragging(false);
    if (tableRef.current) {
      tableRef.current.style.scrollBehavior = 'smooth';
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    if (tableRef.current) {
      tableRef.current.style.scrollBehavior = 'smooth';
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !tableRef.current) return;
    e.preventDefault();
    const x = e.pageX - tableRef.current.offsetLeft;
    const walk = (x - startX) * 2; // Scroll speed multiplier
    tableRef.current.scrollLeft = scrollLeft - walk;
  };

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      // Do NOT pass maxRows — let the backend detect the limit from the
      // natural language text ("Top 10" → 10, "Show all" → all records).
      const response = await nlQueryAPI.search(query);
      setResults(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to execute query. Please try again.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!query.trim()) {
      setError('Please enter a search query first');
      return;
    }

    setDownloading(true);
    setError(null);

    try {
      // No maxRows override — use same limit the search used.
      const response = await nlQueryAPI.downloadExcel(query);
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
      link.setAttribute('download', `query_results_${timestamp}.xlsx`);
      
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to download Excel file. Please try again.');
      console.error('Download error:', err);
    } finally {
      setDownloading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  return (
    <DashboardLayout>
      <style jsx global>{`
        /* Custom scrollbar styling for table */
        .table-scroll::-webkit-scrollbar {
          height: 12px;
          width: 12px;
        }
        .table-scroll::-webkit-scrollbar-track {
          background: #f1f5f9;
          border-radius: 10px;
        }
        .table-scroll::-webkit-scrollbar-thumb {
          background: #3b82f6;
          border-radius: 10px;
          border: 2px solid #f1f5f9;
        }
        .table-scroll::-webkit-scrollbar-thumb:hover {
          background: #2563eb;
        }
        .table-scroll::-webkit-scrollbar-corner {
          background: #f1f5f9;
        }
      `}</style>
      <div className="space-y-6 p-6 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 min-h-screen">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-1 flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl shadow-lg">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              AI-Powered Search
            </h1>
            <p className="text-base text-gray-600">Ask questions in plain English, get instant data insights</p>
          </div>
        </div>

        {/* Search Card */}
        <div className="bg-white rounded-xl shadow-lg border border-blue-200 overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Search className="w-5 h-5" />
              Natural Language Query
            </h2>
            <p className="text-sm text-blue-100 mt-1">
              Example: "Show me all mavericks who are available for deployment" or "Top 10 students by CGPA"
            </p>
          </div>
          
          <div className="p-6">
            <div className="flex gap-3">
              <div className="flex-1">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask a question about your data..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                  disabled={loading}
                />
              </div>
              <button
                onClick={handleSearch}
                disabled={loading || !query.trim()}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
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
              <button
                onClick={handleDownload}
                disabled={downloading || !query.trim()}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
              >
                {downloading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Downloading...
                  </>
                ) : (
                  <>
                    <Download className="w-5 h-5" />
                    Excel
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-red-900">Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Statistics Cards */}
        {results && results.statistics && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg shadow-md p-5 border-l-4 border-blue-500">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Total Rows</p>
                    <p className="text-3xl font-bold text-gray-900">{results.statistics.total_rows || 0}</p>
                  </div>
                  <div className="p-3 bg-blue-50 rounded-xl">
                    <Database className="w-8 h-8 text-blue-600" />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-5 border-l-4 border-purple-500">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Columns</p>
                    <p className="text-3xl font-bold text-gray-900">{results.statistics.columns?.length || 0}</p>
                  </div>
                  <div className="p-3 bg-purple-50 rounded-xl">
                    <TrendingUp className="w-8 h-8 text-purple-600" />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-5 border-l-4 border-green-500">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Execution Time</p>
                    <p className="text-3xl font-bold text-gray-900">{results.statistics.execution_time_ms?.toFixed(0) || 0}<span className="text-lg text-gray-500">ms</span></p>
                  </div>
                  <div className="p-3 bg-green-50 rounded-xl">
                    <Sparkles className="w-8 h-8 text-green-600" />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-5 border-l-4 border-yellow-500">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Status</p>
                    <p className="text-sm font-bold text-green-700 flex items-center gap-2">
                      <CheckCircle className="w-5 h-5" />
                      Success
                    </p>
                  </div>
                  <div className="p-3 bg-yellow-50 rounded-xl">
                    <CheckCircle className="w-8 h-8 text-yellow-600" />
                  </div>
                </div>
              </div>
            </div>

            {/* Query Info */}
            {results.query_info && (
              <div className="bg-white rounded-lg shadow-md p-5">
                <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-purple-600" />
                  Query Information
                </h3>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm font-semibold text-gray-600 mb-1">Your Question</p>
                    <p className="text-base text-gray-900 bg-blue-50 p-3 rounded-lg">{results.query_info.natural_query}</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-600 mb-1">AI Explanation</p>
                    <p className="text-base text-gray-700 bg-purple-50 p-3 rounded-lg">{results.query_info.explanation}</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-600 mb-1">Generated SQL</p>
                    <pre className="text-sm text-gray-900 bg-gray-50 p-3 rounded-lg overflow-x-auto border border-gray-200 font-mono">
                      {results.query_info.sql}
                    </pre>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-600 mb-1">Tables Used</p>
                    <div className="flex flex-wrap gap-2">
                      {results.query_info.tables_used?.map((table, idx) => (
                        <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-semibold">
                          {table}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Results Table */}
            {results.data && results.data.length > 0 && results.statistics?.columns && (
              <div className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="bg-gradient-to-r from-gray-800 to-gray-900 p-4">
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Database className="w-5 h-5" />
                    Query Results ({results.statistics.total_rows || results.data.length} rows)
                  </h3>
                </div>

                {/* Scrollable table container - mouse drag enabled */}
                <div
                  ref={tableRef}
                  className="table-scroll overflow-x-auto overflow-y-auto max-h-[600px] select-none"
                  style={{
                    scrollbarWidth: 'thin',
                    scrollbarColor: '#3B82F6 #E5E7EB',
                    cursor: isDragging ? 'grabbing' : 'grab',
                    scrollBehavior: 'smooth'
                  }}
                  onMouseDown={handleMouseDown}
                  onMouseLeave={handleMouseLeave}
                  onMouseUp={handleMouseUp}
                  onMouseMove={handleMouseMove}
                >
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b-2 border-gray-200 sticky top-0 z-20">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider border-r border-gray-200 bg-gray-50 sticky left-0 z-30">
                          #
                        </th>
                        {results.statistics.columns.map((column, idx) => (
                          <th key={idx} className="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider border-r border-gray-200 whitespace-nowrap min-w-[150px]">
                            {column}
                            <span className="block text-xs font-normal text-gray-500 mt-0.5 normal-case">
                              {results.statistics.column_types?.[column] || 'unknown'}
                            </span>
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 bg-white">
                      {results.data.map((row, rowIdx) => (
                        <tr key={rowIdx} className="hover:bg-blue-50 transition-colors">
                          <td className="px-4 py-3 text-sm font-semibold text-gray-600 border-r border-gray-200 bg-gray-50 sticky left-0 z-10">
                            {rowIdx + 1}
                          </td>
                          {results.statistics.columns.map((column, colIdx) => (
                            <td key={colIdx} className="px-4 py-3 text-sm text-gray-900 border-r border-gray-200 whitespace-nowrap min-w-[150px]">
                              {row[column] !== null && row[column] !== undefined
                                ? String(row[column])
                                : <span className="text-gray-400 italic">null</span>
                              }
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}

