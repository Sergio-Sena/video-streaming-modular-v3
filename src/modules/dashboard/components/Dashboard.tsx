import { useState, useEffect } from 'react'
import { authService } from '../../auth/services/authService'
import { FileUpload } from '../../files/components/FileUpload/FileUpload'
import { StorageStats } from '../../files/components/StorageStats'
import { FileList } from '../../files/components/FileList'
import { eventBus } from '../../../core/engine/EventBus'

export const Dashboard = () => {
  const [user, setUser] = useState(() => authService.getUser())
  const [activeTab, setActiveTab] = useState<'files' | 'upload' | 'storage'>('files')
  const [isLoading, setIsLoading] = useState(false)
  const [dashboardState, setDashboardState] = useState<any>(null)
  const [notifications, setNotifications] = useState<any[]>([])

  const handleLogout = async () => {
    console.log('Dashboard - Emitindo evento de logout via EventBus')
    eventBus.emit('auth:logout-request')
  }



  useEffect(() => {
    // Escutar eventos do DashboardModule
    eventBus.on('dashboard:state-updated', handleDashboardStateUpdate)
    eventBus.on('dashboard:notification', handleNotification)
    eventBus.on('auth:logout-success', handleLogoutSuccess)
    
    return () => {
      eventBus.off('dashboard:state-updated', handleDashboardStateUpdate)
      eventBus.off('dashboard:notification', handleNotification)
      eventBus.off('auth:logout-success', handleLogoutSuccess)
    }
  }, [])

  const handleDashboardStateUpdate = (state: any) => {
    console.log('Dashboard - State updated via EventBus:', state.stats)
    setDashboardState(state)
    if (state.user) {
      setUser(state.user)
    }
  }

  const handleNotification = (notification: any) => {
    console.log('Dashboard - Notification via EventBus:', notification.type, notification.message)
    const notificationWithId = { ...notification, id: Date.now() }
    setNotifications(prev => [...prev, notificationWithId])
    
    // Auto-remove notification after 3 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== notificationWithId.id))
    }, 3000)
  }

  const handleLogoutSuccess = () => {
    console.log('Dashboard - Logout success, redirecting...')
    window.location.href = '/login'
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'files':
        return <FileList />
      case 'upload':
        return <FileUpload />
      case 'storage':
        return <StorageStats />
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-700 relative overflow-hidden">
      {/* Neon background effects */}
      <div className="absolute inset-0 bg-gradient-to-r from-neon-cyan/5 via-transparent to-neon-purple/5"></div>
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-neon-cyan/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-neon-purple/10 rounded-full blur-3xl animate-pulse"></div>
      
      {/* Header */}
      <header className="relative z-10 bg-black/20 backdrop-blur-sm border-b border-neon-cyan/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="text-2xl font-bold flex items-center gap-2">
                <span className="text-xl">🎬</span>
                <span className="neon-text neon-glow">Mediaflow</span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-300">Olá, {user?.name}</span>
              {dashboardState?.stats && (
                <div className="text-xs text-gray-400">
                  {dashboardState.stats.totalFiles} arquivos • 
                  {dashboardState.stats.activeUploads} uploads •
                  {dashboardState.stats.isPlaying ? ' ▶️ Playing' : ''}
                </div>
              )}
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600/80 hover:bg-red-600 text-white rounded-lg transition-all duration-300 backdrop-blur-sm border border-red-500/30"
              >
                Sair
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="relative z-10 bg-black/10 backdrop-blur-sm border-b border-neon-cyan/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'files', label: '📁 Arquivos' },
              { id: 'upload', label: '📤 Upload' },
              { id: 'storage', label: '💾 Armazenamento' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-2 border-b-2 font-medium text-sm transition-all duration-300 ${
                  activeTab === tab.id
                    ? 'border-neon-cyan text-neon-cyan'
                    : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
                }`}
              >
                {tab.label}
                {tab.count !== undefined && (
                  <span className="ml-2 bg-neon-cyan/20 text-neon-cyan px-2 py-1 rounded-full text-xs">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Notifications */}
      {notifications.length > 0 && (
        <div className="fixed top-4 right-4 z-50 space-y-2">
          {notifications.map((notification) => (
            <div
              key={notification.id}
              className={`px-4 py-3 rounded-lg backdrop-blur-sm border ${
                notification.type === 'success' 
                  ? 'bg-green-600/80 border-green-500/30 text-white'
                  : notification.type === 'error'
                  ? 'bg-red-600/80 border-red-500/30 text-white'
                  : 'bg-blue-600/80 border-blue-500/30 text-white'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-sm">{notification.message}</span>
                <button
                  onClick={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))}
                  className="ml-2 text-white/70 hover:text-white"
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neon-cyan"></div>
          </div>
        ) : (
          renderTabContent()
        )}
      </main>
    </div>
  )
}