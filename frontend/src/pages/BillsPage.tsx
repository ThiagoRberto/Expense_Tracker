import { useState, type FormEvent } from 'react'
import { billsApi } from '../api/entities'
import { useAsync } from '../hooks/useAsync'
import { useUser } from '../context/UserContext'
import { AsyncSection } from '../components/AsyncSection'
import { formatCurrency } from '../lib/format'

export function BillsPage() {
  const { userId } = useUser()
  const { data: bills, error, loading, reload } = useAsync(
    () => billsApi.list(userId as number),
    [userId],
  )
  const [name, setName] = useState('')
  const [billValue, setBillValue] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setFormError(null)
    setSubmitting(true)
    try {
      await billsApi.create(userId as number, { name, bill_value: Number(billValue) })
      setName('')
      setBillValue('')
      reload()
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Erro ao criar conta fixa')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-base font-semibold text-slate-900">Contas fixas</h2>
      <AsyncSection loading={loading} error={error}>
        {bills && bills.length > 0 ? (
          <ul className="divide-y divide-slate-200 rounded-md border border-slate-200 bg-white">
            {bills.map((bill) => (
              <li key={bill.id} className="flex items-center justify-between px-4 py-2">
                <span>{bill.name}</span>
                <span className="font-medium">{formatCurrency(bill.bill_value)}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-500">Nenhuma conta fixa cadastrada ainda.</p>
        )}
      </AsyncSection>

      <form onSubmit={handleSubmit} className="max-w-sm space-y-3">
        <div>
          <label htmlFor="bill-name" className="block text-sm text-slate-700">
            Nome
          </label>
          <input
            id="bill-name"
            required
            value={name}
            onChange={(event) => setName(event.target.value)}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label htmlFor="bill-value" className="block text-sm text-slate-700">
            Valor
          </label>
          <input
            id="bill-value"
            type="number"
            step="0.01"
            min="0"
            required
            value={billValue}
            onChange={(event) => setBillValue(event.target.value)}
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
          {submitting ? 'Salvando...' : 'Adicionar conta fixa'}
        </button>
      </form>
    </div>
  )
}
