import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { DashboardPage } from './DashboardPage'
import { UserProvider } from '../context/UserContext'

const MOCK_USER = {
  id: 1,
  name: 'Ana',
  budget_ceiling: 3000,
  bills: [],
  expenses: [],
  incomes: [],
  investments: [],
}

const MOCK_INVOICES = {
  months_ahead: 6,
  invoices: [
    { month: 7, year: 2026, total: 500 },
    { month: 8, year: 2026, total: 0 },
  ],
}

function setupDefaultHandlers(
  overrides: {
    summary?: Record<string, unknown>
    user?: Record<string, unknown>
    invoices?: Record<string, unknown>
  } = {},
) {
  server.use(
    http.get('/api/users/1/summary', () =>
      HttpResponse.json(
        overrides.summary ?? {
          balance: 500,
          net_worth: 12000,
          total_income: 3000,
          total_spending: 2500,
          budget_status: 'WARNING',
        },
      ),
    ),
    http.get('/api/users/1', () => HttpResponse.json(overrides.user ?? MOCK_USER)),
    http.get('/api/users/1/monthly-invoices', () =>
      HttpResponse.json(overrides.invoices ?? MOCK_INVOICES),
    ),
  )
}

function renderWithUser(userId: number) {
  localStorage.setItem('expense-tracker.currentUserId', String(userId))
  return render(
    <UserProvider>
      <DashboardPage />
    </UserProvider>,
  )
}

describe('DashboardPage', () => {
  it('renders the four financial summary cards', async () => {
    setupDefaultHandlers()
    renderWithUser(1)

    expect(await screen.findByText('Próximo do teto')).toBeInTheDocument()
    expect(screen.getByText(/12\.000,00/)).toBeInTheDocument()
    expect(screen.getByText('Receitas')).toBeInTheDocument()
    expect(screen.getByText('Gastos')).toBeInTheDocument()
  })

  it('displays the current budget ceiling value and an edit button', async () => {
    setupDefaultHandlers()
    renderWithUser(1)

    expect(await screen.findByText(/Teto orçamentário:/)).toBeInTheDocument()
    expect(screen.getByText('Editar')).toBeInTheDocument()
  })

  it('shows "não definido" when the user has no budget ceiling', async () => {
    setupDefaultHandlers({ user: { ...MOCK_USER, budget_ceiling: null } })
    renderWithUser(1)

    expect(await screen.findByText(/não definido/)).toBeInTheDocument()
  })

  it('omits the status badge when budget_status is null', async () => {
    setupDefaultHandlers({
      summary: {
        balance: 500,
        net_worth: 12000,
        total_income: 3000,
        total_spending: 2500,
        budget_status: null,
      },
    })
    renderWithUser(1)

    await screen.findByText('Saldo do mês')
    expect(screen.queryByText('Dentro do teto')).not.toBeInTheDocument()
    expect(screen.queryByText('Próximo do teto')).not.toBeInTheDocument()
  })

  it('allows editing the budget ceiling', async () => {
    setupDefaultHandlers()
    server.use(
      http.patch('/api/users/1', async ({ request }) => {
        const body = (await request.json()) as Record<string, unknown>
        return HttpResponse.json({ ...MOCK_USER, budget_ceiling: body.budget_ceiling })
      }),
    )
    renderWithUser(1)

    await userEvent.click(await screen.findByText('Editar'))
    const input = screen.getByPlaceholderText('Novo teto')
    await userEvent.clear(input)
    await userEvent.type(input, '5000')
    await userEvent.click(screen.getByRole('button', { name: 'Salvar' }))

    await waitFor(() => expect(screen.queryByPlaceholderText('Novo teto')).not.toBeInTheDocument())
  })

  it('shows the monthly invoices section', async () => {
    setupDefaultHandlers()
    renderWithUser(1)

    expect(await screen.findByText('Faturas futuras (próximos 6 meses)')).toBeInTheDocument()
    expect(screen.getByText('Julho/2026')).toBeInTheDocument()
    expect(screen.getByText('Agosto/2026')).toBeInTheDocument()
  })

  it('shows an error message when the summary request fails', async () => {
    server.use(
      http.get('/api/users/1/summary', () =>
        HttpResponse.json({ detail: 'User not found' }, { status: 404 }),
      ),
      http.get('/api/users/1', () => HttpResponse.json(MOCK_USER)),
      http.get('/api/users/1/monthly-invoices', () => HttpResponse.json(MOCK_INVOICES)),
    )
    renderWithUser(1)

    expect(await screen.findByRole('alert')).toBeInTheDocument()
  })
})
