export function formatCurrency(value: number): string {
  return normalizeSpaces(
    value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }),
  )
}

function normalizeSpaces(value: string): string {
  return value.replace(NBSP_PATTERN, ' ')
}

const NBSP_PATTERN = new RegExp(String.fromCharCode(160), 'g')

const MONTH_NAMES = [
  'Janeiro',
  'Fevereiro',
  'Março',
  'Abril',
  'Maio',
  'Junho',
  'Julho',
  'Agosto',
  'Setembro',
  'Outubro',
  'Novembro',
  'Dezembro',
]

export function formatMonthYear(month: number, year: number): string {
  const name = MONTH_NAMES[month - 1] ?? String(month)
  return `${name}/${year}`
}

export function statusLabel(status: 'OK' | 'WARNING' | 'EXCEEDED'): string {
  switch (status) {
    case 'OK':
      return 'Dentro do teto'
    case 'WARNING':
      return 'Próximo do teto'
    case 'EXCEEDED':
      return 'Teto excedido'
  }
}
