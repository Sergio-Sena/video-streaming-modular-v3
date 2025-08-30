/**
 * Player Module - Versão com Controles SEMPRE Visíveis
 * Solução definitiva para controles que somem
 */
class PlayerModuleFixed {
    constructor() {
        this.modal = null;
        this.video = null;
        this.player = null;
        this.controlsInterval = null;
        this.init();
    }

    init() {
        this.createModal();
        
        // Close modal events
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
        
        console.log('🎬 Iniciando player com controles fixos:', videoName);
        
        this.modal.innerHTML = `
            <div class="modal-content" id="modalContent">
                <button class="close-btn" onclick="window.playerModule.close()">×</button>
                <div class="video-container">
                    <video id="videoPlayer" 
                           class="video-js vjs-default-skin vjs-controls-enabled" 
                           controls 
                           preload="auto" 
                           width="100%" 
                           height="100%" 
                           data-setup='{"fluid": true, "responsive": true, "userActions": {"hotkeys": true}}'
                           onloadedmetadata="window.playerModule.detectOrientation(this)"
                           style="object-fit: contain !important;">
                        <source src="${videoUrl}" type="video/mp4">
                        <p>Seu navegador não suporta reprodução de vídeo.</p>
                    </video>
                </div>
            </div>
        `;
        
        // Inicializa Video.js com configuração anti-hide
        setTimeout(() => {
            if (typeof videojs !== 'undefined') {
                this.player = videojs('videoPlayer', {
                    fluid: true,
                    responsive: true,
                    controls: true,
                    preload: 'auto',
                    playbackRates: [0.5, 1, 1.25, 1.5, 2],
                    // CONFIGURAÇÕES ANTI-HIDE
                    inactivityTimeout: 0,  // Nunca esconder por inatividade
                    userActions: {
                        hotkeys: true,
                        click: false,  // Desabilita hide no clique
                        doubleClick: false
                    }
                });
                
                this.player.ready(() => {
                    console.log('✅ Video.js inicializado com controles fixos');
                    
                    // MÉTODO 1: Desabilitar comportamento de hide
                    this.player.off('userinactive');
                    this.player.off('useractive');
                    
                    // MÉTODO 2: Forçar classe controls-enabled
                    const playerEl = this.player.el();
                    playerEl.classList.add('vjs-controls-enabled');
                    playerEl.classList.remove('vjs-user-inactive');
                    
                    // MÉTODO 3: CSS Override agressivo
                    this.injectControlsCSS();
                    
                    // MÉTODO 4: Interval de segurança (reduzido)
                    this.controlsInterval = setInterval(() => {
                        this.forceControlsVisible();
                    }, 1000);  // Reduzido para 1s
                    
                    // MÉTODO 5: Event listeners para manter controles
                    this.setupControlsEvents();
                    
                    this.setupVideoSource(videoUrl, videoName);
                });
                
            } else {
                console.log('Video.js não disponível, usando HTML5');
                this.setupHTMLVideo(videoUrl, videoName);
            }
        }, 500);
        
        this.modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    injectControlsCSS() {
        // Injeta CSS ultra-agressivo para manter controles
        const style = document.createElement('style');
        style.id = 'force-controls-css';
        style.textContent = `
            /* FORÇAR CONTROLES SEMPRE VISÍVEIS */
            .video-js .vjs-control-bar {
                display: flex !important;
                opacity: 1 !important;
                visibility: visible !important;
                transform: translateY(0) !important;
                transition: none !important;
                position: absolute !important;
                bottom: 0 !important;
                left: 0 !important;
                right: 0 !important;
                background: rgba(0, 0, 0, 0.8) !important;
                z-index: 2000 !important;
                pointer-events: auto !important;
            }
            
            /* Sobrescrever TODOS os estados */
            .video-js:not(.vjs-user-inactive) .vjs-control-bar,
            .video-js.vjs-user-inactive .vjs-control-bar,
            .video-js.vjs-has-started .vjs-control-bar,
            .video-js.vjs-paused .vjs-control-bar,
            .video-js.vjs-playing .vjs-control-bar {
                display: flex !important;
                opacity: 1 !important;
                visibility: visible !important;
                transform: translateY(0) !important;
            }
            
            /* Garantir que botões sejam visíveis */
            .video-js .vjs-control-bar .vjs-button,
            .video-js .vjs-control-bar .vjs-time-control,
            .video-js .vjs-control-bar .vjs-progress-control {
                display: block !important;
                opacity: 1 !important;
            }
        `;
        document.head.appendChild(style);
    }

    forceControlsVisible() {
        if (!this.player) return;
        
        const playerEl = this.player.el();
        if (playerEl) {
            // Remove classe que esconde controles
            playerEl.classList.remove('vjs-user-inactive');
            playerEl.classList.add('vjs-controls-enabled');
            
            // Força controles visíveis
            const controlBar = playerEl.querySelector('.vjs-control-bar');
            if (controlBar) {
                controlBar.style.cssText = `
                    display: flex !important;
                    opacity: 1 !important;
                    visibility: visible !important;
                    transform: translateY(0) !important;
                    position: absolute !important;
                    bottom: 0 !important;
                    background: rgba(0, 0, 0, 0.8) !important;
                    z-index: 2000 !important;
                `;
            }
        }
    }

    setupControlsEvents() {
        if (!this.player) return;
        
        // Intercepta eventos que escondem controles
        this.player.on('userinactive', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('🚫 Bloqueado evento userinactive');
            return false;
        });
        
        // Força controles em todos os eventos
        ['play', 'pause', 'seeking', 'seeked', 'timeupdate'].forEach(event => {
            this.player.on(event, () => {
                this.forceControlsVisible();
            });
        });
    }

    setupVideoSource(videoUrl, videoName) {
        const ext = videoName.toLowerCase().split('.').pop();
        
        if (ext === 'ts' || ext === 'm2ts' || ext === 'mts') {
            console.log('Arquivo TS detectado');
            this.setupHLSPlayer(videoUrl, videoName);
        } else {
            this.player.src({
                src: videoUrl,
                type: this.getVideoMimeType(videoName)
            });
        }
    }

    setupHLSPlayer(videoUrl, videoName) {
        if (typeof Hls !== 'undefined' && Hls.isSupported()) {
            const hls = new Hls();
            hls.loadSource(videoUrl);
            hls.attachMedia(this.player.tech().el());
            this.hls = hls;
        } else {
            this.player.src({
                src: videoUrl,
                type: 'video/mp4'
            });
        }
    }

    setupHTMLVideo(videoUrl, videoName) {
        const container = document.querySelector('.video-container');
        if (container) {
            container.innerHTML = `
                <video id="videoPlayerHTML5" 
                       controls 
                       preload="auto" 
                       width="100%" 
                       height="100%"
                       style="background: #000; object-fit: contain;"
                       onloadedmetadata="window.playerModule.detectOrientation(this)">
                    <source src="${videoUrl}" type="video/mp4">
                    <p>Seu navegador não suporta reprodução de vídeo.</p>
                </video>
            `;
            
            this.video = document.getElementById('videoPlayerHTML5');
            if (this.video) {
                this.video.controls = true;
                this.video.load();
            }
        }
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

    getVideoMimeType(filename) {
        const ext = filename.toLowerCase().split('.').pop();
        const mimeTypes = {
            'mp4': 'video/mp4',
            'avi': 'video/x-msvideo',
            'mov': 'video/quicktime',
            'webm': 'video/webm',
            'mkv': 'video/x-matroska',
            'ts': 'video/mp2t',
            'm2ts': 'video/mp2t',
            'mts': 'video/mp2t'
        };
        return mimeTypes[ext] || 'video/mp4';
    }

    close() {
        this.modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        
        // Limpar interval
        if (this.controlsInterval) {
            clearInterval(this.controlsInterval);
            this.controlsInterval = null;
        }
        
        // Remover CSS injetado
        const injectedCSS = document.getElementById('force-controls-css');
        if (injectedCSS) {
            injectedCSS.remove();
        }
        
        // Limpar HLS
        if (this.hls) {
            this.hls.destroy();
            this.hls = null;
        }
        
        // Limpar Video.js
        if (this.player && typeof this.player.dispose === 'function') {
            this.player.dispose();
            this.player = null;
        } else if (this.video) {
            this.video.pause();
            this.video = null;
        }
    }

    toggleFullscreen() {
        if (this.player && this.player.isFullscreen) {
            if (this.player.isFullscreen()) {
                this.player.exitFullscreen();
            } else {
                this.player.requestFullscreen();
            }
        } else if (this.video) {
            if (this.video.requestFullscreen) {
                this.video.requestFullscreen();
            }
        }
    }
}