import { createContext, useContext, useMemo, useState, type ReactNode } from 'react'

const ID_KEY = 'expense-tracker.currentUserId'
const NAME_KEY = 'expense-tracker.currentUserName'

interface UserContextValue {
  userId: number | null
  userName: string | null
  setUser: (userId: number | null, userName: string | null) => void
}

const UserContext = createContext<UserContextValue | undefined>(undefined)

function readStoredUserId(): number | null {
  const raw = localStorage.getItem(ID_KEY)
  if (!raw) return null
  const parsed = Number(raw)
  return Number.isFinite(parsed) ? parsed : null
}

function readStoredUserName(): string | null {
  return localStorage.getItem(NAME_KEY)
}

export function UserProvider({ children }: { children: ReactNode }) {
  const [userId, setUserIdState] = useState<number | null>(readStoredUserId)
  const [userName, setUserNameState] = useState<string | null>(readStoredUserName)

  const setUser = (nextId: number | null, nextName: string | null) => {
    setUserIdState(nextId)
    setUserNameState(nextName)
    if (nextId === null) {
      localStorage.removeItem(ID_KEY)
      localStorage.removeItem(NAME_KEY)
    } else {
      localStorage.setItem(ID_KEY, String(nextId))
      if (nextName) localStorage.setItem(NAME_KEY, nextName)
    }
  }

  const value = useMemo(() => ({ userId, userName, setUser }), [userId, userName])

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>
}

export function useUser() {
  const context = useContext(UserContext)
  if (!context) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}
