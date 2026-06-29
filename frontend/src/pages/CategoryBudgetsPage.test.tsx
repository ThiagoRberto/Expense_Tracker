import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { CategoryBudgetsPage } from './CategoryBudgetsPage'
import { UserProvider } from '../context/UserContext'

function renderWithUser(userId: number) {
  localStorage.setItem('expense-tracker.currentUserId', String(userId))
  return render(
    <UserProvider>
      <CategoryBudgetsPage />
    </UserProvider>,
  )
}

describe('CategoryBudgetsPage', () => {
  it('shows alerts with each category status', async () => {
    server.use(
      http.get('/api/users/1/category-alerts', () =>
        HttpResponse.json({
          alerts: [
            { category: 'alimentação', total: 850, ceiling: 800, status: 'EXCEEDED' },
            { category: 'lazer', total: 50, ceiling: 200, status: 'OK' },
          ],
        }),
      ),
    )

    renderWithUser(1)

    expect(await screen.findByText('alimentação')).toBeInTheDocument()
    expect(screen.getByText('Teto excedido')).toBeInTheDocument()
    expect(screen.getByText('lazer')).toBeInTheDocument()
    expect(screen.getByText('Dentro do teto')).toBeInTheDocument()
  })

  it('shows an empty state with no budgets defined', async () => {
    server.use(
      http.get('/api/users/1/category-alerts', () => HttpResponse.json({ alerts: [] })),
    )

    renderWithUser(1)

    expect(
      await screen.findByText('Nenhum teto orçamentário definido ainda.'),
    ).toBeInTheDocument()
  })

  it('creates a new category budget and reloads alerts', async () => {
    let callCount = 0
    server.use(
      http.get('/api/users/1/category-alerts', () => {
        callCount += 1
        return HttpResponse.json({
          alerts:
            callCount === 1
              ? []
              : [{ category: 'transporte', total: 0, ceiling: 300, status: 'OK' }],
        })
      }),
      http.post('/api/users/1/category-budgets', async ({ request }) => {
        const body = await request.json()
        return HttpResponse.json({ id: 1, user_id: 1, ...(body as object) }, { status: 201 })
      }),
    )

    renderWithUser(1)
    await screen.findByText('Nenhum teto orçamentário definido ainda.')

    await userEvent.type(screen.getByLabelText('Categoria'), 'transporte')
    await userEvent.type(screen.getByLabelText('Teto'), '300')
    await userEvent.click(screen.getByRole('button', { name: 'Definir teto' }))

    await waitFor(() => expect(screen.getByText('transporte')).toBeInTheDocument())
  })

  it('shows a form error on a 409 duplicate category', async () => {
    server.use(
      http.get('/api/users/1/category-alerts', () => HttpResponse.json({ alerts: [] })),
      http.post('/api/users/1/category-budgets', () =>
        HttpResponse.json({ detail: 'categoria já possui teto' }, { status: 409 }),
      ),
    )

    renderWithUser(1)
    await screen.findByText('Nenhum teto orçamentário definido ainda.')

    await userEvent.type(screen.getByLabelText('Categoria'), 'transporte')
    await userEvent.type(screen.getByLabelText('Teto'), '300')
    await userEvent.click(screen.getByRole('button', { name: 'Definir teto' }))

    expect(await screen.findByRole('alert')).toBeInTheDocument()
  })
})
