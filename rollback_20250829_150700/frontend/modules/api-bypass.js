/**
 * Módulo API Bypass - Para teste sem backend
 * Simula funcionalidades para testar frontend
 */
class APIBypassModule {
    constructor() {
        this.baseUrl = 'https://4y3erwjgak.execute-api.us-east-1.amazonaws.com/prod';
        this.token = localStorage.getItem('authToken');
    }

    // Simular listagem de vídeos
    async getVideos(showHierarchy = false) {
        console.log('🎬 Simulando carregamento de vídeos...');
        
        // Simular delay de rede
        await new Promise(resolve => setTimeout(resolve, 500));
        
        return {
            success: true,
            videos: [
                {
                    key: 'videos/exemplo1.mp4',
                    name: 'Vídeo Exemplo 1',
                    size: 1024000,
                    lastModified: new Date().toISOString(),
                    url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
                },
                {
                    key: 'videos/exemplo2.mp4', 
                    name: 'Vídeo Exemplo 2',
                    size: 2048000,
                    lastModified: new Date().toISOString(),
                    url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4'
                }
            ]
        };
    }

    // Simular URL de upload
    async getUploadUrl(fileName, fileType, fileSize, folderPath = '') {
        console.log('📤 Simulando URL de upload...', { fileName, fileSize });
        
        // Simular delay
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Retornar URL fake para teste
        return {
            success: true,
            uploadUrl: 'https://httpbin.org/put', // URL de teste que aceita PUT
            key: `${folderPath}${fileName}`,
            message: 'URL de upload simulada'
        };
    }

    // Simular upload para S3
    async uploadToS3(uploadUrl, file, onProgress) {
        console.log('⬆️ Simulando upload...', { size: file.size });
        
        return new Promise((resolve) => {
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 20;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(interval);
                    
                    if (onProgress) {
                        onProgress(100, file.size, file.size);
                    }
                    
                    console.log('✅ Upload simulado concluído');
                    resolve({ success: true });
                } else {
                    if (onProgress) {
                        const loaded = (progress / 100) * file.size;
                        onProgress(progress, loaded, file.size);
                    }
                }
            }, 100);
        });
    }

    // Simular delete
    async deleteVideo(videoKey) {
        console.log('🗑️ Simulando delete...', { videoKey });
        await new Promise(resolve => setTimeout(resolve, 200));
        return { success: true, message: 'Vídeo removido (simulado)' };
    }

    async deleteFolder(folderKey) {
        console.log('🗑️ Simulando delete pasta...', { folderKey });
        await new Promise(resolve => setTimeout(resolve, 200));
        return { success: true, message: 'Pasta removida (simulada)' };
    }

    // Métodos de autenticação
    logout() {
        console.log('🚪 Logout bypass...');
        this.token = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('userEmail');
    }

    isAuthenticated() {
        const token = localStorage.getItem('authToken');
        console.log('🔍 Check auth bypass:', !!token);
        return !!token;
    }

    // Multipart (não implementado no bypass)
    async getPartUrl(uploadId, partNumber, key) {
        throw new Error('Multipart não suportado no modo bypass');
    }

    async completeMultipart(uploadId, parts, key) {
        throw new Error('Multipart não suportado no modo bypass');
    }

    async uploadChunk(url, chunk) {
        throw new Error('Upload chunk não suportado no modo bypass');
    }

    // Método request genérico (para compatibilidade)
    async request(endpoint, options = {}) {
        console.log('🔄 Request bypass:', endpoint, options.method || 'GET');
        
        // Simular resposta baseada no endpoint
        if (endpoint.includes('/videos')) {
            if (options.method === 'GET') {
                return this.getVideos();
            }
        }
        
        return { success: true, message: 'Request simulado' };
    }
}