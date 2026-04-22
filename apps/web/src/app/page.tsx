"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="text-center space-y-6">
        <h1 className="text-5xl font-bold text-gray-900">
          Maverick Talent Insights
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl">
          AI-Powered Training Performance & Competency Tracking Dashboard
        </p>
        <div className="pt-8 space-y-2">
          <p className="text-sm text-gray-500">✅ Day 1-3: Foundation Complete!</p>
          <p className="text-sm text-gray-500">Backend API + Frontend Ready</p>
        </div>
        <div className="pt-8 flex gap-4 justify-center">
          <Link
            href="/login"
            className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            Sign In →
          </Link>
          <Link
            href="/register"
            className="inline-flex items-center justify-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            Register
          </Link>
        </div>
      </div>
    </main>
  );
}
