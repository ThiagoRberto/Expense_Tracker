import { NavLink, Outlet } from 'react-router-dom'
import { useUser } from '../context/UserContext'

const NAV_ITEMS = [
  { to: '/', label: 'Resumo' },
  { to: '/receitas', label: 'Receitas' },
  { to: '/despesas', label: 'Despesas' },
  { to: '/contas', label: 'Contas fixas' },
  { to: '/investimentos', label: 'Investimentos' },
  { to: '/categorias', label: 'Tetos por categoria' },
  { to: '/parcelas', label: 'Parcelas' },
  { to: '/faturas', label: 'Faturas futuras' },
]

export function Layout() {
  const { userId, userName, setUser } = useUser()

  return (
    <div className="min-h-screen bg-zinc-950">
      <header className="border-b border-zinc-800 bg-zinc-900">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <h1 className="text-lg font-semibold text-zinc-100">
            <span className="text-orange-500">Expense</span> Tracker
          </h1>
          {userId !== null && (
            <button
              type="button"
              onClick={() => setUser(null, null)}
              className="text-sm text-zinc-400 hover:text-zinc-200 transition-colors"
            >
              Trocar usuário ({userName ?? `#${userId}`})
            </button>
          )}
        </div>
        {userId !== null && (
          <nav className="mx-auto flex max-w-5xl gap-4 overflow-x-auto px-6 pb-3 text-sm">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  isActive
                    ? 'whitespace-nowrap font-medium text-orange-400 border-b-2 border-orange-400 pb-0.5'
                    : 'whitespace-nowrap text-zinc-400 hover:text-zinc-200 transition-colors'
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        )}
      </header>
      <main className="mx-auto max-w-5xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  )
}
