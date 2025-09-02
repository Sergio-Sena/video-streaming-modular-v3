import { useState, useEffect } from 'react'
import { fileService } from '../services/fileService'
import { folderService, SimpleFolder } from '../services/folderService'
import { SimpleFolderTabs } from './FolderNavigation'

// Componente para preview de imagem com presigned URL
const ImagePreview = ({ fileId, fileName }: { fileId: string, fileName: string }) => {
  const [imageUrl, setImageUrl] = useState<string | null>(null)
  const [showFallback, setShowFallback] = useState(false)

  useEffect(() => {
    const loadImageUrl = async () => {
      try {
        const url = await fileService.getDownloadUrl(fileId)
        setImageUrl(url)
      } catch (error) {
        console.error('Error loading image preview:', error)
        setShowFallback(true)
      }
    }
    loadImageUrl()
  }, [fileId])

  if (showFallback || !imageUrl) {
    return <div className="text-2xl">🖼️</div>
  }

  return (
    <img 
      src={imageUrl}
      alt={fileName}
      className="w-12 h-12 object-cover rounded border border-gray-600"
      onError={() => setShowFallback(true)}
    />
  )
}

interface FileListProps {
  onRefresh?: () => void
}

export const FileList = ({ onRefresh }: FileListProps) => {
  const [allFiles, setAllFiles] = useState<any[]>([])
  const [filteredFiles, setFilteredFiles] = useState<any[]>([])
  const [folders, setFolders] = useState<SimpleFolder[]>([])
  const [currentFolder, setCurrentFolder] = useState('Todos')
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadFiles = async () => {
    try {
      setLoading(true)
      setError(null)
      const fileList = await fileService.getFiles()
      
      setAllFiles(fileList)
      setFolders(folderService.extractFoldersFromFiles(fileList))
      updateFilteredFiles(fileList, currentFolder)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar arquivos')
    } finally {
      setLoading(false)
    }
  }
  
  // Atualizar arquivos filtrados
  const updateFilteredFiles = (files: any[], folder: string) => {
    const filtered = folderService.getFilesInFolder(files, folder)
    setFilteredFiles(filtered)
  }

  // Mudar pasta
  const handleFolderChange = (folder: string) => {
    setCurrentFolder(folder)
    setSearchTerm('')
    updateFilteredFiles(allFiles, folder)
  }
  
  // Filtrar arquivos por busca
  const handleSearch = (term: string) => {
    setSearchTerm(term)
    if (!term.trim()) {
      updateFilteredFiles(allFiles, currentFolder)
    } else {
      const filtered = allFiles.filter(file => 
        file.name.toLowerCase().includes(term.toLowerCase())
      )
      setFilteredFiles(filtered)
    }
  }

  const handleDelete = async (fileId: string) => {
    if (!confirm('Tem certeza que deseja deletar este arquivo?')) return
    
    try {
      await fileService.deleteFile(fileId)
      await loadFiles()
      onRefresh?.()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Erro ao deletar arquivo')
    }
  }

  const handleDownload = async (fileId: string, fileName: string) => {
    try {
      const downloadUrl = await fileService.getDownloadUrl(fileId)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = fileName
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Erro ao baixar arquivo')
    }
  }

  useEffect(() => {
    loadFiles()
  }, [])

  // Auto-reload quando onRefresh é chamado
  useEffect(() => {
    if (onRefresh) {
      loadFiles()
    }
  }, [onRefresh])
  
  // Atualizar quando pasta muda
  useEffect(() => {
    if (allFiles.length > 0) {
      updateFilteredFiles(allFiles, currentFolder)
    }
  }, [currentFolder, allFiles])

  if (loading) {
    return (
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-cyan-500/20 p-6">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
          <span className="ml-3 text-gray-300">Carregando arquivos...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-red-500/20 p-6">
        <div className="text-center py-8">
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={loadFiles}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-cyan-500/20 p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">Meus Arquivos</h2>
          <button
            onClick={loadFiles}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors text-sm"
          >
            Atualizar
          </button>
        </div>
        
        {/* Abas de pastas */}
        <SimpleFolderTabs
          folders={folders}
          currentFolder={currentFolder}
          onFolderChange={handleFolderChange}
        />
        
        {/* Campo de busca */}
        <div className="relative">
          <input
            type="text"
            placeholder="Buscar arquivos..."
            value={searchTerm}
            onChange={(e) => handleSearch(e.target.value)}
            className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-cyan-500 focus:outline-none"
          />
          <div className="absolute right-3 top-2.5 text-gray-400">
            🔍
          </div>
        </div>
      </div>

      {filteredFiles.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📁</div>
          <p className="text-gray-400 text-lg mb-2">
            {searchTerm ? `Nenhum arquivo encontrado para "${searchTerm}"` : 
             currentFolder === 'Todos' ? 'Nenhum arquivo encontrado' : `Nenhum arquivo em ${currentFolder}`}
          </p>
          <p className="text-gray-500 text-sm">Faça upload do seu primeiro arquivo!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredFiles.map((file) => (
            <div
              key={file.id}
              className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-700/50 hover:border-cyan-500/30 transition-colors"
            >
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 flex items-center justify-center">
                  {file.type.startsWith('image/') ? (
                    <ImagePreview fileId={file.id} fileName={file.name} />
                  ) : (
                    <div className="text-2xl">
                      {file.type.includes('pdf') ? '📄' : 
                       file.type.includes('video') ? '🎥' : 
                       file.type.includes('audio') ? '🎵' : '📄'}
                    </div>
                  )}
                </div>
                <div>
                  <p className="text-white font-medium truncate max-w-[300px]" title={file.name}>{file.name}</p>
                  <p className="text-gray-400 text-sm">
                    {folderService.formatSize(file.size)} • {new Date(file.lastModified).toLocaleDateString()}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleDownload(file.id, file.name)}
                  className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-sm transition-colors"
                >
                  Download
                </button>
                <button
                  onClick={() => handleDelete(file.id)}
                  className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-sm transition-colors"
                >
                  Deletar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}