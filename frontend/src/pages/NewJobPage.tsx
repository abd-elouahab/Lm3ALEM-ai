import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, Upload, ArrowLeft, ArrowRight, MapPin, Sparkles, ChevronDown, PartyPopper } from 'lucide-react';
import { specialties, cities } from '@/lib/mockData';
import { Navbar } from '@/components/Navbar';
import { toast } from 'sonner';
import * as LucideIcons from 'lucide-react';
import api from '@/lib/api';


const SPECIALTY_DISPLAY: Record<string, { label: string; icon: string; color: string }> = {
  zlayji: { label: 'Carrelage & Zellige', icon: '🪟', color: '#f59e0b' },
  sebbagh: { label: 'Peinture', icon: '🎨', color: '#3b82f6' },
  gebbas: { label: 'Plâtre & Fissures', icon: '🏠', color: '#8b5cf6' },
  plombier: { label: 'Plomberie', icon: '🔧', color: '#06b6d4' },
  electricien: { label: 'Électricité', icon: '⚡', color: '#eab308' },
};

const steps = ['المشكل', 'تحليل الذكاء الاصطناعي', 'تأكيد الطلب'];

const confidenceLabels: Record<string, string> = { high: 'عالية', medium: 'متوسطة', low: 'ضعيفة' };
const complexityLabels: Record<string, string> = { simple: 'ساهل', moyenne: 'متوسط', complexe: 'صعيب' };

interface AiResult {
  problem_type: string;
  description: string;
  diagnosis_notes?: string;
  severity: number;
  surface_area_m2: number;
  complexity: string;
  nb_elements_affected: number;
  confidence: string;
  price: number;
  duration_hours: number;
}

const NewJobPage = () => {
  const [step, setStep] = useState(0);

  // New Client Fields
  const [clientName, setClientName] = useState('');
  const [clientPhone, setClientPhone] = useState('');

  const [clientComment, setClientComment] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [photoPreviewUrl, setPhotoPreviewUrl] = useState<string>('');
  const [photos, setPhotos] = useState<string[]>([]);

  const [analyzing, setAnalyzing] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);
  const [aiResult, setAiResult] = useState<AiResult | null>(null);
  const [detectedProblemType, setDetectedProblemType] = useState<string>('');

  const [createdJobId, setCreatedJobId] = useState<number | null>(null);
  const [shouldShowOverride, setShouldShowOverride] = useState(false);
  const [matchedArtisan, setMatchedArtisan] = useState<{
    full_name: string;
    specialty: string;
    city: string;
    ranking_score: number;
    total_jobs: number;
    profile_photo_url: string | null;
    phone?: string | null;
  } | null>(null);

  const [city, setCity] = useState('Agadir');
  const [clientLocation] = useState({ lat: 30.4278, lng: -9.5981 });
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  // Chat state
  const [messages, setMessages] = useState<{ role: string, content: string }[]>([]);
  const [inputText, setInputText] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [imageBase64, setImageBase64] = useState('');

  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (photoPreviewUrl) {
        URL.revokeObjectURL(photoPreviewUrl);
      }
      setSelectedFile(file);
      setPhotoPreviewUrl(URL.createObjectURL(file));
      setPhotos([file.name]);
    }
  };

  useEffect(() => {
    return () => {
      if (photoPreviewUrl) {
        URL.revokeObjectURL(photoPreviewUrl);
      }
    };
  }, [photoPreviewUrl]);

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setStep(1); // Move to AI screen (chat UI)

    // If we haven't started chatting yet
    if (!messages.length) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const base64 = (e.target?.result as string).split(',')[1];
        if (base64) {
          setImageBase64(base64);
          startChat(base64);
        }
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const startChat = async (base64: string) => {
    setChatLoading(true);
    try {
      const res = await api.post('/jobs/chat', {
        image_base64: base64,
        conversation_history: [],
        is_first_message: true
      });
      const data = res.data;
      // Store image_description as a hidden system message so Turn 2+ can use it
      const imageDescMsg = data.image_description
        ? [{ role: 'system', content: `IMAGE:${data.image_description}` }]
        : [];
      setMessages([
        ...imageDescMsg,
        { role: 'assistant', content: data.message }
      ]);
      if (data.is_final) {
        setAiResult(data.analysis);
        setDetectedProblemType(data.analysis.problem_type);
        setAnalyzed(true);
      }
    } catch {
      toast.error('غلط ديال الاتصال بالذكاء الاصطناعي. عاود من جديد.');
    } finally {
      setChatLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputText.trim()) return;
    const userMsg = { role: 'user', content: inputText };
    // Include the full history (including hidden system image description) when sending
    const newHistory = [...messages, userMsg];
    // Display only non-system messages in UI
    setMessages(newHistory);
    setInputText('');
    setChatLoading(true);

    try {
      const res = await api.post('/jobs/chat', {
        image_base64: imageBase64,
        conversation_history: newHistory, // includes hidden IMAGE: system message
        is_first_message: false
      });
      const data = res.data;
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: data.message }
      ]);
      if (data.is_final) {
        setAiResult(data.analysis);
        setDetectedProblemType(data.analysis.problem_type);
        setAnalyzed(true);
      }
    } catch {
      toast.error('غلط فالإرسال. عاود من جديد.');
    } finally {
      setChatLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!aiResult) return;
    try {
      setSubmitting(true);
      let uploadedPhotoUrl = '';
      if (selectedFile) {
        const formData = new FormData();
        formData.append('file', selectedFile);
        const uploadRes = await api.post('/jobs/upload-photo', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        uploadedPhotoUrl = uploadRes.data?.photo_url || '';
      }

      const jobResponse = await api.post('/jobs', {
        problem_type: detectedProblemType,
        symptom: clientComment || '',
        client_name: clientName,
        client_phone: clientPhone,
        photo_url: uploadedPhotoUrl,
        city: city,
        client_latitude: clientLocation.lat,
        client_longitude: clientLocation.lng,
        ai_description: aiResult.description,
        diagnosis_notes: aiResult.diagnosis_notes,
        severity: aiResult.severity,
        surface_area_m2: aiResult.surface_area_m2,
        complexity: aiResult.complexity,
        nb_elements_affected: aiResult.nb_elements_affected,
        estimated_price: aiResult.price,
        estimated_duration_hours: aiResult.duration_hours,
      });

      setCreatedJobId(jobResponse.data.id);
      await api.post('/match', { job_id: jobResponse.data.id });

      try {
        const artisanRes = await api.get(`/jobs/${jobResponse.data.id}/matched-artisan`);
        setMatchedArtisan(artisanRes.data);
      } catch (err) {
        console.error("Could not fetch matched artisan", err);
      }

      setSubmitted(true);
      toast.success('تم إرسال الطلب بنجاح');
    } catch {
      toast.error('غلط فالإرسال. عاود مرة اخرى.');
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted && createdJobId) {
    return (
      <div className="min-h-screen bg-background pb-12">
        <Navbar />
        <div className="container mx-auto px-4 max-w-lg mt-8">

          {/* Success header */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200, damping: 15 }}
            className="mb-6 text-center"
          >
            <div className="relative w-24 h-24 mx-auto mb-4">
              <div className="flex h-full w-full items-center justify-center rounded-full bg-success/10 relative z-10">
                <Check className="h-10 w-10 text-success" />
              </div>
              {[0, 1].map((i) => (
                <div key={i} className="absolute inset-0 rounded-full border border-success/30 animate-radar" style={{ animationDelay: `${i * 0.5}s` }} />
              ))}
            </div>
            <h2 className="text-2xl font-extrabold text-foreground mb-2">تم تسجيل الطلب ديالك!</h2>
            <p className="text-muted-foreground text-sm">الذكاء الاصطناعي قلب ولقا ليك أحسن معلم لهاد المشكل.</p>
          </motion.div>

          {/* Matched artisan card */}
          {matchedArtisan && (
            <motion.div
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
              className="rounded-2xl bg-accent/5 border border-accent/20 p-6 mb-8 shadow-sm relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 p-3">
                <span className="flex items-center gap-1 text-[10px] font-bold text-success bg-success/10 px-2 py-1 rounded-full">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-success"></span>
                  </span>
                  تم الاختيار
                </span>
              </div>
              <h3 className="text-center font-bold text-accent mb-6">هاد هو المعلم لي غادي يوصلك عندو الطلب</h3>

              <div className="flex flex-col items-center">
                <div className="h-20 w-20 rounded-full bg-accent/20 flex flex-shrink-0 items-center justify-center text-3xl font-bold text-accent mb-4 border-2 border-background shadow-sm">
                  {matchedArtisan.full_name.charAt(0).toUpperCase() || 'M'}
                </div>
                <h4 className="text-xl font-extrabold text-foreground text-center">{matchedArtisan.full_name}</h4>
                <p className="text-sm font-semibold text-accent mb-3">{SPECIALTY_DISPLAY[matchedArtisan.specialty]?.label || matchedArtisan.specialty}</p>

                <div className="flex items-center gap-4 text-sm text-muted-foreground bg-background rounded-full px-4 py-2 border border-border mt-1">
                  <span className="flex items-center gap-1.5 font-medium"><MapPin className="h-4 w-4" /> {matchedArtisan.city || city}</span>
                  <div className="w-px h-4 bg-border" />
                  <span className="flex items-center gap-1.5 font-bold text-warning">
                    <PartyPopper className="h-4 w-4" /> {matchedArtisan.ranking_score}/100
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mt-3">خدمات مكملّة: {matchedArtisan.total_jobs ?? 0}</p>
                {matchedArtisan.phone && (
                  <p className="text-sm font-semibold text-foreground mt-1">الهاتف: {matchedArtisan.phone}</p>
                )}
              </div>
            </motion.div>
          )}

          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }} className="flex flex-col gap-3">
            <button
              onClick={() => navigate(`/client/jobs/${createdJobId}`)}
              className="w-full rounded-xl bg-accent px-6 py-4 text-base font-bold text-white shadow-accent hover:opacity-90 transition-opacity"
            >
              شوف تفاصيل الطلب ديالك
            </button>
            <button
              onClick={() => navigate('/client/dashboard')}
              className="w-full rounded-xl border border-border bg-card px-6 py-4 text-sm font-semibold hover:bg-muted transition-colors"
            >
              الرجوع للوحة التحكم
            </button>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        {/* Progress */}
        <div className="flex items-center justify-between mb-10">
          {steps.map((s, i) => (
            <div key={s} className="flex items-center gap-2">
              <div className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold transition-all ${i <= step ? 'bg-accent text-accent-foreground' : 'bg-muted text-muted-foreground'
                }`}>
                {i < step ? <Check className="h-4 w-4" /> : i + 1}
              </div>
              <span className={`text-sm font-medium hidden sm:block ${i <= step ? 'text-foreground' : 'text-muted-foreground'}`}>{s}</span>
              {i < steps.length - 1 && <div className={`w-8 md:w-16 h-0.5 ${i < step ? 'bg-accent' : 'bg-border'}`} />}
            </div>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {step === 0 && (
            <motion.div key="step0" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <h2 className="text-2xl font-extrabold text-foreground mb-2">شنو المشكل لي عندك؟</h2>
              <p className="text-muted-foreground mb-8">صور المشكل باش الذكاء الاصطناعي ديالنا يحللو.</p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="text-sm font-medium mb-1 block">الاسم الكامل (اختياري)</label>
                  <input
                    type="text"
                    value={clientName}
                    onChange={e => setClientName(e.target.value)}
                    placeholder="الاسم ديالك"
                    className="w-full rounded-xl border border-input bg-card p-3 text-sm focus:outline-none focus:ring-2 focus:ring-accent/50"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">رقم الهاتف (اختياري)</label>
                  <input
                    type="text"
                    value={clientPhone}
                    onChange={e => setClientPhone(e.target.value)}
                    placeholder="+212600000000"
                    className="w-full rounded-xl border border-input bg-card p-3 text-sm focus:outline-none focus:ring-2 focus:ring-accent/50"
                  />
                </div>
              </div>

              {/* Photo upload */}
              {photos.length === 0 ? (
                <label className="w-full rounded-2xl border-2 border-dashed border-border bg-muted/30 p-12 text-center hover:border-accent/50 hover:bg-accent/5 transition-all group cursor-pointer block">
                  <input type="file" accept="image/*" className="hidden" onChange={handlePhotoUpload} />
                  <Upload className="h-10 w-10 text-muted-foreground mx-auto mb-3 group-hover:text-accent transition-colors" />
                  <p className="font-semibold text-foreground mb-1">صور المشكل</p>
                  <p className="text-sm text-muted-foreground">الذكاء الاصطناعي غيحلل الصورة وغيعرف المشكل بوحدو.<br />JPG, PNG — ما تفوتش 10MB</p>
                </label>
              ) : (
                <div className="rounded-2xl border border-border bg-card p-4 mb-4 flex justify-between items-center">
                  <div className="flex items-center gap-3">
                    {photoPreviewUrl ? (
                      <img
                        src={photoPreviewUrl}
                        alt="Aperçu"
                        className="h-16 w-16 rounded-xl object-cover border border-border"
                      />
                    ) : (
                      <div className="h-16 w-16 rounded-xl bg-muted shimmer" />
                    )}
                    <div>
                      <p className="font-medium text-sm text-foreground">{selectedFile?.name || 'صورة'}</p>
                      <p className="text-xs text-success">واجدة للتحليل</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      if (photoPreviewUrl) {
                        URL.revokeObjectURL(photoPreviewUrl);
                      }
                      setPhotos([]);
                      setSelectedFile(null);
                      setPhotoPreviewUrl('');
                    }}
                    className="text-sm text-destructive hover:underline"
                  >
                    بدل الصورة
                  </button>
                </div>
              )}

              <textarea
                value={clientComment}
                onChange={(e) => setClientComment(e.target.value)}
                placeholder="تعليق (اختياري) - شرح لينا المشكل باختصار..."
                className="w-full rounded-2xl border border-input bg-card p-4 text-sm resize-none h-24 focus:outline-none focus:ring-2 focus:ring-accent/50 mt-4 transition-all"
              />

              <div className="flex justify-end mt-8">
                <button
                  disabled={!selectedFile}
                  onClick={handleAnalyze}
                  className="inline-flex items-center gap-2 rounded-xl bg-accent px-6 py-3 text-sm font-bold text-accent-foreground shadow-accent disabled:opacity-50 transition-all"
                >
                  تحليل بالذكاء الاصطناعي <ArrowRight className="h-4 w-4" />
                </button>
              </div>
            </motion.div>
          )}

          {/* AI Analysis Step (Step 1) */}
          {step === 1 && (
            <motion.div key="step1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="flex flex-col h-[70vh]">
              <h2 className="text-2xl font-extrabold text-foreground mb-2 flex-shrink-0">تحليل الذكاء الاصطناعي</h2>
              <p className="text-muted-foreground mb-4 flex-shrink-0">تكلم مع المساعد ديالنا باش نزيدو نفهمو المشكل</p>

              {/* Chat Area */}
              <div className="flex-1 flex flex-col bg-card rounded-2xl border border-border overflow-hidden shadow-sm">

                {/* Messages List */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4 flex flex-col">
                  {messages.filter(msg => msg.role !== 'system').map((msg, idx) => (
                    <div key={idx} className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${msg.role === 'assistant'
                      ? 'bg-muted/50 text-foreground self-start rounded-tl-sm'
                      : 'bg-accent text-accent-foreground self-end rounded-tr-sm'
                      }`}>
                      {msg.content}
                    </div>
                  ))}

                  {chatLoading && (
                    <div className="bg-muted/50 text-foreground self-start rounded-2xl rounded-tl-sm px-4 py-4 max-w-[85%] flex items-center gap-1.5 h-10">
                      <div className="w-1.5 h-1.5 rounded-full bg-foreground/40 animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-1.5 h-1.5 rounded-full bg-foreground/40 animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-1.5 h-1.5 rounded-full bg-foreground/40 animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  )}
                </div>

                {/* Input Area (only if not final analyzed and not loading the first message) */}
                {!analyzed && (
                  <div className="p-3 border-t border-border bg-card flex gap-2">
                    <input
                      type="text"
                      value={inputText}
                      onChange={e => setInputText(e.target.value)}
                      onKeyDown={e => e.key === 'Enter' && sendMessage()}
                      placeholder="جوابك..."
                      className="flex-1 rounded-full border border-input bg-background px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent/50"
                      disabled={chatLoading}
                    />
                    <button
                      onClick={sendMessage}
                      disabled={chatLoading || !inputText.trim()}
                      className="h-10 w-10 flex-shrink-0 rounded-full bg-accent text-accent-foreground flex items-center justify-center disabled:opacity-50"
                    >
                      <ArrowRight className="h-4 w-4" />
                    </button>
                  </div>
                )}
              </div>

              {/* Final Result Card (Shows up after Chat finishes) */}
              {analyzed && aiResult && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                  {/* AI Result Card */}
                  <div className="rounded-2xl border-2 border-accent/20 bg-card overflow-hidden shadow-lg relative">
                    <div className="absolute top-4 left-4 bg-accent/10 text-accent text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1">
                      <Sparkles className="h-3 w-3" /> تحليل الذكاء الاصطناعي
                    </div>

                    <div className="p-6 pb-0">
                      <p className="text-sm text-muted-foreground font-medium mb-3">المشكل لي لقينا :</p>

                      {/* Detected Specialty Hero block */}
                      <div className="flex items-center gap-4 mb-6 bg-muted/30 p-4 rounded-xl border border-border">
                        <div className="flex-shrink-0 flex items-center justify-center w-16 h-16 rounded-full" style={{ backgroundColor: `${SPECIALTY_DISPLAY[detectedProblemType]?.color}15` }}>
                          <span className="text-3xl">{SPECIALTY_DISPLAY[detectedProblemType]?.icon || '🔧'}</span>
                        </div>
                        <div>
                          <h3 className="text-2xl font-extrabold text-foreground">{SPECIALTY_DISPLAY[detectedProblemType]?.label || detectedProblemType}</h3>
                        </div>
                      </div>

                      <div className="space-y-4 mb-6 text-sm">
                        <div>
                          <span className="text-muted-foreground block mb-1">الشرح :</span>
                          <p className="text-foreground font-medium">{aiResult.description}</p>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                          <div className="bg-muted/20 p-3 rounded-lg border border-border/50">
                            <div className="text-muted-foreground text-xs mb-1">درجة الخطورة :</div>
                            <div className="flex gap-1">
                              {[1, 2, 3, 4, 5].map(i => (
                                <div key={i} className={`h-2 text-xs flex-1 rounded-full ${i <= aiResult.severity ? 'bg-destructive' : 'bg-muted'}`} />
                              ))}
                              <span className="text-xs ml-2 font-bold">{aiResult.severity}/5</span>
                            </div>
                          </div>
                          <div className="bg-muted/20 p-3 rounded-lg border border-border/50">
                            <div className="text-muted-foreground text-xs mb-1">المساحة :</div>
                            <div className="font-bold text-foreground">~{aiResult.surface_area_m2}m²</div>
                          </div>
                          <div className="bg-muted/20 p-3 rounded-lg border border-border/50">
                            <div className="text-muted-foreground text-xs mb-1">الصعوبة :</div>
                            <div className="font-bold text-accent">{complexityLabels[aiResult.complexity] || aiResult.complexity}</div>
                          </div>
                          <div className="bg-muted/20 p-3 rounded-lg border border-border/50">
                            <div className="text-muted-foreground text-xs mb-1">ثقة الذكاء الاصطناعي :</div>
                            <div className="font-bold text-success flex items-center gap-1">
                              <Check className="h-3 w-3" />
                              {confidenceLabels[aiResult.confidence] || aiResult.confidence}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="bg-accent/5 p-6 border-t border-accent/10 flex flex-col items-center text-center">
                      <p className="text-sm text-foreground font-semibold mb-1">تقدير الثمن</p>
                      <p className="text-4xl font-extrabold text-[#c05621]">{Math.round(aiResult.price)} <span className="text-xl">MAD</span></p>
                      <p className="text-sm text-muted-foreground mt-2">الوقت المقدر : ~{aiResult.duration_hours}h</p>
                    </div>
                  </div>

                  <div className="text-center mt-4">
                    <p className="text-xs text-muted-foreground mb-2">
                      الذكاء الاصطناعي عرف المشكل. إلا بان ليك الغلط، يمكن ليك تبدل.
                    </p>
                    <button type="button" onClick={() => setShouldShowOverride(!shouldShowOverride)} className="text-sm text-accent hover:underline font-medium">
                      بدل التخصص
                    </button>

                    {/* Specialty Override Dropdown */}
                    <AnimatePresence>
                      {shouldShowOverride && (
                        <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="mt-4 overflow-hidden">
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
                            {specialties.map((s) => {
                              // eslint-disable-next-line @typescript-eslint/no-explicit-any
                              const Icon = (LucideIcons as any)[s.icon] || LucideIcons.Wrench;
                              return (
                                <button
                                  key={s.id}
                                  onClick={() => { setDetectedProblemType(s.id); setShouldShowOverride(false); }}
                                  className={`rounded-xl border p-3 flex items-center gap-3 transition-all ${detectedProblemType === s.id ? 'border-accent bg-accent/5 shadow-sm' : 'border-border bg-card'
                                    }`}
                                >
                                  <div className={`p-2 rounded-lg ${detectedProblemType === s.id ? 'bg-accent/10 text-accent' : 'bg-muted text-muted-foreground'}`}>
                                    <Icon className="h-4 w-4" />
                                  </div>
                                  <span className="font-semibold text-sm">{s.nameFr}</span>
                                </button>
                              )
                            })}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </motion.div>
              )}

              <div className="flex justify-between mt-8">
                <button type="button" onClick={() => setStep(0)} className="inline-flex items-center gap-2 rounded-xl border border-border px-5 py-3 text-sm font-medium hover:bg-muted transition-all">
                  <ArrowRight className="h-4 w-4" /> رجوع
                </button>
                <button
                  disabled={analyzing || !aiResult}
                  onClick={() => setStep(2)}
                  className="inline-flex items-center gap-2 rounded-xl bg-accent px-6 py-3 text-sm font-bold text-accent-foreground shadow-accent disabled:opacity-50 transition-all"
                >
                  زيد لقدام <ArrowLeft className="h-4 w-4" />
                </button>
              </div>
            </motion.div>
          )}

          {/* Confirmation Step (Step 2) */}
          {step === 2 && (
            <motion.div key="step2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <h2 className="text-2xl font-extrabold text-foreground mb-2">تأكيد الطلب</h2>
              <p className="text-muted-foreground mb-8">شوف واش كولشي هو هاداك قبل ما تصيفط الطلب</p>

              <div className="rounded-2xl border border-border bg-card p-6 space-y-5">
                <div className="flex justify-between items-center pb-4 border-b border-border">
                  <span className="text-sm text-muted-foreground">التخصص</span>
                  <span className="font-semibold text-foreground">{SPECIALTY_DISPLAY[detectedProblemType]?.label || detectedProblemType}</span>
                </div>
                <div className="pb-4 border-b border-border">
                  <span className="text-sm text-muted-foreground block mb-2">شرح الذكاء الاصطناعي</span>
                  <p className="text-sm text-foreground">{aiResult?.description || '—'}</p>
                </div>
                <div className="flex justify-between items-center pb-4 border-b border-border">
                  <span className="text-sm text-muted-foreground">الثمن التقريبي</span>
                  <span className="font-bold text-foreground text-lg">{aiResult ? `${Math.round(aiResult.price)} MAD` : '—'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> المدينة</span>
                  <div className="relative">
                    <select value={city} onChange={e => setCity(e.target.value)} className="bg-card border border-input rounded-lg px-3 py-1.5 text-sm font-medium appearance-none pr-8 focus:outline-none focus:ring-2 focus:ring-accent/50">
                      {cities.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                    <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground pointer-events-none" />
                  </div>
                </div>
              </div>

              <div className="flex justify-between mt-8">
                <button type="button" onClick={() => setStep(1)} className="inline-flex items-center gap-2 rounded-xl border border-border px-5 py-3 text-sm font-medium hover:bg-muted transition-all">
                  <ArrowRight className="h-4 w-4" /> رجوع
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={submitting || !aiResult}
                  className="inline-flex items-center gap-2 rounded-xl bg-accent px-8 py-3 text-sm font-bold text-accent-foreground shadow-accent transition-all hover:opacity-90 disabled:opacity-50"
                >
                  {submitting ? 'جاري الإرسال...' : 'صيفط الطلب'}
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default NewJobPage;
