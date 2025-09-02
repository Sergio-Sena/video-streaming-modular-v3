import { useState, useRef } from 'react'
import { uploadService } from '../../services/uploadService'

interface DropZoneProps {
  onFilesSelected: (files: File[]) => void
  disabled?: boolean
}

export const DropZone = ({ onFilesSelected, disabled }: DropZoneProps) => {
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const folderInputRef = useRef<HTMLInputElement>(null)


  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    if (!disabled) {
      setIsDragOver(true)
    }
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    
    if (disabled) return

    const items = e.dataTransfer.items
    if (items) {
      // Processar pastas e arquivos
      const files = await uploadService.processDirectoryFiles(items)
      if (files.length > 0) {
        onFilesSelected(files)
      }
    } else {
      // Fallback para arquivos simples
      const files = Array.from(e.dataTransfer.files)
      onFilesSelected(files)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files) {
      onFilesSelected(Array.from(files))
    }
    // Reset input
    e.target.value = ''
  }



  return (
    <div
      className={`
        relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300
        ${isDragOver 
          ? 'border-cyan-400 bg-cyan-400/10 scale-105' 
          : 'border-gray-600 hover:border-cyan-500/50'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => !disabled && fileInputRef.current?.click()}
    >
      {/* Hidden inputs */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        className="hidden"
        onChange={handleFileSelect}
        disabled={disabled}
      />
      <input
        ref={folderInputRef}
        type="file"
        {...({ webkitdirectory: '' } as any)}
        multiple
        className="hidden"
        onChange={handleFileSelect}
        disabled={disabled}
      />


      {/* Drop zone content */}
      <div className="space-y-4">
        <div className="text-6xl">
          {isDragOver ? '📁' : '☁️'}
        </div>
        
        <div>
          <p className="text-xl font-semibold text-white mb-2">
            {isDragOver ? 'Solte os arquivos aqui' : 'Arraste arquivos ou pastas'}
          </p>
          <p className="text-gray-400 text-sm mb-4">
            Ou clique para selecionar arquivos
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex justify-center space-x-3">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation()
              fileInputRef.current?.click()
            }}
            disabled={disabled}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors disabled:opacity-50 text-sm"
          >
            📄 Arquivos
          </button>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation()
              folderInputRef.current?.click()
            }}
            disabled={disabled}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 text-sm"
          >
            📁 Pastas
          </button>
        </div>

        {/* File info */}
        <div className="text-xs text-gray-500 mt-4">
          <p>Máximo: 5GB por arquivo</p>
          <p>📁 Organização automática:</p>
          <p>📸 Fotos • 🎥 Vídeos • 📄 Documentos • 📁 Outros</p>
        </div>
      </div>
    </div>
  )
}