import { apiClient } from './client'
import type {
  Bill,
  BillCreate,
  CategoryBudget,
  CategoryBudgetCreate,
  Expense,
  ExpenseCreate,
  Income,
  IncomeCreate,
  Investment,
  InvestmentCreate,
} from '../types/api'

export const billsApi = {
  list: (userId: number) => apiClient.get<Bill[]>(`/users/${userId}/bills`),
  create: (userId: number, payload: BillCreate) =>
    apiClient.post<Bill>(`/users/${userId}/bills`, payload),
  delete: (userId: number, billId: number) =>
    apiClient.delete(`/users/${userId}/bills/${billId}`),
}

export const expensesApi = {
  list: (userId: number) => apiClient.get<Expense[]>(`/users/${userId}/expenses`),
  create: (userId: number, payload: ExpenseCreate) =>
    apiClient.post<Expense>(`/users/${userId}/expenses`, payload),
  delete: (userId: number, expenseId: number) =>
    apiClient.delete(`/users/${userId}/expenses/${expenseId}`),
}

export const incomesApi = {
  list: (userId: number) => apiClient.get<Income[]>(`/users/${userId}/incomes`),
  create: (userId: number, payload: IncomeCreate) =>
    apiClient.post<Income>(`/users/${userId}/incomes`, payload),
  delete: (userId: number, incomeId: number) =>
    apiClient.delete(`/users/${userId}/incomes/${incomeId}`),
}

export const investmentsApi = {
  list: (userId: number) => apiClient.get<Investment[]>(`/users/${userId}/investments`),
  create: (userId: number, payload: InvestmentCreate) =>
    apiClient.post<Investment>(`/users/${userId}/investments`, payload),
  delete: (userId: number, investmentId: number) =>
    apiClient.delete(`/users/${userId}/investments/${investmentId}`),
}

export const categoryBudgetsApi = {
  list: (userId: number) =>
    apiClient.get<CategoryBudget[]>(`/users/${userId}/category-budgets`),
  create: (userId: number, payload: CategoryBudgetCreate) =>
    apiClient.post<CategoryBudget>(`/users/${userId}/category-budgets`, payload),
  delete: (userId: number, budgetId: number) =>
    apiClient.delete(`/users/${userId}/category-budgets/${budgetId}`),
}
