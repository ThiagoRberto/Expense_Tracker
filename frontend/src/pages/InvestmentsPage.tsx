import { useState, type FormEvent } from 'react'
import { investmentsApi } from '../api/entities'
import { useAsync } from '../hooks/useAsync'
import { useUser } from '../context/UserContext'
import { AsyncSection } from '../components/AsyncSection'
import { formatCurrency } from '../lib/format'

export function InvestmentsPage() {
  const { userId } = useUser()
  const { data: investments, error, loading, reload } = useAsync(
    () => investmentsApi.list(userId as number),
    [userId],
  )
  const [name, setName] = useState('')
  const [valueInvested, setValueInvested] = useState('')
  const [dividends, setDividends] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setFormError(null)
    setSubmitting(true)
    try {
      await investmentsApi.create(userId as number, {
        name,
        value_invested: Number(valueInvested),
        dividends: dividends.trim() ? Number(dividends) : undefined,
      })
      setName('')
      setValueInvested('')
      setDividends('')
      reload()
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Erro ao criar investimento')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-base font-semibold text-slate-900">Investimentos</h2>
      <AsyncSection loading={loading} error={error}>
        {investments && investments.length > 0 ? (
          <ul className="divide-y divide-slate-200 rounded-md border border-slate-200 bg-white">
            {investments.map((investment) => (
              <li key={investment.id} className="flex items-center justify-between px-4 py-2">
                <span>{investment.name}</span>
                <span className="font-medium">
                  {formatCurrency(investment.value_invested)} (+
                  {formatCurrency(investment.dividends)})
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-500">Nenhum investimento cadastrado ainda.</p>
        )}
      </AsyncSection>

      <form onSubmit={handleSubmit} className="max-w-sm space-y-3">
        <div>
          <label htmlFor="investment-name" className="block text-sm text-slate-700">
            Nome
          </label>
          <input
            id="investment-name"
            required
            value={name}
            onChange={(event) => setName(event.target.value)}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label htmlFor="investment-value" className="block text-sm text-slate-700">
            Capital investido
          </label>
          <input
            id="investment-value"
            type="number"
            step="0.01"
            min="0"
            required
            value={valueInvested}
            onChange={(event) => setValueInvested(event.target.value)}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label htmlFor="investment-dividends" className="block text-sm text-slate-700">
            Dividendos (opcional)
          </label>
          <input
            id="investment-dividends"
            type="number"
            step="0.01"
            min="0"
            value={dividends}
            onChange={(event) => setDividends(event.target.value)}
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
          {submitting ? 'Salvando...' : 'Adicionar investimento'}
        </button>
      </form>
    </div>
  )
}
