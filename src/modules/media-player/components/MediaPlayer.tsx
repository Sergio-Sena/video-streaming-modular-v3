import { useState, useEffect } from 'react'
import { eventBus } from '../../../core/engine/EventBus'
import { appConfig } from '../../../core/config/AppConfig'
import { apiClient } from '../../../shared/services/apiClient'
import { tokenManager } from '../../../shared/services/tokenManager'

interface MediaPlayerProps {
  file: any
  position?: { top: number; left: number } | null
  onClose: () => void
}

export const MediaPlayer = ({ file, position, onClose }: MediaPlayerProps) => {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [mediaUrl, setMediaUrl] = useState<string | null>(null)

  useEffect(() => {
    const loadMedia = async () => {
      try {
        setIsLoading(true)
        setError(null)

        // Emitir evento para carregar arquivo
        eventBus.emit('player:load-file', { file })

        // Usar URL assinada diretamente (mais simples)
        console.log('MediaPlayer - Solicitando URL assinada:', file.name)
        const response = await apiClient.get(`/files/${encodeURIComponent(file.name)}/download`)
        
        if (!response.ok) {
          throw new Error(`Erro ${response.status}: ${response.statusText}`)
        }
        
        const data = await response.json()
        console.log('MediaPlayer - URL assinada recebida')
        setMediaUrl(data.downloadUrl)

        setIsLoading(false)
      } catch (err) {
        setError('Erro ao carregar mídia')
        setIsLoading(false)
      }
    }

    loadMedia()
  }, [file])

  const renderMedia = () => {
    if (!mediaUrl) return null

    const fileType = appConfig.getFileType(file.name)

    switch (fileType) {
      case 'video':
        return (
          <video
            controls
            autoPlay
            className="object-contain"
            style={{ maxWidth: '80vw', maxHeight: '70vh' }}
            onPlay={() => {
              console.log('🎥 Video started playing:', file.name)
              eventBus.emit('player:playing', { file })
            }}
            onError={(e) => {
              console.error('🎥 Video error:', e)
              console.error('🎥 Video URL:', mediaUrl)
              setError(`Erro ao carregar vídeo: ${file.name}`)
            }}
            onLoadStart={() => console.log('🎥 Video load started:', mediaUrl)}
            onCanPlay={() => console.log('🎥 Video can play:', file.name)}
          >
            <source src={mediaUrl} type="video/mp4" />
            Seu navegador não suporta reprodução de vídeo.
          </video>
        )
      
      case 'audio':
        return (
          <div className="flex flex-col items-center justify-center h-64">
            <div className="text-6xl mb-4">🎵</div>
            <audio
              src={mediaUrl}
              controls
              autoPlay
              className="w-full max-w-md"
              onPlay={() => eventBus.emit('player:playing', { file })}
            />
          </div>
        )
      
      case 'image':
        return (
          <img
            src={mediaUrl}
            alt={file.name}
            className="object-contain"
            style={{ maxWidth: '80vw', maxHeight: '70vh' }}
          />
        )
      
      case 'document':
        return (
          <iframe
            src={mediaUrl}
            className="w-full h-96 border-0"
            title={file.name}
          />
        )
      
      default:
        return (
          <div className="flex flex-col items-center justify-center h-64">
            <div className="text-6xl mb-4">📄</div>
            <p className="text-gray-400">Tipo de arquivo não suportado para visualização</p>
          </div>
        )
    }
  }

  return (
    <div 
      className="fixed z-50"
      style={{
        top: position ? `${position.top}px` : '50%',
        left: '50%',
        transform: position ? 'translateX(-50%)' : 'translate(-50%, -50%)'
      }}
    >
      <div className="bg-gray-900 rounded-xl border border-cyan-500/20 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="text-2xl">
              {appConfig.isVideoFile(file.name) ? '🎥' :
               appConfig.isAudioFile(file.name) ? '🎵' :
               appConfig.isImageFile(file.name) ? '🖼️' : '📄'}
            </div>
            <div>
              <h3 className="text-white font-medium">{file.name}</h3>
              <p className="text-gray-400 text-sm">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-4 flex justify-center">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
              <span className="ml-3 text-gray-300">Carregando...</span>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-64">
              <p className="text-red-400">{error}</p>
            </div>
          ) : (
            renderMedia()
          )}
        </div>
      </div>
    </div>
  )
}