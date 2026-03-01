import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore, type UserRole } from '@/store/authStore';

export const ProtectedRoute = ({ allowedRole }: { allowedRole?: UserRole }) => {
  const { isAuthenticated, user } = useAuthStore();

  if (!isAuthenticated) return <Navigate to="/auth" replace />;
  if (allowedRole && user?.role !== allowedRole) {
    return <Navigate to={user?.role === 'artisan' ? '/artisan/dashboard' : '/client/dashboard'} replace />;
  }
  return <Outlet />;
};
