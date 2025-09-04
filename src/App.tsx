import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import LoginPage from './modules/auth/components/LoginPage'
import ForgotPasswordPage from './modules/auth/components/ForgotPasswordPage'
import ResetPasswordPage from './modules/auth/components/ResetPasswordPage'
import { ProtectedRoute } from './modules/auth/components/ProtectedRoute'
import { Dashboard } from './modules/dashboard/components/Dashboard'
import { moduleRegistry } from './core/engine/ModuleRegistry'
import { eventBus } from './core/engine/EventBus'
import { appConfig } from './core/config/AppConfig'
import { AuthModule } from './modules/auth/AuthModule'
import { StorageModule } from './modules/storage/StorageModule'
import { MediaPlayerModule } from './modules/media-player/MediaPlayerModule'
import { UploadModule } from './modules/upload/UploadModule'
import { DashboardModule } from './modules/dashboard/DashboardModule'

const queryClient = new QueryClient()

// ⚙️ INICIALIZAR Core System
appConfig.init()

// 🔐 REGISTRAR AuthModule
moduleRegistry.register({
  name: 'auth',
  loader: async () => new AuthModule()
})

// 📁 REGISTRAR StorageModule
moduleRegistry.register({
  name: 'storage',
  loader: async () => new StorageModule()
})

// 🎥 REGISTRAR MediaPlayerModule
moduleRegistry.register({
  name: 'media-player',
  loader: async () => new MediaPlayerModule()
})

// 📤 REGISTRAR UploadModule
moduleRegistry.register({
  name: 'upload',
  loader: async () => new UploadModule()
})

// 🎛️ REGISTRAR DashboardModule
moduleRegistry.register({
  name: 'dashboard',
  loader: async () => new DashboardModule()
})

// 🚀 INICIALIZAR TODOS OS MÓDULOS
Promise.all([
  moduleRegistry.init('auth'),
  moduleRegistry.init('storage'),
  moduleRegistry.init('media-player'),
  moduleRegistry.init('upload'),
  moduleRegistry.init('dashboard')
]).then(() => {
  console.log('📊 Module Status:', moduleRegistry.getStatus())
  
  // 📞 ESCUTAR eventos de autenticação
  eventBus.on('auth:status-changed', (data) => {
    console.log('🔐 Auth status changed:', data)
  })
  
  eventBus.on('auth:login-success', (data) => {
    console.log('✅ Login successful:', data.user?.name)
  })
  
  eventBus.on('auth:logout-success', () => {
    console.log('👋 Logout successful')
  })
  
  // 📞 ESCUTAR eventos de storage
  eventBus.on('storage:files-loaded', (data) => {
    console.log('📁 Files loaded:', data.total, 'files')
    console.log('📊 Types:', `${data.videos} videos, ${data.images} images, ${data.audios} audios, ${data.documents} docs`)
  })
  
  eventBus.on('storage:file-deleted', (data) => {
    console.log('🗑️ File deleted:', data.fileName)
  })
  
  // 📞 ESCUTAR eventos de media player
  eventBus.on('player:file-loaded', (data) => {
    console.log('🎥 File loaded in player:', data.file.name, 'Engine:', data.engine)
  })
  
  eventBus.on('player:playing', (data) => {
    console.log('▶️ Playing:', data.file.name)
  })
  
  // 📊 ESCUTAR eventos do dashboard
  eventBus.on('dashboard:state-updated', (data) => {
    console.log('🎛️ Dashboard state:', `${data.stats.totalFiles} files, ${data.stats.activeUploads} uploads, playing: ${data.stats.isPlaying}`)
  })
  
  eventBus.on('dashboard:notification', (data) => {
    console.log(`🔔 ${data.type.toUpperCase()}:`, data.message)
  })
  
  // Teste automático removido
})

function App() {
  console.log('🎬 Mediaflow App started with ALL MODULES (8/8)')
  return (
    <QueryClientProvider client={queryClient}>
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-700 relative overflow-hidden">
          {/* Neon background effects */}
          <div className="absolute inset-0 bg-gradient-to-r from-neon-cyan/5 via-transparent to-neon-purple/5"></div>
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-neon-cyan/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-neon-purple/10 rounded-full blur-3xl animate-pulse"></div>
          <Routes>
            <Route path="/" element={<LoginPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
          </Routes>
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App