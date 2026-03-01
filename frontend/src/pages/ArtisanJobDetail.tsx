import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Phone, MapPin, CheckCircle2, Clock, Camera } from 'lucide-react';
import { Navbar } from '@/components/Navbar';
import { StatusBadge } from '@/components/StatusBadge';
import { specialties } from '@/lib/mockData';
import api from '@/lib/api';
import { toast } from 'sonner';

interface Job {
  id: number;
  problem_type: string;
  symptom: string | null;
  ai_description: string | null;
  diagnosis_notes: string | null;
  severity: number | null;
  complexity: string | null;
  estimated_price: number | null;
  final_price: number | null;
  status: string;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  client_name?: string;
  client_phone?: string;
  client_city?: string;
  city?: string;
  photo_url?: string;
  guarantee_status?: string | null;
}

const SPECIALTY_LABELS: Record<string, string> = {
  zlayji: 'زليج',
  sebbagh: 'صباغة',
  gebbas: 'جبس',
  plombier: 'صياكة',
  electricien: 'كهرباء',
};

const COMPLEXITY_LABELS: Record<string, string> = {
  simple: 'بسيط',
  moyenne: 'متوسط',
  complexe: 'معقد',
};

const ArtisanJobDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [afterPhotoUrl, setAfterPhotoUrl] = useState('');
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  const [handlingClaim, setHandlingClaim] = useState(false);

  const fetchJob = useCallback(async () => {
    if (!id) return;
    try {
      const res = await api.get(`/jobs/${id}`);
      setJob(res.data);
    } catch {
      toast.error('غلط فتحميل تفاصيل الطلب');
      setJob(null);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { fetchJob(); }, [fetchJob]);

  const handleStartWork = async () => {
    if (!id) return;
    try {
      setStarting(true);
      const now = new Date();
      const end = new Date(now.getTime() + 2 * 60 * 60 * 1000);
      await api.patch(`/jobs/${id}/confirm-dates`, {
        confirmed_start: now.toISOString(),
        confirmed_end: end.toISOString(),
      });
      toast.success('بدات الخدمة!');
      fetchJob();
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(msg || 'غلط');
    } finally {
      setStarting(false);
    }
  };

  const handleComplete = async () => {
    if (!id) return;
    try {
      setCompleting(true);
      await api.patch(`/jobs/${id}/complete`, {
        after_photo_url: afterPhotoUrl || undefined,
      });
      toast.success('كملات الخدمة! ضمانة 48 ساعة بدات.');
      setShowCompleteModal(false);
      navigate('/artisan/dashboard');
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(msg || 'غلط فإعلان الإتمام');
    } finally {
      setCompleting(false);
    }
  };

  const handleClaimAccept = async () => {
    if (!id) return;
    try {
      setHandlingClaim(true);
      await api.patch(`/jobs/${id}/claim-accept`);
      toast.success('قبلتي الرجوع فالضمان');
      fetchJob();
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(msg || 'غلط فالقبول');
    } finally {
      setHandlingClaim(false);
    }
  };

  const handleClaimRefuse = async () => {
    if (!id) return;
    try {
      setHandlingClaim(true);
      const res = await api.patch(`/jobs/${id}/claim-refuse`);
      toast.warning(`رفضتي الرجوع فالضمان. خصم 10 نقاط + تحويل ${res.data?.savings_transferred_to_platform ?? 0} MAD للمنصة.`);
      navigate('/artisan/dashboard');
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(msg || 'غلط فالرفض');
    } finally {
      setHandlingClaim(false);
    }
  };

  if (loading && !job) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="container mx-auto px-4 py-8">
          <div className="h-64 rounded-2xl bg-card animate-pulse border border-border" />
        </div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="container mx-auto px-4 py-8 text-center">
          <p className="text-muted-foreground">ما لقيناش هاد الطلب.</p>
          <button onClick={() => navigate('/artisan/dashboard')} className="mt-4 text-accent hover:underline">رجع للوح التحكم</button>
        </div>
      </div>
    );
  }

  const artisanPrice = job.estimated_price ? Math.round(job.estimated_price * 0.5) : (job.final_price ? Math.round(job.final_price * 0.5) : null);
  const clientCity = job.client_city || job.city || '—';
  const specialtyLabel = SPECIALTY_LABELS[job.problem_type] || specialties.find(s => s.id === job.problem_type)?.nameFr || job.problem_type;
  const isAccepted = ['accepted', 'in_progress', 'completed'].includes(job.status);

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="container mx-auto px-4 py-6 max-w-2xl">

        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <button onClick={() => navigate('/artisan/dashboard')} className="rounded-full p-2 hover:bg-muted transition-colors">
            <ArrowLeft className="h-5 w-5 text-foreground" />
          </button>
          <div className="flex-1">
            <h1 className="text-xl font-bold text-foreground">{specialtyLabel}</h1>
            <div className="flex items-center gap-2 mt-0.5">
              <StatusBadge status={job.status} />
              <span className="text-xs text-muted-foreground">طلب #{job.id}</span>
            </div>
          </div>
          {artisanPrice != null && (
            <div className="text-right">
              <p className="text-xs text-muted-foreground">ربحك</p>
              <p className="text-2xl font-extrabold text-accent">{artisanPrice} <span className="text-sm">MAD</span></p>
            </div>
          )}
        </div>

        {/* ── CLIENT CONTACT CARD (shown after accept) ── */}
        {isAccepted && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            className="mb-5 rounded-2xl bg-gradient-to-br from-accent/10 to-accent/5 border-2 border-accent/30 p-5 shadow-lg"
          >
            <h2 className="text-sm font-bold text-accent mb-3 flex items-center gap-2">
              <Phone className="h-4 w-4" /> اتصل بالعميل — رتبو موعد ديال الخدمة
            </h2>
            <div className="space-y-3">
              {(job.client_name) && (
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent text-white font-bold text-lg flex-shrink-0">
                    {job.client_name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-bold text-foreground">{job.client_name}</p>
                    <p className="text-xs text-muted-foreground flex items-center gap-1">
                      <MapPin className="h-3 w-3" />{clientCity}
                    </p>
                  </div>
                </div>
              )}
              {job.client_phone && (
                <a
                  href={`tel:${job.client_phone}`}
                  className="flex items-center justify-center gap-3 w-full rounded-xl bg-accent text-white py-3.5 font-bold text-base hover:opacity-90 transition-opacity shadow-md"
                >
                  <Phone className="h-5 w-5" />
                  {job.client_phone}
                </a>
              )}
              {!job.client_phone && !job.client_name && (
                <p className="text-sm text-muted-foreground text-center">معلومات العميل مش موجودة</p>
              )}
            </div>
          </motion.div>
        )}

        {/* Problem Photo */}
        {job.photo_url && (
          <div className="mb-5 rounded-2xl overflow-hidden border border-border shadow-sm">
            <img src={job.photo_url} alt="صورة المشكلة" className="w-full max-h-64 object-cover" />
            <div className="bg-card px-4 py-2 text-xs text-muted-foreground">صورة المشكلة من العميل</div>
          </div>
        )}

        {/* Problem Details */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="rounded-2xl border border-border bg-card p-5 mb-5 space-y-4">
          <h3 className="font-bold text-foreground">تفاصيل المشكلة</h3>

          {job.ai_description && (
            <div>
              <p className="text-xs text-muted-foreground mb-1">الوصف</p>
              <p className="text-sm text-foreground leading-relaxed">{job.ai_description}</p>
            </div>
          )}
          {job.diagnosis_notes && (
            <div>
              <p className="text-xs text-muted-foreground mb-1">ملاحظات</p>
              <p className="text-sm text-foreground leading-relaxed">{job.diagnosis_notes}</p>
            </div>
          )}

          <div className="grid grid-cols-3 gap-3">
            {job.severity && (
              <div className="bg-muted/40 rounded-xl p-3">
                <p className="text-xs text-muted-foreground mb-1">الخطورة</p>
                <div className="flex gap-0.5">
                  {[1, 2, 3, 4, 5].map(i => (
                    <div key={i} className={`flex-1 h-1.5 rounded-full ${i <= job.severity! ? 'bg-destructive' : 'bg-muted'}`} />
                  ))}
                </div>
              </div>
            )}
            {job.complexity && (
              <div className="bg-muted/40 rounded-xl p-3">
                <p className="text-xs text-muted-foreground mb-1">الصعوبة</p>
                <p className="text-sm font-semibold text-foreground">{COMPLEXITY_LABELS[job.complexity] || job.complexity}</p>
              </div>
            )}
            <div className="bg-accent/10 rounded-xl p-3">
              <p className="text-xs text-muted-foreground mb-1">ربحك</p>
              <p className="text-sm font-bold text-accent">{artisanPrice != null ? `${artisanPrice} MAD` : '—'}</p>
            </div>
          </div>
        </motion.div>

        {/* Action Buttons */}
        {job.guarantee_status === 'claimed' && job.status === 'accepted' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mb-3">
            <div className="rounded-2xl border border-warning/30 bg-warning/10 p-4 mb-3 text-sm text-foreground">
              هاد الخدمة فيها شكاية فالضمان. خاصك تقبل الرجوع ولا ترفض.
            </div>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={handleClaimAccept}
                disabled={handlingClaim}
                className="w-full rounded-2xl bg-accent text-white py-3 font-bold hover:opacity-90 disabled:opacity-60"
              >
                {handlingClaim ? 'جاري...' : 'نقبل الرجوع'}
              </button>
              <button
                onClick={handleClaimRefuse}
                disabled={handlingClaim}
                className="w-full rounded-2xl bg-destructive/10 border border-destructive/30 text-destructive py-3 font-bold hover:bg-destructive/20 disabled:opacity-60"
              >
                نرفض (خصم 10% من الادخار)
              </button>
            </div>
          </motion.div>
        )}

        {job.status === 'accepted' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <button
              onClick={handleStartWork}
              disabled={starting || (job.guarantee_status === 'claimed')}
              className="w-full flex items-center justify-center gap-2 rounded-2xl bg-accent text-white py-4 font-bold text-base hover:opacity-90 transition-opacity disabled:opacity-60"
            >
              <Clock className="h-5 w-5" />
              {starting ? 'تحضير…' : 'ابدا الخدمة'}
            </button>
          </motion.div>
        )}

        {job.status === 'in_progress' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <button
              onClick={() => setShowCompleteModal(true)}
              className="w-full flex items-center justify-center gap-2 rounded-2xl bg-success text-white py-4 font-bold text-base hover:opacity-90 transition-opacity"
            >
              <CheckCircle2 className="h-5 w-5" /> الخدمة كملات
            </button>
          </motion.div>
        )}

        {job.status === 'completed' && (
          <div className="rounded-2xl bg-success/10 border border-success/30 text-success p-4 text-center font-semibold">
            ✅ الخدمة كملات — ضمانة 48 ساعة نشيطة
          </div>
        )}
      </div>

      {/* Complete Modal */}
      {showCompleteModal && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 p-4">
          <motion.div
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="w-full max-w-lg rounded-2xl bg-card p-6 shadow-xl border border-border"
          >
            <h3 className="font-bold text-foreground text-lg mb-2">تأكيد إتمام الخدمة</h3>
            <p className="text-sm text-muted-foreground mb-4">واش أكيد كملات؟ ضمانة 48 ساعة غادي تبدا.</p>
            <div className="mb-4">
              <label className="flex items-center gap-2 text-sm font-medium text-foreground mb-2">
                <Camera className="h-4 w-4" /> صورة بعد الخدمة (اختياري)
              </label>
              <input
                type="url"
                value={afterPhotoUrl}
                onChange={e => setAfterPhotoUrl(e.target.value)}
                placeholder="رابط الصورة..."
                className="w-full rounded-xl border border-input bg-background px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-accent/50"
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowCompleteModal(false)}
                className="flex-1 rounded-xl border border-border py-3 text-sm font-semibold hover:bg-muted transition-colors"
              >
                إلغاء
              </button>
              <button
                onClick={handleComplete}
                disabled={completing}
                className="flex-1 rounded-xl bg-success text-white py-3 text-sm font-bold hover:opacity-90 disabled:opacity-60"
              >
                {completing ? 'جاري…' : 'نعم، كملات'}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default ArtisanJobDetail;
