import { useState, type FormEvent } from 'react'
import { expensesApi } from '../api/entities'
import { useAsync } from '../hooks/useAsync'
import { useUser } from '../context/UserContext'
import { AsyncSection } from '../components/AsyncSection'
import { formatCurrency } from '../lib/format'

export function ExpensesPage() {
  const { userId } = useUser()
  const { data: expenses, error, loading, reload } = useAsync(
    () => expensesApi.list(userId as number),
    [userId],
  )
  const [name, setName] = useState('')
  const [category, setCategory] = useState('')
  const [expenseValue, setExpenseValue] = useState('')
  const [installment, setInstallment] = useState('1')
  const [startMonth, setStartMonth] = useState('')
  const [startYear, setStartYear] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setFormError(null)
    setSubmitting(true)
    try {
      await expensesApi.create(userId as number, {
        name,
        category: category.trim() || undefined,
        expense_value: Number(expenseValue),
        installment: installment.trim() ? Number(installment) : undefined,
        start_month: startMonth.trim() ? Number(startMonth) : undefined,
        start_year: startYear.trim() ? Number(startYear) : undefined,
      })
      setName('')
      setCategory('')
      setExpenseValue('')
      setInstallment('1')
      setStartMonth('')
      setStartYear('')
      reload()
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Erro ao criar despesa')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-base font-semibold text-slate-900">Despesas</h2>
      <AsyncSection loading={loading} error={error}>
        {expenses && expenses.length > 0 ? (
          <ul className="divide-y divide-slate-200 rounded-md border border-slate-200 bg-white">
            {expenses.map((expense) => (
              <li key={expense.id} className="flex items-center justify-between px-4 py-2">
                <span>
                  {expense.name}{' '}
                  <span className="text-xs text-slate-400">({expense.category})</span>
                </span>
                <span className="font-medium">
                  {formatCurrency(expense.expense_value)}
                  {expense.installment > 1 ? ` em ${expense.installment}x` : ''}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-500">Nenhuma despesa cadastrada ainda.</p>
        )}
      </AsyncSection>

      <form onSubmit={handleSubmit} className="max-w-sm space-y-3">
        <div>
          <label htmlFor="expense-name" className="block text-sm text-slate-700">
            Nome
          </label>
          <input
            id="expense-name"
            required
            value={name}
            onChange={(event) => setName(event.target.value)}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label htmlFor="expense-category" className="block text-sm text-slate-700">
            Categoria (opcional)
          </label>
          <input
            id="expense-category"
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label htmlFor="expense-value" className="block text-sm text-slate-700">
            Valor total
          </label>
          <input
            id="expense-value"
            type="number"
            step="0.01"
            min="0"
            required
            value={expenseValue}
            onChange={(event) => setExpenseValue(event.target.value)}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label htmlFor="expense-installment" className="block text-sm text-slate-700">
            Número de parcelas
          </label>
          <input
            id="expense-installment"
            type="number"
            min="1"
            value={installment}
            onChange={(event) => setInstallment(event.target.value)}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div className="flex gap-3">
          <div className="flex-1">
            <label htmlFor="expense-start-month" className="block text-sm text-slate-700">
              Mês da 1ª parcela
            </label>
            <input
              id="expense-start-month"
              type="number"
              min="1"
              max="12"
              value={startMonth}
              onChange={(event) => setStartMonth(event.target.value)}
              className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
          <div className="flex-1">
            <label htmlFor="expense-start-year" className="block text-sm text-slate-700">
              Ano da 1ª parcela
            </label>
            <input
              id="expense-start-year"
              type="number"
              min="1"
              value={startYear}
              onChange={(event) => setStartYear(event.target.value)}
              className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
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
          {submitting ? 'Salvando...' : 'Adicionar despesa'}
        </button>
      </form>
    </div>
  )
}
