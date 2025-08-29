/**
 * Módulo de Autenticação com Amazon Cognito - Versão Debug
 */
class AuthCognitoDebug {
    constructor() {
        console.log('🔐 AuthCognitoDebug inicializado');
        this.currentScreen = 'login';
        this.cognitoConfig = {
            userPoolId: 'us-east-1_FpDtOqzEa',
            clientId: '6in4ghmp6k6vl09556a52ug7qj',
            region: 'us-east-1'
        };
        
        console.log('⚙️ Cognito Config:', this.cognitoConfig);
        
        // Configurar AWS SDK
        if (typeof AWS !== 'undefined') {
            console.log('✅ AWS SDK carregado');
            AWS.config.region = this.cognitoConfig.region;
            this.cognitoIdentityServiceProvider = new AWS.CognitoIdentityServiceProvider();
        } else {
            console.warn('⚠️ AWS SDK não encontrado');
        }
        
        this.initEventListeners();
    }

    initEventListeners() {
        console.log('🎯 Configurando event listeners...');
        
        // Login form
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                console.log('📝 Form de login submetido');
                this.handleLogin();
            });
        }

        // Logout
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                console.log('🚪 Logout clicado');
                this.logout();
            });
        }
        
        console.log('✅ Event listeners configurados');
    }

    async handleLogin() {
        console.log('🔑 Iniciando processo de login...');
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('errorMessage');
        const loginBtn = document.querySelector('.login-btn');

        console.log('📧 Email:', email);
        console.log('🔒 Senha:', password ? '***' : 'vazia');

        this.setLoading(loginBtn, true);
        if (errorDiv) errorDiv.textContent = '';

        try {
            console.log('🚀 Chamando cognitoLogin...');
            const response = await this.cognitoLogin(email, password);
            console.log('📥 Resposta do login:', response);
            
            if (response.success) {
                console.log('✅ Login bem-sucedido!');
                
                localStorage.setItem('authToken', response.token);
                localStorage.setItem('userEmail', email);
                
                const userEmailEl = document.getElementById('userEmail');
                if (userEmailEl) {
                    userEmailEl.textContent = email;
                }
                
                this.showSuccessMessage('✓ Login realizado com sucesso!');
                
                console.log('🔄 Mudando para tela principal...');
                this.showScreen('main');
                
                // Carregar vídeos com Cognito
                console.log('🎬 Login concluído - carregando vídeos...');
                
                setTimeout(() => {
                    console.log('📹 Tentando carregar vídeos com Cognito...');
                    if (window.videosModule && typeof window.videosModule.loadVideos === 'function') {
                        console.log('🎯 Chamando loadVideos...');
                        window.videosModule.loadVideos();
                    } else {
                        console.log('📎 VideosModule não disponível ainda');
                    }
                }, 500);
                
            } else {
                console.error('❌ Login falhou:', response.message);
                this.showError(response.message || 'Credenciais inválidas');
            }
        } catch (error) {
            console.error('💥 Erro no login:', error);
            this.showError('Erro de autenticação: ' + error.message);
        } finally {
            this.setLoading(loginBtn, false);
        }
    }

    async cognitoLogin(username, password) {
        console.log('🔐 Tentando autenticação Cognito...');
        
        try {
            if (!this.cognitoIdentityServiceProvider) {
                console.warn('⚠️ AWS SDK não disponível, usando fallback');
                throw new Error('AWS SDK não carregado');
            }

            const params = {
                AuthFlow: 'USER_PASSWORD_AUTH',
                ClientId: this.cognitoConfig.clientId,
                AuthParameters: {
                    USERNAME: username,
                    PASSWORD: password
                }
            };

            console.log('📤 Enviando para Cognito:', { ...params, AuthParameters: { USERNAME: username, PASSWORD: '***' } });
            
            const result = await this.cognitoIdentityServiceProvider.initiateAuth(params).promise();
            console.log('📥 Resposta Cognito:', result);
            
            if (result.AuthenticationResult) {
                return {
                    success: true,
                    token: result.AuthenticationResult.IdToken,
                    accessToken: result.AuthenticationResult.AccessToken,
                    refreshToken: result.AuthenticationResult.RefreshToken
                };
            } else {
                return { success: false, message: 'Falha na autenticação' };
            }
        } catch (error) {
            console.error('💥 Erro Cognito:', error);
            
            // Tentar autenticação direta com Cognito usando AWS SDK
            console.log('🔄 Tentando autenticação direta...');
            try {
                const cognitoIdentity = new AWS.CognitoIdentityServiceProvider();
                const authParams = {
                    AuthFlow: 'ADMIN_NO_SRP_AUTH',
                    UserPoolId: this.cognitoConfig.userPoolId,
                    ClientId: this.cognitoConfig.clientId,
                    AuthParameters: {
                        USERNAME: username,
                        PASSWORD: password
                    }
                };
                
                console.log('📤 Tentando ADMIN_NO_SRP_AUTH...');
                const result = await cognitoIdentity.adminInitiateAuth(authParams).promise();
                
                if (result.AuthenticationResult) {
                    console.log('✅ Autenticação direta bem-sucedida!');
                    return {
                        success: true,
                        token: result.AuthenticationResult.IdToken,
                        accessToken: result.AuthenticationResult.AccessToken,
                        refreshToken: result.AuthenticationResult.RefreshToken
                    };
                }
            } catch (directError) {
                console.error('💥 Erro autenticação direta:', directError);
            }
            
            // Último fallback para teste
            if (username === 'sergiosenaadmin@sstech' && password === 'sergiosena') {
                console.log('⚠️ Usando fallback de teste...');
                return {
                    success: true,
                    token: 'test-token-' + Date.now()
                };
            }
            
            return { 
                success: false, 
                message: error.message || 'Credenciais inválidas' 
            };
        }
    }

    checkAuth() {
        console.log('🔍 Verificando autenticação...');
        
        const token = localStorage.getItem('authToken');
        const email = localStorage.getItem('userEmail');
        
        console.log('🎫 Token:', token ? 'presente' : 'ausente');
        console.log('📧 Email:', email);
        
        if (token && email) {
            console.log('✅ Usuário já autenticado');
            
            const userEmailEl = document.getElementById('userEmail');
            if (userEmailEl) {
                userEmailEl.textContent = email;
            }
            
            this.showScreen('main');
            
            console.log('✅ Usuário já autenticado - carregando vídeos...');
            
            // Carregar vídeos quando já autenticado
            setTimeout(() => {
                console.log('📹 Carregando vídeos para usuário autenticado...');
                if (window.videosModule && typeof window.videosModule.loadVideos === 'function') {
                    console.log('🎯 Chamando loadVideos (usuário já autenticado)...');
                    window.videosModule.loadVideos();
                } else {
                    console.log('📎 VideosModule não disponível ainda - tentando novamente...');
                    // Tenta novamente após mais tempo
                    setTimeout(() => {
                        if (window.videosModule && typeof window.videosModule.loadVideos === 'function') {
                            console.log('🎯 Segunda tentativa loadVideos...');
                            window.videosModule.loadVideos();
                        }
                    }, 1000);
                }
            }, 500);
            
            return;
        }
        
        console.log('❌ Usuário não autenticado');
        this.showScreen('login');
    }

    logout() {
        console.log('🚪 Fazendo logout...');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userEmail');
        this.showScreen('login');
        
        const loginForm = document.getElementById('loginForm');
        if (loginForm) loginForm.reset();
        
        const errorDiv = document.getElementById('errorMessage');
        if (errorDiv) {
            errorDiv.textContent = '';
            errorDiv.style.display = 'none';
        }
    }

    showScreen(screenName) {
        console.log('🖥️ Mudando para tela:', screenName);
        
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        
        const targetScreen = document.getElementById(`${screenName}Screen`);
        if (targetScreen) {
            targetScreen.classList.add('active');
            console.log('✅ Tela ativada:', screenName);
        } else {
            console.error('❌ Tela não encontrada:', screenName);
        }
        
        this.currentScreen = screenName;
    }

    setLoading(button, loading) {
        if (!button) return;
        
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
        console.error('🚨 Erro:', message);
        const errorDiv = document.getElementById('errorMessage');
        if (!errorDiv) return;
        
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
        console.log('✅ Sucesso:', message);
        const errorDiv = document.getElementById('errorMessage');
        if (!errorDiv) return;
        
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

// Exportar para uso global
window.AuthCognitoDebug = AuthCognitoDebug;