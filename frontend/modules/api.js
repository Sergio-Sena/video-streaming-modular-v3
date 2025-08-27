/**
 * Módulo da API
 * Gerencia comunicação com o backend AWS
 */
class APIModule {
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

        if (this.token && !options.skipAuth) {
            config.headers.Authorization = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                let errorMessage = `Erro ${response.status}: ${response.statusText}`;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.message || errorMessage;
                } catch (e) {
                    // Se não conseguir parsear JSON, usa mensagem padrão
                }
                throw new Error(errorMessage);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            
            if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
                throw new Error('Erro de conexão. Verifique sua internet.');
            }
            
            throw error;
        }
    }

    async login(email, password, mfaToken) {
        const response = await this.request('/auth', {
            method: 'POST',
            body: JSON.stringify({ email, password, mfaToken }),
            skipAuth: true
        });

        if (response.success && response.token) {
            this.token = response.token;
            localStorage.setItem('authToken', this.token);
            localStorage.setItem('userEmail', response.user.email);
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
        return await this.request('/auth', {
            method: 'POST',
            body: JSON.stringify({ action: 'verify-mfa', mfaToken }),
            skipAuth: true
        });
    }

    async getUploadUrl(fileName, fileType, fileSize) {
        return await this.request('/videos', {
            method: 'POST',
            body: JSON.stringify({ fileName, fileType, fileSize })
        });
    }

    async getVideos() {
        return await this.request('/videos', {
            method: 'GET'
        });
    }

    async uploadToS3(uploadUrl, file, onProgress) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable && onProgress) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    onProgress(percentComplete);
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    resolve({ success: true });
                } else {
                    reject(new Error('Erro no upload'));
                }
            });

            xhr.addEventListener('error', () => {
                reject(new Error('Erro de rede'));
            });

            xhr.open('PUT', uploadUrl);
            xhr.setRequestHeader('Content-Type', file.type);
            xhr.send(file);
        });
    }

    logout() {
        this.token = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('userEmail');
    }

    isAuthenticated() {
        return !!this.token;
    }
}