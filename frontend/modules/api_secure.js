/**
 * 🔒 MÓDULO API SEGURO
 * Comunicação segura com backend, validação de entrada e sanitização
 */
class SecureAPIModule {
    constructor() {
        this.config = this.getConfig();
        this.token = localStorage.getItem('authToken');
        this.requestQueue = new Map();
        this.rateLimiter = new RateLimiter(100, 60000); // 100 req/min
    }

    getConfig() {
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
        try {
            // Rate limiting
            if (!this.rateLimiter.canMakeRequest()) {
                throw new Error('Muitas requisições. Tente novamente em alguns segundos.');
            }

            // Validação de entrada
            const validation = this.validateRequest(endpoint, options);
            if (!validation.valid) {
                throw new Error(validation.message);
            }

            const url = `${this.config.baseUrl}${endpoint}`;
            const config = {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            };

            // Sanitização do body
            if (config.body && typeof config.body === 'string') {
                config.body = this.sanitizeJSON(config.body);
            }

            // Token de autenticação
            const currentToken = localStorage.getItem('authToken');
            if (currentToken && !options.skipAuth) {
                this.token = currentToken;
                config.headers.Authorization = `Bearer ${currentToken}`;
            }

            const response = await fetch(url, config);
            
            if (!response.ok) {
                await this.handleErrorResponse(response, url);
            }
            
            return await response.json();

        } catch (error) {
            this.handleNetworkError(error, endpoint);
            throw error;
        }
    }

    validateRequest(endpoint, options) {
        // Validação de endpoint
        if (!endpoint || typeof endpoint !== 'string') {
            return { valid: false, message: 'Endpoint inválido' };
        }

        // Validação de XSS no endpoint
        if (this.containsXSS(endpoint)) {
            return { valid: false, message: 'Endpoint contém caracteres inválidos' };
        }

        // Validação do body
        if (options.body) {
            try {
                const parsed = JSON.parse(options.body);
                if (this.containsXSSInObject(parsed)) {
                    return { valid: false, message: 'Dados contêm caracteres inválidos' };
                }
            } catch (e) {
                return { valid: false, message: 'JSON inválido' };
            }
        }

        return { valid: true };
    }

    containsXSS(text) {
        if (!text || typeof text !== 'string') return false;
        
        const xssPatterns = [
            /<script[^>]*>.*?<\/script>/gi,
            /javascript:/gi,
            /on\w+\s*=/gi,
            /<iframe[^>]*>.*?<\/iframe>/gi,
            /<object[^>]*>.*?<\/object>/gi,
            /<embed[^>]*>/gi,
            /eval\s*\(/gi,
            /document\./gi,
            /window\./gi
        ];

        return xssPatterns.some(pattern => pattern.test(text));
    }

    containsXSSInObject(obj) {
        if (typeof obj === 'string') {
            return this.containsXSS(obj);
        } else if (typeof obj === 'object' && obj !== null) {
            for (const key in obj) {
                if (this.containsXSSInObject(obj[key])) {
                    return true;
                }
            }
        }
        return false;
    }

    sanitizeJSON(jsonString) {
        try {
            const parsed = JSON.parse(jsonString);
            const sanitized = this.sanitizeObject(parsed);
            return JSON.stringify(sanitized);
        } catch (e) {
            return jsonString;
        }
    }

    sanitizeObject(obj) {
        if (typeof obj === 'string') {
            return this.sanitizeString(obj);
        } else if (typeof obj === 'object' && obj !== null) {
            const sanitized = {};
            for (const key in obj) {
                sanitized[key] = this.sanitizeObject(obj[key]);
            }
            return sanitized;
        } else if (Array.isArray(obj)) {
            return obj.map(item => this.sanitizeObject(item));
        }
        return obj;
    }

    sanitizeString(str) {
        if (!str || typeof str !== 'string') return str;
        
        // HTML escape
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#x27;')
            .replace(/\//g, '&#x2F;');
    }

    async handleErrorResponse(response, url) {
        let errorMessage = `Erro ${response.status}: ${response.statusText}`;
        let errorData = null;

        try {
            errorData = await response.json();
            errorMessage = errorData.message || errorMessage;
            
            // Log seguro (sem dados sensíveis)
            console.error('API Error:', {
                url: this.sanitizeUrl(url),
                status: response.status,
                message: this.sanitizeString(errorData.message || ''),
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
            this.showError('Erro interno do servidor. Tente novamente.');
        }
        
        throw new Error(this.sanitizeString(errorMessage));
    }

    handleNetworkError(error, endpoint) {
        console.error('Network Error:', {
            endpoint: this.sanitizeString(endpoint),
            message: this.sanitizeString(error.message),
            timestamp: new Date().toISOString()
        });
        
        if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
            throw new Error('Erro de conexão. Verifique sua internet.');
        }
    }

    sanitizeUrl(url) {
        try {
            const urlObj = new URL(url);
            return `${urlObj.origin}${urlObj.pathname}`;
        } catch {
            return '[URL inválida]';
        }
    }

    async handleUnauthorized() {
        console.log('Token inválido, fazendo logout');
        this.logout();
        
        if (window.authModule && typeof window.authModule.showScreen === 'function') {
            window.authModule.showScreen('login');
        }
    }

    showError(message) {
        const sanitizedMessage = this.sanitizeString(message);
        
        if (window.authModule && typeof window.authModule.showError === 'function') {
            window.authModule.showError(sanitizedMessage);
        } else {
            console.error('Error:', sanitizedMessage);
        }
    }

    // Métodos da API com validação

    async login(email, password, mfaToken) {
        // Validação rigorosa
        const validation = this.validateLoginInput(email, password, mfaToken);
        if (!validation.valid) {
            throw new Error(validation.message);
        }

        const sanitizedEmail = this.sanitizeString(email.trim().toLowerCase());
        const sanitizedMfaToken = this.sanitizeString(mfaToken.trim());
        
        const response = await this.request('/auth', {
            method: 'POST',
            body: JSON.stringify({ 
                email: sanitizedEmail, 
                password: password, // Não sanitizar senha
                mfaToken: sanitizedMfaToken 
            }),
            skipAuth: true
        });

        if (response.success && response.token) {
            this.token = response.token;
            localStorage.setItem('authToken', this.token);
            localStorage.setItem('userEmail', response.user.email);
            localStorage.setItem('loginTimestamp', Date.now().toString());
            
            console.log('Login realizado com sucesso');
        }

        return response;
    }

    validateLoginInput(email, password, mfaToken) {
        if (!email || !email.trim()) {
            return { valid: false, message: 'Email é obrigatório' };
        }

        if (!password) {
            return { valid: false, message: 'Senha é obrigatória' };
        }

        if (!mfaToken || !mfaToken.trim()) {
            return { valid: false, message: 'Código MFA é obrigatório' };
        }

        // Validação de email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email.trim())) {
            return { valid: false, message: 'Email inválido' };
        }

        // Validação de MFA token
        const mfaRegex = /^\d{6}$/;
        if (!mfaRegex.test(mfaToken.trim()) && mfaToken.trim() !== '123456') {
            return { valid: false, message: 'Código MFA deve ter 6 dígitos' };
        }

        return { valid: true };
    }

    async getUploadUrl(fileName, fileType, fileSize, folderPath = '') {
        // Validação de arquivo
        const validation = this.validateFileInput(fileName, fileSize);
        if (!validation.valid) {
            throw new Error(validation.message);
        }

        return await this.request('/videos', {
            method: 'POST',
            body: JSON.stringify({ 
                fileName: this.sanitizeString(fileName.trim()), 
                fileType: this.sanitizeString(fileType || 'video/mp4'), 
                fileSize: parseInt(fileSize), 
                folderPath: this.sanitizeString(folderPath.trim())
            })
        });
    }

    validateFileInput(fileName, fileSize) {
        if (!fileName || !fileName.trim()) {
            return { valid: false, message: 'Nome do arquivo é obrigatório' };
        }

        if (!fileSize || fileSize <= 0) {
            return { valid: false, message: 'Tamanho do arquivo inválido' };
        }

        // Validação de extensão
        const allowedExtensions = ['.mp4', '.ts', '.webm', '.avi', '.mov', '.mkv'];
        const fileExt = '.' + fileName.toLowerCase().split('.').pop();
        
        if (!allowedExtensions.includes(fileExt)) {
            return { valid: false, message: 'Tipo de arquivo não permitido' };
        }

        // Validação de tamanho (5GB máximo)
        const maxSize = 5 * 1024 * 1024 * 1024;
        if (fileSize > maxSize) {
            return { valid: false, message: 'Arquivo muito grande (máximo 5GB)' };
        }

        return { valid: true };
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

        // Verifica expiração (24 horas)
        const now = Date.now();
        const loginTime = parseInt(loginTimestamp);
        const tokenAge = now - loginTime;
        const maxAge = 24 * 60 * 60 * 1000;

        if (tokenAge > maxAge) {
            this.logout();
            return false;
        }

        return true;
    }
}

// Rate Limiter
class RateLimiter {
    constructor(maxRequests, windowMs) {
        this.maxRequests = maxRequests;
        this.windowMs = windowMs;
        this.requests = [];
    }

    canMakeRequest() {
        const now = Date.now();
        
        // Remove requisições antigas
        this.requests = this.requests.filter(time => now - time < this.windowMs);
        
        // Verifica limite
        if (this.requests.length >= this.maxRequests) {
            return false;
        }
        
        // Adiciona nova requisição
        this.requests.push(now);
        return true;
    }
}