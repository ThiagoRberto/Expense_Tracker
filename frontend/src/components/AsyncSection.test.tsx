import { render, screen } from '@testing-library/react'
import { AsyncSection } from './AsyncSection'

describe('AsyncSection', () => {
  it('shows a loading message while loading', () => {
    render(
      <AsyncSection loading error={null}>
        <p>conteúdo</p>
      </AsyncSection>,
    )
    expect(screen.getByText('Carregando...')).toBeInTheDocument()
    expect(screen.queryByText('conteúdo')).not.toBeInTheDocument()
  })

  it('shows the error message when present', () => {
    render(
      <AsyncSection loading={false} error="falha na rede">
        <p>conteúdo</p>
      </AsyncSection>,
    )
    expect(screen.getByRole('alert')).toHaveTextContent('falha na rede')
    expect(screen.queryByText('conteúdo')).not.toBeInTheDocument()
  })

  it('renders children when loaded without error', () => {
    render(
      <AsyncSection loading={false} error={null}>
        <p>conteúdo</p>
      </AsyncSection>,
    )
    expect(screen.getByText('conteúdo')).toBeInTheDocument()
  })
})
