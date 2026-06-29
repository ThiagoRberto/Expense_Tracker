import { useState, type FormEvent } from 'react'
import { useAsync } from '../hooks/useAsync'
import { usersApi } from '../api/users'
import { useUser } from '../context/UserContext'
import { AsyncSection } from '../components/AsyncSection'

export function SelectUserPage() {
  const { setUserId } = useUser()
  const { data: users, error, loading } = useAsync(() => usersApi.list(), [])
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [budgetCeiling, setBudgetCeiling] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleCreate(event: FormEvent) {
    event.preventDefault()
    setFormError(null)
    setSubmitting(true)
    try {
      const ceiling = budgetCeiling.trim() ? Number(budgetCeiling) : undefined
      const user = await usersApi.create({
        name,
        password,
        budget_ceiling: ceiling,
      })
      setUserId(user.id)
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Erro ao criar usuário')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-8">
      <section>
        <h2 className="mb-3 text-base font-semibold text-slate-900">Selecionar usuário</h2>
        <AsyncSection loading={loading} error={error}>
          {users && users.length > 0 ? (
            <ul className="divide-y divide-slate-200 rounded-md border border-slate-200 bg-white">
              {users.map((user) => (
                <li key={user.id} className="flex items-center justify-between px-4 py-2">
                  <span>{user.name}</span>
                  <button
                    type="button"
                    onClick={() => setUserId(user.id)}
                    className="rounded bg-indigo-600 px-3 py-1 text-sm text-white hover:bg-indigo-700"
                  >
                    Entrar
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-slate-500">Nenhum usuário cadastrado ainda.</p>
          )}
        </AsyncSection>
      </section>

      <section>
        <h2 className="mb-3 text-base font-semibold text-slate-900">Criar novo usuário</h2>
        <form onSubmit={handleCreate} className="max-w-sm space-y-3">
          <div>
            <label htmlFor="name" className="block text-sm text-slate-700">
              Nome
            </label>
            <input
              id="name"
              required
              value={name}
              onChange={(event) => setName(event.target.value)}
              className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm text-slate-700">
              Senha
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label htmlFor="budget_ceiling" className="block text-sm text-slate-700">
              Teto orçamentário (opcional)
            </label>
            <input
              id="budget_ceiling"
              type="number"
              step="0.01"
              min="0"
              value={budgetCeiling}
              onChange={(event) => setBudgetCeiling(event.target.value)}
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
            {submitting ? 'Criando...' : 'Criar usuário'}
          </button>
        </form>
      </section>
    </div>
  )
}
