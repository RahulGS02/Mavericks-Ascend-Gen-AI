/**
 * Authentication state management with Zustand
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type UserRole = 'maverick' | 'trainer' | 'hr' | 'manager' | 'super_admin';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  login: (user: User, token: string) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      setUser: (user) => set({ user, isAuthenticated: true }),
      
      setToken: (token) => {
        localStorage.setItem('access_token', token);
        set({ token });
      },
      
      login: (user, token) => {
        localStorage.setItem('access_token', token);
        set({ user, token, isAuthenticated: true });
      },
      
      logout: () => {
        // Clear all auth-related storage
        localStorage.removeItem('access_token');
        localStorage.removeItem('auth-storage');
        sessionStorage.clear();
        set({ user: null, token: null, isAuthenticated: false });
      },
      
      setLoading: (loading) => set({ isLoading: loading }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
