import { useState } from 'react'
import { authService } from '../services/authService'
import { apiClient } from '../../../shared/services/apiClient'

export const AuthTest = () => {
  const [result, setResult] = useState('')

  const testAuth = async () => {
    try {
      setResult('Testando...')
      
      // 1. Login
      const loginResult = await authService.login('senanetworker@gmail.com', 'sergiosena')
      console.log('Login result:', loginResult)
      
      // 2. Verificar localStorage
      const token = localStorage.getItem('auth_token')
      const user = localStorage.getItem('auth_user')
      console.log('Token no localStorage:', token ? 'OK' : 'ERRO')
      console.log('User no localStorage:', user ? 'OK' : 'ERRO')
      
      // 3. Testar requisição
      const response = await apiClient.get('/files')
      console.log('Response status:', response.status)
      
      if (response.ok) {
        const data = await response.json()
        setResult(`✅ Sucesso! ${data.files.length} arquivos encontrados`)
      } else {
        setResult(`❌ Erro ${response.status}`)
      }
      
    } catch (error) {
      console.error('Erro no teste:', error)
      setResult(`❌ Erro: ${error.message}`)
    }
  }

  return (
    <div className="p-4 bg-gray-800 text-white">
      <h3>Teste de Autenticação React</h3>
      <button 
        onClick={testAuth}
        className="bg-blue-600 px-4 py-2 rounded mt-2"
      >
        Testar Auth
      </button>
      <div className="mt-4">{result}</div>
    </div>
  )
}