import { useState, useEffect } from 'react'

export const LogCapture = () => {
  const [logs, setLogs] = useState<string[]>([])

  useEffect(() => {
    const originalLog = console.log
    const originalWarn = console.warn
    const originalError = console.error

    console.log = (...args) => {
      const message = args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
      ).join(' ')
      setLogs(prev => [...prev, `[LOG] ${message}`])
      originalLog(...args)
    }

    console.warn = (...args) => {
      const message = args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
      ).join(' ')
      setLogs(prev => [...prev, `[WARN] ${message}`])
      originalWarn(...args)
    }

    console.error = (...args) => {
      const message = args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
      ).join(' ')
      setLogs(prev => [...prev, `[ERROR] ${message}`])
      originalError(...args)
    }

    return () => {
      console.log = originalLog
      console.warn = originalWarn
      console.error = originalError
    }
  }, [])

  const clearLogs = () => setLogs([])

  return (
    <div className="fixed bottom-4 right-4 w-96 max-h-80 bg-black/90 text-green-400 p-4 rounded-lg overflow-auto text-xs font-mono z-50">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-white font-bold">Console Logs</h3>
        <button 
          onClick={clearLogs}
          className="bg-red-600 px-2 py-1 rounded text-white text-xs"
        >
          Limpar
        </button>
      </div>
      <div className="space-y-1">
        {logs.map((log, index) => (
          <div key={index} className="break-words">
            {log}
          </div>
        ))}
      </div>
    </div>
  )
}