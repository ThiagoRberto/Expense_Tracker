import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { ExpensesPage } from './ExpensesPage'
import { UserProvider } from '../context/UserContext'

function renderWithUser(userId: number) {
  localStorage.setItem('expense-tracker.currentUserId', String(userId))
  return render(
    <UserProvider>
      <ExpensesPage />
    </UserProvider>,
  )
}

describe('ExpensesPage', () => {
  it('lists existing expenses, showing the installment count when parceled', async () => {
    server.use(
      http.get('/api/users/1/expenses', () =>
        HttpResponse.json([
          {
            id: 1,
            name: 'Notebook',
            category: 'eletrônicos',
            expense_value: 3000,
            installment: 12,
            start_month: 1,
            start_year: 2026,
            user_id: 1,
          },
        ]),
      ),
    )

    renderWithUser(1)

    expect(await screen.findByText(/Notebook/)).toBeInTheDocument()
    expect(screen.getByText('(eletrônicos)')).toBeInTheDocument()
    expect(screen.getByText(/em 12x/)).toBeInTheDocument()
  })

  it('does not show an installment suffix for single-payment expenses', async () => {
    server.use(
      http.get('/api/users/1/expenses', () =>
        HttpResponse.json([
          {
            id: 2,
            name: 'Mercado',
            category: 'geral',
            expense_value: 250,
            installment: 1,
            start_month: 1,
            start_year: 2026,
            user_id: 1,
          },
        ]),
      ),
    )

    renderWithUser(1)

    await screen.findByText(/Mercado/)
    expect(screen.queryByText(/em 1x/)).not.toBeInTheDocument()
  })

  it('submits a new parceled expense with the chosen fields', async () => {
    let listCallCount = 0
    server.use(
      http.get('/api/users/1/expenses', () => {
        listCallCount += 1
        return HttpResponse.json(
          listCallCount === 1
            ? []
            : [
                {
                  id: 3,
                  name: 'Celular',
                  category: 'eletrônicos',
                  expense_value: 1200,
                  installment: 6,
                  start_month: 3,
                  start_year: 2026,
                  user_id: 1,
                },
              ],
        )
      }),
      http.post('/api/users/1/expenses', async ({ request }) => {
        const body = (await request.json()) as Record<string, unknown>
        expect(body).toMatchObject({
          name: 'Celular',
          category: 'eletrônicos',
          expense_value: 1200,
          installment: 6,
          start_month: 3,
          start_year: 2026,
        })
        return HttpResponse.json({ id: 3, user_id: 1, ...body }, { status: 201 })
      }),
    )

    renderWithUser(1)
    await screen.findByText('Nenhuma despesa cadastrada ainda.')

    await userEvent.type(screen.getByLabelText('Nome'), 'Celular')
    await userEvent.type(screen.getByLabelText('Categoria (opcional)'), 'eletrônicos')
    await userEvent.type(screen.getByLabelText('Valor total'), '1200')
    const installmentInput = screen.getByLabelText('Número de parcelas')
    await userEvent.clear(installmentInput)
    await userEvent.type(installmentInput, '6')
    await userEvent.selectOptions(screen.getByLabelText('Mês da 1ª parcela'), '3')
    await userEvent.selectOptions(screen.getByLabelText('Ano da 1ª parcela'), '2026')
    await userEvent.click(screen.getByRole('button', { name: 'Adicionar despesa' }))

    await waitFor(() => expect(screen.getByText(/Celular/)).toBeInTheDocument())
  })
})
