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
      <h2 className="text-base font-semibold text-slate-900">Projeção de parcelas</h2>
      <AsyncSection loading={loading} error={error}>
        {data && data.projections.length > 0 ? (
          <div className="space-y-4">
            {data.projections.map((projection) => (
              <div
                key={projection.expense_id}
                className="rounded-md border border-slate-200 bg-white p-4"
              >
                <p className="font-medium">
                  {projection.expense_name}{' '}
                  <span className="text-xs text-slate-400">({projection.category})</span>
                </p>
                <p className="text-xs text-slate-500">
                  Total: {formatCurrency(projection.total_value)} em{' '}
                  {projection.installments}x
                </p>
                <ul className="mt-2 grid grid-cols-2 gap-1 text-sm sm:grid-cols-3">
                  {projection.entries.map((entry) => (
                    <li key={entry.installment_number} className="flex justify-between">
                      <span className="text-slate-500">
                        {entry.installment_number}/{projection.installments} —{' '}
                        {formatMonthYear(entry.month, entry.year)}
                      </span>
                      <span className="font-medium">{formatCurrency(entry.amount)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">Nenhuma despesa parcelada encontrada.</p>
        )}
      </AsyncSection>
    </div>
  )
}
