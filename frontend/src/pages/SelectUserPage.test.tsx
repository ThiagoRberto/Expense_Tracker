import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { SelectUserPage } from './SelectUserPage'
import { UserProvider, useUser } from '../context/UserContext'

function CurrentUserProbe() {
  const { userId } = useUser()
  return <p data-testid="current-user">{userId ?? 'none'}</p>
}

function renderPage() {
  return render(
    <UserProvider>
      <SelectUserPage />
      <CurrentUserProbe />
    </UserProvider>,
  )
}

describe('SelectUserPage', () => {
  it('lists existing users and lets the user pick one', async () => {
    server.use(
      http.get('/api/users', () =>
        HttpResponse.json([{ id: 7, name: 'Ana', budget_ceiling: null, bills: [], expenses: [], incomes: [], investments: [] }]),
      ),
    )

    renderPage()

    expect(await screen.findByText('Ana')).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(screen.getByTestId('current-user')).toHaveTextContent('7')
  })

  it('shows an empty state when there are no users', async () => {
    server.use(http.get('/api/users', () => HttpResponse.json([])))

    renderPage()

    expect(await screen.findByText('Nenhum usuário cadastrado ainda.')).toBeInTheDocument()
  })

  it('creates a new user and logs in as them', async () => {
    server.use(
      http.get('/api/users', () => HttpResponse.json([])),
      http.post('/api/users', async ({ request }) => {
        const body = (await request.json()) as Record<string, unknown>
        return HttpResponse.json(
          { id: 42, ...body, bills: [], expenses: [], incomes: [], investments: [] },
          { status: 201 },
        )
      }),
    )

    renderPage()
    await screen.findByText('Nenhum usuário cadastrado ainda.')

    await userEvent.type(screen.getByLabelText('Nome'), 'Bia')
    await userEvent.type(screen.getByLabelText('Senha'), 'segredo123')
    await userEvent.click(screen.getByRole('button', { name: 'Criar usuário' }))

    await waitFor(() =>
      expect(screen.getByTestId('current-user')).toHaveTextContent('42'),
    )
  })

  it('shows a form error when user creation fails', async () => {
    server.use(
      http.get('/api/users', () => HttpResponse.json([])),
      http.post('/api/users', () =>
        HttpResponse.json({ detail: 'nome já existe' }, { status: 409 }),
      ),
    )

    renderPage()
    await screen.findByText('Nenhum usuário cadastrado ainda.')

    await userEvent.type(screen.getByLabelText('Nome'), 'Bia')
    await userEvent.type(screen.getByLabelText('Senha'), 'segredo123')
    await userEvent.click(screen.getByRole('button', { name: 'Criar usuário' }))

    expect(await screen.findByRole('alert')).toBeInTheDocument()
    expect(screen.getByTestId('current-user')).toHaveTextContent('none')
  })
})
