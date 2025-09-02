import { useState } from 'react'
import { Link } from 'react-router-dom'
import { authService } from '../services/authService'

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    setSuccess('')

    try {
      // Tentar login real com API
      const result = await authService.login(formData.email, formData.password)
      setSuccess('Login realizado com sucesso!')
      console.log('Login successful:', result)
      
      // Redirecionar para dashboard
      setTimeout(() => {
        window.location.href = '/dashboard'
      }, 1000)
    } catch (err) {
      console.error('Login error:', err)
      setError('Email ou senha inválidos')
    } finally {
      setIsLoading(false)
    }
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