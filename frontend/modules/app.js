/**
 * Aplicação Principal Modular
 * Inicializa e coordena todos os módulos
 */
class VideoStreamingApp {
    constructor() {
        this.initModules();
        this.init();
    }

    initModules() {
        // Inicializar módulos na ordem correta
        window.api = new APIModule();
        window.authModule = new AuthModule();
        window.videosModule = new VideosModule();
        window.playerModule = new PlayerModule();
    }

    init() {
        // Verificar autenticação inicial
        window.authModule.checkAuth();
        
        // Carregar credenciais lembradas
        this.loadRememberedCredentials();
    }

    loadRememberedCredentials() {
        const rememberedEmail = localStorage.getItem('rememberedEmail');
        const rememberedPassword = localStorage.getItem('rememberedPassword');
        
        if (rememberedEmail && rememberedPassword) {
            document.getElementById('email').value = rememberedEmail;
            document.getElementById('password').value = rememberedPassword;
            document.getElementById('rememberMe').checked = true;
        }
    }
}

// Inicializar aplicação quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.app = new VideoStreamingApp();
});