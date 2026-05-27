"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Calendar, Clock, MapPin, Video, ExternalLink,
  BookOpen, FileText, AlertCircle, ChevronDown, ChevronUp,
  GraduationCap, CheckCircle, XCircle, PlayCircle
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';
import { useAuthStore } from '@/store/authStore';

interface ScheduleItem {
  id: string;
  type: 'TRAINING' | 'ASSESSMENT';
  title: string;
  description: string;
  batch_name: string;
  scheduled_date: string | null;
  duration_minutes: number;
  duration_hours: number;
  location: string;
  link: string;
  link_label: string;
  status: string;
  is_online: boolean;
  max_marks?: number;
  passing_marks?: number;
}

const STATUS_CONFIG: Record<string, { label: string; className: string; icon: React.ReactNode }> = {
  SCHEDULED:    { label: 'Scheduled',    className: 'bg-blue-100 text-blue-700',   icon: <Calendar className="w-3 h-3" /> },
  IN_PROGRESS:  { label: 'In Progress',  className: 'bg-green-100 text-green-700', icon: <PlayCircle className="w-3 h-3" /> },
  COMPLETED:    { label: 'Completed',    className: 'bg-gray-100 text-gray-600',   icon: <CheckCircle className="w-3 h-3" /> },
  CANCELLED:    { label: 'Cancelled',    className: 'bg-red-100 text-red-700',     icon: <XCircle className="w-3 h-3" /> },
};

function formatDate(iso: string | null) {
  if (!iso) return 'Date TBD';
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
}

function formatTime(iso: string | null) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function isToday(iso: string | null) {
  if (!iso) return false;
  return new Date(iso).toDateString() === new Date().toDateString();
}

function isTomorrow(iso: string | null) {
  if (!iso) return false;
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  return new Date(iso).toDateString() === tomorrow.toDateString();
}

function isPast(iso: string | null) {
  if (!iso) return false;
  return new Date(iso) < new Date();
}

export default function StudentSchedulePage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [items, setItems] = useState<ScheduleItem[]>([]);
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'past'>('upcoming');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'maverick') {
      router.push('/login');
      return;
    }
    fetchSchedule();
  }, [isAuthenticated, user, router]);

  const fetchSchedule = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/maverick/dashboard/schedule');
      setItems(res.data.schedule ?? []);
    } catch {
      toast.error('Failed to load schedule');
    } finally {
      setLoading(false);
    }
  };

  const filtered = items.filter(item => {
    if (filter === 'upcoming') return !isPast(item.scheduled_date) || item.status === 'IN_PROGRESS';
    if (filter === 'past')     return isPast(item.scheduled_date) && item.status !== 'IN_PROGRESS';
    return true;
  });

  const upcomingCount = items.filter(i => !isPast(i.scheduled_date) || i.status === 'IN_PROGRESS').length;

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto" />
            <p className="mt-4 text-gray-600">Loading schedule...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6 max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Training Schedule</h1>
            <p className="text-gray-500 mt-1">
              {upcomingCount} upcoming item{upcomingCount !== 1 ? 's' : ''} · {items.length} total
            </p>
          </div>

          {/* Filter tabs */}
          <div className="flex gap-1 bg-gray-100 rounded-lg p-1 text-sm">
            {(['upcoming', 'all', 'past'] as const).map(f => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1.5 rounded-md font-medium capitalize transition-colors ${
                  filter === f ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        {/* Empty state */}
        {filtered.length === 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-8 text-center">
            <Calendar className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
            <h2 className="text-lg font-semibold text-gray-900 mb-1">
              {filter === 'upcoming' ? 'No Upcoming Sessions' : 'No Sessions Found'}
            </h2>
            <p className="text-gray-600 text-sm">
              {filter === 'upcoming'
                ? 'Your trainer has not scheduled any upcoming sessions yet. Check back later.'
                : 'No sessions match this filter.'}
            </p>
          </div>
        )}

        {/* Schedule list */}
        <div className="space-y-3">
          {filtered.map(item => {
            const statusCfg = STATUS_CONFIG[item.status] ?? STATUS_CONFIG['SCHEDULED'];
            const today = isToday(item.scheduled_date);
            const tomorrow = isTomorrow(item.scheduled_date);
            const past = isPast(item.scheduled_date) && item.status !== 'IN_PROGRESS';
            const expanded = expandedId === item.id;

            return (
              <div
                key={item.id}
                className={`bg-white rounded-xl border-2 overflow-hidden transition-all ${
                  today
                    ? 'border-blue-500 shadow-md'
                    : past
                    ? 'border-gray-200 opacity-75'
                    : 'border-gray-200 hover:border-blue-200 hover:shadow-sm'
                }`}
              >
                {/* Today banner */}
                {today && (
                  <div className="bg-blue-600 text-white text-xs font-semibold px-4 py-1 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" /> Today
                  </div>
                )}
                {tomorrow && !today && (
                  <div className="bg-orange-500 text-white text-xs font-semibold px-4 py-1">
                    Tomorrow
                  </div>
                )}

                {/* Main row */}
                <div className="p-4">
                  <div className="flex items-start gap-3">
                    {/* Type icon */}
                    <div className={`p-2 rounded-lg flex-shrink-0 ${
                      item.type === 'ASSESSMENT' ? 'bg-purple-100' : 'bg-blue-100'
                    }`}>
                      {item.type === 'ASSESSMENT'
                        ? <FileText className="w-5 h-5 text-purple-600" />
                        : <BookOpen className="w-5 h-5 text-blue-600" />}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2 flex-wrap">
                        <div>
                          <h3 className="font-semibold text-gray-900">{item.title}</h3>
                          <div className="flex items-center gap-2 mt-1 flex-wrap">
                            {/* Type badge */}
                            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                              item.type === 'ASSESSMENT'
                                ? 'bg-purple-100 text-purple-700'
                                : 'bg-blue-100 text-blue-700'
                            }`}>
                              {item.type}
                            </span>
                            {/* Status badge */}
                            <span className={`text-xs px-2 py-0.5 rounded-full font-medium flex items-center gap-1 ${statusCfg.className}`}>
                              {statusCfg.icon} {statusCfg.label}
                            </span>
                            {/* Batch name */}
                            {item.batch_name && (
                              <span className="text-xs text-gray-500 flex items-center gap-1">
                                <GraduationCap className="w-3 h-3" /> {item.batch_name}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Expand toggle */}
                        <button
                          onClick={() => setExpandedId(expanded ? null : item.id)}
                          className="text-gray-400 hover:text-gray-600 flex-shrink-0"
                        >
                          {expanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                        </button>
                      </div>

                      {/* Date / duration row */}
                      <div className="flex flex-wrap gap-4 mt-2 text-sm text-gray-600">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-4 h-4 text-gray-400" />
                          {formatDate(item.scheduled_date)}
                          {item.scheduled_date && (
                            <span className="text-gray-500">&nbsp;{formatTime(item.scheduled_date)}</span>
                          )}
                        </span>
                        {item.duration_minutes > 0 && (
                          <span className="flex items-center gap-1">
                            <Clock className="w-4 h-4 text-gray-400" />
                            {item.duration_minutes >= 60
                              ? `${item.duration_hours}h`
                              : `${item.duration_minutes}min`}
                          </span>
                        )}
                        {item.is_online ? (
                          <span className="flex items-center gap-1 text-green-600">
                            <Video className="w-4 h-4" /> Online
                          </span>
                        ) : item.location ? (
                          <span className="flex items-center gap-1">
                            <MapPin className="w-4 h-4 text-gray-400" /> {item.location}
                          </span>
                        ) : null}
                        {item.type === 'ASSESSMENT' && item.max_marks !== undefined && (
                          <span className="text-xs text-gray-500">
                            Marks: {item.passing_marks}/{item.max_marks} to pass
                          </span>
                        )}
                      </div>

                      {/* Action link — always visible */}
                      {item.link && (
                        <a
                          href={item.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={e => e.stopPropagation()}
                          className={`inline-flex items-center gap-1.5 mt-3 px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                            item.type === 'ASSESSMENT'
                              ? 'bg-purple-600 hover:bg-purple-700 text-white'
                              : 'bg-blue-600 hover:bg-blue-700 text-white'
                          }`}
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                          {item.link_label || 'Open Link'}
                        </a>
                      )}
                    </div>
                  </div>

                  {/* Expanded description */}
                  {expanded && item.description && (
                    <div className="mt-4 pt-4 border-t border-gray-100 text-sm text-gray-700 leading-relaxed">
                      {item.description}
                    </div>
                  )}
                  {expanded && !item.description && (
                    <div className="mt-4 pt-4 border-t border-gray-100 text-sm text-gray-400 italic">
                      No description provided.
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer tip */}
        {filtered.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3 text-sm text-blue-900">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-blue-600" />
            <p>Click the arrow on any card to see the full description. Use the link button to join meetings or open assessments.</p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
