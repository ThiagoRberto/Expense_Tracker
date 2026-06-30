import { useState, type FormEvent } from 'react'
import { investmentsApi } from '../api/entities'
import { useAsync } from '../hooks/useAsync'
import { useUser } from '../context/UserContext'
import { AsyncSection } from '../components/AsyncSection'
import { formatCurrency } from '../lib/format'

const INPUT = 'mt-1 w-full rounded border border-zinc-600 bg-zinc-800 px-3 py-2 text-sm text-zinc-100'
const BTN_PRIMARY = 'rounded bg-orange-500 px-4 py-2 text-sm font-medium text-white hover:bg-orange-600 disabled:opacity-50 transition-colors'

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
  const [deletingId, setDeletingId] = useState<number | null>(null)

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

  async function handleDelete(id: number) {
    await investmentsApi.delete(userId as number, id)
    setDeletingId(null)
    reload()
  }

  return (
    <div className="space-y-6">
      <h2 className="text-base font-semibold text-zinc-100">Investimentos</h2>
      <AsyncSection loading={loading} error={error}>
        {investments && investments.length > 0 ? (
          <ul className="divide-y divide-zinc-800 rounded-md border border-zinc-700 bg-zinc-900">
            {investments.map((investment) => (
              <li key={investment.id} className="flex items-center justify-between px-4 py-2">
                <span className="text-zinc-200">{investment.name}</span>
                <div className="flex items-center gap-3">
                  <span className="font-medium text-zinc-100">
                    {formatCurrency(investment.value_invested)}{' '}
                    <span className="text-xs text-green-400">
                      +{formatCurrency(investment.dividends)}
                    </span>
                  </span>
                  {deletingId === investment.id ? (
                    <span className="flex items-center gap-1 text-xs">
                      <button onClick={() => handleDelete(investment.id)} className="text-red-400 hover:text-red-300 transition-colors">Confirmar</button>
                      <span className="text-zinc-600">|</span>
                      <button onClick={() => setDeletingId(null)} className="text-zinc-400 hover:text-zinc-200 transition-colors">Cancelar</button>
                    </span>
                  ) : (
                    <button
                      onClick={() => setDeletingId(investment.id)}
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
          <p className="text-sm text-zinc-500">Nenhum investimento cadastrado ainda.</p>
        )}
      </AsyncSection>

      <form onSubmit={handleSubmit} className="max-w-sm space-y-3">
        <div>
          <label htmlFor="investment-name" className="block text-sm text-zinc-300">Nome</label>
          <input id="investment-name" required value={name} onChange={(e) => setName(e.target.value)} className={INPUT} />
        </div>
        <div>
          <label htmlFor="investment-value" className="block text-sm text-zinc-300">Capital investido</label>
          <input
            id="investment-value"
            type="number"
            step="0.01"
            min="0"
            required
            value={valueInvested}
            onChange={(e) => setValueInvested(e.target.value)}
            className={INPUT}
          />
        </div>
        <div>
          <label htmlFor="investment-dividends" className="block text-sm text-zinc-300">Dividendos (opcional)</label>
          <input
            id="investment-dividends"
            type="number"
            step="0.01"
            min="0"
            value={dividends}
            onChange={(e) => setDividends(e.target.value)}
            className={INPUT}
          />
        </div>
        {formError && <p role="alert" className="text-sm text-red-400">{formError}</p>}
        <button type="submit" disabled={submitting} className={BTN_PRIMARY}>
          {submitting ? 'Salvando...' : 'Adicionar investimento'}
        </button>
      </form>
    </div>
  )
}
