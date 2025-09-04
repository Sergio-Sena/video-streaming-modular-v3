import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { eventBus } from '../../../core/engine/EventBus'

interface LoginFormData {
  email: string
  password: string
}

const LoginForm = () => {
  const [formData, setFormData] = useState<LoginFormData>({
    email: 'senanetworker@gmail.com',
    password: 'sergiosena'
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    // Escutar eventos de autenticação
    eventBus.on('auth:login-success', handleLoginSuccess)
    eventBus.on('auth:login-error', handleLoginError)
    
    return () => {
      eventBus.off('auth:login-success', handleLoginSuccess)
      eventBus.off('auth:login-error', handleLoginError)
    }
  }, [])

  const handleLoginSuccess = (data: any) => {
    console.log('LoginForm - Login bem-sucedido via EventBus:', data.user?.name)
    setSuccess('Login realizado com sucesso!')
    setIsLoading(false)
    
    setTimeout(() => {
      window.location.href = '/dashboard'
    }, 300)
  }

  const handleLoginError = (data: { error: string }) => {
    console.error('LoginForm - Erro no login via EventBus:', data.error)
    setError(data.error)
    setIsLoading(false)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    setSuccess('')

    console.log('LoginForm - Emitindo evento de login:', { email: formData.email })
    eventBus.emit('auth:login-request', { 
      email: formData.email, 
      password: formData.password 
    })
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-neon-cyan mb-3">
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          required
          className="input-neon"
          placeholder="senanetworker@gmail.com"
          value={formData.email}
          onChange={handleChange}
        />
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-neon-cyan mb-3">
          Senha
        </label>
        <input
          id="password"
          name="password"
          type="password"
          required
          className="input-neon"
          placeholder="sergiosena"
          value={formData.password}
          onChange={handleChange}
        />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-lg text-sm">
          {success}
        </div>
      )}

      <button
        type="submit"
        disabled={isLoading}
        className="btn-neon w-full disabled:opacity-50 disabled:cursor-not-allowed animate-pulse-neon"
      >
        {isLoading ? (
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            Entrando...
          </div>
        ) : (
          'Entrar'
        )}
      </button>

      <div className="text-center">
        <Link 
          to="/forgot-password" 
          className="text-sm text-neon-purple hover:text-neon-pink transition-colors duration-300"
        >
          Esqueceu sua senha?
        </Link>
      </div>

      <div className="text-center text-xs text-gray-400 mt-4 p-3 bg-dark-800/50 rounded-lg border border-neon-cyan/20">
        <p className="text-neon-cyan">Desenvolvimento: senanetworker@gmail.com / sergiosena</p>
      </div>
    </form>
  )
}

export default LoginForm