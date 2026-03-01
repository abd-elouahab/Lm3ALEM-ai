import { type JobStatus, statusLabels } from '@/lib/mockData';
import { cn } from '@/lib/utils';

const statusStyles: Record<string, string> = {
  pending: 'bg-status-pending/10 text-status-pending border-status-pending/20',
  matching: 'bg-status-matching/10 text-status-matching border-status-matching/20 pulse-blue',
  assigned: 'bg-status-assigned/10 text-status-assigned border-status-assigned/20',
  accepted: 'bg-status-assigned/10 text-status-assigned border-status-assigned/20',
  in_progress: 'bg-status-progress/10 text-status-progress border-status-progress/20',
  completed: 'bg-status-done/10 text-status-done border-status-done/20',
  disputed: 'bg-status-dispute/10 text-status-dispute border-status-dispute/20',
  dispute: 'bg-status-dispute/10 text-status-dispute border-status-dispute/20',
  cancelled: 'bg-muted text-muted-foreground border-border',
  guarantee: 'bg-status-guarantee/10 text-status-guarantee border-status-guarantee/20',
};

export const StatusBadge = ({ status }: { status: string }) => (
  <span className={cn('inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border', statusStyles[status] || statusStyles.pending)}>
    <span className={cn('w-1.5 h-1.5 rounded-full', {
      'bg-status-pending': status === 'pending',
      'bg-status-matching': status === 'matching',
      'bg-status-assigned': status === 'assigned' || status === 'accepted',
      'bg-status-progress': status === 'in_progress',
      'bg-status-done': status === 'completed',
      'bg-status-dispute': status === 'dispute' || status === 'disputed',
      'bg-status-guarantee': status === 'guarantee',
      'bg-muted-foreground': status === 'cancelled',
    })} />
    {statusLabels[status] || status}
  </span>
);
