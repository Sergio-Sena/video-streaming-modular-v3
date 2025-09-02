import { useState } from 'react'
import { Link } from 'react-router-dom'
import { authService } from '../services/authService'

const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      await authService.forgotPassword(email)
      setSuccess(true)
    } catch (err) {
      setError('Erro ao enviar email de recuperação')
    } finally {
      setIsLoading(false)
    }
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-gradient-to-r from-neon-cyan to-neon-purple rounded-full flex items-center justify-center mb-6 shadow-neon-cyan animate-pulse-neon">
              <svg className="w-8 h-8 text-black" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
            <h1 className="text-3xl font-bold mb-4">
              <span className="neon-text neon-glow">Email Enviado!</span>
            </h1>
            <p className="text-gray-300 mb-6">
              Verifique sua caixa de entrada e siga as instruções para redefinir sua senha.
            </p>
          </div>

          <div className="glass-card p-8 shadow-neon-cyan/20 text-center">
            <p className="text-gray-400 mb-6">
              Não recebeu o email? Verifique sua pasta de spam ou tente novamente.
            </p>
            <Link
              to="/login"
              className="btn-neon inline-block"
            >
              Voltar ao Login
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative z-10">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4">
            <span className="neon-text neon-glow">Esqueci</span>{' '}
            <span className="text-white">a Senha</span>
          </h1>
          <p className="text-gray-300 text-lg">
            Digite seu email para receber instruções de recuperação
          </p>
          <div className="mt-4 h-1 w-20 mx-auto bg-gradient-to-r from-neon-cyan to-neon-purple rounded-full shadow-neon-cyan"></div>
        </div>

        {/* Form */}
        <div className="glass-card p-8 shadow-neon-cyan/20">
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
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            {error && (
              <div className="bg-red-900/50 border border-red-500/50 text-red-300 px-4 py-3 rounded-lg text-sm backdrop-blur-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="btn-neon w-full disabled:opacity-50 disabled:cursor-not-allowed animate-pulse-neon"
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-black mr-2"></div>
                  Enviando...
                </div>
              ) : (
                'Enviar Email de Recuperação'
              )}
            </button>

            <div className="text-center">
              <Link 
                to="/login" 
                className="text-sm text-neon-purple hover:text-neon-pink transition-colors duration-300"
              >
                ← Voltar ao Login
              </Link>
            </div>
          </form>
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-gray-400">
          <p>© 2025 Drive Online. Todos os direitos reservados.</p>
        </div>
      </div>
    </div>
  )
}

export default ForgotPasswordPage