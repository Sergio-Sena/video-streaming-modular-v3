import { useState, useEffect } from 'react'
import { authService } from '../services/authService'

export const AuthDebug = () => {
  const [debugInfo, setDebugInfo] = useState<any>({})

  useEffect(() => {
    const token = authService.getToken()
    const user = authService.getUser()
    const isAuth = authService.isAuthenticated()
    
    setDebugInfo({
      token: token ? `${token.substring(0, 20)}...` : 'null',
      user: user,
      isAuthenticated: isAuth,
      localStorage: {
        auth_token: localStorage.getItem('auth_token') ? 'exists' : 'null',
        auth_user: localStorage.getItem('auth_user') ? 'exists' : 'null'
      }
    })
  }, [])

  return (
    <div className="fixed top-4 right-4 bg-black/80 text-white p-4 rounded-lg text-xs max-w-sm z-50">
      <h3 className="text-yellow-400 font-bold mb-2">Auth Debug</h3>
      <pre>{JSON.stringify(debugInfo, null, 2)}</pre>
    </div>
  )
}