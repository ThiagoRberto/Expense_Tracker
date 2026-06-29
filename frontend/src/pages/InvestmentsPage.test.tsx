import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { InvestmentsPage } from './InvestmentsPage'
import { UserProvider } from '../context/UserContext'

function renderWithUser(userId: number) {
  localStorage.setItem('expense-tracker.currentUserId', String(userId))
  return render(
    <UserProvider>
      <InvestmentsPage />
    </UserProvider>,
  )
}

describe('InvestmentsPage', () => {
  it('lists existing investments with dividends', async () => {
    server.use(
      http.get('/api/users/1/investments', () =>
        HttpResponse.json([
          { id: 1, name: 'Tesouro', value_invested: 1000, dividends: 50, user_id: 1 },
        ]),
      ),
    )

    renderWithUser(1)

    expect(await screen.findByText('Tesouro')).toBeInTheDocument()
    expect(screen.getByText(/1\.000,00/)).toBeInTheDocument()
    expect(screen.getByText(/50,00/)).toBeInTheDocument()
  })

  it('submits a new investment without dividends and reloads the list', async () => {
    let listCallCount = 0
    server.use(
      http.get('/api/users/1/investments', () => {
        listCallCount += 1
        return HttpResponse.json(
          listCallCount === 1
            ? []
            : [{ id: 2, name: 'Ações', value_invested: 300, dividends: 0, user_id: 1 }],
        )
      }),
      http.post('/api/users/1/investments', async ({ request }) => {
        const body = (await request.json()) as Record<string, unknown>
        return HttpResponse.json(
          { id: 2, user_id: 1, dividends: 0, ...body },
          { status: 201 },
        )
      }),
    )

    renderWithUser(1)
    await screen.findByText('Nenhum investimento cadastrado ainda.')

    await userEvent.type(screen.getByLabelText('Nome'), 'Ações')
    await userEvent.type(screen.getByLabelText('Capital investido'), '300')
    await userEvent.click(screen.getByRole('button', { name: 'Adicionar investimento' }))

    await waitFor(() => expect(screen.getByText('Ações')).toBeInTheDocument())
  })
})
