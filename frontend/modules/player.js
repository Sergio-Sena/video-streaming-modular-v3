/**
 * Módulo do Player de Vídeo
 * Gerencia reprodução de vídeos em modal
 */
class PlayerModule {
    constructor() {
        this.modal = null;
        this.video = null;
        this.init();
    }

    init() {
        // Criar modal se não existir
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
        // Verificar se modal já existe
        if (document.getElementById('videoModal')) {
            this.modal = document.getElementById('videoModal');
            return;
        }

        // Criar modal dinamicamente
        this.modal = document.createElement('div');
        this.modal.id = 'videoModal';
        this.modal.className = 'modal';
        this.modal.style.display = 'none';
        document.body.appendChild(this.modal);
    }

    play(videoUrl, videoName) {
        // Verifica se URL é válida
        if (!videoUrl || videoUrl === 'undefined') {
            console.error('URL do vídeo inválida:', videoUrl);
            alert('Erro: URL do vídeo não encontrada');
            return;
        }
        
        // Corrige URL para CloudFront
        if (videoUrl.includes('videos.sstechnologies-cloud.com')) {
            videoUrl = videoUrl.replace('videos.sstechnologies-cloud.com', 'd2we88koy23cl4.cloudfront.net');
        }
        
        // Garante que a URL está correta
        if (!videoUrl.startsWith('http')) {
            videoUrl = `https://d2we88koy23cl4.cloudfront.net/${videoUrl}`;
        }
        
        console.log('🎬 URL final do vídeo:', videoUrl);
        
        console.log('Iniciando player para:', videoName, 'URL:', videoUrl);
        
        this.modal.innerHTML = `
            <div class="modal-content" id="modalContent">
                <button class="close-btn" onclick="window.playerModule.close()">×</button>
                <div class="video-container">
                    <video id="videoPlayer" 
                           class="video-js vjs-default-skin" 
                           controls 
                           preload="auto" 
                           width="100%" 
                           height="100%" 
                           data-setup='{"fluid": true, "responsive": true}'
                           onloadedmetadata="window.playerModule.detectOrientation(this)"
                           style="object-fit: contain !important; object-position: center !important;">
                        <source src="${videoUrl}" type="video/mp4">
                        <p class="vjs-no-js">
                            Para ver este vídeo, ative o JavaScript e considere atualizar para um
                            <a href="https://videojs.com/html5-video-support/" target="_blank">
                                navegador que suporte HTML5 video
                            </a>.
                        </p>
                    </video>
                </div>
            </div>
        `;
        
        // Inicializa Video.js com HLS.js
        setTimeout(() => {
            if (typeof videojs !== 'undefined') {
                this.player = videojs('videoPlayer', {
                    fluid: true,
                    responsive: true,
                    playbackRates: [0.5, 1, 1.25, 1.5, 2],
                    controls: true,
                    preload: 'auto',
                    width: '100%',
                    height: '100%',
                    techOrder: ['html5'],
                    html5: {
                        vhs: {
                            overrideNative: true
                        },
                        nativeVideoTracks: false,
                        nativeAudioTracks: false
                    },
                    userActions: {
                        hotkeys: true
                    }
                });
                

                
                this.player.ready(() => {
                    console.log('Video.js player ready');
                    
                    // Forçar controles sempre visíveis
                    this.player.controls(true);
                    this.player.el().setAttribute('controls', 'controls');
                    
                    // Remover botão play após iniciar
                    this.player.on('play', () => {
                        const bigPlayButton = this.player.el().querySelector('.vjs-big-play-button');
                        if (bigPlayButton) {
                            bigPlayButton.style.display = 'none';
                        }
                    });
                    
                    // Forçar exibição da barra de controles SEMPRE
                    this.forceControlsInterval = setInterval(() => {
                        const playerEl = this.player.el();
                        const controlBar = playerEl?.querySelector('.vjs-control-bar');
                        
                        if (controlBar) {
                            controlBar.style.cssText = `
                                display: flex !important;
                                opacity: 1 !important;
                                visibility: visible !important;
                                transform: translateY(0) !important;
                                position: absolute !important;
                                bottom: 0 !important;
                                left: 0 !important;
                                right: 0 !important;
                                z-index: 2000 !important;
                                background: rgba(0, 0, 0, 0.8) !important;
                                pointer-events: auto !important;
                            `;
                        }
                        
                        if (playerEl) {
                            playerEl.classList.remove('vjs-user-inactive');
                            playerEl.classList.add('vjs-controls-enabled');
                            
                            const video = playerEl.querySelector('video');
                            if (video) {
                                video.setAttribute('controls', 'controls');
                                video.controls = true;
                            }
                        }
                    }, 300);
                    
                    this.setupVideoSource(videoUrl, videoName);
                });
                
                this.player.on('error', () => {
                    console.error('Video.js error:', this.player.error());
                    this.tryHLSFallback(videoUrl, videoName);
                });
            } else {
                console.log('Video.js não carregado, usando HTML5 padrão');
                this.setupHTMLVideoWithControls(videoUrl, videoName);
            }
        }, 500);
        
        this.modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    close() {
        this.modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        
        // Limpar interval de controles
        if (this.forceControlsInterval) {
            clearInterval(this.forceControlsInterval);
            this.forceControlsInterval = null;
        }
        
        // Limpa HLS.js se estiver ativo
        if (this.hls) {
            this.hls.destroy();
            this.hls = null;
        }
        
        if (this.player && typeof this.player.dispose === 'function') {
            this.player.dispose();
            this.player = null;
        } else if (this.video) {
            this.video.pause();
            this.video = null;
        }
    }

    toggleFullscreen() {
        if (this.video) {
            if (this.video.requestFullscreen) {
                this.video.requestFullscreen();
            } else if (this.video.webkitRequestFullscreen) {
                this.video.webkitRequestFullscreen();
            } else if (this.video.msRequestFullscreen) {
                this.video.msRequestFullscreen();
            }
        }
    }

    toggleFullscreen() {
        const vlcEmbed = document.getElementById('vlc');
        const video = document.getElementById('videoPlayer');
        
        if (vlcEmbed && vlcEmbed.playlist) {
            // VLC Plugin fullscreen
            try {
                vlcEmbed.video.toggleFullscreen();
            } catch (e) {
                console.log('VLC fullscreen não suportado');
            }
        } else if (video) {
            // HTML5 video fullscreen
            if (video.requestFullscreen) {
                video.requestFullscreen();
            } else if (video.webkitRequestFullscreen) {
                video.webkitRequestFullscreen();
            } else if (video.msRequestFullscreen) {
                video.msRequestFullscreen();
            }
        }
    }
    
    setupVideoSource(videoUrl, videoName) {
        const ext = videoName.toLowerCase().split('.').pop();
        
        if (ext === 'ts' || ext === 'm2ts' || ext === 'mts') {
            console.log('Arquivo TS detectado, tentando HLS.js');
            this.setupHLSPlayer(videoUrl, videoName);
        } else {
            console.log('Arquivo padrão, usando Video.js normal');
            this.player.src({
                src: videoUrl,
                type: this.getVideoMimeType(videoName)
            });
        }
    }
    
    setupHLSPlayer(videoUrl, videoName) {
        // Para arquivos .ts individuais, tentar reprodução direta primeiro
        console.log('Arquivo .ts detectado, tentando reprodução direta');
        
        // Verifica se é um arquivo .m3u8 (playlist HLS) ou .ts individual
        if (videoUrl.includes('.m3u8')) {
            console.log('Arquivo .m3u8 detectado, usando HLS.js');
            this.initializeHLS(videoUrl);
        } else {
            console.log('Arquivo .ts individual, tentando como MP4');
            this.tryDirectPlay(videoUrl, videoName);
        }
    }
    
    initializeHLS(videoUrl) {
        if (typeof Hls !== 'undefined' && Hls.isSupported()) {
            const hls = new Hls({
                enableWorker: true,
                lowLatencyMode: false,
                backBufferLength: 90
            });
            
            hls.loadSource(videoUrl);
            hls.attachMedia(this.player.tech().el());
            
            hls.on(Hls.Events.MANIFEST_PARSED, () => {
                console.log('HLS manifest parsed, iniciando reprodução');
                this.player.play();
            });
            
            hls.on(Hls.Events.ERROR, (event, data) => {
                console.error('HLS Error:', data);
                if (data.fatal) {
                    console.log('Erro fatal HLS, tentando fallback');
                    this.tryDirectPlay(videoUrl.replace('.m3u8', '.ts'));
                }
            });
            
            this.hls = hls;
        } else {
            console.log('HLS.js não suportado');
            this.tryDirectPlay(videoUrl.replace('.m3u8', '.ts'));
        }
    }
    
    tryDirectPlay(videoUrl, videoName) {
        console.log('Tentando reprodução direta como MP4');
        
        if (this.player && typeof this.player.src === 'function') {
            // Força tipo MP4 para arquivos .ts
            const mimeType = videoName.toLowerCase().endsWith('.ts') ? 'video/mp4' : this.getVideoMimeType(videoName);
            this.player.src({
                src: videoUrl,
                type: mimeType
            });
            
            // Adiciona listeners para debug
            this.player.on('error', () => {
                console.error('Video.js direct play error:', this.player.error());
                console.log('Tentando fallback HTML5');
                this.setupHTMLVideo(videoUrl, videoName);
            });
        } else {
            console.log('Player não disponível, usando HTML5');
            this.setupHTMLVideo(videoUrl, videoName);
        }
    }
    
    tryHLSFallback(videoUrl, videoName) {
        const ext = videoName.toLowerCase().split('.').pop();
        if (ext === 'ts' || ext === 'm2ts' || ext === 'mts') {
            console.log('Erro no Video.js, tentando HLS direto');
            this.setupHTMLVideo(videoUrl, videoName);
        }
    }
    
    setupHTMLVideo(videoUrl, videoName) {
        console.log('🎬 Configurando HTML5 video:', videoUrl);
        this.setupHTMLVideoWithControls(videoUrl, videoName);
    }
    
    setupHTMLVideoWithControls(videoUrl, videoName) {
        console.log('🎬 Configurando HTML5 video com controles:', videoUrl);
        
        // Remove Video.js e cria elemento HTML5 com controles completos
        const container = document.querySelector('.video-container');
        if (container) {
            container.innerHTML = `
                <div class="html5-player-wrapper">
                    <video id="videoPlayerHTML5" 
                           controls 
                           controlsList="nodownload"
                           preload="auto" 
                           width="100%" 
                           height="100%"
                           style="background: #000; outline: none; object-fit: contain !important; object-position: center !important;"
                           crossorigin="anonymous"
                           onloadedmetadata="window.playerModule.detectOrientation(this)">
                        <source src="${videoUrl}" type="video/mp4">
                        <p>Seu navegador não suporta o elemento video.</p>
                    </video>
                    <div class="custom-controls">
                        <button onclick="window.playerModule.toggleFullscreen()" class="fullscreen-btn">
                            🔲 Tela Cheia
                        </button>
                        <button onclick="window.playerModule.changeSpeed(0.5)" class="speed-btn">0.5x</button>
                        <button onclick="window.playerModule.changeSpeed(1)" class="speed-btn">1x</button>
                        <button onclick="window.playerModule.changeSpeed(1.5)" class="speed-btn">1.5x</button>
                        <button onclick="window.playerModule.changeSpeed(2)" class="speed-btn">2x</button>
                    </div>
                </div>
            `;
            
            const video = document.getElementById('videoPlayerHTML5');
            this.video = video;
            
            if (video) {
                // Forçar controles nativos SEMPRE visíveis
                video.controls = true;
                video.setAttribute('controls', 'controls');
                
                // Garantir que controles nunca desapareçam
                video.addEventListener('mouseleave', () => {
                    video.controls = true;
                });
                
                video.addEventListener('click', () => {
                    video.controls = true;
                });
                
                video.addEventListener('loadstart', () => console.log('✅ HTML5: Carregamento iniciado'));
                video.addEventListener('canplay', () => console.log('✅ HTML5: Pode reproduzir'));
                video.addEventListener('error', (e) => {
                    console.error('❌ HTML5 Error:', e);
                    console.error('Video error details:', video.error);
                    
                    // Tenta URL direta do S3 como fallback
                    const s3Url = videoUrl.replace('d2we88koy23cl4.cloudfront.net', 'video-streaming-sstech-eaddf6a1.s3.amazonaws.com');
                    console.log('🔄 Tentando URL S3 direta:', s3Url);
                    video.src = s3Url;
                    video.load();
                });
                
                video.load();
            }
        }
    }
    
    changeSpeed(rate) {
        if (this.video) {
            this.video.playbackRate = rate;
            console.log(`Velocidade alterada para: ${rate}x`);
        } else if (this.player && this.player.playbackRate) {
            this.player.playbackRate(rate);
        }
    }
    
    detectOrientation(videoElement) {
        const modalContent = document.getElementById('modalContent');
        if (videoElement && modalContent) {
            const width = videoElement.videoWidth;
            const height = videoElement.videoHeight;
            
            console.log(`📐 Dimensões do vídeo: ${width}x${height}`);
            
            if (height > width) {
                console.log('📱 Vídeo vertical detectado');
                modalContent.classList.add('vertical-video');
            } else {
                console.log('📺 Vídeo horizontal detectado');
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
            'wmv': 'video/x-ms-wmv',
            'flv': 'video/x-flv',
            'webm': 'video/webm',
            'mkv': 'video/x-matroska',
            'm4v': 'video/x-m4v',
            '3gp': 'video/3gpp',
            'vob': 'video/dvd',
            'ogv': 'video/ogg',
            'ts': 'video/mp2t',
            'm2ts': 'video/mp2t',
            'mts': 'video/mp2t'
        };
        return mimeTypes[ext] || 'video/mp4';
    }

    testUrl(url) {
        console.log('Testando URL:', url);
        fetch(url, { method: 'HEAD' })
            .then(response => {
                console.log('Status:', response.status);
                console.log('Headers:', [...response.headers.entries()]);
                if (response.ok) {
                    alert(`URL OK! Status: ${response.status}`);
                } else {
                    alert(`Erro na URL! Status: ${response.status}`);
                }
            })
            .catch(error => {
                console.error('Erro ao testar URL:', error);
                alert(`Erro de rede: ${error.message}`);
            });
    }
    
    downloadVideo(url, name) {
        const a = document.createElement('a');
        a.href = url;
        a.download = name;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
}