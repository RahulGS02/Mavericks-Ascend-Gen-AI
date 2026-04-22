"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import DashboardLayout from '@/components/DashboardLayout';
import { Users, BookOpen, Briefcase, TrendingUp } from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  if (!user) {
    return null;
  }

  // Mock stats - will be replaced with real API calls
  const stats = [
    {
      label: 'Total Mavericks',
      value: '24',
      icon: <Users className="w-8 h-8 text-blue-600" />,
      change: '+12%',
      positive: true,
    },
    {
      label: 'Active Batches',
      value: '3',
      icon: <BookOpen className="w-8 h-8 text-green-600" />,
      change: '+5%',
      positive: true,
    },
    {
      label: 'Deployments',
      value: '15',
      icon: <Briefcase className="w-8 h-8 text-purple-600" />,
      change: '+8%',
      positive: true,
    },
    {
      label: 'Success Rate',
      value: '87%',
      icon: <TrendingUp className="w-8 h-8 text-orange-600" />,
      change: '+3%',
      positive: true,
    },
  ];

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Welcome back, {user.name}! Here's an overview of your platform.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-6 mb-8 md:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat, index) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    {stat.label}
                  </p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">
                    {stat.value}
                  </p>
                  <p
                    className={`mt-2 text-sm ${
                      stat.positive ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {stat.change} from last month
                  </p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">{stat.icon}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Recent Mavericks */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Recent Mavericks
            </h2>
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-medium">M{i}</span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">
                        Maverick Student {i}
                      </p>
                      <p className="text-sm text-gray-500">
                        maverick{i}@example.com
                      </p>
                    </div>
                  </div>
                  <span className="px-3 py-1 text-xs font-medium text-green-700 bg-green-100 rounded-full">
                    Active
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Upcoming Assessments */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Upcoming Assessments
            </h2>
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900">
                      Python Assessment {i}
                    </p>
                    <p className="text-sm text-gray-500">Batch 2024-Q1</p>
                  </div>
                  <span className="text-sm text-gray-600">
                    {i} days
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
