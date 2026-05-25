"use client";

import { ReactNode, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore, UserRole } from '@/store/authStore';
import {
  Home, Users, BookOpen, Briefcase, BarChart3, Settings,
  LogOut, Menu, X, GraduationCap, Calendar, FileText, UserPlus,
  TrendingUp, Award, Clock, Target, Shield, DollarSign, Sparkles
} from 'lucide-react';
import NotificationBell from './NotificationBell';

interface NavItem {
  label: string;
  href: string;
  icon: ReactNode;
  roles: UserRole[];
}

const navigationItems: NavItem[] = [
  // Super Admin Exclusive Navigation
  {
    label: 'Admin Dashboard',
    href: '/admin/dashboard',
    icon: <Shield className="w-5 h-5" />,
    roles: ['super_admin'],
  },
  {
    label: 'User Management',
    href: '/admin/users',
    icon: <Users className="w-5 h-5" />,
    roles: ['super_admin'],
  },
  {
    label: 'Organization Analytics',
    href: '/admin/analytics',
    icon: <BarChart3 className="w-5 h-5" />,
    roles: ['super_admin'],
  },
  {
    label: 'AI Cost Analytics',
    href: '/admin/ai-analytics',
    icon: <DollarSign className="w-5 h-5" />,
    roles: ['super_admin'],
  },

  // HR & Admin Navigation
  {
    label: 'HR Dashboard',
    href: '/dashboard',
    icon: <Home className="w-5 h-5" />,
    roles: ['hr'], // Removed super_admin - they have their own dashboard
  },
  {
    label: 'AI Talent Search',
    href: '/hr/talent-search',
    icon: <Sparkles className="w-5 h-5" />,
    roles: ['super_admin', 'hr', 'manager'],
  },
  {
    label: 'Pending Profiles',
    href: '/hr/pending',
    icon: <Users className="w-5 h-5" />,
    roles: ['super_admin', 'hr'],
  },
  {
    label: 'Mavericks',
    href: '/mavericks',
    icon: <Users className="w-5 h-5" />,
    roles: ['super_admin', 'hr'],
  },
  {
    label: 'Pipelines',
    href: '/pipelines',
    icon: <BookOpen className="w-5 h-5" />,
    roles: ['super_admin', 'hr'],
  },
  {
    label: 'Batches',
    href: '/batches',
    icon: <GraduationCap className="w-5 h-5" />,
    roles: ['super_admin', 'hr'],
  },
  {
    label: 'Trainers',
    href: '/trainers',
    icon: <UserPlus className="w-5 h-5" />,
    roles: ['super_admin', 'hr'],
  },
  {
    label: 'Assessments',
    href: '/assessments',
    icon: <FileText className="w-5 h-5" />,
    roles: ['super_admin', 'hr'],
  },
  {
    label: 'Deployments',
    href: '/deployments',
    icon: <Briefcase className="w-5 h-5" />,
    roles: ['super_admin', 'hr', 'manager'],
  },
  {
    label: 'Analytics',
    href: '/analytics',
    icon: <BarChart3 className="w-5 h-5" />,
    roles: ['hr'],  // Removed super_admin - they have Organization Analytics
  },

  // Trainer Navigation
  {
    label: 'Dashboard',
    href: '/trainer/dashboard',
    icon: <Home className="w-5 h-5" />,
    roles: ['trainer'],
  },
  {
    label: 'My Batches',
    href: '/trainer/batches',
    icon: <GraduationCap className="w-5 h-5" />,
    roles: ['trainer'],
  },
  {
    label: 'Assessments',
    href: '/trainer/assessments',
    icon: <FileText className="w-5 h-5" />,
    roles: ['trainer'],
  },

  // Manager Navigation
  {
    label: 'Dashboard',
    href: '/manager/dashboard',
    icon: <Home className="w-5 h-5" />,
    roles: ['manager'],
  },
  {
    label: 'Search Talent',
    href: '/manager/search',
    icon: <Users className="w-5 h-5" />,
    roles: ['manager'],
  },
  {
    label: 'Deployment Requests',
    href: '/deployments/requests',
    icon: <Briefcase className="w-5 h-5" />,
    roles: ['manager'],
  },
  {
    label: 'My Team',
    href: '/manager/team',
    icon: <Users className="w-5 h-5" />,
    roles: ['manager'],
  },
  {
    label: 'Analytics',
    href: '/trainer/analytics',
    icon: <BarChart3 className="w-5 h-5" />,
    roles: ['trainer'],
  },

  // Student (Maverick) Navigation
  {
    label: 'My Dashboard',
    href: '/student/dashboard',
    icon: <Home className="w-5 h-5" />,
    roles: ['maverick'],
  },
  {
    label: 'My Progress',
    href: '/student/progress',
    icon: <TrendingUp className="w-5 h-5" />,
    roles: ['maverick'],
  },
  {
    label: 'My Batch',
    href: '/student/batch',
    icon: <Users className="w-5 h-5" />,
    roles: ['maverick'],
  },
  {
    label: 'My Assessments',
    href: '/student/assessments',
    icon: <Award className="w-5 h-5" />,
    roles: ['maverick'],
  },
  {
    label: 'Training Schedule',
    href: '/student/schedule',
    icon: <Calendar className="w-5 h-5" />,
    roles: ['maverick'],
  },
  {
    label: 'My Profile',
    href: '/student/profile',
    icon: <Target className="w-5 h-5" />,
    roles: ['maverick'],
  },

  // Common
  {
    label: 'Settings',
    href: '/settings',
    icon: <Settings className="w-5 h-5" />,
    roles: ['super_admin', 'hr', 'trainer', 'manager', 'maverick'],
  },
];

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isClient, setIsClient] = useState(false);

  // Ensure we're on the client before accessing router
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Handle auth redirect on client side only
  useEffect(() => {
    if (isClient && !user) {
      router.push('/login');
    }
  }, [isClient, user, router]);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  // Show nothing during SSR or while checking auth
  if (!isClient || !user) {
    return null;
  }

  // Filter navigation based on user role
  const allowedNavItems = navigationItems.filter((item) =>
    item.roles.includes(user.role)
  );

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b">
            <h1 className="text-xl font-bold text-blue-900">
              Maverick Ascend
            </h1>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* User Info */}
          <div className="px-6 py-4 border-b">
            <p className="text-sm font-medium text-gray-900">{user.name}</p>
            <p className="text-xs text-gray-500">{user.email}</p>
            <span className="inline-block px-2 py-1 mt-2 text-xs font-medium text-blue-700 bg-blue-100 rounded">
              {user.role.replace('_', ' ').toUpperCase()}
            </span>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
            {allowedNavItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-600 transition-colors"
                onClick={() => setSidebarOpen(false)}
              >
                {item.icon}
                <span className="ml-3 text-sm font-medium">{item.label}</span>
              </Link>
            ))}
          </nav>

          {/* Logout Button */}
          <div className="p-4 border-t">
            <button
              onClick={handleLogout}
              className="flex items-center w-full px-4 py-3 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
            >
              <LogOut className="w-5 h-5" />
              <span className="ml-3 text-sm font-medium">Logout</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top Bar */}
        <header className="flex items-center justify-between h-16 px-6 bg-white border-b">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden"
          >
            <Menu className="w-6 h-6" />
          </button>

          <div className="flex items-center space-x-4">
            <NotificationBell />
            <span className="text-sm text-gray-600">
              Welcome back, <span className="font-medium">{user.name}</span>
            </span>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100">
          {children}
        </main>
      </div>
    </div>
  );
}
