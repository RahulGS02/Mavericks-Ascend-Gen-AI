"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import { authAPI } from '@/lib/api';
import { toast } from 'sonner';

export default function LoginPage() {
  const router = useRouter();
  const { login, setLoading } = useAuthStore();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setLoading(true);

    try {
      // Login request
      const response = await authAPI.login(email, password);
      const { access_token } = response.data;

      // Get user info
      const userResponse = await authAPI.getCurrentUser();
      const user = userResponse.data;

      // Save to store
      login(user, access_token);

      toast.success('Login successful!');
      
      // Redirect based on role
      if (user.role === 'super_admin' || user.role === 'hr') {
        router.push('/dashboard');
      } else if (user.role === 'trainer') {
        router.push('/trainer/dashboard');
      } else if (user.role === 'manager') {
        router.push('/manager/dashboard');
      } else {
        router.push('/maverick/dashboard');
      }
    } catch (error: any) {
      console.error('Login error:', error);
      toast.error(error.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setIsSubmitting(false);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50 px-4">
      <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-lg">
        <div>
          <h2 className="text-center text-3xl font-bold text-gray-900">
            Maverick Insights
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Sign in to your account
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleLogin}>
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="admin@maverick.com"
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="••••••••"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Signing in...' : 'Sign in'}
            </button>
          </div>

          <div className="text-sm text-center">
            <Link href="/register" className="font-medium text-blue-600 hover:text-blue-500">
              Don't have an account? Register
            </Link>
          </div>
        </form>

        <div className="mt-6 border-t pt-6">
          <p className="text-xs text-gray-500 text-center mb-2">Test Credentials:</p>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-gray-50 p-2 rounded">
              <p className="font-semibold">Admin</p>
              <p className="text-gray-600">admin@maverick.com</p>
              <p className="text-gray-600">admin123</p>
            </div>
            <div className="bg-gray-50 p-2 rounded">
              <p className="font-semibold">HR</p>
              <p className="text-gray-600">hr@maverick.com</p>
              <p className="text-gray-600">hr123</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
