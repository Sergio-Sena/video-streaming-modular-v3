interface ProgressBarProps {
  progress: number
  status: 'pending' | 'uploading' | 'completed' | 'error'
  fileName: string
  fileSize: number
  error?: string
  destination?: string
}

export const ProgressBar = ({ progress, status, fileName, fileSize, error, destination }: ProgressBarProps) => {
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getStatusColor = () => {
    switch (status) {
      case 'completed': return 'bg-green-500'
      case 'error': return 'bg-red-500'
      case 'uploading': return 'bg-cyan-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusIcon = () => {
    switch (status) {
      case 'completed': return '✅'
      case 'error': return '❌'
      case 'uploading': return '⏳'
      default: return '⏸️'
    }
  }

  return (
    <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-3">
          <span className="text-lg">{getStatusIcon()}</span>
          <div>
            <p className="text-white font-medium text-sm truncate max-w-[200px]" title={fileName}>
              {fileName}
            </p>
            <p className="text-gray-400 text-xs">
              {formatFileSize(fileSize)}
              {destination && (
                <span className="ml-2 text-cyan-400">
                  → 📁 {destination}
                </span>
              )}
            </p>
          </div>
        </div>
        
        <div className="text-right">
          <p className="text-sm font-medium text-white">
            {Math.round(progress)}%
          </p>
          <p className="text-xs text-gray-400 capitalize">
            {status === 'uploading' ? 'Enviando...' : 
             status === 'completed' ? 'Concluído' :
             status === 'error' ? 'Erro' : 'Aguardando'}
          </p>
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${getStatusColor()}`}
          style={{ width: `${Math.min(progress, 100)}%` }}
        ></div>
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-900/30 border border-red-500/50 rounded p-2 mt-2">
          <p className="text-red-400 text-xs">{error}</p>
        </div>
      )}

      {/* Upload speed for active uploads */}
      {status === 'uploading' && progress > 0 && (
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>
            {formatFileSize((fileSize * progress) / 100)} / {formatFileSize(fileSize)}
          </span>
          <span>
            {progress < 100 ? 'Enviando...' : 'Finalizando...'}
          </span>
        </div>
      )}
    </div>
  )
}