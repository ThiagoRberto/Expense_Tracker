import { analyticsApi } from '../api/analytics'
import { useAsync } from '../hooks/useAsync'
import { useUser } from '../context/UserContext'
import { AsyncSection } from '../components/AsyncSection'
import { formatCurrency, formatMonthYear } from '../lib/format'

export function InstallmentsPage() {
  const { userId } = useUser()
  const { data, error, loading } = useAsync(
    () => analyticsApi.installments(userId as number),
    [userId],
  )

  return (
    <div className="space-y-6">
      <h2 className="text-base font-semibold text-zinc-100">Projeção de parcelas</h2>
      <AsyncSection loading={loading} error={error}>
        {data && data.projections.length > 0 ? (
          <div className="space-y-4">
            {data.projections.map((projection) => (
              <div
                key={projection.expense_id}
                className="rounded-md border border-zinc-700 bg-zinc-900 p-4"
              >
                <p className="font-medium text-zinc-100">
                  {projection.expense_name}{' '}
                  <span className="text-xs text-zinc-500">({projection.category})</span>
                </p>
                <p className="text-xs text-zinc-500">
                  Total: {formatCurrency(projection.total_value)} em {projection.installments}x
                </p>
                <ul className="mt-3 divide-y divide-zinc-800 border-t border-zinc-800">
                  {projection.entries.map((entry) => (
                    <li key={entry.installment_number} className="flex items-center justify-between py-1.5 text-sm">
                      <span className="text-zinc-400">
                        {entry.installment_number}/{projection.installments} —{' '}
                        {formatMonthYear(entry.month, entry.year)}
                      </span>
                      <span className="font-medium text-zinc-200">{formatCurrency(entry.amount)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-zinc-500">Nenhuma despesa parcelada encontrada.</p>
        )}
      </AsyncSection>
    </div>
  )
}
