import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { Wrench, LogOut, Bell, Menu, X, User } from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const dashboardPath = user?.role === 'artisan' ? '/artisan/dashboard' : '/client/dashboard';

  return (
    <nav className="sticky top-0 z-50 border-b border-border bg-card/80 backdrop-blur-xl">
      <div className="w-full flex h-16 items-center justify-between pr-4 md:pr-8 pl-0">
        <Link to="/" className="flex items-center group">
          <img src="/placeholder.svg" alt="L'M3alem Logo" className="h-14 md:h-16 w-auto object-contain scale-110 md:scale-125 origin-left" />
        </Link>

        {/* Desktop */}
        <div className="hidden md:flex items-center gap-4">
          {isAuthenticated ? (
            <>
              <Link to={dashboardPath} className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                لوحة التحكم
              </Link>
              <button className="relative p-2 rounded-lg hover:bg-muted transition-colors">
                <Bell className="h-5 w-5 text-muted-foreground" />
                <span className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full bg-accent text-accent-foreground text-[10px] font-bold flex items-center justify-center">2</span>
              </button>
              <div className="flex items-center gap-3 pl-3 border-l border-border">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-bold">
                  {user?.name?.charAt(0) || 'U'}
                </div>
                <span className="text-sm font-medium">{user?.name}</span>
                <button onClick={handleLogout} className="p-2 rounded-lg hover:bg-muted transition-colors text-muted-foreground hover:text-destructive">
                  <LogOut className="h-4 w-4" />
                </button>
              </div>
            </>
          ) : (
            <div className="flex items-center gap-3">
              <Link to="/auth" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                تسجيل الدخول
              </Link>
              <Link to="/auth?tab=register" className="inline-flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-accent-foreground shadow-accent hover:opacity-90 transition-opacity">
                تسجل معانا
              </Link>
            </div>
          )}
        </div>

        {/* Mobile toggle */}
        <button className="md:hidden p-2" onClick={() => setMobileOpen(!mobileOpen)}>
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="md:hidden border-t border-border bg-card overflow-hidden"
          >
            <div className="p-4 space-y-3">
              {isAuthenticated ? (
                <>
                  <div className="flex items-center gap-3 pb-3 border-b border-border">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold">
                      {user?.name?.charAt(0) || 'U'}
                    </div>
                    <div>
                      <p className="font-semibold text-sm">{user?.name}</p>
                      <p className="text-xs text-muted-foreground capitalize">{user?.role}</p>
                    </div>
                  </div>
                  <Link to={dashboardPath} onClick={() => setMobileOpen(false)} className="block py-2 text-sm font-medium">لوحة التحكم</Link>
                  <button onClick={handleLogout} className="flex items-center gap-2 py-2 text-sm font-medium text-destructive">
                    <LogOut className="h-4 w-4" /> خروج
                  </button>
                </>
              ) : (
                <>
                  <Link to="/auth" onClick={() => setMobileOpen(false)} className="block py-2 text-sm font-medium">تسجيل الدخول</Link>
                  <Link to="/auth?tab=register" onClick={() => setMobileOpen(false)} className="block py-2 text-sm font-medium text-accent">تسجل معانا</Link>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};
