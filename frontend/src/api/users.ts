import { apiClient } from './client'
import type { User, UserCreate } from '../types/api'

export const usersApi = {
  list: () => apiClient.get<User[]>('/users'),
  get: (userId: number) => apiClient.get<User>(`/users/${userId}`),
  create: (payload: UserCreate) => apiClient.post<User>('/users', payload),
  login: (name: string, password: string) =>
    apiClient.post<User>('/users/login', { name, password }),
  updateBudgetCeiling: (userId: number, budgetCeiling: number | null) =>
    apiClient.patch<User>(`/users/${userId}`, { budget_ceiling: budgetCeiling }),
}
