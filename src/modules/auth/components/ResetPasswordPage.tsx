import { useState, useEffect } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import { authService } from '../services/authService'

const ResetPasswordPage = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')
  
  const [formData, setFormData] = useState({
    newPassword: '',
    confirmPassword: ''
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [tokenValid, setTokenValid] = useState<boolean | null>(null)

  useEffect(() => {
    if (!token) {
      setError('Token de reset inválido ou expirado')
      setTokenValid(false)
      return
    }
    
    // Validar token
    validateToken()
  }, [token])

  const validateToken = async () => {
    try {
      await authService.validateResetToken(token!)
      setTokenValid(true)
    } catch (err) {
      setError('Token de reset inválido ou expirado')
      setTokenValid(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    // Validações
    if (formData.newPassword.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres')
      setIsLoading(false)
      return
    }

    if (formData.newPassword !== formData.confirmPassword) {
      setError('As senhas não coincidem')
      setIsLoading(false)
      return
    }

    try {
      await authService.resetPassword(token!, formData.newPassword)
      setSuccess(true)
      
      // Redirecionar após 3 segundos
      setTimeout(() => {
        navigate('/login')
      }, 3000)
    } catch (err) {
      setError('Erro ao redefinir senha. Tente novamente.')
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

  // Token inválido
  if (tokenValid === false) {
    return (
      <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-red-500/20 border border-red-500/50 rounded-full flex items-center justify-center mb-6">
              <svg className="w-8 h-8 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </div>
            <h1 className="text-3xl font-bold mb-4">
              <span className="text-red-400">Token Inválido</span>
            </h1>
            <p className="text-gray-300 mb-6">
              O link de reset de senha é inválido ou expirou.
            </p>
          </div>

          <div className="glass-card p-8 shadow-neon-cyan/20 text-center">
            <p className="text-gray-400 mb-6">
              Solicite um novo link de recuperação de senha.
            </p>
            <Link
              to="/forgot-password"
              className="btn-neon inline-block mr-4"
            >
              Solicitar Novo Link
            </Link>
            <Link
              to="/login"
              className="text-neon-purple hover:text-neon-pink transition-colors duration-300"
            >
              Voltar ao Login
            </Link>
          </div>
        </div>
      </div>
    )
  }

  // Sucesso
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
              <span className="neon-text neon-glow">Senha Alterada!</span>
            </h1>
            <p className="text-gray-300 mb-6">
              Sua senha foi redefinida com sucesso. Redirecionando para o login...
            </p>
          </div>

          <div className="glass-card p-8 shadow-neon-cyan/20 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-neon-cyan mx-auto mb-4"></div>
            <p className="text-gray-400">
              Aguarde, você será redirecionado em instantes.
            </p>
          </div>
        </div>
      </div>
    )
  }

  // Loading token validation
  if (tokenValid === null) {
    return (
      <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-neon-cyan mx-auto mb-6"></div>
            <p className="text-gray-300">Validando token...</p>
          </div>
        </div>
      </div>
    )
  }

  // Form de reset
  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative z-10">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4">
            <span className="neon-text neon-glow">Nova</span>{' '}
            <span className="text-white">Senha</span>
          </h1>
          <p className="text-gray-300 text-lg">
            Digite sua nova senha
          </p>
          <div className="mt-4 h-1 w-20 mx-auto bg-gradient-to-r from-neon-cyan to-neon-purple rounded-full shadow-neon-cyan"></div>
        </div>

        {/* Form */}
        <div className="glass-card p-8 shadow-neon-cyan/20">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="newPassword" className="block text-sm font-medium text-neon-cyan mb-3">
                Nova Senha
              </label>
              <input
                id="newPassword"
                name="newPassword"
                type="password"
                required
                className="input-neon"
                placeholder="Digite sua nova senha"
                value={formData.newPassword}
                onChange={handleChange}
                minLength={6}
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-neon-cyan mb-3">
                Confirmar Senha
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                className="input-neon"
                placeholder="Confirme sua nova senha"
                value={formData.confirmPassword}
                onChange={handleChange}
                minLength={6}
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
                  Redefinindo...
                </div>
              ) : (
                'Redefinir Senha'
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

export default ResetPasswordPage