/**
 * Módulo de Autenticação
 * Gerencia login, MFA e sessões de usuário
 */
class AuthModule {
    constructor() {
        this.currentScreen = 'login';
        this.initEventListeners();
    }

    initEventListeners() {
        // Login form
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        // MFA setup
        document.getElementById('registerBtn').addEventListener('click', () => {
            this.setupMFA();
        });

        // MFA verification
        document.getElementById('verifyMfaForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.verifyMFA();
        });

        // Back to login
        document.getElementById('backToLogin').addEventListener('click', () => {
            this.showScreen('login');
        });

        // Logout
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.logout();
        });
    }

    async handleLogin() {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const mfaToken = document.getElementById('mfaToken').value;
        const errorDiv = document.getElementById('errorMessage');
        const loginBtn = document.querySelector('.login-btn');

        this.setLoading(loginBtn, true);
        errorDiv.textContent = '';

        try {
            const response = await window.api.login(email, password, mfaToken);
            
            if (response.success) {
                errorDiv.textContent = '';
                errorDiv.style.display = 'none';
                
                document.getElementById('userEmail').textContent = email;
                
                if (document.getElementById('rememberMe').checked) {
                    localStorage.setItem('rememberedEmail', email);
                    localStorage.setItem('rememberedPassword', password);
                }
                
                this.showSuccessMessage('✓ Login realizado com sucesso!');
                this.showToast('Bem-vindo ao Video Streaming SStech!', 'success');
                
                this.showScreen('main');
                window.videosModule.loadVideos();
                
            } else {
                this.showError(response.message || 'Credenciais inválidas');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showError(this.getErrorMessage(error));
        } finally {
            this.setLoading(loginBtn, false);
        }
    }

    async setupMFA() {
        try {
            const response = await window.api.setupMFA();
            
            if (response.success) {
                document.getElementById('manualKey').textContent = response.manualKey;
                
                const qrContainer = document.getElementById('qrContainer');
                qrContainer.innerHTML = `<img src="${response.qrCode}" alt="QR Code">`;
                
                this.showScreen('mfaSetup');
                this.nextStep(2);
            }
        } catch (error) {
            alert('Erro ao configurar MFA: ' + error.message);
        }
    }

    async verifyMFA() {
        const mfaToken = document.getElementById('verifyToken').value;
        
        try {
            const response = await window.api.verifyMFA(mfaToken);
            
            if (response.success) {
                alert('MFA configurado com sucesso!');
                this.showScreen('login');
            } else {
                alert('Código inválido. Tente novamente.');
            }
        } catch (error) {
            alert('Erro na verificação: ' + error.message);
        }
    }

    checkAuth() {
        const token = localStorage.getItem('authToken');
        const email = localStorage.getItem('userEmail');
        
        if (token && email) {
            try {
                // Verifica se token não expirou
                const payload = JSON.parse(atob(token.split('.')[1]));
                const now = Math.floor(Date.now() / 1000);
                
                if (payload.exp > now) {
                    document.getElementById('userEmail').textContent = email;
                    this.showScreen('main');
                    window.videosModule.loadVideos();
                    return;
                }
            } catch (e) {
                console.log('Token inválido, fazendo logout');
                this.logout();
            }
        }
        this.showScreen('login');
    }

    logout() {
        window.api.logout();
        this.showScreen('login');
        document.getElementById('loginForm').reset();
        
        const errorDiv = document.getElementById('errorMessage');
        errorDiv.textContent = '';
        errorDiv.style.display = 'none';
    }

    showScreen(screenName) {
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        
        const targetScreen = document.getElementById(`${screenName}Screen`);
        if (targetScreen) {
            targetScreen.classList.add('active');
        }
        
        this.currentScreen = screenName;
        
        if (screenName === 'main') {
            document.body.scrollTop = 0;
            document.documentElement.scrollTop = 0;
        }
    }

    nextStep(step) {
        document.querySelectorAll('.setup-step').forEach(s => s.classList.add('hidden'));
        document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
        
        document.getElementById(`step${step}`).classList.remove('hidden');
        document.querySelector(`[data-step="${step}"]`).classList.add('active');
    }

    setLoading(button, loading) {
        const spinner = button.querySelector('.loading-spinner');
        const text = button.querySelector('span');
        
        if (loading) {
            button.disabled = true;
            spinner.style.display = 'block';
            text.style.opacity = '0.7';
        } else {
            button.disabled = false;
            spinner.style.display = 'none';
            text.style.opacity = '1';
        }
    }

    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        errorDiv.className = 'error-message show';
        errorDiv.style.backgroundColor = '#dc3545';
        errorDiv.style.color = 'white';
        errorDiv.style.padding = '10px';
        errorDiv.style.borderRadius = '5px';
        errorDiv.style.marginTop = '10px';
        
        setTimeout(() => {
            errorDiv.classList.remove('show');
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 300);
        }, 5000);
    }

    showSuccessMessage(message) {
        const errorDiv = document.getElementById('errorMessage');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        errorDiv.className = 'success-message show';
        errorDiv.style.backgroundColor = '#28a745';
        errorDiv.style.color = 'white';
        errorDiv.style.padding = '10px';
        errorDiv.style.borderRadius = '5px';
        errorDiv.style.marginTop = '10px';
        
        setTimeout(() => {
            errorDiv.classList.remove('show');
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 300);
        }, 2000);
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }

    getErrorMessage(error) {
        if (error.message.includes('conexão')) {
            return 'Erro de conexão. Verifique se o servidor está rodando.';
        } else if (error.message.includes('CORS')) {
            return 'Erro de CORS. Verifique a configuração do servidor.';
        } else if (error.message.includes('Credenciais inválidas')) {
            return 'Email ou senha incorretos.';
        } else if (error.message.includes('MFA')) {
            return 'Código MFA inválido. Verifique o Google Authenticator.';
        } else if (error.message.includes('Failed to fetch')) {
            return 'Servidor não encontrado.';
        }
        return error.message || 'Erro desconhecido. Tente novamente.';
    }
}