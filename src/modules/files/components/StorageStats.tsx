import { useState, useEffect } from 'react'
import { fileService, StorageInfo } from '../services/fileService'

export const StorageStats = () => {
  const [storage, setStorage] = useState<StorageInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadStorageInfo = async () => {
    try {
      setLoading(true)
      setError(null)
      const storageInfo = await fileService.getStorageInfo()
      setStorage(storageInfo)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar informações')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadStorageInfo()
  }, [])

  if (loading) {
    return (
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-cyan-500/20 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="h-8 bg-gray-700 rounded mb-2"></div>
          <div className="h-4 bg-gray-700 rounded w-1/2"></div>
        </div>
      </div>
    )
  }

  if (error || !storage) {
    return (
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-red-500/20 p-6">
        <p className="text-red-400 text-center">{error || 'Erro ao carregar dados'}</p>
      </div>
    )
  }

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-cyan-500/20 p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Armazenamento</h3>
      
      <div className="space-y-4">
        {/* Barra de progresso */}
        <div>
          <div className="flex justify-between text-sm text-gray-300 mb-2">
            <span>{fileService.formatFileSize(storage.used)} usado</span>
            <span>5 <span className="text-cyan-400">TB</span></span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-cyan-500 to-blue-500 h-3 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(storage.percentage, 100)}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            {storage.percentage.toFixed(1)}% utilizado
          </p>
        </div>

        {/* Estatísticas */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-3 bg-gray-800/50 rounded-lg">
            <p className="text-2xl font-bold text-cyan-400">{storage.files}</p>
            <p className="text-xs text-gray-400">Arquivos</p>
          </div>
          <div className="text-center p-3 bg-gray-800/50 rounded-lg">
            <p className="text-2xl font-bold text-blue-400">
              {fileService.formatFileSize(storage.project_total)}
            </p>
            <p className="text-xs text-gray-400">Total Projeto</p>
          </div>
        </div>

        {/* Alerta se quase cheio */}
        {storage.percentage > 80 && (
          <div className="bg-yellow-900/30 border border-yellow-500/50 rounded-lg p-3">
            <p className="text-yellow-400 text-sm">
              ⚠️ Armazenamento quase cheio! Considere deletar arquivos antigos.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}