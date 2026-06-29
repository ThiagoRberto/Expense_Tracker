import { useState, type FormEvent } from 'react'
import { categoryBudgetsApi } from '../api/entities'
import { analyticsApi } from '../api/analytics'
import { useAsync } from '../hooks/useAsync'
import { useUser } from '../context/UserContext'
import { AsyncSection } from '../components/AsyncSection'
import { StatusBadge } from '../components/StatusBadge'
import { formatCurrency } from '../lib/format'

export function CategoryBudgetsPage() {
  const { userId } = useUser()
  const {
    data: alerts,
    error: alertsError,
    loading: alertsLoading,
    reload: reloadAlerts,
  } = useAsync(() => analyticsApi.categoryAlerts(userId as number), [userId])
  const [category, setCategory] = useState('')
  const [ceiling, setCeiling] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setFormError(null)
    setSubmitting(true)
    try {
      await categoryBudgetsApi.create(userId as number, {
        category,
        ceiling: Number(ceiling),
      })
      setCategory('')
      setCeiling('')
      reloadAlerts()
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Erro ao criar teto orçamentário')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-base font-semibold text-slate-900">Tetos por categoria</h2>
      <AsyncSection loading={alertsLoading} error={alertsError}>
        {alerts && alerts.alerts.length > 0 ? (
          <ul className="divide-y divide-slate-200 rounded-md border border-slate-200 bg-white">
            {alerts.alerts.map((alert) => (
              <li
                key={alert.category}
                className="flex items-center justify-between px-4 py-2"
              >
                <div>
                  <p className="font-medium">{alert.category}</p>
                  <p className="text-xs text-slate-500">
                    {formatCurrency(alert.total)} de {formatCurrency(alert.ceiling)}
                  </p>
                </div>
                <StatusBadge status={alert.status} />
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-500">Nenhum teto orçamentário definido ainda.</p>
        )}
      </AsyncSection>

      <form onSubmit={handleSubmit} className="max-w-sm space-y-3">
        <div>
          <label htmlFor="budget-category" className="block text-sm text-slate-700">
            Categoria
          </label>
          <input
            id="budget-category"
            required
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label htmlFor="budget-ceiling" className="block text-sm text-slate-700">
            Teto
          </label>
          <input
            id="budget-ceiling"
            type="number"
            step="0.01"
            min="0.01"
            required
            value={ceiling}
            onChange={(event) => setCeiling(event.target.value)}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        {formError && (
          <p role="alert" className="text-sm text-red-600">
            {formError}
          </p>
        )}
        <button
          type="submit"
          disabled={submitting}
          className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          {submitting ? 'Salvando...' : 'Definir teto'}
        </button>
      </form>
    </div>
  )
}
