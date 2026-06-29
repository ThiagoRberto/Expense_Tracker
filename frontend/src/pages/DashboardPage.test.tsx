import { render, screen } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { DashboardPage } from './DashboardPage'
import { UserProvider } from '../context/UserContext'

function renderWithUser(userId: number) {
  localStorage.setItem('expense-tracker.currentUserId', String(userId))
  return render(
    <UserProvider>
      <DashboardPage />
    </UserProvider>,
  )
}

describe('DashboardPage', () => {
  it('renders the financial summary cards', async () => {
    server.use(
      http.get('/api/users/1/summary', () =>
        HttpResponse.json({
          balance: 500,
          net_worth: 12000,
          total_income: 3000,
          total_spending: 2500,
          budget_status: 'WARNING',
        }),
      ),
    )

    renderWithUser(1)

    expect(await screen.findByText('Próximo do teto')).toBeInTheDocument()
    expect(screen.getByText(/12\.000,00/)).toBeInTheDocument()
  })

  it('omits the budget status badge when the user has no ceiling set', async () => {
    server.use(
      http.get('/api/users/1/summary', () =>
        HttpResponse.json({
          balance: 500,
          net_worth: 12000,
          total_income: 3000,
          total_spending: 2500,
          budget_status: null,
        }),
      ),
    )

    renderWithUser(1)

    await screen.findByText(/3\.000,00/)
    expect(screen.queryByText('Teto orçamentário:')).not.toBeInTheDocument()
  })

  it('shows an error message when the request fails', async () => {
    server.use(
      http.get('/api/users/1/summary', () =>
        HttpResponse.json({ detail: 'User not found' }, { status: 404 }),
      ),
    )

    renderWithUser(1)

    expect(await screen.findByRole('alert')).toBeInTheDocument()
  })
})
