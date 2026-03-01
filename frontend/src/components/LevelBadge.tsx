import { cn } from '@/lib/utils';

const levelConfig: Record<string, { label: string; classes: string }> = {
  apprenti: { label: 'متعلم', classes: 'bg-level-apprenti/10 text-level-apprenti border-level-apprenti/20' },
  compagnon: { label: 'صانع', classes: 'bg-level-compagnon/10 text-level-compagnon border-level-compagnon/20' },
  maitre: { label: 'معلم', classes: 'bg-level-maitre/10 text-level-maitre border-level-maitre/20' },
  maalem: { label: 'لمعلم الكبير', classes: 'bg-level-maalem/10 text-level-maalem border-level-maalem/20 glow-purple' },
};

export const LevelBadge = ({ level }: { level: string }) => {
  const config = levelConfig[level] || levelConfig.apprenti;
  return (
    <span className={cn('inline-flex items-center px-3 py-1 rounded-full text-xs font-bold border', config.classes)}>
      {config.label}
    </span>
  );
};
