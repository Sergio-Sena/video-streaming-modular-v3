import { useState, useEffect } from 'react'
import { authService } from '../../auth/services/authService'
import { VideoList } from '../../player/components/VideoList'
import { FileUpload } from '../../files/components/FileUpload/FileUpload'
import { StorageStats } from '../../files/components/StorageStats'
import { VideoFile } from '../../player/services/playerService'

export const Dashboard = () => {
  const [user] = useState(() => authService.getUser())
  const [videos, setVideos] = useState<VideoFile[]>([])
  const [activeTab, setActiveTab] = useState<'videos' | 'upload' | 'storage'>('videos')
  const [isLoading, setIsLoading] = useState(false)

  const handleLogout = async () => {
    authService.logout()
    window.location.href = '/login'
  }

  const loadVideos = async () => {
    setIsLoading(true)
    try {
      // Simular carregamento de vídeos - integrar com API real
      const mockVideos: VideoFile[] = [
        {
          id: '1',
          name: 'video-exemplo.mp4',
          url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
          type: 'video/mp4',
          size: 15728640,
          lastModified: new Date().toISOString()
        }
      ]
      setVideos(mockVideos)
    } catch (error) {
      console.error('Erro ao carregar vídeos:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadVideos()
  }, [])

  const renderTabContent = () => {
    switch (activeTab) {
      case 'videos':
        return <VideoList videos={videos} onRefresh={loadVideos} />
      case 'upload':
        return <FileUpload onUploadComplete={loadVideos} />
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
              <div className="text-2xl font-bold">
                <span className="neon-text neon-glow">Drive</span>
                <span className="text-white ml-2">Online</span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-300">Olá, {user?.name}</span>
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
              { id: 'videos', label: '🎥 Vídeos', count: videos.length },
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