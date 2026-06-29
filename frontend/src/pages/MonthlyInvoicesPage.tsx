import { useState } from 'react'
import { analyticsApi } from '../api/analytics'
import { useAsync } from '../hooks/useAsync'
import { useUser } from '../context/UserContext'
import { AsyncSection } from '../components/AsyncSection'
import { formatCurrency, formatMonthYear } from '../lib/format'

export function MonthlyInvoicesPage() {
  const { userId } = useUser()
  const [monthsAhead, setMonthsAhead] = useState(6)
  const { data, error, loading } = useAsync(
    () => analyticsApi.monthlyInvoices(userId as number, monthsAhead),
    [userId, monthsAhead],
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-slate-900">Faturas futuras</h2>
        <label className="flex items-center gap-2 text-sm text-slate-700">
          Meses à frente
          <input
            type="number"
            min="1"
            value={monthsAhead}
            onChange={(event) => setMonthsAhead(Number(event.target.value) || 1)}
            className="w-20 rounded border border-slate-300 px-2 py-1 text-sm"
          />
        </label>
      </div>
      <AsyncSection loading={loading} error={error}>
        {data && data.invoices.length > 0 ? (
          <ul className="divide-y divide-slate-200 rounded-md border border-slate-200 bg-white">
            {data.invoices.map((invoice) => (
              <li
                key={`${invoice.month}-${invoice.year}`}
                className="flex items-center justify-between px-4 py-2"
              >
                <span>{formatMonthYear(invoice.month, invoice.year)}</span>
                <span className="font-medium">{formatCurrency(invoice.total)}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-500">Nenhuma fatura projetada.</p>
        )}
      </AsyncSection>
    </div>
  )
}
