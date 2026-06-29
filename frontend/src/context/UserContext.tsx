import { createContext, useContext, useMemo, useState, type ReactNode } from 'react'

const STORAGE_KEY = 'expense-tracker.currentUserId'

interface UserContextValue {
  userId: number | null
  setUserId: (userId: number | null) => void
}

const UserContext = createContext<UserContextValue | undefined>(undefined)

function readStoredUserId(): number | null {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return null
  const parsed = Number(raw)
  return Number.isFinite(parsed) ? parsed : null
}

export function UserProvider({ children }: { children: ReactNode }) {
  const [userId, setUserIdState] = useState<number | null>(readStoredUserId)

  const setUserId = (next: number | null) => {
    setUserIdState(next)
    if (next === null) {
      localStorage.removeItem(STORAGE_KEY)
    } else {
      localStorage.setItem(STORAGE_KEY, String(next))
    }
  }

  const value = useMemo(() => ({ userId, setUserId }), [userId])

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>
}

export function useUser() {
  const context = useContext(UserContext)
  if (!context) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}
