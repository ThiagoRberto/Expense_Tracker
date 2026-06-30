import { useState, type FormEvent } from 'react'
import { incomesApi } from '../api/entities'
import { useAsync } from '../hooks/useAsync'
import { useUser } from '../context/UserContext'
import { AsyncSection } from '../components/AsyncSection'
import { formatCurrency } from '../lib/format'

const INPUT = 'mt-1 w-full rounded border border-zinc-600 bg-zinc-800 px-3 py-2 text-sm text-zinc-100'
const BTN_PRIMARY = 'rounded bg-orange-500 px-4 py-2 text-sm font-medium text-white hover:bg-orange-600 disabled:opacity-50 transition-colors'

export function IncomesPage() {
  const { userId } = useUser()
  const { data: incomes, error, loading, reload } = useAsync(
    () => incomesApi.list(userId as number),
    [userId],
  )
  const [name, setName] = useState('')
  const [incomeValue, setIncomeValue] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [deletingId, setDeletingId] = useState<number | null>(null)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setFormError(null)
    setSubmitting(true)
    try {
      await incomesApi.create(userId as number, { name, income_value: Number(incomeValue) })
      setName('')
      setIncomeValue('')
      reload()
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Erro ao criar receita')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(id: number) {
    await incomesApi.delete(userId as number, id)
    setDeletingId(null)
    reload()
  }

  return (
    <div className="space-y-6">
      <h2 className="text-base font-semibold text-zinc-100">Receitas</h2>
      <AsyncSection loading={loading} error={error}>
        {incomes && incomes.length > 0 ? (
          <ul className="divide-y divide-zinc-800 rounded-md border border-zinc-700 bg-zinc-900">
            {incomes.map((income) => (
              <li key={income.id} className="flex items-center justify-between px-4 py-2">
                <span className="text-zinc-200">{income.name}</span>
                <div className="flex items-center gap-3">
                  <span className="font-medium text-zinc-100">{formatCurrency(income.income_value)}</span>
                  {deletingId === income.id ? (
                    <span className="flex items-center gap-1 text-xs">
                      <button onClick={() => handleDelete(income.id)} className="text-red-400 hover:text-red-300 transition-colors">Confirmar</button>
                      <span className="text-zinc-600">|</span>
                      <button onClick={() => setDeletingId(null)} className="text-zinc-400 hover:text-zinc-200 transition-colors">Cancelar</button>
                    </span>
                  ) : (
                    <button
                      onClick={() => setDeletingId(income.id)}
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
          <p className="text-sm text-zinc-500">Nenhuma receita cadastrada ainda.</p>
        )}
      </AsyncSection>

      <form onSubmit={handleSubmit} className="max-w-sm space-y-3">
        <div>
          <label htmlFor="income-name" className="block text-sm text-zinc-300">Nome</label>
          <input id="income-name" required value={name} onChange={(e) => setName(e.target.value)} className={INPUT} />
        </div>
        <div>
          <label htmlFor="income-value" className="block text-sm text-zinc-300">Valor</label>
          <input
            id="income-value"
            type="number"
            step="0.01"
            min="0"
            required
            value={incomeValue}
            onChange={(e) => setIncomeValue(e.target.value)}
            className={INPUT}
          />
        </div>
        {formError && <p role="alert" className="text-sm text-red-400">{formError}</p>}
        <button type="submit" disabled={submitting} className={BTN_PRIMARY}>
          {submitting ? 'Salvando...' : 'Adicionar receita'}
        </button>
      </form>
    </div>
  )
}
