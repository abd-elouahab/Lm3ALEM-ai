import { create } from 'zustand';

export type UserRole = 'client' | 'artisan';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  phone?: string;
  city?: string;
  specialty?: string;
  avatar?: string;
  level?: string;
  rankingScore?: number;
  available?: boolean;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
  isClient: () => boolean;
  isArtisan: () => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: localStorage.getItem('token'),
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  isAuthenticated: !!localStorage.getItem('token'),
  login: (token, user) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    set({ token, user, isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    set({ token: null, user: null, isAuthenticated: false });
  },
  updateUser: (updates) =>
    set((state) => {
      const updated = { ...state.user!, ...updates };
      localStorage.setItem('user', JSON.stringify(updated));
      return { user: updated };
    }),
  isClient: () => (JSON.parse(localStorage.getItem('user') || '{}') as User)?.role === 'client',
  isArtisan: () => (JSON.parse(localStorage.getItem('user') || '{}') as User)?.role === 'artisan',
}));
