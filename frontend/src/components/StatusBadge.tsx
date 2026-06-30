import type { BudgetStatus } from '../types/api'
import { statusLabel } from '../lib/format'

const COLORS: Record<BudgetStatus, string> = {
  OK: 'bg-green-900 text-green-300',
  WARNING: 'bg-amber-900 text-amber-300',
  EXCEEDED: 'bg-red-900 text-red-300',
}

export function StatusBadge({ status }: { status: BudgetStatus }) {
  return (
    <span className={`rounded-full px-2 py-1 text-xs font-medium ${COLORS[status]}`}>
      {statusLabel(status)}
    </span>
  )
}
