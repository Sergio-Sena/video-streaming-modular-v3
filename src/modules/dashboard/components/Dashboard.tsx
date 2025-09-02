import { useState } from 'react'
import { authService } from '../../auth/services/authService'
import { FileList } from '../../files/components/FileList'
import { StorageStats } from '../../files/components/StorageStats'
import { FileUpload } from '../../files/components/FileUpload/FileUpload'

export const Dashboard = () => {
  const [user] = useState(() => authService.getUser())
  const [refreshKey, setRefreshKey] = useState(0)
  const [showUpload, setShowUpload] = useState(false)

  const handleLogout = async () => {
    await authService.logout()
    window.location.href = '/login'
  }

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1)
  }

  const handleUploadComplete = () => {
    handleRefresh()
    setShowUpload(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-cyan-500/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                Drive Online
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-300">Olá, {user?.name}</span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                Sair
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Upload Section */}
          {showUpload ? (
            <FileUpload 
              onUploadComplete={handleUploadComplete}
              onClose={() => setShowUpload(false)}
            />
          ) : (
            <div className="text-center">
              <button
                onClick={() => {
                  console.log('Upload button clicked!')
                  setShowUpload(true)
                }}
                className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors font-medium text-lg cursor-pointer z-10 relative"
                style={{ pointerEvents: 'auto' }}
              >
                📤 Fazer Upload
              </button>
              <p className="text-gray-400 text-sm mt-2">Estado: {showUpload ? 'Aberto' : 'Fechado'}</p>
            </div>
          )}

          {/* Dashboard Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Storage Stats */}
            <div className="lg:col-span-1">
              <StorageStats key={refreshKey} />
            </div>

            {/* File List */}
            <div className="lg:col-span-2">
              <FileList key={refreshKey} onRefresh={handleRefresh} />
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}