import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Star, CheckCircle2, DollarSign, ToggleLeft, ToggleRight, Play, Eye, Check, X, MapPin } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { Navbar } from '@/components/Navbar';
import { StatusBadge } from '@/components/StatusBadge';
import { LevelBadge } from '@/components/LevelBadge';
import { specialties } from '@/lib/mockData';
import { toast } from 'sonner';
import api from '@/lib/api';

interface Job {
  id: number;
  problem_type: string;
  ai_description: string | null;
  symptom: string | null;
  status: string;
  artisan_id: number | null;
  estimated_price: number | null;
  final_price: number | null;
  created_at: string;
  city?: string;
  client_city?: string;
  photo_url?: string;
  client_name?: string;
  client_phone?: string;
  guarantee_status?: string | null;
}

interface ArtisanProfile {
  id: number;
  full_name: string | null;
  specialty: string;
  city: string;
  is_available: boolean;
  ranking_score: number;
  total_jobs: number;
  savings: number;
}

const SPECIALTY_LABELS: Record<string, string> = {
  zlayji: 'زليج',
  sebbagh: 'صباغة',
  gebbas: 'جبس',
  plombier: 'صياكة',
  electricien: 'كهرباء',
};

function getArtisanLevel(score: number, totalJobs: number): string {
  if (score >= 90 && totalJobs >= 50) return 'maalem';
  if (score >= 75 && totalJobs >= 20) return 'maitre';
  if (score >= 60 && totalJobs >= 5) return 'compagnon';
  return 'apprenti';
}

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({ opacity: 1, y: 0, transition: { delay: i * 0.08, duration: 0.4 } }),
};

const ArtisanDashboard = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<ArtisanProfile | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [available, setAvailable] = useState(true);
  const [togglingAvailability, setTogglingAvailability] = useState(false);

  const fetchDashboard = useCallback(async () => {
    try {
      const [profileRes, jobsRes] = await Promise.all([
        api.get('/artisans/me'),
        api.get('/jobs'),
      ]);
      setProfile(profileRes.data);
      setAvailable(profileRes.data.is_available);
      setJobs(jobsRes.data);
    } catch {
      toast.error('غلط فتحميل لوح التحكم');
      setProfile(null);
      setJobs([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboard();
    // Poll every 15 seconds for new offers
    const interval = setInterval(fetchDashboard, 15000);
    return () => clearInterval(interval);
  }, [fetchDashboard]);

  const toggleAvailability = async () => {
    if (!profile) return;
    const newVal = !available;
    try {
      setTogglingAvailability(true);
      await api.patch(`/artisans/${profile.id}/availability`, { is_available: newVal });
      setAvailable(newVal);
      toast.success(newVal ? 'أنت متاح دابا' : 'غيرت حالتك لـ غير متاح');
    } catch {
      toast.error('غلط فتغيير الحالة');
    } finally {
      setTogglingAvailability(false);
    }
  };

  const handleAccept = async (jobId: number) => {
    try {
      await api.patch(`/jobs/${jobId}/accept`);
      toast.success('قبلتي الطلب! شوف تفاصيل العميل');
      fetchDashboard();
      navigate(`/artisan/jobs/${jobId}`);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(msg || 'غلط فالقبول');
    }
  };

  const handleRefuse = async (jobId: number) => {
    try {
      const res = await api.patch(`/jobs/${jobId}/refuse`);
      const deducted = res.data?.points_deducted ?? 10;
      toast.warning(`رفضتي الطلب ← تنقصك -${deducted} (وحتى ${deducted}-) نقطة. نقطتك دابا: ${res.data?.new_score ?? '—'}`);
      fetchDashboard();
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(msg || 'غلط فالرفض');
    }
  };

  const pendingOffers = jobs.filter((j) => j.status === 'matching');
  const activeJobs = jobs.filter((j) => ['accepted', 'in_progress'].includes(j.status));
  const completedJobs = jobs.filter((j) => j.status === 'completed');
  const totalEarnings = completedJobs.reduce((sum, j) => sum + (j.final_price ?? 0) * 0.5, 0);

  const stats = [
    { icon: CheckCircle2, label: 'خدمات كملو', value: String(completedJobs.length), color: 'text-success' },
    { icon: Star, label: 'تنقيط', value: profile ? String(Math.round(profile.ranking_score)) : '—', color: 'text-warning' },
    { icon: DollarSign, label: 'الأرباح', value: `${Math.round(totalEarnings)} MAD`, color: 'text-foreground' },
    { icon: DollarSign, label: 'الادخار', value: `${Math.round(profile?.savings ?? 0)} MAD`, color: 'text-success' },
    { icon: MapPin, label: 'المدينة', value: profile?.city || '—', color: 'text-accent' },
  ];

  if (loading && !profile) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="container mx-auto px-4 py-8">
          <div className="rounded-2xl border border-border bg-card p-6 mb-6 animate-pulse">
            <div className="h-16 w-16 rounded-full bg-muted mb-4" />
            <div className="h-6 w-48 bg-muted rounded mb-2" />
            <div className="h-4 w-32 bg-muted rounded" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="container mx-auto px-4 py-8">

        {/* Profile summary */}
        <motion.div initial="hidden" animate="visible" variants={fadeUp} custom={0} className="rounded-2xl border border-border bg-card p-6 mb-6 shadow-card">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-5">
            <div className="relative">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold text-xl">
                {(profile?.full_name || user?.name)?.charAt(0) || 'M'}
              </div>
              <div className="absolute -bottom-1 -right-1">
                <LevelBadge level={profile ? getArtisanLevel(profile.ranking_score, profile.total_jobs) : 'apprenti'} />
              </div>
            </div>
            <div className="flex-1">
              <h1 className="text-xl font-extrabold text-foreground">{profile?.full_name || user?.name}</h1>
              <p className="text-sm text-muted-foreground">
                {SPECIALTY_LABELS[profile?.specialty || ''] || specialties.find(s => s.id === profile?.specialty)?.nameFr || 'معلم'} • {profile?.city || 'آسفي'}
              </p>
              <div className="mt-2 flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 rounded-full bg-muted overflow-hidden">
                    <div className="h-full rounded-full bg-accent" style={{ width: `${profile ? Math.min(100, profile.ranking_score) : 35}%` }} />
                  </div>
                  <span className="text-xs font-semibold text-muted-foreground">{profile?.ranking_score ?? 35}/100</span>
                </div>
              </div>
            </div>
            <button
              onClick={toggleAvailability}
              disabled={loading || togglingAvailability}
              className={`flex items-center gap-3 rounded-xl px-5 py-3 font-semibold text-sm transition-all disabled:opacity-50 ${available ? 'bg-success/10 text-success border border-success/30' : 'bg-muted text-muted-foreground border border-border'}`}
            >
              {available ? <ToggleRight className="h-5 w-5" /> : <ToggleLeft className="h-5 w-5" />}
              {available ? 'أنا موجود' : 'غير متاح'}
            </button>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div initial="hidden" animate="visible" className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          {stats.map((s, i) => (
            <motion.div key={s.label} variants={fadeUp} custom={i + 1} className="rounded-2xl border border-border bg-card p-5 shadow-card">
              <s.icon className={`h-5 w-5 ${s.color} mb-3`} />
              <p className="text-2xl font-extrabold text-foreground">{s.value}</p>
              <p className="text-xs text-muted-foreground font-medium">{s.label}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Pending Offers */}
        {pendingOffers.length > 0 && (
          <motion.div initial="hidden" animate="visible" variants={fadeUp} custom={5} className="mb-8">
            <h2 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
              🔔 طلبات جديدة وصلاتك
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-destructive text-white text-[11px] font-bold animate-pulse">
                {pendingOffers.length}
              </span>
            </h2>
            <div className="space-y-4">
              {pendingOffers.map((offer) => {
                const specialtyLabel = SPECIALTY_LABELS[offer.problem_type] || offer.problem_type;
                const desc = offer.ai_description?.slice(0, 80) || offer.symptom?.slice(0, 80) || specialtyLabel;
                const artisanPrice = offer.estimated_price ? Math.round(offer.estimated_price * 0.5) : null;

                return (
                  <div key={offer.id} className="rounded-2xl border-2 border-accent/40 bg-gradient-to-br from-accent/5 to-card p-5 shadow-card">
                    <div className="flex items-start gap-4 mb-4">
                      {/* Photo */}
                      {offer.photo_url ? (
                        <img
                          src={offer.photo_url}
                          alt="مشكلة العميل"
                          className="w-20 h-20 rounded-xl object-cover border-2 border-border flex-shrink-0"
                        />
                      ) : (
                        <div className="w-20 h-20 rounded-xl bg-muted flex items-center justify-center flex-shrink-0 text-3xl">
                          {offer.problem_type === 'electricien' ? '⚡' :
                            offer.problem_type === 'plombier' ? '🔧' :
                              offer.problem_type === 'zlayji' ? '🪟' :
                                offer.problem_type === 'sebbagh' ? '🎨' : '🏗️'}
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-bold bg-accent/20 text-accent px-2 py-0.5 rounded-full">{specialtyLabel}</span>
                        </div>
                        <p className="font-semibold text-foreground text-sm leading-relaxed">{desc}{desc.length >= 80 ? '…' : ''}</p>
                        <p className="text-sm text-muted-foreground flex items-center gap-1 mt-1.5">
                          <MapPin className="h-3.5 w-3.5" />
                          {offer.client_city || offer.city || '—'}
                        </p>
                      </div>
                      {/* Price for artisan (50%) */}
                      <div className="text-right flex-shrink-0">
                        <p className="text-xs text-muted-foreground">ربحك</p>
                        <p className="text-2xl font-extrabold text-accent">
                          {artisanPrice != null ? `${artisanPrice}` : '—'}
                        </p>
                        {artisanPrice != null && <p className="text-xs text-muted-foreground">MAD</p>}
                      </div>
                    </div>
                    <div className="flex gap-3">
                      <button
                        onClick={() => handleAccept(offer.id)}
                        className="flex-1 flex items-center justify-center gap-2 rounded-xl border border-emerald-300 bg-emerald-100 py-3 text-sm font-extrabold text-emerald-900 hover:bg-emerald-200 transition-colors shadow-sm"
                        title="قبول الطلب"
                        aria-label="قبول الطلب"
                      >
                        <Check className="h-4 w-4" /> نقبل الطلب
                      </button>
                      <button
                        onClick={() => handleRefuse(offer.id)}
                        className="flex-1 flex items-center justify-center gap-2 rounded-xl bg-destructive/10 border border-destructive/30 py-3 text-sm font-bold text-destructive hover:bg-destructive/20 transition-colors"
                      >
                        <X className="h-4 w-4" /> رفض الطلب ( خصم 10 نقاط )
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}

        {pendingOffers.length === 0 && (
          <motion.div variants={fadeUp} custom={5} initial="hidden" animate="visible" className="mb-8 rounded-2xl border border-dashed border-border bg-card p-8 text-center">
            <p className="text-4xl mb-3">⏳</p>
            <p className="text-foreground font-semibold">ما وصلك حتى طلب دابا</p>
            <p className="text-sm text-muted-foreground mt-1">خليك متاح وانتظر — غادي يوصلك إشعار</p>
          </motion.div>
        )}

        {/* Active Jobs */}
        <motion.div initial="hidden" animate="visible" variants={fadeUp} custom={6}>
          <h2 className="text-lg font-bold text-foreground mb-4">الخدمات لي شاد دابا</h2>
          {activeJobs.length === 0 && !loading ? (
            <p className="text-muted-foreground text-sm">ما شاد حتى خدمة دابا.</p>
          ) : (
            <div className="space-y-3">
              {activeJobs.map((job, i) => {
                const artisanPrice = job.final_price ? Math.round(job.final_price * 0.5) : (job.estimated_price ? Math.round(job.estimated_price * 0.5) : null);
                const desc = job.ai_description?.slice(0, 50) || job.symptom?.slice(0, 50) || SPECIALTY_LABELS[job.problem_type] || job.problem_type;
                return (
                  <motion.div key={job.id} variants={fadeUp} custom={i + 7} className="rounded-2xl border border-border bg-card p-5 shadow-card">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <p className="font-semibold text-foreground">{desc}{(job.ai_description?.length || job.symptom?.length || 0) > 50 ? '…' : ''}</p>
                        <p className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
                          <MapPin className="h-3 w-3" />{job.client_city || job.city || '—'}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-accent">{artisanPrice != null ? `${artisanPrice} MAD` : '—'}</span>
                        <StatusBadge status={job.status} />
                      </div>
                    </div>
                    <div className="flex gap-2 justify-end">
                      {job.status === 'accepted' && (
                        <button
                          onClick={() => navigate(`/artisan/jobs/${job.id}`)}
                          className="inline-flex items-center gap-1.5 rounded-lg bg-accent/10 px-3 py-1.5 text-xs font-semibold text-accent hover:bg-accent/20 transition-colors"
                        >
                          <Play className="h-3 w-3" /> ابدا الخدمة
                        </button>
                      )}
                      <button
                        onClick={() => navigate(`/artisan/jobs/${job.id}`)}
                        className="inline-flex items-center gap-1.5 rounded-lg bg-muted px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-muted/80 transition-colors"
                      >
                        <Eye className="h-3 w-3" /> تفاصيل
                      </button>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </motion.div>

        {/* Earnings breakdown */}
        <motion.div initial="hidden" animate="visible" variants={fadeUp} custom={9} className="mt-8 rounded-2xl border border-border bg-card p-6 shadow-card">
          <h2 className="font-bold text-foreground mb-4">تقسيم الأرباح</h2>
          <p className="text-sm text-muted-foreground mb-3">الادخار الحالي ديالك: <span className="font-bold text-success">{Math.round(profile?.savings ?? 0)} MAD</span></p>
          <div className="space-y-3">
            {[
              { label: 'أرباحك (50%)', pct: 50, color: 'bg-accent' },
              { label: 'التوفير (30%)', pct: 30, color: 'bg-success' },
              { label: 'المنصة (20%)', pct: 20, color: 'bg-muted-foreground' },
            ].map((item) => (
              <div key={item.label}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-muted-foreground">{item.label}</span>
                  <span className="font-semibold text-foreground">{item.pct}%</span>
                </div>
                <div className="h-2 rounded-full bg-muted overflow-hidden">
                  <div className={`h-full rounded-full ${item.color}`} style={{ width: `${item.pct}%` }} />
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ArtisanDashboard;
