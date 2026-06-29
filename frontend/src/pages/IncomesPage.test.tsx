import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { IncomesPage } from './IncomesPage'
import { UserProvider } from '../context/UserContext'

function renderWithUser(userId: number) {
  localStorage.setItem('expense-tracker.currentUserId', String(userId))
  return render(
    <UserProvider>
      <IncomesPage />
    </UserProvider>,
  )
}

describe('IncomesPage', () => {
  it('lists existing incomes', async () => {
    server.use(
      http.get('/api/users/1/incomes', () =>
        HttpResponse.json([{ id: 1, name: 'Salário', income_value: 5000, user_id: 1 }]),
      ),
    )

    renderWithUser(1)

    expect(await screen.findByText('Salário')).toBeInTheDocument()
    expect(screen.getByText(/5\.000,00/)).toBeInTheDocument()
  })

  it('shows an empty state with no incomes', async () => {
    server.use(http.get('/api/users/1/incomes', () => HttpResponse.json([])))

    renderWithUser(1)

    expect(await screen.findByText('Nenhuma receita cadastrada ainda.')).toBeInTheDocument()
  })

  it('submits the form and reloads the list', async () => {
    let listCallCount = 0
    server.use(
      http.get('/api/users/1/incomes', () => {
        listCallCount += 1
        return HttpResponse.json(
          listCallCount === 1
            ? []
            : [{ id: 2, name: 'Freela', income_value: 800, user_id: 1 }],
        )
      }),
      http.post('/api/users/1/incomes', async ({ request }) => {
        const body = await request.json()
        return HttpResponse.json({ id: 2, user_id: 1, ...(body as object) }, { status: 201 })
      }),
    )

    renderWithUser(1)
    await screen.findByText('Nenhuma receita cadastrada ainda.')

    await userEvent.type(screen.getByLabelText('Nome'), 'Freela')
    await userEvent.type(screen.getByLabelText('Valor'), '800')
    await userEvent.click(screen.getByRole('button', { name: 'Adicionar receita' }))

    await waitFor(() => expect(screen.getByText('Freela')).toBeInTheDocument())
  })

  it('shows a form error when creation fails', async () => {
    server.use(
      http.get('/api/users/1/incomes', () => HttpResponse.json([])),
      http.post('/api/users/1/incomes', () =>
        HttpResponse.json({ detail: 'valor inválido' }, { status: 422 }),
      ),
    )

    renderWithUser(1)
    await screen.findByText('Nenhuma receita cadastrada ainda.')

    await userEvent.type(screen.getByLabelText('Nome'), 'Freela')
    await userEvent.type(screen.getByLabelText('Valor'), '800')
    await userEvent.click(screen.getByRole('button', { name: 'Adicionar receita' }))

    expect(await screen.findByRole('alert')).toBeInTheDocument()
  })
})
