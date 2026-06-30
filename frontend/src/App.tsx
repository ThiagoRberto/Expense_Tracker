import type { ReactNode } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { UserProvider, useUser } from './context/UserContext'
import { SelectUserPage } from './pages/SelectUserPage'
import { DashboardPage } from './pages/DashboardPage'
import { IncomesPage } from './pages/IncomesPage'
import { ExpensesPage } from './pages/ExpensesPage'
import { BillsPage } from './pages/BillsPage'
import { InvestmentsPage } from './pages/InvestmentsPage'
import { CategoryBudgetsPage } from './pages/CategoryBudgetsPage'
import { InstallmentsPage } from './pages/InstallmentsPage'
import { MonthlyInvoicesPage } from './pages/MonthlyInvoicesPage'

function RequireUser({ children }: { children: ReactNode }) {
  const { userId } = useUser()
  if (userId === null) return <Navigate to="/login" replace />
  return <>{children}</>
}

function AppRoutes() {
  const { userId } = useUser()

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route
          path="/login"
          element={userId === null ? <SelectUserPage /> : <Navigate to="/" replace />}
        />
        <Route
          path="/"
          element={
            <RequireUser>
              <DashboardPage />
            </RequireUser>
          }
        />
        <Route
          path="/receitas"
          element={
            <RequireUser>
              <IncomesPage />
            </RequireUser>
          }
        />
        <Route
          path="/despesas"
          element={
            <RequireUser>
              <ExpensesPage />
            </RequireUser>
          }
        />
        <Route
          path="/contas"
          element={
            <RequireUser>
              <BillsPage />
            </RequireUser>
          }
        />
        <Route
          path="/investimentos"
          element={
            <RequireUser>
              <InvestmentsPage />
            </RequireUser>
          }
        />
        <Route
          path="/categorias"
          element={
            <RequireUser>
              <CategoryBudgetsPage />
            </RequireUser>
          }
        />
        <Route
          path="/parcelas"
          element={
            <RequireUser>
              <InstallmentsPage />
            </RequireUser>
          }
        />
        <Route
          path="/faturas"
          element={
            <RequireUser>
              <MonthlyInvoicesPage />
            </RequireUser>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}

function App() {
  return (
    <UserProvider>
      <AppRoutes />
    </UserProvider>
  )
}

export default App
