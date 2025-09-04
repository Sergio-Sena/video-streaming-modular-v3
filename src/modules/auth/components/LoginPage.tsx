import LoginForm from './LoginForm'

const LoginPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative z-10">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-5xl font-bold mb-4 flex items-center justify-center gap-3">
            <span className="text-4xl">🎬</span>
            <span className="neon-text neon-glow">Mediaflow</span>
          </h1>
          <p className="text-gray-300 text-lg">
            Acesse seus arquivos de qualquer lugar
          </p>
          <div className="mt-4 h-1 w-20 mx-auto bg-gradient-to-r from-neon-cyan to-neon-purple rounded-full shadow-neon-cyan"></div>
        </div>

        {/* Login Form */}
        <div className="glass-card p-8 shadow-neon-cyan/20">
          <LoginForm />
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-gray-400">
          <p>© 2025 Mediaflow. Sistema modular de mídia.</p>
        </div>
      </div>
    </div>
  )
}

export default LoginPage