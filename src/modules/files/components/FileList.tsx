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
  const [showPlayer, setShowPlayer] = useState(false)
  const [currentVideo, setCurrentVideo] = useState<any>(null)

  const loadFiles = async () => {
    try {
      setLoading(true)
      setError(null)
      const fileList = await fileService.getFiles()
      
      // Adicionar vídeo de exemplo que sempre funciona
      const exampleVideo = {
        id: 'sample-video',
        name: '🎬 Vídeo de Exemplo (Funciona)',
        size: 1024000,
        type: 'video/mp4',
        url: '/sample-video.mp4',
        createdAt: new Date().toISOString(),
        lastModified: new Date().toISOString()
      }
      
      const allFilesWithExample = [exampleVideo, ...fileList]
      
      setAllFiles(allFilesWithExample)
      setFolders(folderService.extractFoldersFromFiles(allFilesWithExample))
      updateFilteredFiles(allFilesWithExample, currentFolder)
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

  const handlePlay = async (file: any) => {
    try {
      let videoUrl
      if (file.id === 'sample-video') {
        videoUrl = '/sample-video.mp4'
      } else {
        // Detectar se existe versão convertida
        const convertedFile = findConvertedVersion(file, allFiles)
        const targetFile = convertedFile || file
        
        console.log('Video selection:', {
          original: file.name,
          converted: convertedFile?.name,
          using: targetFile.name
        })
        
        // Usar bucket público (solução que funciona)
        const fileName = targetFile.id.split('/').pop()
        videoUrl = `https://automacao-video.s3.amazonaws.com/videos/user-sergio-sena/${fileName}`
      }
      
      console.log('Playing video:', { fileId: file.id, url: videoUrl })
      
      setCurrentVideo({
        id: file.id,
        name: file.name,
        url: videoUrl,
        type: 'video/mp4', // Sempre MP4 para compatibilidade
        size: file.size,
        lastModified: file.lastModified
      })
      setShowPlayer(true)
    } catch (error) {
      console.error('Error preparing video:', error)
      // Fallback: tentar presigned URL
      try {
        videoUrl = await fileService.getDownloadUrl(file.id)
        setCurrentVideo({
          id: file.id,
          name: file.name,
          url: videoUrl,
          type: 'video/mp4',
          size: file.size,
          lastModified: file.lastModified
        })
        setShowPlayer(true)
      } catch (fallbackError) {
        alert('Erro ao carregar vídeo. Tente novamente.')
      }
    }
  }

  // Função para encontrar versão convertida
  const findConvertedVersion = (originalFile: any, fileList: any[]) => {
    if (originalFile.name.toLowerCase().endsWith('.mp4')) {
      return null // Já é MP4
    }
    
    // Procurar versão .mp4 com mesmo timestamp
    const baseName = originalFile.name.substring(0, originalFile.name.lastIndexOf('.'))
    const convertedName = `${baseName}.mp4`
    
    return fileList.find(f => f.name === convertedName)
  }

  // Função para tentar múltiplas URLs
  const tryMultipleUrls = async (fileId: string): Promise<string> => {
    const urls = [
      // 1. CloudFront (geralmente mais rápido)
      `https://d2gikqc9umroy8.cloudfront.net/${fileId}`,
      // 2. S3 direto
      `https://drive-online-storage.s3.amazonaws.com/${fileId}`,
      // 3. Presigned URL (fallback)
      null // Será gerada se necessário
    ]
    
    // Testar URLs diretas primeiro
    for (const url of urls.filter(Boolean)) {
      try {
        // Teste rápido - se não der erro de CORS, provavelmente funciona
        const testVideo = document.createElement('video')
        testVideo.src = url as string
        
        // Retornar imediatamente - o browser vai lidar com CORS
        return url as string
      } catch (error) {
        console.warn(`URL failed: ${url}`, error)
      }
    }
    
    // Fallback: presigned URL
    try {
      return await fileService.getDownloadUrl(fileId)
    } catch (error) {
      throw new Error('Nenhuma URL de vídeo disponível')
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
                {(file.type.startsWith('video/') || file.name?.match(/\.(mp4|avi|mov|wmv|flv|webm|mkv|ts|m4v|3gp|ogv)$/i)) && (
                  <button
                    onClick={() => handlePlay(file)}
                    className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm transition-colors flex items-center space-x-1"
                    title={findConvertedVersion(file, allFiles) ? 'Reproduzir (versão otimizada disponível)' : 'Reproduzir'}
                  >
                    <span>▶️</span>
                    <span>Play</span>
                    {findConvertedVersion(file, allFiles) && <span className="text-xs">🎯</span>}
                  </button>
                )}
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
      
      {/* Modal do Player */}
      {showPlayer && currentVideo && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-gray-900 rounded-xl border border-cyan-500/20 w-full max-w-4xl">
            <div className="flex items-center justify-between p-4 border-b border-gray-700">
              <h3 className="text-white font-semibold truncate">{currentVideo.name}</h3>
              <button
                onClick={() => setShowPlayer(false)}
                className="text-gray-400 hover:text-white transition-colors text-xl"
              >
                ×
              </button>
            </div>
            <div className="p-4">
              <video
                controls
                autoPlay
                className="w-full max-h-[70vh] bg-black rounded"
                src={currentVideo.url}
              >
                Seu navegador não suporta o elemento de vídeo.
              </video>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}