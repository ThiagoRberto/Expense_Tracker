import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { MonthlyInvoicesPage } from './MonthlyInvoicesPage'
import { UserProvider } from '../context/UserContext'

function renderWithUser(userId: number) {
  localStorage.setItem('expense-tracker.currentUserId', String(userId))
  return render(
    <UserProvider>
      <MonthlyInvoicesPage />
    </UserProvider>,
  )
}

describe('MonthlyInvoicesPage', () => {
  it('lists projected invoices for the default window', async () => {
    server.use(
      http.get('/api/users/1/monthly-invoices', ({ request }) => {
        const url = new URL(request.url)
        expect(url.searchParams.get('months_ahead')).toBe('6')
        return HttpResponse.json({
          months_ahead: 6,
          invoices: [
            { month: 1, year: 2026, total: 500 },
            { month: 2, year: 2026, total: 0 },
          ],
        })
      }),
    )

    renderWithUser(1)

    expect(await screen.findByText('Janeiro/2026')).toBeInTheDocument()
    expect(screen.getByText('Fevereiro/2026')).toBeInTheDocument()
  })

  it('refetches with a new months_ahead when the input changes', async () => {
    server.use(
      http.get('/api/users/1/monthly-invoices', ({ request }) => {
        const url = new URL(request.url)
        const monthsAhead = url.searchParams.get('months_ahead')
        return HttpResponse.json({
          months_ahead: Number(monthsAhead),
          invoices:
            monthsAhead === '6'
              ? [{ month: 1, year: 2026, total: 100 }]
              : [
                  { month: 1, year: 2026, total: 100 },
                  { month: 2, year: 2026, total: 200 },
                  { month: 3, year: 2026, total: 0 },
                ],
        })
      }),
    )

    renderWithUser(1)
    await screen.findByText('Janeiro/2026')

    const input = screen.getByLabelText('Meses à frente')
    await userEvent.clear(input)
    await userEvent.type(input, '3')

    await waitFor(() => expect(screen.getByText('Março/2026')).toBeInTheDocument())
  })

  it('shows an empty state when there are no invoices', async () => {
    server.use(
      http.get('/api/users/1/monthly-invoices', () =>
        HttpResponse.json({ months_ahead: 6, invoices: [] }),
      ),
    )

    renderWithUser(1)

    expect(await screen.findByText('Nenhuma fatura projetada.')).toBeInTheDocument()
  })
})
