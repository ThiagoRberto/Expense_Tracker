import { analyticsApi } from '../api/analytics'
import { useAsync } from '../hooks/useAsync'
import { useUser } from '../context/UserContext'
import { AsyncSection } from '../components/AsyncSection'
import { StatusBadge } from '../components/StatusBadge'
import { formatCurrency } from '../lib/format'

function Card({ label, value, tone }: { label: string; value: string; tone?: 'positive' | 'negative' }) {
  const valueClass =
    tone === 'positive'
      ? 'text-green-700'
      : tone === 'negative'
        ? 'text-red-700'
        : 'text-slate-900'
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <p className="text-sm text-slate-500">{label}</p>
      <p className={`mt-1 text-2xl font-semibold ${valueClass}`}>{value}</p>
    </div>
  )
}

export function DashboardPage() {
  const { userId } = useUser()
  const { data, error, loading } = useAsync(
    () => analyticsApi.summary(userId as number),
    [userId],
  )

  return (
    <div className="space-y-6">
      <h2 className="text-base font-semibold text-slate-900">Resumo financeiro</h2>
      <AsyncSection loading={loading} error={error}>
        {data && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card
              label="Saldo do mês"
              value={formatCurrency(data.balance)}
              tone={data.balance >= 0 ? 'positive' : 'negative'}
            />
            <Card label="Patrimônio líquido" value={formatCurrency(data.net_worth)} />
            <Card label="Receitas" value={formatCurrency(data.total_income)} />
            <Card label="Gastos" value={formatCurrency(data.total_spending)} />
          </div>
        )}
        {data?.budget_status && (
          <div className="mt-4 flex items-center gap-2">
            <span className="text-sm text-slate-600">Teto orçamentário:</span>
            <StatusBadge status={data.budget_status} />
          </div>
        )}
      </AsyncSection>
    </div>
  )
}
