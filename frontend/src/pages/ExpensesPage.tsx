import { useState, type FormEvent } from 'react'
import { expensesApi } from '../api/entities'
import { useAsync } from '../hooks/useAsync'
import { useUser } from '../context/UserContext'
import { AsyncSection } from '../components/AsyncSection'
import { formatCurrency } from '../lib/format'

const INPUT = 'mt-1 w-full rounded border border-zinc-600 bg-zinc-800 px-3 py-2 text-sm text-zinc-100'
const SELECT = 'mt-1 w-full rounded border border-zinc-600 bg-zinc-800 px-3 py-2 text-sm text-zinc-100'
const BTN_PRIMARY = 'rounded bg-orange-500 px-4 py-2 text-sm font-medium text-white hover:bg-orange-600 disabled:opacity-50 transition-colors'

const MONTHS = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
]

const currentYear = new Date().getFullYear()
const YEARS = Array.from({ length: 11 }, (_, i) => currentYear - 2 + i)

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
  const [startMonth, setStartMonth] = useState(String(new Date().getMonth() + 1))
  const [startYear, setStartYear] = useState(String(currentYear))
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [deletingId, setDeletingId] = useState<number | null>(null)

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
        start_month: startMonth ? Number(startMonth) : undefined,
        start_year: startYear ? Number(startYear) : undefined,
      })
      setName('')
      setCategory('')
      setExpenseValue('')
      setInstallment('1')
      setStartMonth(String(new Date().getMonth() + 1))
      setStartYear(String(currentYear))
      reload()
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Erro ao criar despesa')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(id: number) {
    await expensesApi.delete(userId as number, id)
    setDeletingId(null)
    reload()
  }

  return (
    <div className="space-y-6">
      <h2 className="text-base font-semibold text-zinc-100">Despesas</h2>
      <AsyncSection loading={loading} error={error}>
        {expenses && expenses.length > 0 ? (
          <ul className="divide-y divide-zinc-800 rounded-md border border-zinc-700 bg-zinc-900">
            {expenses.map((expense) => (
              <li key={expense.id} className="flex items-center justify-between px-4 py-2">
                <span className="text-zinc-200">
                  {expense.name}{' '}
                  <span className="text-xs text-zinc-500">({expense.category})</span>
                </span>
                <div className="flex items-center gap-3">
                  <span className="font-medium text-zinc-100">
                    {formatCurrency(expense.expense_value)}
                    {expense.installment > 1 && (
                      <span className="text-xs text-zinc-400"> em {expense.installment}x</span>
                    )}
                  </span>
                  {deletingId === expense.id ? (
                    <span className="flex items-center gap-1 text-xs">
                      <button onClick={() => handleDelete(expense.id)} className="text-red-400 hover:text-red-300 transition-colors">Confirmar</button>
                      <span className="text-zinc-600">|</span>
                      <button onClick={() => setDeletingId(null)} className="text-zinc-400 hover:text-zinc-200 transition-colors">Cancelar</button>
                    </span>
                  ) : (
                    <button
                      onClick={() => setDeletingId(expense.id)}
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
          <p className="text-sm text-zinc-500">Nenhuma despesa cadastrada ainda.</p>
        )}
      </AsyncSection>

      <form onSubmit={handleSubmit} className="max-w-sm space-y-3">
        <div>
          <label htmlFor="expense-name" className="block text-sm text-zinc-300">Nome</label>
          <input id="expense-name" required value={name} onChange={(e) => setName(e.target.value)} className={INPUT} />
        </div>
        <div>
          <label htmlFor="expense-category" className="block text-sm text-zinc-300">Categoria (opcional)</label>
          <input
            id="expense-category"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className={INPUT}
          />
        </div>
        <div>
          <label htmlFor="expense-value" className="block text-sm text-zinc-300">Valor total</label>
          <input
            id="expense-value"
            type="number"
            step="0.01"
            min="0"
            required
            value={expenseValue}
            onChange={(e) => setExpenseValue(e.target.value)}
            className={INPUT}
          />
        </div>
        <div>
          <label htmlFor="expense-installment" className="block text-sm text-zinc-300">Número de parcelas</label>
          <input
            id="expense-installment"
            type="number"
            min="1"
            value={installment}
            onChange={(e) => setInstallment(e.target.value)}
            className={INPUT}
          />
        </div>
        <div className="flex gap-3">
          <div className="flex-1">
            <label htmlFor="expense-start-month" className="block text-sm text-zinc-300">Mês da 1ª parcela</label>
            <select
              id="expense-start-month"
              value={startMonth}
              onChange={(e) => setStartMonth(e.target.value)}
              className={SELECT}
            >
              {MONTHS.map((label, i) => (
                <option key={i + 1} value={i + 1}>
                  {label}
                </option>
              ))}
            </select>
          </div>
          <div className="flex-1">
            <label htmlFor="expense-start-year" className="block text-sm text-zinc-300">Ano da 1ª parcela</label>
            <select
              id="expense-start-year"
              value={startYear}
              onChange={(e) => setStartYear(e.target.value)}
              className={SELECT}
            >
              {YEARS.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
          </div>
        </div>
        {formError && <p role="alert" className="text-sm text-red-400">{formError}</p>}
        <button type="submit" disabled={submitting} className={BTN_PRIMARY}>
          {submitting ? 'Salvando...' : 'Adicionar despesa'}
        </button>
      </form>
    </div>
  )
}
