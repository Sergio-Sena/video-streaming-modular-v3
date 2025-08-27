/**
 * API de Teste Local - Simula 100% da funcionalidade AWS
 */
class APIModule {
    constructor() {
        this.isLocal = window.location.hostname === 'localhost';
        this.token = localStorage.getItem('authToken');
        this.videos = JSON.parse(localStorage.getItem('testVideos')) || [];
    }

    async login(email, password, mfaToken) {
        console.log('🧪 LOGIN LOCAL:', { email, password, mfaToken });
        
        // Simular delay de rede
        await this.delay(500);
        
        if (email === 'sergiosenaadmin@sstech' && password === 'sergiosena') {
            this.token = 'test-jwt-' + Date.now();
            localStorage.setItem('authToken', this.token);
            localStorage.setItem('userEmail', email);
            
            return {
                success: true,
                token: this.token,
                user: { email }
            };
        }
        
        return { success: false, message: 'Credenciais inválidas' };
    }

    async setupMFA() {
        console.log('🧪 SETUP MFA LOCAL');
        await this.delay(300);
        
        return {
            success: true,
            qrCode: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
            manualKey: 'JBSWY3DPEHPK3PXP'
        };
    }

    async verifyMFA(mfaToken) {
        console.log('🧪 VERIFY MFA LOCAL:', mfaToken);
        await this.delay(200);
        
        return { success: true, message: 'MFA configurado!' };
    }

    async getVideos() {
        console.log('🧪 GET VIDEOS LOCAL');
        await this.delay(400);
        
        return {
            success: true,
            videos: this.videos
        };
    }

    async getUploadUrl(fileName, fileType, fileSize) {
        console.log('🧪 GET UPLOAD URL LOCAL:', { fileName, fileType, fileSize });
        await this.delay(200);
        
        return {
            success: true,
            uploadUrl: 'fake-upload-url',
            key: `videos/${Date.now()}-${fileName}`,
            message: 'URL de upload gerada'
        };
    }

    async uploadToS3(uploadUrl, file, onProgress) {
        console.log('🧪 UPLOAD TO S3 LOCAL:', file.name);
        
        return new Promise((resolve) => {
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 30;
                if (progress > 100) progress = 100;
                
                if (onProgress) onProgress(progress);
                
                if (progress >= 100) {
                    clearInterval(interval);
                    
                    // Adicionar vídeo à lista local
                    const newVideo = {
                        key: `videos/${Date.now()}-${file.name}`,
                        name: file.name,
                        size: file.size,
                        lastModified: new Date().toISOString(),
                        url: URL.createObjectURL(file) // URL local para preview
                    };
                    
                    this.videos.push(newVideo);
                    localStorage.setItem('testVideos', JSON.stringify(this.videos));
                    
                    resolve({ success: true });
                }
            }, 100);
        });
    }

    async deleteVideo(videoKey) {
        console.log('🧪 DELETE VIDEO LOCAL:', videoKey);
        await this.delay(300);
        
        this.videos = this.videos.filter(video => video.key !== videoKey);
        localStorage.setItem('testVideos', JSON.stringify(this.videos));
        
        return { success: true, message: 'Vídeo deletado' };
    }

    logout() {
        console.log('🧪 LOGOUT LOCAL');
        this.token = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('userEmail');
    }

    isAuthenticated() {
        return !!this.token;
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}