import { useState, type FormEvent } from 'react'
import { incomesApi } from '../api/entities'
import { useAsync } from '../hooks/useAsync'
import { useUser } from '../context/UserContext'
import { AsyncSection } from '../components/AsyncSection'
import { formatCurrency } from '../lib/format'

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

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setFormError(null)
    setSubmitting(true)
    try {
      await incomesApi.create(userId as number, {
        name,
        income_value: Number(incomeValue),
      })
      setName('')
      setIncomeValue('')
      reload()
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Erro ao criar receita')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-base font-semibold text-slate-900">Receitas</h2>
      <AsyncSection loading={loading} error={error}>
        {incomes && incomes.length > 0 ? (
          <ul className="divide-y divide-slate-200 rounded-md border border-slate-200 bg-white">
            {incomes.map((income) => (
              <li key={income.id} className="flex items-center justify-between px-4 py-2">
                <span>{income.name}</span>
                <span className="font-medium">{formatCurrency(income.income_value)}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-500">Nenhuma receita cadastrada ainda.</p>
        )}
      </AsyncSection>

      <form onSubmit={handleSubmit} className="max-w-sm space-y-3">
        <div>
          <label htmlFor="income-name" className="block text-sm text-slate-700">
            Nome
          </label>
          <input
            id="income-name"
            required
            value={name}
            onChange={(event) => setName(event.target.value)}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label htmlFor="income-value" className="block text-sm text-slate-700">
            Valor
          </label>
          <input
            id="income-value"
            type="number"
            step="0.01"
            min="0"
            required
            value={incomeValue}
            onChange={(event) => setIncomeValue(event.target.value)}
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
          {submitting ? 'Salvando...' : 'Adicionar receita'}
        </button>
      </form>
    </div>
  )
}
