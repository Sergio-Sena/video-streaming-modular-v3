/**
 * Service Worker para interceptar requests de vídeo e contornar CORS
 */

const CACHE_NAME = 'drive-online-video-cache-v1'
const API_BASE = 'https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod'

// Instalar service worker
self.addEventListener('install', (event) => {
  console.log('Video Proxy SW: Installing...')
  self.skipWaiting()
})

// Ativar service worker
self.addEventListener('activate', (event) => {
  console.log('Video Proxy SW: Activating...')
  event.waitUntil(self.clients.claim())
})

// Interceptar requests
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url)
  
  // Interceptar apenas requests de vídeo
  if (url.pathname.includes('/video-proxy/')) {
    event.respondWith(handleVideoRequest(event.request))
  }
})

async function handleVideoRequest(request) {
  try {
    const url = new URL(request.url)
    const fileId = url.searchParams.get('fileId')
    
    if (!fileId) {
      return new Response('Missing fileId parameter', { status: 400 })
    }
    
    console.log('Video Proxy SW: Handling request for', fileId)
    
    // Verificar cache primeiro
    const cache = await caches.open(CACHE_NAME)
    const cachedResponse = await cache.match(request)
    
    if (cachedResponse) {
      console.log('Video Proxy SW: Serving from cache')
      return cachedResponse
    }
    
    // Tentar vídeo convertido primeiro
    const convertedId = getConvertedVideoId(fileId)
    let s3Response
    
    if (convertedId !== fileId) {
      try {
        const convertedUrl = await getPresignedUrl(convertedId)
        s3Response = await fetch(convertedUrl, {
          method: request.method,
          headers: { 'Range': request.headers.get('Range') || '' }
        })
        
        if (s3Response.ok) {
          console.log('Video Proxy SW: Using converted video')
        } else {
          throw new Error('Converted video not found')
        }
      } catch (error) {
        console.log('Video Proxy SW: Converted video failed, trying original')
        s3Response = null
      }
    }
    
    // Se não conseguiu o convertido, usar original
    if (!s3Response || !s3Response.ok) {
      const originalUrl = await getPresignedUrl(fileId)
      s3Response = await fetch(originalUrl, {
        method: request.method,
        headers: { 'Range': request.headers.get('Range') || '' }
      })
    }
    
    if (!s3Response.ok) {
      throw new Error(`S3 request failed: ${s3Response.status}`)
    }
    
    // Criar response com headers CORS corretos
    const responseHeaders = new Headers()
    responseHeaders.set('Access-Control-Allow-Origin', '*')
    responseHeaders.set('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
    responseHeaders.set('Access-Control-Expose-Headers', 'Content-Range, Content-Length, Accept-Ranges')
    responseHeaders.set('Content-Type', 'video/mp4') // Forçar video/mp4
    responseHeaders.set('Content-Length', s3Response.headers.get('Content-Length') || '0')
    responseHeaders.set('Accept-Ranges', 'bytes')
    
    if (s3Response.headers.get('Content-Range')) {
      responseHeaders.set('Content-Range', s3Response.headers.get('Content-Range'))
    }
    
    const response = new Response(s3Response.body, {
      status: s3Response.status,
      statusText: s3Response.statusText,
      headers: responseHeaders
    })
    
    if (s3Response.status === 200) {
      cache.put(request, response.clone())
    }
    
    return response
    
  } catch (error) {
    console.error('Video Proxy SW: Error handling request', error)
    return new Response(`Proxy error: ${error.message}`, { status: 500 })
  }
}

function getConvertedVideoId(fileId) {
  if (fileId.toLowerCase().endsWith('.mp4')) {
    return fileId
  }
  const baseName = fileId.substring(0, fileId.lastIndexOf('.'))
  return `${baseName}.mp4`
}

async function getPresignedUrl(fileId) {
  // Simular chamada para obter presigned URL
  // Em produção, isso seria uma chamada para seu backend
  const response = await fetch(`${API_BASE}/files/${encodeURIComponent(fileId)}/download-url`, {
    headers: {
      'Authorization': `Bearer ${await getStoredToken()}`
    }
  })
  
  if (!response.ok) {
    throw new Error('Failed to get presigned URL')
  }
  
  const data = await response.json()
  return data.downloadUrl
}

async function getStoredToken() {
  // Obter token do localStorage via message
  return new Promise((resolve) => {
    self.clients.matchAll().then(clients => {
      if (clients.length > 0) {
        clients[0].postMessage({ type: 'GET_TOKEN' })
        
        // Timeout fallback
        setTimeout(() => resolve(''), 1000)
      } else {
        resolve('')
      }
    })
    
    // Escutar resposta
    self.addEventListener('message', function handler(event) {
      if (event.data.type === 'TOKEN_RESPONSE') {
        self.removeEventListener('message', handler)
        resolve(event.data.token)
      }
    })
  })
}