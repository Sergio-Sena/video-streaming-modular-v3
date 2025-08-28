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
        
        // Registrar service worker
        this.registerServiceWorker();
        
        // Inicializar touch handler
        if (window.TouchHandler) {
            window.touchHandler = new window.TouchHandler();
        }
    }

    registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => console.log('SW registered:', registration))
                .catch(error => console.log('SW registration failed:', error));
        }
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