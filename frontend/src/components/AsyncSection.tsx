import type { ReactNode } from 'react'

interface AsyncSectionProps {
  loading: boolean
  error: string | null
  children: ReactNode
}

export function AsyncSection({ loading, error, children }: AsyncSectionProps) {
  if (loading) {
    return <p className="text-sm text-zinc-400">Carregando...</p>
  }
  if (error) {
    return (
      <p className="text-sm text-red-400" role="alert">
        Erro: {error}
      </p>
    )
  }
  return <>{children}</>
}
