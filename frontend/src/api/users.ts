import { apiClient } from './client'
import type { User, UserCreate } from '../types/api'

export const usersApi = {
  list: () => apiClient.get<User[]>('/users'),
  get: (userId: number) => apiClient.get<User>(`/users/${userId}`),
  create: (payload: UserCreate) => apiClient.post<User>('/users', payload),
}
