import { useState, useRef, useEffect } from 'react'
import { VideoPlayer } from './VideoPlayer'
import { playerService, VideoFile, PlaylistItem } from '../services/playerService'

interface PlaylistPlayerProps {
  videos: VideoFile[]
  initialIndex?: number
  onClose: () => void
}

export const PlaylistPlayer = ({ videos, initialIndex = 0, onClose }: PlaylistPlayerProps) => {
  const [currentIndex, setCurrentIndex] = useState(initialIndex)
  const [showPlaylist, setShowPlaylist] = useState(false)
  const [autoPlay, setAutoPlay] = useState(true)
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    playerService.setPlaylist(videos)
    playerService.setCurrentIndex(initialIndex)
  }, [videos, initialIndex])

  const currentVideo = videos[currentIndex]

  const handleVideoEnd = () => {
    if (autoPlay && currentIndex < videos.length - 1) {
      playNext()
    }
  }

  const playNext = () => {
    if (currentIndex < videos.length - 1) {
      setCurrentIndex(currentIndex + 1)
      playerService.setCurrentIndex(currentIndex + 1)
    }
  }

  const playPrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1)
      playerService.setCurrentIndex(currentIndex - 1)
    }
  }

  const playVideo = (index: number) => {
    setCurrentIndex(index)
    playerService.setCurrentIndex(index)
  }

  if (!currentVideo) return null

  return (
    <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-sm flex">
      {/* Main Player Area */}
      <div className="flex-1 relative">
        <VideoPlayer
          src={currentVideo.url}
          title={`${currentVideo.name} (${currentIndex + 1}/${videos.length})`}
          onClose={onClose}
        />

        {/* Player Controls Overlay */}
        <div className="absolute bottom-20 left-4 right-4 flex items-center justify-between z-20">
          {/* Previous/Next Controls */}
          <div className="flex items-center space-x-4">
            <button
              onClick={playPrevious}
              disabled={currentIndex === 0}
              className="w-12 h-12 bg-neon-cyan/20 hover:bg-neon-cyan/30 disabled:bg-gray-600/20 disabled:text-gray-500 rounded-full flex items-center justify-center text-neon-cyan transition-all duration-300 border border-neon-cyan/30"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/>
              </svg>
            </button>

            <button
              onClick={playNext}
              disabled={currentIndex === videos.length - 1}
              className="w-12 h-12 bg-neon-cyan/20 hover:bg-neon-cyan/30 disabled:bg-gray-600/20 disabled:text-gray-500 rounded-full flex items-center justify-center text-neon-cyan transition-all duration-300 border border-neon-cyan/30"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
              </svg>
            </button>
          </div>

          {/* Playlist Toggle */}
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2 text-white text-sm">
              <input
                type="checkbox"
                checked={autoPlay}
                onChange={(e) => setAutoPlay(e.target.checked)}
                className="rounded border-neon-cyan/30 bg-dark-800/50 text-neon-cyan focus:ring-neon-cyan"
              />
              <span>Auto Play</span>
            </label>

            <button
              onClick={() => setShowPlaylist(!showPlaylist)}
              className="w-12 h-12 bg-neon-purple/20 hover:bg-neon-purple/30 rounded-full flex items-center justify-center text-neon-purple transition-all duration-300 border border-neon-purple/30"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M15 6H3v2h12V6zm0 4H3v2h12v-2zM3 16h8v-2H3v2zM17 6v8.18c-.31-.11-.65-.18-1-.18-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3V8h3V6h-5z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Playlist Sidebar */}
      <div className={`w-80 bg-black/80 backdrop-blur-sm border-l border-neon-cyan/20 transition-transform duration-300 ${
        showPlaylist ? 'translate-x-0' : 'translate-x-full'
      }`}>
        <div className="p-4 border-b border-neon-cyan/20">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-neon-cyan">
              Playlist ({videos.length})
            </h3>
            <button
              onClick={() => setShowPlaylist(false)}
              className="w-8 h-8 bg-neon-cyan/20 hover:bg-neon-cyan/30 rounded-full flex items-center justify-center text-neon-cyan transition-all duration-300"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="overflow-y-auto h-full pb-20">
          {videos.map((video, index) => (
            <div
              key={video.id}
              onClick={() => playVideo(index)}
              className={`p-4 border-b border-gray-700/50 cursor-pointer transition-all duration-300 ${
                index === currentIndex
                  ? 'bg-neon-cyan/10 border-neon-cyan/30'
                  : 'hover:bg-gray-800/50'
              }`}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 bg-dark-700 rounded flex items-center justify-center text-xs text-gray-400">
                  {index + 1}
                </div>
                
                <div className="flex-1 min-w-0">
                  <h4 className={`font-medium truncate ${
                    index === currentIndex ? 'text-neon-cyan' : 'text-white'
                  }`}>
                    {video.name}
                  </h4>
                  <p className="text-xs text-gray-400 mt-1">
                    {playerService.formatFileSize(video.size)}
                  </p>
                </div>

                {index === currentIndex && (
                  <div className="flex-shrink-0">
                    <div className="w-3 h-3 bg-neon-cyan rounded-full animate-pulse"></div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}