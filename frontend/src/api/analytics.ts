import { apiClient } from './client'
import type {
  CategoryAlertsResponse,
  FinancialSummary,
  InstallmentsResponse,
  MonthlyInvoicesResponse,
} from '../types/api'

export const analyticsApi = {
  summary: (userId: number) =>
    apiClient.get<FinancialSummary>(`/users/${userId}/summary`),
  categoryAlerts: (userId: number) =>
    apiClient.get<CategoryAlertsResponse>(`/users/${userId}/category-alerts`),
  installments: (userId: number) =>
    apiClient.get<InstallmentsResponse>(`/users/${userId}/installments`),
  monthlyInvoices: (userId: number, monthsAhead?: number) =>
    apiClient.get<MonthlyInvoicesResponse>(
      `/users/${userId}/monthly-invoices${monthsAhead ? `?months_ahead=${monthsAhead}` : ''}`,
    ),
}
