import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, ArrowRight, Star, Image } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { LevelBadge } from '@/components/LevelBadge';
import api from '@/lib/api';
import { specialties } from '@/lib/mockData';

interface ArtisanProfileData {
  id: number;
  full_name: string | null;
  specialty: string;
  city: string;
  ranking_score: number;
  total_jobs: number;
  created_at: string;
}

interface RatingItem {
  score: number;
  comment: string | null;
  created_at: string;
}

function getArtisanLevel(score: number, totalJobs: number): string {
  if (score >= 90 && totalJobs >= 50) return 'maalem';
  if (score >= 75 && totalJobs >= 20) return 'maitre';
  if (score >= 60 && totalJobs >= 5) return 'compagnon';
  return 'apprenti';
}

const ArtisanProfile = () => {
  const [profile, setProfile] = useState<ArtisanProfileData | null>(null);
  const [ratings, setRatings] = useState<RatingItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await api.get('/artisans/me');
        setProfile(res.data);
        const r = await api.get(`/ratings/${res.data.id}`);
        setRatings(r.data?.ratings ?? []);
      } catch {
        setProfile(null);
        setRatings([]);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading && !profile) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="container mx-auto px-4 py-8 max-w-2xl">
          <div className="h-6 w-32 rounded bg-muted animate-pulse mb-6" />
          <div className="rounded-2xl border border-border bg-card p-8 h-64 animate-pulse" />
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="container mx-auto px-4 py-8 max-w-2xl text-center">
          <p className="text-muted-foreground">مالقيناش هاد البروفايل.</p>
          <Link to="/artisan/dashboard" className="text-accent font-semibold mt-2 inline-block">رجوع</Link>
        </div>
      </div>
    );
  }

  const level = getArtisanLevel(profile.ranking_score, profile.total_jobs);
  const memberYear = profile.created_at ? new Date(profile.created_at).getFullYear() : '—';

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <Link to="/artisan/dashboard" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors">
          <ArrowRight className="h-4 w-4" /> رجوع
        </Link>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          {/* Hero */}
          <div className="rounded-2xl gradient-hero p-8 mb-6 text-center relative overflow-hidden">
            <div className="absolute inset-0 zellige-pattern" />
            <div className="relative">
              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-accent text-accent-foreground font-bold text-2xl mx-auto mb-4 ring-4 ring-accent-foreground/20">
                {(profile.full_name || 'A').charAt(0)}
              </div>
              <h1 className="text-2xl font-extrabold text-gradient mb-2">{profile.full_name || 'Artisan'}</h1>
              <p className="text-primary-foreground/60 mb-3">{specialties.find(s => s.id === profile.specialty)?.nameFr || profile.specialty} • {profile.city}</p>
              <LevelBadge level={level} />
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-4 gap-3 mb-6">
            {[
              { label: 'خدمات', value: String(profile.total_jobs) },
              { label: 'تنقيط', value: profile.ranking_score ? profile.ranking_score.toFixed(1) : '—' },
              { label: 'عضو من', value: String(memberYear) },
              { label: 'الأداء', value: `${Math.round(profile.ranking_score)}%` },
            ].map((s) => (
              <div key={s.label} className="rounded-xl border border-border bg-card p-3 text-center">
                <p className="text-lg font-extrabold text-foreground">{s.value}</p>
                <p className="text-[10px] text-muted-foreground font-medium">{s.label}</p>
              </div>
            ))}
          </div>

          {/* Portfolio */}
          <div className="rounded-2xl border border-border bg-card p-6 mb-6">
            <h3 className="font-bold text-foreground mb-4 flex items-center gap-2"><Image className="h-5 w-5" /> الأعمال ديالي</h3>
            <div className="grid grid-cols-3 gap-2">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="aspect-square rounded-xl bg-muted shimmer" />
              ))}
            </div>
          </div>

          {/* Reviews */}
          <div className="rounded-2xl border border-border bg-card p-6">
            <h3 className="font-bold text-foreground mb-4">آراء الكليان</h3>
            <div className="space-y-4">
              {ratings.length === 0 ? (
                <p className="text-sm text-muted-foreground">باقي مكاين حتى رأي.</p>
              ) : (
                ratings.map((r, i) => (
                  <div key={i} className="pb-4 border-b border-border last:border-0 last:pb-0">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center text-xs font-bold text-muted-foreground">
                          •
                        </div>
                        <span className="font-medium text-sm text-foreground">عميل</span>
                      </div>
                      <div className="flex gap-0.5">
                        {Array.from({ length: r.score }).map((_, j) => (
                          <Star key={j} className="h-3 w-3 fill-warning text-warning" />
                        ))}
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground">{r.comment || '—'}</p>
                    <p className="text-xs text-muted-foreground mt-1">{r.created_at ? new Date(r.created_at).toLocaleDateString('fr-FR') : ''}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ArtisanProfile;
