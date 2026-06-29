import type { BudgetStatus } from '../types/api'
import { statusLabel } from '../lib/format'

const COLORS: Record<BudgetStatus, string> = {
  OK: 'bg-green-100 text-green-700',
  WARNING: 'bg-amber-100 text-amber-700',
  EXCEEDED: 'bg-red-100 text-red-700',
}

export function StatusBadge({ status }: { status: BudgetStatus }) {
  return (
    <span className={`rounded-full px-2 py-1 text-xs font-medium ${COLORS[status]}`}>
      {statusLabel(status)}
    </span>
  )
}
