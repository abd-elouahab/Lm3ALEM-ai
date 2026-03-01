import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { Wrench, User as UserIcon, HardHat, Mail, Lock, Phone, ChevronDown, Eye, EyeOff } from 'lucide-react';
import { useAuthStore, type UserRole, type User } from '@/store/authStore';
import { specialties, cities, cityCoords } from '@/lib/mockData';
import { toast } from 'sonner';
import zelligePattern from '@/assets/zellige-pattern.jpg';
import api from '@/lib/api';

const AuthPage = () => {
  const [searchParams] = useSearchParams();
  const [tab, setTab] = useState<'login' | 'register'>(searchParams.get('tab') === 'register' ? 'register' : 'login');
  const [role, setRole] = useState<UserRole | null>((searchParams.get('role') as UserRole) || null);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login, isAuthenticated, user } = useAuthStore();

  // Default to client when on register tab so the form is valid and city field is shown
  useEffect(() => {
    if (tab === 'register' && role === null) {
      setRole('client');
    }
  }, [tab, role]);

  useEffect(() => {
    if (isAuthenticated && user) {
      navigate(user.role === 'artisan' ? '/artisan/dashboard' : '/client/dashboard');
    }
  }, [isAuthenticated, user, navigate]);

  const { register, handleSubmit, formState: { errors } } = useForm();

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const onSubmit = async (data: any) => {
    setLoading(true);
    const timeoutMs = 20000;
    try {
      if (tab === 'login') {
        const formData = new URLSearchParams();
        formData.append('username', data.email);
        formData.append('password', data.password);
        const tokenRes = await api.post('/auth/login', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          timeout: timeoutMs,
        });
        const token = tokenRes.data.access_token;
        const meRes = await api.get('/auth/me', { headers: { Authorization: `Bearer ${token}` } });
        const u = meRes.data;
        const frontendUser: User = {
          id: String(u.id),
          name: u.full_name,
          email: u.email,
          role: u.role as UserRole,
          phone: u.phone ?? undefined,
          city: undefined,
          specialty: undefined,
        };
        login(token, frontendUser);
        toast.success('دخلت بنجاح !');
        navigate(frontendUser.role === 'artisan' ? '/artisan/dashboard' : '/client/dashboard');
      } else {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const payload: any = {
          email: data.email,
          password: data.password,
          full_name: data.name || data.email?.split('@')[0] || 'Utilisateur',
          role: role || 'client',
          phone: data.phone || null,
        };
        if (role === 'artisan') {
          payload.specialty = data.specialty;
          const coords = cityCoords[data.city] || cityCoords['Agadir'];
          payload.city = coords.city;
          payload.latitude = coords.lat;
          payload.longitude = coords.lng;
        } else {
          const coords = cityCoords[data.client_city || 'Agadir'] || cityCoords['Agadir'];
          payload.client_city = coords.city;
          payload.client_latitude = coords.lat;
          payload.client_longitude = coords.lng;
        }
        const regRes = await api.post('/auth/register', payload, { timeout: timeoutMs });
        const u = regRes.data;
        const formData = new URLSearchParams();
        formData.append('username', data.email);
        formData.append('password', data.password);
        const tokenRes = await api.post('/auth/login', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          timeout: timeoutMs,
        });
        const token = tokenRes.data.access_token;
        const frontendUser: User = {
          id: String(u.id),
          name: u.full_name,
          email: u.email,
          role: u.role as UserRole,
          phone: u.phone ?? undefined,
          city: role === 'artisan' ? payload.city : payload.client_city,
          specialty: role === 'artisan' ? payload.specialty : undefined,
        };
        login(token, frontendUser);
        toast.success('Compte créé avec succès !');
        navigate(frontendUser.role === 'artisan' ? '/artisan/dashboard' : '/client/dashboard');
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      let msg = 'غلط فالدخول';
      if (tab === 'login') msg = 'الإيميل أو كلمة السر غالطة';
      if (err.code === 'ECONNABORTED' || !err.response) {
        msg = 'الخادم ما جاوبش. تأكد أن الباك إند شارط على localhost:8000';
      } else if (err.response?.data?.detail) {
        const d = err.response.data.detail;
        msg = Array.isArray(d) ? d[0]?.msg || String(d) : String(d);
      }
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <div className="absolute inset-0 gradient-hero" />
        <div className="absolute inset-0 opacity-[0.08] bg-cover bg-center" style={{ backgroundImage: `url(${zelligePattern})` }} />
        <div className="relative flex flex-col items-center justify-center p-12 text-center w-full">
          <div className="flex items-center justify-center mb-8">
            <img src="/placeholder.svg" alt="L'M3alem Logo" className="h-16 w-auto object-contain" />
          </div>
          <h2 className="text-2xl font-bold text-primary-foreground/90 mb-4 max-w-md">
            المنصة لي كتربط المعلمين ديال سوس ماسة بلي محتاجينهم
          </h2>
          <p className="text-primary-foreground/50 max-w-sm">
            ذكاء اصطناعي • ماتشينغ ذكي • ضمان 48 ساعة
          </p>
        </div>
      </div>

      {/* Right panel */}
      <div className="flex-1 flex items-center justify-center p-6 md:p-12 bg-background">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center justify-center mb-8">
            <img src="/placeholder.svg" alt="L'M3alem Logo" className="h-12 w-auto object-contain" />
          </div>

          {/* Tab toggle */}
          <div className="flex rounded-xl bg-muted p-1 mb-8">
            {(['login', 'register'] as const).map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all ${tab === t ? 'bg-card text-foreground shadow-sm' : 'text-muted-foreground'
                  }`}
              >
                {t === 'login' ? 'دخول' : 'تسجيل'}
              </button>
            ))}
          </div>

          <AnimatePresence mode="wait">
            <motion.div
              key={tab}
              initial={{ opacity: 0, x: tab === 'login' ? -20 : 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: tab === 'login' ? 20 : -20 }}
              transition={{ duration: 0.2 }}
            >
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                {tab === 'register' && (
                  <>
                    <div className="space-y-3">
                      <label className="text-sm font-semibold text-foreground">أنا :</label>
                      <div className="grid grid-cols-2 gap-3">
                        {[
                          { value: 'client' as UserRole, icon: UserIcon, label: 'أنا عميل', desc: '' },
                          { value: 'artisan' as UserRole, icon: HardHat, label: 'أنا معلم', desc: '' },
                        ].map((r) => (
                          <button
                            key={r.value}
                            type="button"
                            onClick={() => setRole(r.value)}
                            className={`rounded-xl border-2 p-4 text-left transition-all ${role === r.value
                              ? 'border-accent bg-accent/5 shadow-sm'
                              : 'border-border hover:border-muted-foreground/30'
                              }`}
                          >
                            <r.icon className={`h-6 w-6 mb-2 ${role === r.value ? 'text-accent' : 'text-muted-foreground'}`} />
                            <p className="font-bold text-sm text-foreground">{r.label}</p>
                            <p className="text-xs text-muted-foreground">{r.desc}</p>
                          </button>
                        ))}
                      </div>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-foreground mb-1.5 block">الاسم الكامل</label>
                      <input
                        {...register('name', { required: tab === 'register' ? 'Requis' : false })}
                        className="w-full rounded-xl border border-input bg-card px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-accent/50 transition-all"
                        placeholder="الاسم الكامل"
                      />
                    </div>
                    {role === 'client' && (
                      <div>
                        <label className="text-sm font-medium text-foreground mb-1.5 block">المدينة</label>
                        <div className="relative">
                          <select
                            {...register('client_city')}
                            className="w-full rounded-xl border border-input bg-card px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-accent/50 appearance-none transition-all"
                          >
                            {cities.map((c) => (
                              <option key={c} value={c}>{c}</option>
                            ))}
                          </select>
                          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
                        </div>
                      </div>
                    )}
                  </>
                )}

                <div>
                  <label className="text-sm font-medium text-foreground mb-1.5 block">الإيميل</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <input
                      {...register('email', { required: 'Requis' })}
                      type="email"
                      className="w-full rounded-xl border border-input bg-card pl-10 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-accent/50 transition-all"
                      placeholder="votre@email.com"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-foreground mb-1.5 block">كلمة السر</label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <input
                      {...register('password', { required: 'Requis' })}
                      type={showPassword ? 'text' : 'password'}
                      className="w-full rounded-xl border border-input bg-card pl-10 pr-12 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-accent/50 transition-all"
                      placeholder="••••••••"
                    />
                    <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                {tab === 'register' && role === 'artisan' && (
                  <>
                    <div>
                      <label className="text-sm font-medium text-foreground mb-1.5 block">التخصص</label>
                      <div className="relative">
                        <select
                          {...register('specialty', { required: role === 'artisan' ? 'Requis' : false })}
                          className="w-full rounded-xl border border-input bg-card px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-accent/50 appearance-none transition-all"
                        >
                          <option value="">اختار التخصص</option>
                          {specialties.map((s) => (
                            <option key={s.id} value={s.id}>{s.name} — {s.nameFr}</option>
                          ))}
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
                      </div>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-foreground mb-1.5 block">المدينة</label>
                      <div className="relative">
                        <select
                          {...register('city', { required: role === 'artisan' ? 'Requis' : false })}
                          className="w-full rounded-xl border border-input bg-card px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-accent/50 appearance-none transition-all"
                        >
                          <option value="">اختار المدينة</option>
                          {cities.map((c) => (
                            <option key={c} value={c}>{c}</option>
                          ))}
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
                      </div>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-foreground mb-1.5 block">رقم الهاتف</label>
                      <div className="relative">
                        <Phone className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <input
                          {...register('phone')}
                          type="tel"
                          className="w-full rounded-xl border border-input bg-card pl-10 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-accent/50 transition-all"
                          placeholder="+212 6XX XX XX XX"
                        />
                      </div>
                    </div>
                  </>
                )}

                {tab === 'login' && (
                  <details className="rounded-xl border border-border bg-muted/30 p-3 text-xs text-muted-foreground">
                    <summary className="cursor-pointer font-semibold text-foreground select-none">🔑 حسابات تجريبية</summary>
                    <div className="mt-2 space-y-1.5">
                      <p className="font-bold text-foreground mt-1">معلمين (artisan):</p>
                      <p>ahmed.zlayji@example.com / maalem123 → زليج - أكادير</p>
                      <p>fatima.sebbagh@example.com / maalem123 → صباغة</p>
                      <p>hassan.plombier@example.com / maalem123 → صياكة</p>
                      <p>khalid.electricien@example.com / maalem123 → كهرباء</p>
                      <p className="font-bold text-foreground mt-1">عملاء (client):</p>
                      <p>client1@test.com / client123</p>
                      <p>client2@test.com / client123</p>
                    </div>
                  </details>
                )}

                <button
                  type="submit"
                  disabled={loading || (tab === 'register' && !role)}
                  className="w-full rounded-xl bg-accent py-3.5 text-sm font-bold text-accent-foreground shadow-accent hover:opacity-90 disabled:opacity-50 transition-all"
                >
                  {loading ? (
                    <span className="inline-flex items-center gap-2">
                      جار التحميل...
                    </span>
                  ) : tab === 'login' ? 'دخل' : "سجل"}
                </button>
              </form>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
