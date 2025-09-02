import { useState, useEffect } from 'react'
import { PlaylistPlayer } from './PlaylistPlayer'
import { playerService, VideoFile } from '../services/playerService'

interface VideoListProps {
  videos: VideoFile[]
  onRefresh?: () => void
}

export const VideoList = ({ videos, onRefresh }: VideoListProps) => {
  const [selectedVideoIndex, setSelectedVideoIndex] = useState<number | null>(null)
  const [filteredVideos, setFilteredVideos] = useState<VideoFile[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'size'>('name')

  useEffect(() => {
    let filtered = videos.filter(video => 
      playerService.isVideoSupported(video.name) &&
      video.name.toLowerCase().includes(searchTerm.toLowerCase())
    )

    // Sort videos
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name)
        case 'date':
          return new Date(b.lastModified).getTime() - new Date(a.lastModified).getTime()
        case 'size':
          return b.size - a.size
        default:
          return 0
      }
    })

    setFilteredVideos(filtered)
    playerService.setPlaylist(filtered)
  }, [videos, searchTerm, sortBy])

  const handlePlayVideo = (video: VideoFile) => {
    const index = filteredVideos.findIndex(v => v.id === video.id)
    setSelectedVideoIndex(index)
  }

  const handleClosePlayer = () => {
    setSelectedVideoIndex(null)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold neon-text neon-glow">
            🎥 Vídeos ({filteredVideos.length})
          </h2>
          <p className="text-gray-400 text-sm mt-1">
            Clique em um vídeo para reproduzir
          </p>
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            className="btn-neon text-sm px-4 py-2"
          >
            🔄 Atualizar
          </button>
        )}
      </div>

      {/* Search and Sort */}
      <div className="glass-card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <input
              type="text"
              placeholder="🔍 Buscar vídeos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-neon"
            />
          </div>

          {/* Sort */}
          <div className="sm:w-48">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'name' | 'date' | 'size')}
              className="input-neon"
            >
              <option value="name">📝 Nome</option>
              <option value="date">📅 Data</option>
              <option value="size">📊 Tamanho</option>
            </select>
          </div>
        </div>
      </div>

      {/* Video Grid */}
      {filteredVideos.length === 0 ? (
        <div className="glass-card p-8 text-center">
          <div className="text-6xl mb-4">🎬</div>
          <h3 className="text-xl font-semibold text-gray-300 mb-2">
            {searchTerm ? 'Nenhum vídeo encontrado' : 'Nenhum vídeo disponível'}
          </h3>
          <p className="text-gray-400">
            {searchTerm 
              ? 'Tente ajustar sua busca ou limpar o filtro'
              : 'Faça upload de vídeos para começar'
            }
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredVideos.map((video) => (
            <div
              key={video.id}
              className="glass-card p-4 hover:shadow-neon-cyan/20 transition-all duration-300 cursor-pointer group"
              onClick={() => handlePlayVideo(video)}
            >
              {/* Thumbnail Placeholder */}
              <div className="aspect-video bg-gradient-to-br from-dark-700 to-dark-800 rounded-lg mb-4 flex items-center justify-center relative overflow-hidden">
                <div className="text-4xl text-neon-cyan/50">🎬</div>
                
                {/* Play Overlay */}
                <div className="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div className="w-16 h-16 bg-neon-cyan/20 rounded-full flex items-center justify-center border-2 border-neon-cyan/50 animate-pulse-neon">
                    <svg className="w-8 h-8 text-neon-cyan ml-1" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </div>
                </div>
              </div>

              {/* Video Info */}
              <div className="space-y-2">
                <h3 className="font-semibold text-white truncate" title={video.name}>
                  {video.name}
                </h3>
                
                <div className="flex items-center justify-between text-sm text-gray-400">
                  <span>{playerService.formatFileSize(video.size)}</span>
                  <span>{formatDate(video.lastModified)}</span>
                </div>

                <div className="flex items-center space-x-2 text-xs text-neon-cyan">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/>
                  </svg>
                  <span>{playerService.getVideoType(video.name).split('/')[1].toUpperCase()}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Playlist Player Modal */}
      {selectedVideoIndex !== null && (
        <PlaylistPlayer
          videos={filteredVideos}
          initialIndex={selectedVideoIndex}
          onClose={handleClosePlayer}
        />
      )}
    </div>
  )
}