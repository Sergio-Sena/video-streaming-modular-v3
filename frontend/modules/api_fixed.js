/**
 * Módulo da API - Versão Corrigida
 * Gerencia comunicação com o backend AWS com segurança aprimorada
 */
class APIModule {
    constructor() {
        // Configuração baseada no ambiente
        this.config = this.getConfig();
        this.token = localStorage.getItem('authToken');
        this.refreshPromise = null;
    }

    getConfig() {
        // Detecta ambiente baseado no hostname
        const hostname = window.location.hostname;
        
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return {
                baseUrl: 'http://localhost:3000',
                environment: 'development'
            };
        } else {
            return {
                baseUrl: 'https://4y3erwjgak.execute-api.us-east-1.amazonaws.com/prod',
                environment: 'production'
            };
        }
    }

    async request(endpoint, options = {}) {
        const url = `${this.config.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Sempre pega token mais recente do localStorage
        const currentToken = localStorage.getItem('authToken');
        if (currentToken && !options.skipAuth) {
            this.token = currentToken;
            config.headers.Authorization = `Bearer ${currentToken}`;
        }

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                await this.handleErrorResponse(response, url, config);
            }
            
            return await response.json();
        } catch (error) {
            this.handleNetworkError(error, url, config);
            throw error;
        }
    }

    async handleErrorResponse(response, url, config) {
        let errorMessage = `Erro ${response.status}: ${response.statusText}`;
        let errorData = null;

        try {
            errorData = await response.json();
            errorMessage = errorData.message || errorMessage;
            
            // Log seguro (sem dados sensíveis)
            console.error('API Error:', {
                url: this.sanitizeUrl(url),
                status: response.status,
                message: errorData.message,
                timestamp: new Date().toISOString()
            });
            
        } catch (e) {
            console.error('API Error (no JSON):', {
                url: this.sanitizeUrl(url),
                status: response.status,
                timestamp: new Date().toISOString()
            });
        }
        
        // Tratamento específico por status
        if (response.status === 401) {
            await this.handleUnauthorized();
        } else if (response.status === 403) {
            this.showError('Acesso negado. Verifique suas permissões.');
        } else if (response.status >= 500) {
            this.showError('Erro interno do servidor. Tente novamente em alguns minutos.');
        }
        
        throw new Error(errorMessage);
    }

    handleNetworkError(error, url, config) {
        // Log seguro de erro de rede
        console.error('Network Error:', {
            url: this.sanitizeUrl(url),
            message: error.message,
            timestamp: new Date().toISOString()
        });
        
        if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
            throw new Error('Erro de conexão. Verifique sua internet.');
        }
    }

    sanitizeUrl(url) {
        // Remove parâmetros sensíveis da URL para logs
        try {
            const urlObj = new URL(url);
            return `${urlObj.origin}${urlObj.pathname}`;
        } catch {
            return '[URL inválida]';
        }
    }

    async handleUnauthorized() {
        console.log('Token inválido ou expirado, fazendo logout');
        this.logout();
        
        // Redireciona para login se não estiver já lá
        if (window.authModule && typeof window.authModule.showScreen === 'function') {
            window.authModule.showScreen('login');
        }
    }

    showError(message) {
        // Mostra erro de forma segura (sem XSS)
        if (window.authModule && typeof window.authModule.showError === 'function') {
            window.authModule.showError(this.sanitizeMessage(message));
        } else {
            console.error('Error:', message);
        }
    }

    sanitizeMessage(message) {
        // Sanitiza mensagem para prevenir XSS
        const div = document.createElement('div');
        div.textContent = message;
        return div.innerHTML;
    }

    async login(email, password, mfaToken) {
        // Validação de entrada
        if (!email || !password || !mfaToken) {
            throw new Error('Todos os campos são obrigatórios');
        }

        // Sanitização básica
        const sanitizedEmail = email.trim().toLowerCase();
        
        const response = await this.request('/auth', {
            method: 'POST',
            body: JSON.stringify({ 
                email: sanitizedEmail, 
                password: password, 
                mfaToken: mfaToken.trim() 
            }),
            skipAuth: true
        });

        if (response.success && response.token) {
            this.token = response.token;
            localStorage.setItem('authToken', this.token);
            localStorage.setItem('userEmail', response.user.email);
            
            // Armazena timestamp do login
            localStorage.setItem('loginTimestamp', Date.now().toString());
            
            console.log('Login realizado com sucesso');
        } else {
            throw new Error(response.message || 'Falha no login');
        }

        return response;
    }

    async setupMFA() {
        return await this.request('/auth', {
            method: 'POST',
            body: JSON.stringify({ action: 'setup-mfa' }),
            skipAuth: true
        });
    }

    async verifyMFA(mfaToken) {
        if (!mfaToken || !mfaToken.trim()) {
            throw new Error('Código MFA é obrigatório');
        }

        return await this.request('/auth', {
            method: 'POST',
            body: JSON.stringify({ 
                action: 'verify-mfa', 
                mfaToken: mfaToken.trim() 
            }),
            skipAuth: true
        });
    }

    async getUploadUrl(fileName, fileType, fileSize, folderPath = '', targetBucket = 'video-streaming-sstech-eaddf6a1') {
        // Validação de entrada
        if (!fileName || !fileName.trim()) {
            throw new Error('Nome do arquivo é obrigatório');
        }

        if (!fileSize || fileSize <= 0) {
            throw new Error('Tamanho do arquivo inválido');
        }

        return await this.request('/videos', {
            method: 'POST',
            body: JSON.stringify({ 
                fileName: fileName.trim(), 
                fileType: fileType || 'video/mp4', 
                fileSize: parseInt(fileSize), 
                folderPath: folderPath.trim(), 
                targetBucket 
            })
        });
    }

    async getVideos(showHierarchy = false) {
        const url = showHierarchy ? '/videos?hierarchy=true' : '/videos';
        return await this.request(url, {
            method: 'GET'
        });
    }

    async deleteVideo(videoKey) {
        if (!videoKey || !videoKey.trim()) {
            throw new Error('Chave do vídeo é obrigatória');
        }

        return await this.request('/videos', {
            method: 'DELETE',
            body: JSON.stringify({ 
                key: videoKey.trim(), 
                type: 'file' 
            })
        });
    }

    async deleteFolder(folderKey) {
        if (!folderKey || !folderKey.trim()) {
            throw new Error('Chave da pasta é obrigatória');
        }

        return await this.request('/videos', {
            method: 'DELETE',
            body: JSON.stringify({ 
                key: folderKey.trim(), 
                type: 'folder' 
            })
        });
    }

    async getPartUrl(uploadId, partNumber, key) {
        // Validação de entrada
        if (!uploadId || !partNumber || !key) {
            throw new Error('Parâmetros de multipart inválidos');
        }

        return await this.request('/videos', {
            method: 'POST',
            body: JSON.stringify({ 
                action: 'get-part-url', 
                uploadId: uploadId.trim(), 
                partNumber: parseInt(partNumber), 
                key: key.trim() 
            })
        });
    }

    async completeMultipart(uploadId, parts, key) {
        // Validação de entrada
        if (!uploadId || !parts || !Array.isArray(parts) || !key) {
            throw new Error('Parâmetros de conclusão inválidos');
        }

        return await this.request('/videos', {
            method: 'POST',
            body: JSON.stringify({ 
                action: 'complete-multipart', 
                uploadId: uploadId.trim(), 
                parts: parts, 
                key: key.trim() 
            })
        });
    }

    async uploadChunk(url, chunk) {
        if (!url || !chunk) {
            throw new Error('URL e chunk são obrigatórios');
        }

        const response = await fetch(url, {
            method: 'PUT',
            body: chunk
        });

        if (!response.ok) {
            throw new Error(`Erro no upload do chunk: ${response.status}`);
        }

        return response.headers.get('ETag');
    }

    async uploadToS3(uploadUrl, file, onProgress) {
        return new Promise((resolve, reject) => {
            if (!uploadUrl || !file) {
                reject(new Error('URL de upload e arquivo são obrigatórios'));
                return;
            }

            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable && onProgress) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    onProgress(percentComplete, e.loaded, e.total);
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    resolve({ success: true });
                } else {
                    reject(new Error(`Erro no upload: ${xhr.status}`));
                }
            });

            xhr.addEventListener('error', () => {
                reject(new Error('Erro de rede no upload'));
            });

            xhr.addEventListener('timeout', () => {
                reject(new Error('Timeout no upload'));
            });

            xhr.open('PUT', uploadUrl);
            xhr.setRequestHeader('Content-Type', file.type);
            xhr.timeout = 300000; // 5 minutos
            xhr.send(file);
        });
    }

    logout() {
        this.token = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('userEmail');
        localStorage.removeItem('loginTimestamp');
        
        console.log('Logout realizado');
    }

    isAuthenticated() {
        const token = localStorage.getItem('authToken');
        const loginTimestamp = localStorage.getItem('loginTimestamp');
        
        if (!token || !loginTimestamp) {
            return false;
        }

        // Verifica se o token não expirou (24 horas)
        const now = Date.now();
        const loginTime = parseInt(loginTimestamp);
        const tokenAge = now - loginTime;
        const maxAge = 24 * 60 * 60 * 1000; // 24 horas em ms

        if (tokenAge > maxAge) {
            console.log('Token expirado por tempo');
            this.logout();
            return false;
        }

        return true;
    }

    getAuthStatus() {
        return {
            authenticated: this.isAuthenticated(),
            email: localStorage.getItem('userEmail'),
            loginTime: localStorage.getItem('loginTimestamp'),
            environment: this.config.environment
        };
    }
}