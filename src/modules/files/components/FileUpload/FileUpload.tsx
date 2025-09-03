import { useState } from 'react'
import { DropZone } from './DropZone'
import { ProgressBar } from './ProgressBar'
import { uploadService, UploadFile } from '../../services/uploadService'

interface FileUploadProps {
  onUploadComplete?: () => void
  onClose?: () => void
}

export const FileUpload = ({ onUploadComplete, onClose }: FileUploadProps) => {
  const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([])
  const [isUploading, setIsUploading] = useState(false)

  const handleFilesSelected = async (files: File[]) => {
    const newUploadFiles: UploadFile[] = []

    for (const file of files) {
      const validation = uploadService.validateFile(file)
      
      const uploadFile: UploadFile = {
        file,
        id: `${Date.now()}-${Math.random()}`,
        name: file.name,
        size: file.size,
        progress: 0,
        status: validation.valid ? 'pending' : 'error',
        error: validation.error
      }

      newUploadFiles.push(uploadFile)
    }

    setUploadFiles(prev => [...prev, ...newUploadFiles])
  }

  const startUpload = async () => {
    setIsUploading(true)
    
    const validFiles = uploadFiles.filter(f => f.status === 'pending')
    
    for (const uploadFile of validFiles) {
      try {
        // Atualizar status para uploading
        setUploadFiles(prev => 
          prev.map(f => 
            f.id === uploadFile.id 
              ? { ...f, status: 'uploading' as const }
              : f
          )
        )

        // Obter URL de upload
        const { uploadUrl, fileId } = await uploadService.getUploadUrl(
          uploadFile.file.name,
          uploadFile.file.size,
          uploadFile.file.type
        )

        // Upload com progress
        await uploadService.uploadLargeFile(
          uploadFile.file,
          uploadUrl,
          (progress) => {
            setUploadFiles(prev => 
              prev.map(f => 
                f.id === uploadFile.id 
                  ? { ...f, progress }
                  : f
              )
            )
          }
        )

        // Confirmar upload e copiar vídeo se necessário
        await uploadService.confirmUpload(fileId)

        // Marcar como completo
        setUploadFiles(prev => 
          prev.map(f => 
            f.id === uploadFile.id 
              ? { ...f, status: 'completed' as const, progress: 100 }
              : f
          )
        )

        // Refresh imediato após cada arquivo
        onUploadComplete?.()

      } catch (error) {
        console.error('Upload error:', error)
        
        setUploadFiles(prev => 
          prev.map(f => 
            f.id === uploadFile.id 
              ? { 
                  ...f, 
                  status: 'error' as const, 
                  error: error instanceof Error ? error.message : 'Erro no upload'
                }
              : f
          )
        )
      }
    }

    setIsUploading(false)
    onUploadComplete?.()
  }

  const removeFile = (fileId: string) => {
    setUploadFiles(prev => prev.filter(f => f.id !== fileId))
  }

  const clearCompleted = () => {
    setUploadFiles(prev => prev.filter(f => f.status !== 'completed'))
  }

  const clearAll = () => {
    setUploadFiles([])
  }

  const hasValidFiles = uploadFiles.some(f => f.status === 'pending')
  const hasCompletedFiles = uploadFiles.some(f => f.status === 'completed')
  const totalFiles = uploadFiles.length
  const completedFiles = uploadFiles.filter(f => f.status === 'completed').length

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-cyan-500/20 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-white">Upload de Arquivos</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        )}
      </div>

      {/* Drop Zone */}
      <div className="mb-6">
        <DropZone 
          onFilesSelected={handleFilesSelected}
          disabled={isUploading}
        />
      </div>

      {/* File List */}
      {uploadFiles.length > 0 && (
        <div className="space-y-4">
          {/* Summary */}
          <div className="flex items-center justify-between bg-gray-800/30 rounded-lg p-3">
            <div className="text-sm text-gray-300">
              {totalFiles} arquivo(s) • {completedFiles} concluído(s)
            </div>
            
            <div className="flex space-x-2">
              {hasCompletedFiles && (
                <button
                  onClick={clearCompleted}
                  className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white rounded text-sm transition-colors"
                >
                  Limpar Concluídos
                </button>
              )}
              
              <button
                onClick={clearAll}
                className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-sm transition-colors"
              >
                Limpar Tudo
              </button>
            </div>
          </div>

          {/* Progress Bars */}
          <div className="space-y-3 max-h-60 overflow-y-auto">
            {uploadFiles.map((uploadFile) => (
              <div key={uploadFile.id} className="relative">
                <ProgressBar
                  progress={uploadFile.progress}
                  status={uploadFile.status}
                  fileName={uploadFile.name}
                  fileSize={uploadFile.size}
                  error={uploadFile.error}
                  destination={uploadService.detectFolder(uploadFile.file.type, uploadFile.file.name)}
                />
                
                {/* Remove button */}
                {uploadFile.status !== 'uploading' && (
                  <button
                    onClick={() => removeFile(uploadFile.id)}
                    className="absolute top-2 right-2 text-gray-400 hover:text-red-400 transition-colors"
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
          </div>

          {/* Upload Button */}
          {hasValidFiles && (
            <div className="flex justify-center pt-4">
              <button
                onClick={startUpload}
                disabled={isUploading}
                className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 disabled:bg-gray-600 text-white rounded-lg transition-colors font-medium disabled:cursor-not-allowed"
              >
                {isUploading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Enviando...
                  </div>
                ) : (
                  `Enviar ${uploadFiles.filter(f => f.status === 'pending').length} arquivo(s)`
                )}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}