import { render, screen } from '@testing-library/react'
import { StatusBadge } from './StatusBadge'

describe('StatusBadge', () => {
  it('renders the Portuguese label for OK', () => {
    render(<StatusBadge status="OK" />)
    expect(screen.getByText('Dentro do teto')).toBeInTheDocument()
  })

  it('renders the Portuguese label for WARNING', () => {
    render(<StatusBadge status="WARNING" />)
    expect(screen.getByText('Próximo do teto')).toBeInTheDocument()
  })

  it('renders the Portuguese label for EXCEEDED', () => {
    render(<StatusBadge status="EXCEEDED" />)
    expect(screen.getByText('Teto excedido')).toBeInTheDocument()
  })
})
