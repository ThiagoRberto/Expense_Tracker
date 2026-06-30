import { useState } from 'react'
import { analyticsApi } from '../api/analytics'
import { useAsync } from '../hooks/useAsync'
import { useUser } from '../context/UserContext'
import { AsyncSection } from '../components/AsyncSection'
import { ExpandableInvoiceList } from '../components/ExpandableInvoiceList'

export function MonthlyInvoicesPage() {
  const { userId } = useUser()
  const [monthsAhead, setMonthsAhead] = useState(6)

  const { data, error, loading } = useAsync(
    () => analyticsApi.monthlyInvoices(userId as number, monthsAhead),
    [userId, monthsAhead],
  )
  const { data: installments } = useAsync(
    () => analyticsApi.installments(userId as number),
    [userId],
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-zinc-100">Faturas futuras</h2>
        <label className="flex items-center gap-2 text-sm text-zinc-400">
          Meses à frente
          <input
            type="number"
            min="1"
            value={monthsAhead}
            onChange={(e) => setMonthsAhead(Number(e.target.value) || 1)}
            className="w-20 rounded border border-zinc-600 bg-zinc-800 px-2 py-1 text-sm text-zinc-100"
          />
        </label>
      </div>
      <AsyncSection loading={loading} error={error}>
        {data && data.invoices.length > 0 ? (
          <ExpandableInvoiceList invoices={data.invoices} installments={installments ?? null} />
        ) : (
          <p className="text-sm text-zinc-500">Nenhuma fatura projetada.</p>
        )}
      </AsyncSection>
    </div>
  )
}
