import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Plus, Briefcase, Clock, CheckCircle2, DollarSign, ArrowLeft, Trash2 } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { Navbar } from '@/components/Navbar';
import { StatusBadge } from '@/components/StatusBadge';
import { specialties } from '@/lib/mockData';
import api from '@/lib/api';
import { toast } from 'sonner';

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({ opacity: 1, y: 0, transition: { delay: i * 0.08, duration: 0.4 } }),
};

interface JobItem {
  id: number;
  problem_type: string;
  symptom: string | null;
  status: string;
  artisan_id: number | null;
  estimated_price_min: number | null;
  estimated_price_max: number | null;
  final_price: number | null;
  created_at: string;
  ai_description?: string | null;
}

const ClientDashboard = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoading(true);
        const response = await api.get<JobItem[]>('/jobs');
        setJobs(response.data || []);
      } catch {
        toast.error('Erreur lors du chargement des demandes');
      } finally {
        setLoading(false);
      }
    };
    fetchJobs();
  }, []);

  const handleDelete = async (e: React.MouseEvent, jobId: number) => {
    e.stopPropagation(); // don't navigate to job detail
    if (!window.confirm('واش متأكد بغيتي تمسح هاد الطلب؟')) return;
    try {
      await api.delete(`/jobs/${jobId}`);
      toast.success('تمسح الطلب بنجاح');
      setJobs(prev => prev.filter(j => j.id !== jobId));
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(msg || 'مشات حاجة غلط');
    }
  };

  const stats = [
    { icon: Briefcase, label: 'طلب خدمة جديد', value: jobs.length, color: 'text-accent' },
    { icon: Clock, label: 'فالخدمة', value: jobs.filter(j => ['matching', 'accepted', 'in_progress'].includes(j.status)).length, color: 'text-warning' },
    { icon: CheckCircle2, label: 'كمل', value: jobs.filter(j => j.status === 'completed').length, color: 'text-success' },
    { icon: DollarSign, label: 'المجموع', value: `${jobs.filter(j => j.status === 'completed').reduce((sum, j) => sum + (j.final_price || 0), 0).toLocaleString('fr-FR')} MAD`, color: 'text-foreground' },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        {/* Welcome */}
        <motion.div initial="hidden" animate="visible" variants={fadeUp} custom={0} className="mb-8">
          <h1 className="text-2xl md:text-3xl font-extrabold text-foreground mb-2">
            مرحبا {user?.name?.split(' ')[0]}
          </h1>
          <p className="text-muted-foreground">تبع الطلبات ديالك من هنا.</p>
        </motion.div>

        {/* Stats */}
        <motion.div initial="hidden" animate="visible" className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {stats.map((s, i) => (
            <motion.div key={s.label} variants={fadeUp} custom={i} className="rounded-2xl border border-border bg-card p-5 shadow-card">
              <s.icon className={`h-5 w-5 ${s.color} mb-3`} />
              <p className="text-2xl font-extrabold text-foreground">{s.value}</p>
              <p className="text-xs text-muted-foreground font-medium">{s.label}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* New Job CTA */}
        <motion.div initial="hidden" animate="visible" variants={fadeUp} custom={4}>
          <Link
            to="/client/new-job"
            className="flex items-center justify-between rounded-2xl gradient-accent p-6 mb-8 group hover:opacity-95 transition-opacity shadow-accent"
          >
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent-foreground/20">
                <Plus className="h-6 w-6 text-accent-foreground" />
              </div>
              <div>
                <p className="text-lg font-bold text-accent-foreground">طلب خدمة جديد</p>
                <p className="text-sm text-accent-foreground/70">صور المشكلة ديالك وحنا نقلبو ليك على معلم</p>
              </div>
            </div>
            <ArrowLeft className="h-5 w-5 text-accent-foreground group-hover:-translate-x-1 transition-transform" />
          </Link>
        </motion.div>

        {/* Jobs List */}
        <motion.div initial="hidden" animate="visible">
          <h2 className="text-lg font-bold text-foreground mb-4">طلباتي</h2>
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="rounded-2xl border border-border bg-card p-5 h-24 animate-pulse bg-muted/30" />
              ))}
            </div>
          ) : jobs.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">ماكاين طلب حتى واحد للحين.</p>
          ) : (
            <div className="space-y-3">
              {jobs.map((job, i) => {
                const spec = specialties.find(s => s.id === job.problem_type);
                const priceStr = job.final_price != null
                  ? `${job.final_price} MAD`
                  : (job.estimated_price_min != null && job.estimated_price_max != null)
                    ? `${job.estimated_price_min} – ${job.estimated_price_max} MAD`
                    : '—';
                const dateStr = job.created_at ? new Date(job.created_at).toLocaleDateString('fr-FR') : '—';
                return (
                  <motion.div
                    key={job.id}
                    variants={fadeUp}
                    custom={i + 5}
                    onClick={() => navigate(`/client/jobs/${job.id}`)}
                    className="rounded-2xl border border-border bg-card p-5 shadow-card hover:shadow-card-hover transition-all cursor-pointer group"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent/10">
                          <span className="text-lg">{spec?.nameFr?.charAt(0) || '?'}</span>
                        </div>
                        <div>
                          <p className="font-semibold text-foreground group-hover:text-accent transition-colors">{spec?.nameFr || job.problem_type} • {job.symptom?.slice(0, 40) || job.ai_description?.slice(0, 40) || 'طلب'}</p>
                          <p className="text-xs text-muted-foreground">{spec?.nameFr} • {dateStr}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <StatusBadge status={job.status} />
                        {['pending', 'matching'].includes(job.status) && (
                          <button
                            onClick={(e) => handleDelete(e, job.id)}
                            className="flex h-8 w-8 items-center justify-center rounded-lg bg-destructive/10 text-destructive hover:bg-destructive/20 transition-colors"
                            title="مسح الطلب"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">
                        {job.artisan_id ? 'لقينا معلم' : 'كنقلبو على معلم...'}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-foreground">{priceStr}</span>
                        <ArrowLeft className="h-4 w-4 text-muted-foreground group-hover:text-accent group-hover:-translate-x-1 transition-all" />
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default ClientDashboard;
