"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import { ArrowRight } from 'lucide-react';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            {/* Logo */}
            <div>
              <h1 className="text-2xl font-black text-blue-900 tracking-tight uppercase">
                MAVERICKS ASCEND
              </h1>
            </div>

            {/* Navigation */}
            <nav className="hidden md:flex items-center space-x-8">
              <Link
                href="/login"
                className="px-6 py-2.5 bg-blue-900 text-white text-sm font-bold uppercase tracking-wide rounded hover:bg-blue-800 transition-colors"
              >
                SIGN IN
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-20">
        <div className="max-w-4xl mx-auto text-center">
          {/* Hero Quote */}
          <div className="space-y-8">
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black leading-tight">
              <span className="text-gray-900">"THE PATH FROM POTENTIAL TO</span>
              <br />
              <span className="text-blue-900">START YOUR ASCENT TO EXCELLENCE."</span>
            </h2>

            {/* CTA Button */}
            <div className="pt-8">
              <Link
                href="/mavericks/register"
                className="inline-flex items-center gap-2 px-10 py-4 bg-blue-900 text-white text-lg font-bold uppercase tracking-wide rounded hover:bg-blue-800 transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-xl"
              >
                REGISTER
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-center items-center">
            {/* Copyright */}
            <div className="text-sm text-gray-600">
              Copyright © {new Date().getFullYear()} Mavericks. All Rights Reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
