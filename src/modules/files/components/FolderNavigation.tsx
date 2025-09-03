interface SimpleFolderTabsProps {
  folders: Array<{name: string, count: number}>
  currentFolder: string
  onFolderChange: (folder: string) => void
}

export const SimpleFolderTabs = ({ 
  folders, 
  currentFolder, 
  onFolderChange 
}: SimpleFolderTabsProps) => {
  const allFolders = folders.find(f => f.name === 'Todos') ? folders : [{name: 'Todos', count: 0}, ...folders]
  
  return (
    <div className="mb-6">
      <div className="flex flex-wrap gap-2">
        {allFolders.map((folder) => (
          <button
            key={folder.name}
            onClick={() => onFolderChange(folder.name)}
            className={`px-4 py-2 rounded-lg transition-colors text-sm ${
              currentFolder === folder.name
                ? 'bg-cyan-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {folder.name === 'Fotos' ? '📸' : 
             folder.name === 'Vídeos' ? '🎥' : 
             folder.name === 'Documentos' ? '📄' : 
             folder.name === 'Outros' ? '📁' : '📂'} {folder.name}
            {folder.count > 0 && (
              <span className="ml-2 text-xs opacity-75">({folder.count})</span>
            )}
          </button>
        ))}
      </div>
    </div>
  )
}