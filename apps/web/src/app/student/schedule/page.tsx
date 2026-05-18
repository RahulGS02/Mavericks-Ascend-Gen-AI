"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Calendar, Clock, MapPin, Video, Users, AlertCircle } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import DashboardLayout from '@/components/DashboardLayout';
import { useAuthStore } from '@/store/authStore';

interface SessionData {
  upcoming_sessions: Array<{
    id: string;
    title: string;
    session_date: string;
    duration_hours: number;
    location: string;
    mode: string;
    attendance_required: boolean;
    description: string;
  }>;
}

export default function StudentSchedulePage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [sessionData, setSessionData] = useState<SessionData | null>(null);

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
      const response = await apiClient.get('/maverick/dashboard/overview');
      setSessionData(response.data);
    } catch (error) {
      console.error('Failed to fetch schedule:', error);
      toast.error('Failed to load schedule');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading schedule...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const upcomingSessions = sessionData?.upcoming_sessions || [];

  return (
    <DashboardLayout>
      <div className="p-6 max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Training Schedule</h1>
          <p className="text-gray-600">Upcoming training sessions and classes</p>
        </div>

        {/* Sessions List */}
        {upcomingSessions.length === 0 ? (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
            <Calendar className="w-12 h-12 text-yellow-600 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No Upcoming Sessions</h2>
            <p className="text-gray-600">There are no scheduled training sessions at the moment.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {upcomingSessions.map((session) => {
              const sessionDate = new Date(session.session_date);
              const isToday = sessionDate.toDateString() === new Date().toDateString();
              const isTomorrow = new Date(sessionDate.getTime() - 86400000).toDateString() === new Date().toDateString();

              return (
                <div
                  key={session.id}
                  className={`bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow ${
                    isToday ? 'border-blue-500' : 'border-gray-200'
                  }`}
                >
                  {/* Date Badge */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">{session.title}</h3>
                      <div className="flex items-center gap-2 text-sm text-gray-600 mb-1">
                        <Calendar className="w-4 h-4" />
                        <span>
                          {sessionDate.toLocaleDateString('en-US', { 
                            month: 'short', 
                            day: 'numeric', 
                            year: 'numeric' 
                          })}
                          {isToday && <span className="ml-2 text-blue-600 font-semibold">(Today)</span>}
                          {isTomorrow && <span className="ml-2 text-orange-600 font-semibold">(Tomorrow)</span>}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Clock className="w-4 h-4" />
                        <span>
                          {sessionDate.toLocaleTimeString('en-US', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })} ({session.duration_hours}h)
                        </span>
                      </div>
                    </div>
                    {session.attendance_required && (
                      <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-700 rounded">
                        Required
                      </span>
                    )}
                  </div>

                  {/* Location/Mode */}
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      {session.mode === 'ONLINE' ? (
                        <>
                          <Video className="w-4 h-4" />
                          <span>Online Session</span>
                        </>
                      ) : (
                        <>
                          <MapPin className="w-4 h-4" />
                          <span>{session.location || 'Location TBD'}</span>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Description */}
                  {session.description && (
                    <p className="text-sm text-gray-600 border-t pt-3">
                      {session.description}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Info Box */}
        {upcomingSessions.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-900">
              <p className="font-medium mb-1">Important Notes:</p>
              <ul className="list-disc list-inside space-y-1 text-blue-800">
                <li>Sessions marked as "Required" must be attended</li>
                <li>Join online sessions 5 minutes before start time</li>
                <li>Contact your trainer if you cannot attend</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
