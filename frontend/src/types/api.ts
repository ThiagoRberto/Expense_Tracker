export type BudgetStatus = 'OK' | 'WARNING' | 'EXCEEDED'

export interface Bill {
  id: number
  name: string
  bill_value: number
  user_id: number
}
export interface BillCreate {
  name: string
  bill_value: number
}

export interface Expense {
  id: number
  name: string
  category: string
  expense_value: number
  installment: number
  start_month: number
  start_year: number
  user_id: number
}
export interface ExpenseCreate {
  name: string
  category?: string
  expense_value: number
  installment?: number
  start_month?: number
  start_year?: number
}

export interface Income {
  id: number
  name: string
  income_value: number
  user_id: number
}
export interface IncomeCreate {
  name: string
  income_value: number
}

export interface Investment {
  id: number
  name: string
  value_invested: number
  dividends: number
  user_id: number
}
export interface InvestmentCreate {
  name: string
  value_invested: number
  dividends?: number
}

export interface CategoryBudget {
  id: number
  category: string
  ceiling: number
  user_id: number
}
export interface CategoryBudgetCreate {
  category: string
  ceiling: number
}

export interface User {
  id: number
  name: string
  budget_ceiling: number | null
  bills: Bill[]
  expenses: Expense[]
  incomes: Income[]
  investments: Investment[]
}
export interface UserCreate {
  name: string
  password: string
  budget_ceiling?: number | null
  bills?: BillCreate[]
  expenses?: ExpenseCreate[]
  incomes?: IncomeCreate[]
  investments?: InvestmentCreate[]
}

export interface FinancialSummary {
  balance: number
  net_worth: number
  total_income: number
  total_spending: number
  budget_status: BudgetStatus | null
}

export interface CategoryAlertItem {
  category: string
  total: number
  ceiling: number
  status: BudgetStatus
}
export interface CategoryAlertsResponse {
  alerts: CategoryAlertItem[]
}

export interface InstallmentEntrySchema {
  installment_number: number
  month: number
  year: number
  amount: number
}
export interface ExpenseProjection {
  expense_id: number
  expense_name: string
  category: string
  total_value: number
  installments: number
  entries: InstallmentEntrySchema[]
}
export interface InstallmentsResponse {
  projections: ExpenseProjection[]
}

export interface MonthlyInvoiceItem {
  month: number
  year: number
  total: number
}
export interface MonthlyInvoicesResponse {
  months_ahead: number
  invoices: MonthlyInvoiceItem[]
}
