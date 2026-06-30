import { useState, type FormEvent } from 'react'
import { categoryBudgetsApi, expensesApi } from '../api/entities'
import { analyticsApi } from '../api/analytics'
import { useAsync } from '../hooks/useAsync'
import { useUser } from '../context/UserContext'
import { AsyncSection } from '../components/AsyncSection'
import { StatusBadge } from '../components/StatusBadge'
import { formatCurrency } from '../lib/format'

const SELECT = 'mt-1 w-full rounded border border-zinc-600 bg-zinc-800 px-3 py-2 text-sm text-zinc-100'
const INPUT = 'mt-1 w-full rounded border border-zinc-600 bg-zinc-800 px-3 py-2 text-sm text-zinc-100'
const BTN_PRIMARY = 'rounded bg-orange-500 px-4 py-2 text-sm font-medium text-white hover:bg-orange-600 disabled:opacity-50 transition-colors'

export function CategoryBudgetsPage() {
  const { userId } = useUser()
  const [reloadToken, setReloadToken] = useState(0)
  const reload = () => setReloadToken((t) => t + 1)

  const { data: alerts, error: alertsError, loading: alertsLoading } = useAsync(
    () => analyticsApi.categoryAlerts(userId as number),
    [userId, reloadToken],
  )
  const { data: budgets } = useAsync(
    () => categoryBudgetsApi.list(userId as number),
    [userId, reloadToken],
  )
  const { data: expenses } = useAsync(
    () => expensesApi.list(userId as number),
    [userId],
  )

  const existingCategories = [...new Set(
    (expenses ?? []).map((e) => e.category).filter(Boolean),
  )].sort()

  const usedCategories = new Set((alerts?.alerts ?? []).map((a) => a.category))
  const availableCategories = existingCategories.filter((c) => !usedCategories.has(c))

  const [category, setCategory] = useState('')
  const [ceiling, setCeiling] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [deletingCategory, setDeletingCategory] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setFormError(null)
    setSubmitting(true)
    try {
      await categoryBudgetsApi.create(userId as number, { category, ceiling: Number(ceiling) })
      setCategory('')
      setCeiling('')
      reload()
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Erro ao criar teto orçamentário')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(category: string) {
    const budget = budgets?.find((b) => b.category === category)
    if (!budget) return
    await categoryBudgetsApi.delete(userId as number, budget.id)
    setDeletingCategory(null)
    reload()
  }

  return (
    <div className="space-y-6">
      <h2 className="text-base font-semibold text-zinc-100">Tetos por categoria</h2>
      <AsyncSection loading={alertsLoading} error={alertsError}>
        {alerts && alerts.alerts.length > 0 ? (
          <ul className="divide-y divide-zinc-800 rounded-md border border-zinc-700 bg-zinc-900">
            {alerts.alerts.map((alert) => (
              <li key={alert.category} className="flex items-center justify-between px-4 py-3">
                <div>
                  <p className="font-medium text-zinc-100">{alert.category}</p>
                  <p className="text-xs text-zinc-500">
                    {formatCurrency(alert.total)} de {formatCurrency(alert.ceiling)}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <StatusBadge status={alert.status} />
                  {deletingCategory === alert.category ? (
                    <span className="flex items-center gap-1 text-xs">
                      <button onClick={() => handleDelete(alert.category)} className="text-red-400 hover:text-red-300 transition-colors">Confirmar</button>
                      <span className="text-zinc-600">|</span>
                      <button onClick={() => setDeletingCategory(null)} className="text-zinc-400 hover:text-zinc-200 transition-colors">Cancelar</button>
                    </span>
                  ) : (
                    <button
                      onClick={() => setDeletingCategory(alert.category)}
                      className="text-xs text-zinc-500 hover:text-red-400 transition-colors"
                    >
                      Excluir
                    </button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-zinc-500">Nenhum teto orçamentário definido ainda.</p>
        )}
      </AsyncSection>

      <form onSubmit={handleSubmit} className="max-w-sm space-y-3">
        <div>
          <label htmlFor="budget-category" className="block text-sm text-zinc-300">Categoria</label>
          {availableCategories.length > 0 ? (
            <select
              id="budget-category"
              required
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className={SELECT}
            >
              <option value="">Selecione uma categoria...</option>
              {availableCategories.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          ) : (
            <input
              id="budget-category"
              required
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="Nome da categoria"
              className={INPUT}
            />
          )}
        </div>
        <div>
          <label htmlFor="budget-ceiling" className="block text-sm text-zinc-300">Teto</label>
          <input
            id="budget-ceiling"
            type="number"
            step="0.01"
            min="0.01"
            required
            value={ceiling}
            onChange={(e) => setCeiling(e.target.value)}
            className={INPUT}
          />
        </div>
        {formError && <p role="alert" className="text-sm text-red-400">{formError}</p>}
        <button
          type="submit"
          disabled={submitting || (availableCategories.length > 0 && !category)}
          className={BTN_PRIMARY}
        >
          {submitting ? 'Salvando...' : 'Definir teto'}
        </button>
      </form>
    </div>
  )
}
