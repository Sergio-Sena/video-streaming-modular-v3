/**
 * Módulo da API - Versão Local (sem CORS)
 * Simula respostas para teste local
 */
class APIModule {
    constructor() {
        this.baseUrl = 'https://4y3erwjgak.execute-api.us-east-1.amazonaws.com/prod';
        this.token = localStorage.getItem('authToken');
        this.isLocal = window.location.hostname === 'localhost';
    }

    async request(endpoint, options = {}) {
        // Para teste local, simular respostas
        if (this.isLocal) {
            return this.simulateResponse(endpoint, options);
        }

        // Código original para produção
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

        const response = await fetch(url, config);
        return await response.json();
    }

    simulateResponse(endpoint, options) {
        console.log('🧪 MODO LOCAL: Simulando resposta para', endpoint);
        
        if (endpoint === '/auth' && options.method === 'POST') {
            const body = JSON.parse(options.body);
            
            if (body.action === 'setup-mfa') {
                return {
                    success: true,
                    qrCode: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
                    manualKey: 'JBSWY3DPEHPK3PXP'
                };
            }
            
            if (body.action === 'verify-mfa') {
                return { success: true, message: 'MFA configurado!' };
            }
            
            // Login simulado
            if (body.email === 'sergiosenaadmin@sstech' && body.password === 'sergiosena') {
                this.token = 'fake-jwt-token-for-local-test';
                localStorage.setItem('authToken', this.token);
                localStorage.setItem('userEmail', body.email);
                
                return {
                    success: true,
                    token: this.token,
                    user: { email: body.email }
                };
            } else {
                return { success: false, message: 'Credenciais inválidas' };
            }
        }
        
        if (endpoint === '/videos' && options.method === 'GET') {
            return {
                success: true,
                videos: [
                    {
                        key: 'videos/1234567890-exemplo.mp4',
                        name: 'exemplo.mp4',
                        size: 1024000,
                        lastModified: new Date().toISOString(),
                        url: 'https://videos.sstechnologies-cloud.com/videos/1234567890-exemplo.mp4'
                    }
                ]
            };
        }
        
        if (endpoint === '/videos' && options.method === 'POST') {
            return {
                success: true,
                uploadUrl: 'https://fake-upload-url.com',
                key: 'videos/fake-key',
                message: 'URL de upload gerada (simulada)'
            };
        }
        
        return { success: false, message: 'Endpoint não simulado' };
    }

    async login(email, password, mfaToken) {
        return await this.request('/auth', {
            method: 'POST',
            body: JSON.stringify({ email, password, mfaToken }),
            skipAuth: true
        });
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
        // Simular upload para teste local
        if (this.isLocal) {
            return new Promise((resolve) => {
                let progress = 0;
                const interval = setInterval(() => {
                    progress += 20;
                    if (onProgress) onProgress(progress);
                    if (progress >= 100) {
                        clearInterval(interval);
                        resolve({ success: true });
                    }
                }, 200);
            });
        }

        // Upload real para produção
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