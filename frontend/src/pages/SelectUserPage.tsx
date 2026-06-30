import { useState, type FormEvent } from 'react'
import { useAsync } from '../hooks/useAsync'
import { usersApi } from '../api/users'
import { useUser } from '../context/UserContext'
import { AsyncSection } from '../components/AsyncSection'
import type { User } from '../types/api'

const INPUT = 'mt-1 w-full rounded border border-zinc-600 bg-zinc-800 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500'
const BTN_PRIMARY = 'rounded bg-orange-500 px-4 py-2 text-sm font-medium text-white hover:bg-orange-600 disabled:opacity-50 transition-colors'

export function SelectUserPage() {
  const { setUser } = useUser()
  const { data: users, error, loading } = useAsync(() => usersApi.list(), [])

  const [loginTarget, setLoginTarget] = useState<User | null>(null)
  const [loginPassword, setLoginPassword] = useState('')
  const [loginError, setLoginError] = useState<string | null>(null)
  const [loginSubmitting, setLoginSubmitting] = useState(false)

  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [budgetCeiling, setBudgetCeiling] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleLogin(event: FormEvent) {
    event.preventDefault()
    if (!loginTarget) return
    setLoginError(null)
    setLoginSubmitting(true)
    try {
      const user = await usersApi.login(loginTarget.name, loginPassword)
      setUser(user.id, user.name)
    } catch {
      setLoginError('Senha incorreta.')
    } finally {
      setLoginSubmitting(false)
    }
  }

  async function handleCreate(event: FormEvent) {
    event.preventDefault()
    setFormError(null)
    setSubmitting(true)
    try {
      const ceiling = budgetCeiling.trim() ? Number(budgetCeiling) : undefined
      const user = await usersApi.create({ name, password, budget_ceiling: ceiling })
      setUser(user.id, user.name)
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Erro ao criar usuário')
    } finally {
      setSubmitting(false)
    }
  }

  if (loginTarget) {
    return (
      <div className="space-y-6">
        <button
          type="button"
          onClick={() => { setLoginTarget(null); setLoginError(null); setLoginPassword('') }}
          className="text-sm text-zinc-400 hover:text-zinc-200 transition-colors"
        >
          ← Voltar
        </button>
        <h2 className="text-base font-semibold text-zinc-100">
          Entrar como <span className="text-orange-400">{loginTarget.name}</span>
        </h2>
        <form onSubmit={handleLogin} className="max-w-sm space-y-3">
          <div>
            <label htmlFor="login-password" className="block text-sm text-zinc-300">Senha</label>
            <input
              id="login-password"
              type="password"
              required
              autoFocus
              value={loginPassword}
              onChange={(e) => setLoginPassword(e.target.value)}
              className={INPUT}
            />
          </div>
          {loginError && <p role="alert" className="text-sm text-red-400">{loginError}</p>}
          <button type="submit" disabled={loginSubmitting} className={BTN_PRIMARY}>
            {loginSubmitting ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
      </div>
    )
  }

  return (
    <div className="space-y-10">
      <section>
        <h2 className="mb-4 text-base font-semibold text-zinc-100">Selecionar usuário</h2>
        <AsyncSection loading={loading} error={error}>
          {users && users.length > 0 ? (
            <ul className="divide-y divide-zinc-800 rounded-md border border-zinc-700 bg-zinc-900">
              {users.map((user) => (
                <li key={user.id} className="flex items-center justify-between px-4 py-3">
                  <span className="text-zinc-200">{user.name}</span>
                  <button
                    type="button"
                    onClick={() => setLoginTarget(user)}
                    className="rounded bg-orange-500 px-3 py-1 text-sm text-white hover:bg-orange-600 transition-colors"
                  >
                    Entrar
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-zinc-500">Nenhum usuário cadastrado ainda.</p>
          )}
        </AsyncSection>
      </section>

      <section>
        <h2 className="mb-4 text-base font-semibold text-zinc-100">Criar novo usuário</h2>
        <form onSubmit={handleCreate} className="max-w-sm space-y-3">
          <div>
            <label htmlFor="name" className="block text-sm text-zinc-300">Nome</label>
            <input id="name" required value={name} onChange={(e) => setName(e.target.value)} className={INPUT} />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm text-zinc-300">Senha</label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={INPUT}
            />
          </div>
          <div>
            <label htmlFor="budget_ceiling" className="block text-sm text-zinc-300">
              Teto orçamentário (opcional)
            </label>
            <input
              id="budget_ceiling"
              type="number"
              step="0.01"
              min="0"
              value={budgetCeiling}
              onChange={(e) => setBudgetCeiling(e.target.value)}
              className={INPUT}
            />
          </div>
          {formError && <p role="alert" className="text-sm text-red-400">{formError}</p>}
          <button type="submit" disabled={submitting} className={BTN_PRIMARY}>
            {submitting ? 'Criando...' : 'Criar usuário'}
          </button>
        </form>
      </section>
    </div>
  )
}
