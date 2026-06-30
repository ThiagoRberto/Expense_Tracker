import { useState, type FormEvent } from 'react'
import { analyticsApi } from '../api/analytics'
import { usersApi } from '../api/users'
import { useAsync } from '../hooks/useAsync'
import { useUser } from '../context/UserContext'
import { AsyncSection } from '../components/AsyncSection'
import { StatusBadge } from '../components/StatusBadge'
import { SpendingDonut } from '../components/SpendingDonut'
import { ExpandableInvoiceList } from '../components/ExpandableInvoiceList'
import { formatCurrency } from '../lib/format'

function Card({
  label,
  value,
  tone,
}: {
  label: string
  value: string
  tone?: 'positive' | 'negative'
}) {
  const valueClass =
    tone === 'positive' ? 'text-green-400' : tone === 'negative' ? 'text-red-400' : 'text-zinc-100'
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-900 p-4">
      <p className="text-sm text-zinc-400">{label}</p>
      <p className={`mt-1 text-2xl font-semibold ${valueClass}`}>{value}</p>
    </div>
  )
}

function BudgetCeilingSection({
  userId,
  currentCeiling,
  onUpdated,
}: {
  userId: number
  currentCeiling: number | null
  onUpdated: () => void
}) {
  const [editing, setEditing] = useState(false)
  const [inputValue, setInputValue] = useState(currentCeiling ? String(currentCeiling) : '')
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setSaving(true)
    try {
      const ceiling = inputValue.trim() ? Number(inputValue) : null
      await usersApi.updateBudgetCeiling(userId, ceiling)
      setEditing(false)
      onUpdated()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao salvar')
    } finally {
      setSaving(false)
    }
  }

  if (editing) {
    return (
      <form onSubmit={handleSubmit} className="flex items-center gap-2">
        <input
          type="number"
          step="0.01"
          min="0.01"
          autoFocus
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Novo teto"
          className="w-40 rounded border border-zinc-600 bg-zinc-800 px-2 py-1 text-sm text-zinc-100"
        />
        <button
          type="submit"
          disabled={saving}
          className="rounded bg-orange-500 px-3 py-1 text-sm text-white hover:bg-orange-600 disabled:opacity-50 transition-colors"
        >
          {saving ? 'Salvando…' : 'Salvar'}
        </button>
        <button
          type="button"
          onClick={() => { setEditing(false); setError(null) }}
          className="text-sm text-zinc-400 hover:text-zinc-200 transition-colors"
        >
          Cancelar
        </button>
        {error && <p role="alert" className="text-sm text-red-400">{error}</p>}
      </form>
    )
  }

  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-zinc-400">
        Teto orçamentário:{' '}
        <span className="font-medium text-zinc-200">
          {currentCeiling ? formatCurrency(currentCeiling) : 'não definido'}
        </span>
      </span>
      <button
        type="button"
        onClick={() => { setInputValue(currentCeiling ? String(currentCeiling) : ''); setEditing(true) }}
        className="text-sm text-orange-400 hover:underline transition-colors"
      >
        Editar
      </button>
    </div>
  )
}

export function DashboardPage() {
  const { userId } = useUser()
  const [summaryReloadToken, setSummaryReloadToken] = useState(0)

  const { data: summary, error: summaryError, loading: summaryLoading } = useAsync(
    () => analyticsApi.summary(userId as number),
    [userId, summaryReloadToken],
  )
  const { data: user, loading: userLoading, error: userError, reload: reloadUser } = useAsync(
    () => usersApi.get(userId as number),
    [userId],
  )
  const { data: invoices, error: invoicesError, loading: invoicesLoading } = useAsync(
    () => analyticsApi.monthlyInvoices(userId as number, 6),
    [userId, summaryReloadToken],
  )
  const { data: installments } = useAsync(
    () => analyticsApi.installments(userId as number),
    [userId, summaryReloadToken],
  )

  return (
    <div className="space-y-8">
      <section>
        <h2 className="mb-4 text-base font-semibold text-zinc-100">Resumo financeiro</h2>
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start">
          <div className="flex-1 space-y-4">
            <AsyncSection loading={summaryLoading} error={summaryError}>
              {summary && (
                <div className="grid grid-cols-2 gap-4">
                  <Card
                    label="Saldo do mês"
                    value={formatCurrency(summary.balance)}
                    tone={summary.balance >= 0 ? 'positive' : 'negative'}
                  />
                  <Card label="Patrimônio líquido" value={formatCurrency(summary.net_worth)} />
                  <Card label="Receitas" value={formatCurrency(summary.total_income)} />
                  <Card label="Gastos" value={formatCurrency(summary.total_spending)} />
                </div>
              )}
            </AsyncSection>

            <AsyncSection loading={userLoading} error={userError}>
              {user && (
                <div className="flex flex-wrap items-center gap-4">
                  <BudgetCeilingSection
                    userId={userId as number}
                    currentCeiling={user.budget_ceiling}
                    onUpdated={() => { reloadUser(); setSummaryReloadToken((t) => t + 1) }}
                  />
                  {summary?.budget_status && <StatusBadge status={summary.budget_status} />}
                </div>
              )}
            </AsyncSection>
          </div>

          <div className="w-full lg:w-72 rounded-lg border border-zinc-700 bg-zinc-900 p-4">
            <p className="mb-2 text-sm font-medium text-zinc-400">Gastos por categoria</p>
            <AsyncSection loading={userLoading} error={userError}>
              {user && <SpendingDonut user={user} />}
            </AsyncSection>
          </div>
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-base font-semibold text-zinc-100">
          Faturas futuras (próximos 6 meses)
        </h2>
        <AsyncSection loading={invoicesLoading} error={invoicesError}>
          {invoices && invoices.invoices.length > 0 ? (
            <ExpandableInvoiceList invoices={invoices.invoices} installments={installments ?? null} />
          ) : (
            <p className="text-sm text-zinc-500">Nenhuma fatura projetada.</p>
          )}
        </AsyncSection>
      </section>
    </div>
  )
}
