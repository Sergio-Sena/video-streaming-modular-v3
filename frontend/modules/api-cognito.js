/**
 * Módulo da API com Cognito
 * Gerencia comunicação com backend usando tokens Cognito
 */
class APICognitoModule {
    constructor() {
        this.baseUrl = 'https://4y3erwjgak.execute-api.us-east-1.amazonaws.com/prod';
        this.token = localStorage.getItem('authToken');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Usar token Cognito
        const currentToken = localStorage.getItem('authToken');
        if (currentToken && !options.skipAuth) {
            this.token = currentToken;
            config.headers.Authorization = `Bearer ${currentToken}`;
        }

        try {
            console.log('🌐 API Request:', { url, method: config.method, hasAuth: !!currentToken });
            
            const response = await fetch(url, config);
            
            console.log('📥 API Response:', { 
                status: response.status, 
                ok: response.ok,
                url: response.url 
            });
            
            if (!response.ok) {
                let errorMessage = `Erro ${response.status}: ${response.statusText}`;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.message || errorMessage;
                    console.error('❌ API Error:', errorData);
                } catch (e) {
                    console.error('❌ API Error (no JSON):', response.status);
                }
                
                // Se erro 401, não fazer logout automático (Cognito gerencia)
                if (response.status === 401) {
                    console.warn('⚠️ Token inválido - necessário relogin');
                }
                
                throw new Error(errorMessage);
            }
            
            const data = await response.json();
            console.log('✅ API Success:', data);
            return data;
            
        } catch (error) {
            console.error('💥 API Error:', error);
            
            if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
                throw new Error('Erro de conexão. Verifique sua internet.');
            }
            
            throw error;
        }
    }

    // Métodos de vídeos (principais)
    async getVideos(showHierarchy = false) {
        console.log('🎬 Carregando vídeos...', { showHierarchy });
        const url = showHierarchy ? '/videos?hierarchy=true' : '/videos';
        return await this.request(url, { method: 'GET' });
    }

    async getUploadUrl(fileName, fileType, fileSize, folderPath = '') {
        console.log('📤 Solicitando URL de upload...', { fileName, fileSize });
        
        // Usar GET temporariamente até POST ser configurado
        const params = new URLSearchParams({
            action: 'get-upload-url',
            filename: fileName,
            contentType: fileType,
            fileSize: fileSize.toString(),
            folderPath: folderPath || ''
        });
        
        return await this.request(`/videos?${params}`, {
            method: 'GET'
        });
    }

    async deleteVideo(videoKey) {
        console.log('🗑️ Deletando vídeo...', { videoKey });
        return await this.request('/videos', {
            method: 'DELETE',
            body: JSON.stringify({ key: videoKey, type: 'file' })
        });
    }

    async deleteFolder(folderKey) {
        console.log('🗑️ Deletando pasta...', { folderKey });
        return await this.request('/videos', {
            method: 'DELETE',
            body: JSON.stringify({ key: folderKey, type: 'folder' })
        });
    }

    // Upload direto para S3 (sem passar pela API)
    async uploadToS3(uploadUrl, file, onProgress) {
        console.log('⬆️ Upload direto S3...', { size: file.size });
        
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable && onProgress) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    onProgress(percentComplete, e.loaded, e.total);
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    console.log('✅ Upload S3 concluído');
                    resolve({ success: true });
                } else {
                    console.error('❌ Erro upload S3:', xhr.status);
                    reject(new Error('Erro no upload'));
                }
            });

            xhr.addEventListener('error', () => {
                console.error('❌ Erro rede upload S3');
                reject(new Error('Erro de rede'));
            });

            xhr.open('PUT', uploadUrl);
            xhr.setRequestHeader('Content-Type', file.type);
            xhr.send(file);
        });
    }

    // Multipart upload
    async getPartUrl(uploadId, partNumber, key) {
        const params = new URLSearchParams({
            action: 'get-part-url',
            uploadId,
            partNumber: partNumber.toString(),
            key
        });
        return await this.request(`/videos?${params}`, { method: 'GET' });
    }

    async completeMultipart(uploadId, parts, key) {
        const params = new URLSearchParams({
            action: 'complete-multipart',
            uploadId,
            key,
            parts: JSON.stringify(parts)
        });
        return await this.request(`/videos?${params}`, { method: 'GET' });
    }

    async uploadChunk(url, chunk) {
        const response = await fetch(url, {
            method: 'PUT',
            body: chunk
        });
        return response.headers.get('ETag');
    }

    // Métodos de autenticação (delegados para Cognito)
    logout() {
        console.log('🚪 Logout API...');
        this.token = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('userEmail');
    }

    isAuthenticated() {
        const token = localStorage.getItem('authToken');
        console.log('🔍 Check auth:', !!token);
        return !!token;
    }
}