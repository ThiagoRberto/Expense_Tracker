import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { BillsPage } from './BillsPage'
import { UserProvider } from '../context/UserContext'

function renderWithUser(userId: number) {
  localStorage.setItem('expense-tracker.currentUserId', String(userId))
  return render(
    <UserProvider>
      <BillsPage />
    </UserProvider>,
  )
}

describe('BillsPage', () => {
  it('lists existing bills', async () => {
    server.use(
      http.get('/api/users/1/bills', () =>
        HttpResponse.json([{ id: 1, name: 'Aluguel', bill_value: 1500, user_id: 1 }]),
      ),
    )

    renderWithUser(1)

    expect(await screen.findByText('Aluguel')).toBeInTheDocument()
    expect(screen.getByText(/1\.500,00/)).toBeInTheDocument()
  })

  it('submits a new bill and reloads the list', async () => {
    let listCallCount = 0
    server.use(
      http.get('/api/users/1/bills', () => {
        listCallCount += 1
        return HttpResponse.json(
          listCallCount === 1 ? [] : [{ id: 2, name: 'Água', bill_value: 90, user_id: 1 }],
        )
      }),
      http.post('/api/users/1/bills', async ({ request }) => {
        const body = await request.json()
        return HttpResponse.json({ id: 2, user_id: 1, ...(body as object) }, { status: 201 })
      }),
    )

    renderWithUser(1)
    await screen.findByText('Nenhuma conta fixa cadastrada ainda.')

    await userEvent.type(screen.getByLabelText('Nome'), 'Água')
    await userEvent.type(screen.getByLabelText('Valor'), '90')
    await userEvent.click(screen.getByRole('button', { name: 'Adicionar conta fixa' }))

    await waitFor(() => expect(screen.getByText('Água')).toBeInTheDocument())
  })
})
