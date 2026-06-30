import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { formatCurrency } from '../lib/format'
import type { User } from '../types/api'

const SLICE_COLORS = [
  '#f97316', '#fb923c', '#fbbf24', '#34d399', '#60a5fa',
  '#a78bfa', '#f472b6', '#38bdf8', '#4ade80', '#facc15',
]

interface Props {
  user: User
}

export function SpendingDonut({ user }: Props) {
  const categoryTotals: Record<string, number> = {}

  for (const expense of user.expenses) {
    const monthly = expense.expense_value / Math.max(expense.installment, 1)
    const cat = expense.category || 'geral'
    categoryTotals[cat] = (categoryTotals[cat] ?? 0) + monthly
  }

  const billsTotal = user.bills.reduce((sum, b) => sum + b.bill_value, 0)

  const data: { name: string; value: number }[] = Object.entries(categoryTotals)
    .map(([name, value]) => ({ name, value: Math.round(value * 100) / 100 }))
    .filter((d) => d.value > 0)

  if (billsTotal > 0) {
    data.push({ name: 'Contas fixas', value: Math.round(billsTotal * 100) / 100 })
  }

  if (data.length === 0) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-sm text-zinc-500">Sem dados de gastos.</p>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={65}
          outerRadius={100}
          paddingAngle={2}
          dataKey="value"
        >
          {data.map((_, index) => (
            <Cell key={index} fill={SLICE_COLORS[index % SLICE_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value) => [formatCurrency(Number(value)), 'Mensal']}
          contentStyle={{ background: '#18181b', border: '1px solid #3f3f46', borderRadius: 8, color: '#f4f4f5' }}
        />
        <Legend
          iconType="circle"
          iconSize={8}
          formatter={(value) => <span style={{ color: '#a1a1aa', fontSize: 12 }}>{value}</span>}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}
