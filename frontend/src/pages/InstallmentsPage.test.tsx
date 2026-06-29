import { render, screen } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { InstallmentsPage } from './InstallmentsPage'
import { UserProvider } from '../context/UserContext'

function renderWithUser(userId: number) {
  localStorage.setItem('expense-tracker.currentUserId', String(userId))
  return render(
    <UserProvider>
      <InstallmentsPage />
    </UserProvider>,
  )
}

describe('InstallmentsPage', () => {
  it('renders the installment entries for each parceled expense', async () => {
    server.use(
      http.get('/api/users/1/installments', () =>
        HttpResponse.json({
          projections: [
            {
              expense_id: 1,
              expense_name: 'Notebook',
              category: 'eletrônicos',
              total_value: 3000,
              installments: 3,
              entries: [
                { installment_number: 1, month: 1, year: 2026, amount: 1000 },
                { installment_number: 2, month: 2, year: 2026, amount: 1000 },
                { installment_number: 3, month: 3, year: 2026, amount: 1000 },
              ],
            },
          ],
        }),
      ),
    )

    renderWithUser(1)

    expect(await screen.findByText(/Notebook/)).toBeInTheDocument()
    expect(screen.getByText(/1\/3 — Janeiro\/2026/)).toBeInTheDocument()
    expect(screen.getByText(/3\/3 — Março\/2026/)).toBeInTheDocument()
  })

  it('shows an empty state when there are no parceled expenses', async () => {
    server.use(
      http.get('/api/users/1/installments', () =>
        HttpResponse.json({ projections: [] }),
      ),
    )

    renderWithUser(1)

    expect(
      await screen.findByText('Nenhuma despesa parcelada encontrada.'),
    ).toBeInTheDocument()
  })
})
