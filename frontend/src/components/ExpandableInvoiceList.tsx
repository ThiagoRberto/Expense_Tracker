import { useState } from 'react'
import { formatCurrency, formatMonthYear } from '../lib/format'
import type { MonthlyInvoiceItem, InstallmentsResponse } from '../types/api'

interface Props {
  invoices: MonthlyInvoiceItem[]
  installments: InstallmentsResponse | null
}

export function ExpandableInvoiceList({ invoices, installments }: Props) {
  const [expandedKey, setExpandedKey] = useState<string | null>(null)

  function toggleExpand(key: string) {
    setExpandedKey((prev) => (prev === key ? null : key))
  }

  function getBreakdown(month: number, year: number) {
    if (!installments) return []
    return installments.projections.flatMap((projection) =>
      projection.entries
        .filter((e) => e.month === month && e.year === year)
        .map((e) => ({
          name: projection.expense_name,
          category: projection.category,
          amount: e.amount,
        })),
    )
  }

  return (
    <ul className="divide-y divide-zinc-800 rounded-md border border-zinc-700 bg-zinc-900">
      {invoices.map((invoice) => {
        const key = `${invoice.month}-${invoice.year}`
        const isExpanded = expandedKey === key
        const breakdown = getBreakdown(invoice.month, invoice.year)

        return (
          <li key={key}>
            <button
              type="button"
              onClick={() => breakdown.length > 0 && toggleExpand(key)}
              className={`flex w-full items-center justify-between px-4 py-2 text-left transition-colors ${
                breakdown.length > 0 ? 'hover:bg-zinc-800 cursor-pointer' : 'cursor-default'
              }`}
            >
              <div className="flex items-center gap-2">
                {breakdown.length > 0 && (
                  <svg
                    className="text-orange-500 shrink-0"
                    style={{ width: 10, height: 10, transition: 'transform 0.15s', transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)' }}
                    viewBox="0 0 10 10"
                    fill="currentColor"
                  >
                    <polygon points="2,1 9,5 2,9" />
                  </svg>
                )}
                <span className="text-sm text-zinc-200">
                  {formatMonthYear(invoice.month, invoice.year)}
                </span>
              </div>
              <span className={`font-medium ${invoice.total > 0 ? 'text-orange-400' : 'text-zinc-500'}`}>
                {formatCurrency(invoice.total)}
              </span>
            </button>
            {isExpanded && breakdown.length > 0 && (
              <ul className="border-t border-zinc-800 bg-zinc-950 px-4 py-2 space-y-1">
                {breakdown.map((item, i) => (
                  <li key={i} className="flex items-center justify-between text-sm">
                    <span className="text-zinc-400">
                      {item.name}{' '}
                      <span className="text-xs text-zinc-600">({item.category})</span>
                    </span>
                    <span className="text-zinc-300">{formatCurrency(item.amount)}</span>
                  </li>
                ))}
              </ul>
            )}
          </li>
        )
      })}
    </ul>
  )
}
