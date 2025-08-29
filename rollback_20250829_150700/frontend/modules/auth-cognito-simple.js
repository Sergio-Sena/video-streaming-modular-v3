/**
 * Módulo de Autenticação com Amazon Cognito - Versão Simplificada
 */
class AuthCognitoModule {
    constructor() {
        this.currentScreen = 'login';
        this.cognitoConfig = {
            userPoolId: 'us-east-1_FpDtOqzEa',
            clientId: '6in4ghmp6k6vl09556a52ug7qj'
        };
        this.initEventListeners();
    }

    initEventListeners() {
        // Login form
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        // Logout
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.logout();
        });
    }

    async handleLogin() {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('errorMessage');
        const loginBtn = document.querySelector('.login-btn');

        this.setLoading(loginBtn, true);
        errorDiv.textContent = '';

        try {
            // Usar AWS SDK diretamente (mais simples que amazon-cognito-identity-js)
            const response = await this.cognitoLogin(email, password);
            
            if (response.success) {
                localStorage.setItem('authToken', response.token);
                localStorage.setItem('userEmail', email);
                
                document.getElementById('userEmail').textContent = email;
                this.showSuccessMessage('✓ Login realizado com sucesso!');
                this.showScreen('main');
                window.videosModule.loadVideos();
            } else {
                this.showError(response.message || 'Credenciais inválidas');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showError('Erro de conexão com Cognito');
        } finally {
            this.setLoading(loginBtn, false);
        }
    }

    async cognitoLogin(email, password) {
        // Simulação - será substituído por integração real
        // Por enquanto, usar credenciais fixas para teste
        if (email === 'sergiosenaadmin@sstech' && password === 'sergiosena') {
            return {
                success: true,
                token: 'cognito-jwt-token-placeholder'
            };
        }
        return { success: false, message: 'Credenciais inválidas' };
    }

    checkAuth() {
        const token = localStorage.getItem('authToken');
        const email = localStorage.getItem('userEmail');
        
        if (token && email) {
            document.getElementById('userEmail').textContent = email;
            this.showScreen('main');
            window.videosModule.loadVideos();
            return;
        }
        this.showScreen('login');
    }

    logout() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('userEmail');
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
    }

    setLoading(button, loading) {
        const spinner = button.querySelector('.loading-spinner');
        const text = button.querySelector('span');
        
        if (loading) {
            button.disabled = true;
            if (spinner) spinner.style.display = 'block';
            if (text) text.style.opacity = '0.7';
        } else {
            button.disabled = false;
            if (spinner) spinner.style.display = 'none';
            if (text) text.style.opacity = '1';
        }
    }

    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        errorDiv.style.backgroundColor = '#dc3545';
        errorDiv.style.color = 'white';
        errorDiv.style.padding = '10px';
        errorDiv.style.borderRadius = '5px';
        errorDiv.style.marginTop = '10px';
        
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }

    showSuccessMessage(message) {
        const errorDiv = document.getElementById('errorMessage');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        errorDiv.style.backgroundColor = '#28a745';
        errorDiv.style.color = 'white';
        errorDiv.style.padding = '10px';
        errorDiv.style.borderRadius = '5px';
        errorDiv.style.marginTop = '10px';
        
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 2000);
    }
}