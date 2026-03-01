export const specialties = [
  { id: 'zlayji', name: 'Zlayji', nameAr: 'زليجي', nameFr: 'Carrelage', icon: 'Grid3X3', description: 'Pose et réparation de carrelage, mosaïque, zellige traditionnel' },
  { id: 'sebbagh', name: 'Sebbagh', nameAr: 'صبّاغ', nameFr: 'Peinture', icon: 'Paintbrush', description: 'Peinture intérieure et extérieure, décoration murale' },
  { id: 'gebbas', name: 'Gebbas', nameAr: 'جبّاس', nameFr: 'Plâtre', icon: 'Square', description: 'Travaux de plâtre, faux plafonds, moulures décoratives' },
  { id: 'plombier', name: 'Plombier', nameAr: 'بلومبي', nameFr: 'Plomberie', icon: 'Wrench', description: 'Réparation de fuites, installation sanitaire, chauffe-eau' },
  { id: 'electricien', name: 'Electricien', nameAr: 'كهربائي', nameFr: 'Électricité', icon: 'Zap', description: 'Installation électrique, dépannage, mise aux normes' },
];

export const cities = [
  'Agadir', 'Inezgane', 'Ait Melloul', 'Tiznit', 'Taroudant',
  'Biougra', 'Chtouka', 'Massa', 'Drarga', 'Dcheira',
];

// City name (display) -> normalized for API; coords for artisan registration
export const cityCoords: Record<string, { city: string; lat: number; lng: number }> = {
  'Agadir': { city: 'agadir', lat: 30.4278, lng: -9.5981 },
  'Inezgane': { city: 'inezgane', lat: 30.3567, lng: -9.5369 },
  'Ait Melloul': { city: 'ait_melloul', lat: 30.3333, lng: -9.5000 },
  'Tiznit': { city: 'tiznit', lat: 29.6974, lng: -9.7316 },
  'Taroudant': { city: 'taroudant', lat: 30.4727, lng: -8.8772 },
  'Biougra': { city: 'biougra', lat: 30.2167, lng: -9.3667 },
  'Chtouka': { city: 'chtouka', lat: 30.0833, lng: -9.4667 },
  'Massa': { city: 'massa', lat: 30.0667, lng: -9.6500 },
  'Drarga': { city: 'drarga', lat: 30.4833, lng: -9.7167 },
  'Dcheira': { city: 'dcheira', lat: 30.3833, lng: -9.5167 },
};

export const levels = [
  { id: 'apprenti', name: 'Apprenti', color: 'level-apprenti' },
  { id: 'compagnon', name: 'Compagnon', color: 'level-compagnon' },
  { id: 'maitre', name: 'Maître Artisan', color: 'level-maitre' },
  { id: 'maalem', name: 'Maître Maâlem', color: 'level-maalem' },
];

export const mockTestimonials = [
  {
    name: 'Fatima Ouakrim',
    city: 'Agadir',
    text: "J'ai trouvé un excellent sebbagh en moins de 2 heures. Le travail était impeccable, et l'estimation du prix était très précise. Je recommande !",
    rating: 5,
    avatar: 'F',
  },
  {
    name: 'Youssef Ait Baha',
    city: 'Inezgane',
    text: "En tant qu'artisan, cette plateforme a changé ma vie. Je reçois des demandes régulières et mes revenus ont augmenté de 40%. Merci L'M3alem AI !",
    rating: 5,
    avatar: 'Y',
  },
  {
    name: 'Amina Tazrouti',
    city: 'Taroudant',
    text: "Le système d'IA a parfaitement identifié le problème de plomberie. L'artisan est arrivé rapidement et a résolu le souci en une heure. Excellent !",
    rating: 5,
    avatar: 'A',
  },
];

export type JobStatus = 'pending' | 'matching' | 'accepted' | 'assigned' | 'in_progress' | 'completed' | 'disputed' | 'dispute' | 'cancelled' | 'guarantee';

export const statusLabels: Record<string, string> = {
  pending: 'في الانتظار',
  matching: 'كنقلبو على معلم',
  accepted: 'لقينا معلم',
  assigned: 'لقينا معلم',
  in_progress: 'فالخدمة',
  completed: 'كمل',
  disputed: 'مشكل',
  dispute: 'مشكل',
  cancelled: 'لغا',
  guarantee: 'ضمان 48 ساعة',
};

export const mockJobs = [
  {
    id: '1',
    type: 'plombier',
    title: 'Fuite robinet cuisine',
    status: 'in_progress' as JobStatus,
    artisan: { name: 'Hassan El Amrani', level: 'maitre', rating: 4.8 },
    date: '2026-02-25',
    estimatedPrice: '200-350 MAD',
    description: 'Fuite au niveau du robinet de la cuisine, goutte-à-goutte constant.',
  },
  {
    id: '2',
    type: 'sebbagh',
    title: 'Peinture salon',
    status: 'completed' as JobStatus,
    artisan: { name: 'Rachid Bouhali', level: 'compagnon', rating: 4.5 },
    date: '2026-02-20',
    estimatedPrice: '800-1200 MAD',
    description: 'Repeindre le salon en blanc cassé, 25m².',
  },
  {
    id: '3',
    type: 'electricien',
    title: 'Prise défectueuse chambre',
    status: 'pending' as JobStatus,
    artisan: null,
    date: '2026-02-28',
    estimatedPrice: '150-250 MAD',
    description: 'Prise qui fait des étincelles dans la chambre principale.',
  },
];

export const mockArtisanJobs = [
  {
    id: '4',
    type: 'plombier',
    title: 'Installation chauffe-eau',
    status: 'assigned' as JobStatus,
    client: { name: 'Karima Essaidi', address: 'Rue Moulay Rachid, Agadir', phone: '+212 6 12 34 56 78' },
    date: '2026-02-28',
    estimatedPrice: '500-800 MAD',
    severity: 3,
    complexity: 'Moyenne',
  },
  {
    id: '5',
    type: 'plombier',
    title: 'Réparation fuite salle de bain',
    status: 'in_progress' as JobStatus,
    client: { name: 'Omar Tazi', address: 'Av. Hassan II, Inezgane', phone: '+212 6 98 76 54 32' },
    date: '2026-02-27',
    estimatedPrice: '300-450 MAD',
    severity: 4,
    complexity: 'Complexe',
  },
];

export const mockPendingOffers = [
  {
    id: '6',
    type: 'plombier',
    title: 'Fuite eau chaude',
    estimatedPrice: '250-400 MAD',
    distance: '3.2 km',
    timeRemaining: 45,
    client: { name: 'Samir H.' },
  },
];
