import { formatCurrency, formatMonthYear, statusLabel } from './format'

describe('formatCurrency', () => {
  it('formats positive values as BRL', () => {
    expect(formatCurrency(1234.5)).toBe('R$ 1.234,50')
  })

  it('formats zero', () => {
    expect(formatCurrency(0)).toBe('R$ 0,00')
  })

  it('formats negative values', () => {
    expect(formatCurrency(-50)).toBe('-R$ 50,00')
  })
})

describe('formatMonthYear', () => {
  it('maps month number to Portuguese name', () => {
    expect(formatMonthYear(1, 2026)).toBe('Janeiro/2026')
    expect(formatMonthYear(12, 2025)).toBe('Dezembro/2025')
  })

  it('falls back to the raw number for out-of-range months', () => {
    expect(formatMonthYear(13, 2026)).toBe('13/2026')
  })
})

describe('statusLabel', () => {
  it('translates each budget status', () => {
    expect(statusLabel('OK')).toBe('Dentro do teto')
    expect(statusLabel('WARNING')).toBe('Próximo do teto')
    expect(statusLabel('EXCEEDED')).toBe('Teto excedido')
  })
})
