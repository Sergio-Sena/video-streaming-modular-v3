import { useState } from 'react'
import { VideoPlayer } from './VideoPlayer'

interface MediaViewerProps {
  file: {
    id: string
    name: string
    url: string
    type: string
    size: number
  }
  onClose: () => void
}

export const MediaViewer = ({ file, onClose }: MediaViewerProps) => {
  const [imageError, setImageError] = useState(false)

  const getFileType = () => {
    const ext = file.name.toLowerCase().split('.').pop()
    
    if (['mp4', 'webm', 'ogg', 'avi', 'mov', 'mkv'].includes(ext || '')) return 'video'
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(ext || '')) return 'image'
    if (['pdf'].includes(ext || '')) return 'pdf'
    if (['txt', 'md'].includes(ext || '')) return 'text'
    return 'document'
  }

  const fileType = getFileType()

  const renderContent = () => {
    switch (fileType) {
      case 'video':
        return <VideoPlayer src={file.url} title={file.name} onClose={onClose} />
      
      case 'image':
        return (
          <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-sm flex items-center justify-center">
            <div className="relative max-w-[90vw] max-h-[90vh]">
              <button
                onClick={onClose}
                className="absolute -top-12 right-0 w-10 h-10 bg-black/50 hover:bg-black/70 rounded-full flex items-center justify-center text-white transition-all duration-300"
              >
                ✕
              </button>
              
              {!imageError ? (
                <img
                  src={file.url}
                  alt={file.name}
                  className="max-w-full max-h-full object-contain rounded-lg"
                  onError={() => setImageError(true)}
                />
              ) : (
                <div className="glass-card p-8 text-center">
                  <div className="text-6xl mb-4">🖼️</div>
                  <p className="text-white">Erro ao carregar imagem</p>
                </div>
              )}
              
              <div className="absolute bottom-4 left-4 bg-black/50 backdrop-blur-sm px-4 py-2 rounded-lg">
                <h3 className="text-white font-medium">{file.name}</h3>
              </div>
            </div>
          </div>
        )
      
      case 'pdf':
        return (
          <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-sm flex items-center justify-center">
            <div className="w-full h-full max-w-6xl max-h-[90vh] bg-white rounded-lg overflow-hidden relative">
              <button
                onClick={onClose}
                className="absolute top-4 right-4 z-10 w-10 h-10 bg-black/50 hover:bg-black/70 rounded-full flex items-center justify-center text-white"
              >
                ✕
              </button>
              <iframe
                src={file.url}
                className="w-full h-full"
                title={file.name}
              />
            </div>
          </div>
        )
      
      default:
        return (
          <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-sm flex items-center justify-center">
            <div className="glass-card p-8 max-w-md text-center">
              <button
                onClick={onClose}
                className="absolute top-4 right-4 w-8 h-8 bg-neon-cyan/20 rounded-full flex items-center justify-center text-neon-cyan"
              >
                ✕
              </button>
              
              <div className="text-6xl mb-4">📄</div>
              <h3 className="text-xl font-semibold text-white mb-2">{file.name}</h3>
              <p className="text-gray-400 mb-6">Arquivo não suportado para visualização</p>
              
              <a
                href={file.url}
                download={file.name}
                className="btn-neon inline-block"
              >
                📥 Download
              </a>
            </div>
          </div>
        )
    }
  }

  return renderContent()
}