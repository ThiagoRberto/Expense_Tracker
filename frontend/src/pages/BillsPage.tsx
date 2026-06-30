import { useState, type FormEvent } from 'react'
import { billsApi } from '../api/entities'
import { useAsync } from '../hooks/useAsync'
import { useUser } from '../context/UserContext'
import { AsyncSection } from '../components/AsyncSection'
import { formatCurrency } from '../lib/format'

const INPUT = 'mt-1 w-full rounded border border-zinc-600 bg-zinc-800 px-3 py-2 text-sm text-zinc-100'
const BTN_PRIMARY = 'rounded bg-orange-500 px-4 py-2 text-sm font-medium text-white hover:bg-orange-600 disabled:opacity-50 transition-colors'

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
  const [deletingId, setDeletingId] = useState<number | null>(null)

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

  async function handleDelete(id: number) {
    await billsApi.delete(userId as number, id)
    setDeletingId(null)
    reload()
  }

  return (
    <div className="space-y-6">
      <h2 className="text-base font-semibold text-zinc-100">Contas fixas</h2>
      <AsyncSection loading={loading} error={error}>
        {bills && bills.length > 0 ? (
          <ul className="divide-y divide-zinc-800 rounded-md border border-zinc-700 bg-zinc-900">
            {bills.map((bill) => (
              <li key={bill.id} className="flex items-center justify-between px-4 py-2">
                <span className="text-zinc-200">{bill.name}</span>
                <div className="flex items-center gap-3">
                  <span className="font-medium text-zinc-100">{formatCurrency(bill.bill_value)}</span>
                  {deletingId === bill.id ? (
                    <span className="flex items-center gap-1 text-xs">
                      <button onClick={() => handleDelete(bill.id)} className="text-red-400 hover:text-red-300 transition-colors">Confirmar</button>
                      <span className="text-zinc-600">|</span>
                      <button onClick={() => setDeletingId(null)} className="text-zinc-400 hover:text-zinc-200 transition-colors">Cancelar</button>
                    </span>
                  ) : (
                    <button
                      onClick={() => setDeletingId(bill.id)}
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
          <p className="text-sm text-zinc-500">Nenhuma conta fixa cadastrada ainda.</p>
        )}
      </AsyncSection>

      <form onSubmit={handleSubmit} className="max-w-sm space-y-3">
        <div>
          <label htmlFor="bill-name" className="block text-sm text-zinc-300">Nome</label>
          <input id="bill-name" required value={name} onChange={(e) => setName(e.target.value)} className={INPUT} />
        </div>
        <div>
          <label htmlFor="bill-value" className="block text-sm text-zinc-300">Valor</label>
          <input
            id="bill-value"
            type="number"
            step="0.01"
            min="0"
            required
            value={billValue}
            onChange={(e) => setBillValue(e.target.value)}
            className={INPUT}
          />
        </div>
        {formError && <p role="alert" className="text-sm text-red-400">{formError}</p>}
        <button type="submit" disabled={submitting} className={BTN_PRIMARY}>
          {submitting ? 'Salvando...' : 'Adicionar conta fixa'}
        </button>
      </form>
    </div>
  )
}
