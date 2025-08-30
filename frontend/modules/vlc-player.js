/**
 * VLC Web Player Module
 * Alternativa usando VLC.js para controles sempre visíveis
 */
class VLCPlayerModule {
    constructor() {
        this.modal = null;
        this.vlcPlayer = null;
        this.init();
    }

    init() {
        this.createModal();
        this.loadVLCScript();
        
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.close();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.close();
            }
        });
    }

    loadVLCScript() {
        // Carrega VLC.js se não estiver disponível
        if (typeof VLC === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/vlc-web-player@latest/dist/vlc.min.js';
            script.onload = () => {
                console.log('✅ VLC.js carregado');
            };
            script.onerror = () => {
                console.error('❌ Erro ao carregar VLC.js');
            };
            document.head.appendChild(script);
        }
    }

    createModal() {
        if (document.getElementById('videoModal')) {
            this.modal = document.getElementById('videoModal');
            return;
        }

        this.modal = document.createElement('div');
        this.modal.id = 'videoModal';
        this.modal.className = 'modal';
        this.modal.style.display = 'none';
        document.body.appendChild(this.modal);
    }

    play(videoUrl, videoName) {
        if (!videoUrl || videoUrl === 'undefined') {
            console.error('URL do vídeo inválida:', videoUrl);
            alert('Erro: URL do vídeo não encontrada');
            return;
        }
        
        // Corrige URL para CloudFront
        if (videoUrl.includes('videos.sstechnologies-cloud.com')) {
            videoUrl = videoUrl.replace('videos.sstechnologies-cloud.com', 'd2we88koy23cl4.cloudfront.net');
        }
        
        if (!videoUrl.startsWith('http')) {
            videoUrl = `https://d2we88koy23cl4.cloudfront.net/${videoUrl}`;
        }
        
        console.log('🎬 Iniciando VLC Player:', videoName);
        
        this.modal.innerHTML = `
            <div class="modal-content" id="modalContent">
                <button class="close-btn" onclick="window.playerModule.close()">×</button>
                <div class="video-container">
                    <div id="vlcContainer" style="width: 100%; height: 500px; background: #000;">
                        <!-- VLC Player será injetado aqui -->
                        <div class="vlc-loading">
                            <div class="loading-spinner-large"></div>
                            <p>Carregando VLC Player...</p>
                        </div>
                    </div>
                    
                    <!-- Fallback para HTML5 -->
                    <video id="fallbackPlayer" 
                           controls 
                           preload="auto" 
                           width="100%" 
                           height="100%"
                           style="display: none; background: #000; object-fit: contain;"
                           onloadedmetadata="window.playerModule.detectOrientation(this)">
                        <source src="${videoUrl}" type="video/mp4">
                    </video>
                </div>
                
                <div class="player-info">
                    <h3>${videoName}</h3>
                    <div class="player-controls">
                        <button onclick="window.playerModule.toggleFullscreen()" class="control-btn">
                            🔲 Tela Cheia
                        </button>
                        <button onclick="window.playerModule.changeSpeed(0.5)" class="control-btn">0.5x</button>
                        <button onclick="window.playerModule.changeSpeed(1)" class="control-btn">1x</button>
                        <button onclick="window.playerModule.changeSpeed(1.5)" class="control-btn">1.5x</button>
                        <button onclick="window.playerModule.changeSpeed(2)" class="control-btn">2x</button>
                    </div>
                </div>
            </div>
        `;
        
        // Tenta inicializar VLC, com fallback para HTML5
        setTimeout(() => {
            this.initializeVLC(videoUrl, videoName);
        }, 500);
        
        this.modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    initializeVLC(videoUrl, videoName) {
        try {
            // Método 1: VLC.js (se disponível)
            if (typeof VLC !== 'undefined') {
                console.log('🎯 Inicializando VLC.js');
                this.setupVLCJS(videoUrl, videoName);
            }
            // Método 2: VLC Plugin (se instalado)
            else if (this.detectVLCPlugin()) {
                console.log('🎯 Inicializando VLC Plugin');
                this.setupVLCPlugin(videoUrl, videoName);
            }
            // Método 3: Fallback HTML5
            else {
                console.log('🎯 VLC não disponível, usando HTML5');
                this.setupHTML5Fallback(videoUrl, videoName);
            }
        } catch (error) {
            console.error('❌ Erro ao inicializar VLC:', error);
            this.setupHTML5Fallback(videoUrl, videoName);
        }
    }

    setupVLCJS(videoUrl, videoName) {
        const container = document.getElementById('vlcContainer');
        
        try {
            this.vlcPlayer = new VLC.VideoPlayer({
                container: container,
                src: videoUrl,
                controls: true,
                autoplay: false,
                width: '100%',
                height: '100%'
            });
            
            this.vlcPlayer.on('ready', () => {
                console.log('✅ VLC.js player pronto');
                container.querySelector('.vlc-loading').style.display = 'none';
            });
            
            this.vlcPlayer.on('error', (error) => {
                console.error('❌ VLC.js error:', error);
                this.setupHTML5Fallback(videoUrl, videoName);
            });
            
        } catch (error) {
            console.error('❌ Erro VLC.js:', error);
            this.setupHTML5Fallback(videoUrl, videoName);
        }
    }

    setupVLCPlugin(videoUrl, videoName) {
        const container = document.getElementById('vlcContainer');
        
        container.innerHTML = `
            <embed type="application/x-vlc-plugin" 
                   pluginspage="http://www.videolan.org"
                   version="VideoLAN.VLCPlugin.2"
                   width="100%"
                   height="100%"
                   id="vlcEmbed"
                   src="${videoUrl}"
                   autoplay="false"
                   controls="true"
                   style="background: #000;">
        `;
        
        const vlcEmbed = document.getElementById('vlcEmbed');
        if (vlcEmbed && vlcEmbed.playlist) {
            console.log('✅ VLC Plugin inicializado');
            this.vlcPlayer = vlcEmbed;
        } else {
            console.log('❌ VLC Plugin não funcional');
            this.setupHTML5Fallback(videoUrl, videoName);
        }
    }

    setupHTML5Fallback(videoUrl, videoName) {
        console.log('🔄 Usando fallback HTML5');
        
        const container = document.getElementById('vlcContainer');
        const fallback = document.getElementById('fallbackPlayer');
        
        container.style.display = 'none';
        fallback.style.display = 'block';
        fallback.src = videoUrl;
        fallback.load();
        
        this.vlcPlayer = fallback;
    }

    detectVLCPlugin() {
        // Detecta se VLC plugin está instalado
        const plugins = navigator.plugins;
        for (let i = 0; i < plugins.length; i++) {
            if (plugins[i].name.toLowerCase().includes('vlc')) {
                return true;
            }
        }
        return false;
    }

    detectOrientation(videoElement) {
        const modalContent = document.getElementById('modalContent');
        if (videoElement && modalContent) {
            const width = videoElement.videoWidth;
            const height = videoElement.videoHeight;
            
            if (height > width) {
                modalContent.classList.add('vertical-video');
            } else {
                modalContent.classList.remove('vertical-video');
            }
        }
    }

    toggleFullscreen() {
        if (this.vlcPlayer) {
            try {
                // VLC Plugin
                if (this.vlcPlayer.video && this.vlcPlayer.video.toggleFullscreen) {
                    this.vlcPlayer.video.toggleFullscreen();
                }
                // VLC.js
                else if (this.vlcPlayer.requestFullscreen) {
                    this.vlcPlayer.requestFullscreen();
                }
                // HTML5 Fallback
                else if (this.vlcPlayer.requestFullscreen) {
                    this.vlcPlayer.requestFullscreen();
                }
            } catch (error) {
                console.error('Erro fullscreen:', error);
            }
        }
    }

    changeSpeed(rate) {
        if (this.vlcPlayer) {
            try {
                // VLC Plugin
                if (this.vlcPlayer.input && this.vlcPlayer.input.rate) {
                    this.vlcPlayer.input.rate = rate;
                }
                // HTML5 Fallback
                else if (this.vlcPlayer.playbackRate !== undefined) {
                    this.vlcPlayer.playbackRate = rate;
                }
                console.log(`Velocidade alterada para: ${rate}x`);
            } catch (error) {
                console.error('Erro ao alterar velocidade:', error);
            }
        }
    }

    close() {
        this.modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        
        // Limpar VLC Player
        if (this.vlcPlayer) {
            try {
                if (this.vlcPlayer.stop) {
                    this.vlcPlayer.stop();
                } else if (this.vlcPlayer.pause) {
                    this.vlcPlayer.pause();
                }
            } catch (error) {
                console.error('Erro ao parar player:', error);
            }
            this.vlcPlayer = null;
        }
    }
}