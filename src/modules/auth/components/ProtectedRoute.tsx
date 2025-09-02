import { ReactNode, useEffect, useState } from 'react'
import { authService } from '../services/authService'

interface ProtectedRouteProps {
  children: ReactNode
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)

  useEffect(() => {
    const checkAuth = () => {
      if (authService.isAuthenticated()) {
        setIsAuthenticated(true)
      } else {
        setIsAuthenticated(false)
        window.location.href = '/login'
      }
    }
    checkAuth()
  }, [])

  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-dark-900 via-dark-800 to-dark-700">
        <div className="text-white">Verificando autenticação...</div>
      </div>
    )
  }

  return isAuthenticated ? <>{children}</> : null
}