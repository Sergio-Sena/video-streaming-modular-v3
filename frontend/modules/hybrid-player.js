/**
 * Hybrid Player Module - Solução Definitiva
 * Combina Video.js corrigido + VLC + HTML5 com controles sempre visíveis
 */
class HybridPlayerModule {
    constructor() {
        this.modal = null;
        this.currentPlayer = null;
        this.playerType = null;
        this.controlsInterval = null;
        this.init();
    }

    init() {
        this.createModal();
        
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
        
        console.log('🎬 Iniciando Hybrid Player:', videoName);
        
        this.modal.innerHTML = `
            <div class="modal-content" id="modalContent">
                <div class="modal-header">
                    <h3>${videoName}</h3>
                    <div class="player-selector">
                        <button class="player-btn active" data-player="videojs">Video.js</button>
                        <button class="player-btn" data-player="html5">HTML5</button>
                        <button class="player-btn" data-player="vlc">VLC</button>
                    </div>
                    <button class="close-btn" onclick="window.playerModule.close()">×</button>
                </div>
                
                <div class="video-container">
                    <!-- Video.js Player -->
                    <div id="videojsContainer" class="player-container active">
                        <video id="videoPlayer" 
                               class="video-js vjs-default-skin" 
                               controls 
                               preload="auto" 
                               width="100%" 
                               height="100%" 
                               data-setup='{"fluid": true, "responsive": true}'
                               onloadedmetadata="window.playerModule.detectOrientation(this)"
                               style="object-fit: contain !important;">
                            <source src="${videoUrl}" type="video/mp4">
                        </video>
                    </div>
                    
                    <!-- HTML5 Player -->
                    <div id="html5Container" class="player-container">
                        <video id="html5Player" 
                               controls 
                               preload="auto" 
                               width="100%" 
                               height="100%"
                               style="background: #000; object-fit: contain;"
                               onloadedmetadata="window.playerModule.detectOrientation(this)">
                            <source src="${videoUrl}" type="video/mp4">
                        </video>
                    </div>
                    
                    <!-- VLC Player -->
                    <div id="vlcContainer" class="player-container">
                        <div class="vlc-placeholder">
                            <div class="loading-spinner-large"></div>
                            <p>Carregando VLC Player...</p>
                            <small>Requer plugin VLC instalado</small>
                        </div>
                    </div>
                </div>
                
                <div class="player-controls">
                    <button onclick="window.playerModule.toggleFullscreen()" class="control-btn">
                        🔲 Tela Cheia
                    </button>
                    <button onclick="window.playerModule.changeSpeed(0.5)" class="control-btn">0.5x</button>
                    <button onclick="window.playerModule.changeSpeed(1)" class="control-btn active">1x</button>
                    <button onclick="window.playerModule.changeSpeed(1.5)" class="control-btn">1.5x</button>
                    <button onclick="window.playerModule.changeSpeed(2)" class="control-btn">2x</button>
                    <div class="player-status" id="playerStatus">Video.js Ativo</div>
                </div>
            </div>
        `;
        
        // Setup player selector
        this.setupPlayerSelector(videoUrl, videoName);
        
        // Inicializa com Video.js corrigido
        setTimeout(() => {
            this.initVideoJS(videoUrl, videoName);
        }, 500);
        
        this.modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    setupPlayerSelector(videoUrl, videoName) {
        const buttons = this.modal.querySelectorAll('.player-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                const playerType = btn.dataset.player;
                this.switchPlayer(playerType, videoUrl, videoName);
                
                // Update active button
                buttons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
    }

    switchPlayer(playerType, videoUrl, videoName) {
        console.log(`🔄 Mudando para player: ${playerType}`);
        
        // Parar player atual
        this.stopCurrentPlayer();
        
        // Esconder todos os containers
        const containers = this.modal.querySelectorAll('.player-container');
        containers.forEach(c => c.classList.remove('active'));
        
        // Mostrar container selecionado
        const targetContainer = document.getElementById(`${playerType}Container`);
        if (targetContainer) {
            targetContainer.classList.add('active');
        }
        
        // Inicializar novo player
        switch (playerType) {
            case 'videojs':
                this.initVideoJS(videoUrl, videoName);
                break;
            case 'html5':
                this.initHTML5(videoUrl, videoName);
                break;
            case 'vlc':
                this.initVLC(videoUrl, videoName);
                break;
        }
        
        this.playerType = playerType;
        document.getElementById('playerStatus').textContent = `${playerType.toUpperCase()} Ativo`;
    }

    initVideoJS(videoUrl, videoName) {
        if (typeof videojs === 'undefined') {
            console.error('Video.js não disponível');
            this.switchPlayer('html5', videoUrl, videoName);
            return;
        }
        
        this.currentPlayer = videojs('videoPlayer', {
            fluid: true,
            responsive: true,
            controls: true,
            preload: 'auto',
            playbackRates: [0.5, 1, 1.25, 1.5, 2],
            // ANTI-HIDE CONFIGURATION
            inactivityTimeout: 0,
            userActions: {
                hotkeys: true,
                click: false,
                doubleClick: false
            }
        });
        
        this.currentPlayer.ready(() => {
            console.log('✅ Video.js inicializado');
            
            // Aplicar correções anti-hide
            this.applyVideoJSFixes();
            
            // Setup source
            this.currentPlayer.src({
                src: videoUrl,
                type: this.getVideoMimeType(videoName)
            });
        });
        
        this.playerType = 'videojs';
    }

    applyVideoJSFixes() {
        if (!this.currentPlayer) return;
        
        // Desabilitar eventos de hide
        this.currentPlayer.off('userinactive');
        this.currentPlayer.off('useractive');
        
        // Forçar classe controls-enabled
        const playerEl = this.currentPlayer.el();
        playerEl.classList.add('vjs-controls-enabled');
        playerEl.classList.remove('vjs-user-inactive');
        
        // Interval de segurança
        this.controlsInterval = setInterval(() => {
            if (playerEl) {
                playerEl.classList.remove('vjs-user-inactive');
                playerEl.classList.add('vjs-controls-enabled');
                
                const controlBar = playerEl.querySelector('.vjs-control-bar');
                if (controlBar) {
                    controlBar.style.cssText = `
                        display: flex !important;
                        opacity: 1 !important;
                        visibility: visible !important;
                        transform: translateY(0) !important;
                    `;
                }
            }
        }, 1000);
        
        console.log('✅ Correções Video.js aplicadas');
    }

    initHTML5(videoUrl, videoName) {
        const video = document.getElementById('html5Player');
        if (video) {
            video.src = videoUrl;
            video.controls = true;
            video.load();
            this.currentPlayer = video;
            this.playerType = 'html5';
            console.log('✅ HTML5 player inicializado');
        }
    }

    initVLC(videoUrl, videoName) {
        const container = document.getElementById('vlcContainer');
        
        // Tenta VLC Plugin
        if (this.detectVLCPlugin()) {
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
            if (vlcEmbed) {
                this.currentPlayer = vlcEmbed;
                this.playerType = 'vlc';
                console.log('✅ VLC Plugin inicializado');
                return;
            }
        }
        
        // Fallback: mostrar instruções
        container.innerHTML = `
            <div class="vlc-instructions">
                <h4>🎬 VLC Web Player</h4>
                <p>Para usar o VLC Player:</p>
                <ol>
                    <li>Instale o <a href="https://www.videolan.org/vlc/" target="_blank">VLC Media Player</a></li>
                    <li>Ative o plugin web no navegador</li>
                    <li>Recarregue a página</li>
                </ol>
                <p><strong>Vantagens do VLC:</strong></p>
                <ul>
                    <li>✅ Controles sempre visíveis</li>
                    <li>✅ Suporte a todos os formatos</li>
                    <li>✅ Performance superior</li>
                    <li>✅ Controles avançados</li>
                </ul>
                <button onclick="window.playerModule.switchPlayer('html5', '${videoUrl}', '${videoName}')" 
                        class="fallback-btn">
                    Usar HTML5 Player
                </button>
            </div>
        `;
        
        console.log('ℹ️ VLC não disponível, mostrando instruções');
    }

    detectVLCPlugin() {
        const plugins = navigator.plugins;
        for (let i = 0; i < plugins.length; i++) {
            if (plugins[i].name.toLowerCase().includes('vlc')) {
                return true;
            }
        }
        return false;
    }

    stopCurrentPlayer() {
        if (this.controlsInterval) {
            clearInterval(this.controlsInterval);
            this.controlsInterval = null;
        }
        
        if (this.currentPlayer) {
            try {
                if (this.playerType === 'videojs' && this.currentPlayer.dispose) {
                    this.currentPlayer.dispose();
                } else if (this.currentPlayer.pause) {
                    this.currentPlayer.pause();
                }
            } catch (error) {
                console.error('Erro ao parar player:', error);
            }
            this.currentPlayer = null;
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

    toggleFullscreen() {
        if (this.currentPlayer) {
            try {
                if (this.playerType === 'videojs' && this.currentPlayer.requestFullscreen) {
                    this.currentPlayer.requestFullscreen();
                } else if (this.currentPlayer.requestFullscreen) {
                    this.currentPlayer.requestFullscreen();
                } else if (this.currentPlayer.video && this.currentPlayer.video.toggleFullscreen) {
                    this.currentPlayer.video.toggleFullscreen();
                }
            } catch (error) {
                console.error('Erro fullscreen:', error);
            }
        }
    }

    changeSpeed(rate) {
        const buttons = this.modal.querySelectorAll('.control-btn');
        buttons.forEach(btn => {
            btn.classList.remove('active');
            if (btn.textContent === `${rate}x`) {
                btn.classList.add('active');
            }
        });
        
        if (this.currentPlayer) {
            try {
                if (this.playerType === 'videojs' && this.currentPlayer.playbackRate) {
                    this.currentPlayer.playbackRate(rate);
                } else if (this.currentPlayer.playbackRate !== undefined) {
                    this.currentPlayer.playbackRate = rate;
                } else if (this.currentPlayer.input && this.currentPlayer.input.rate) {
                    this.currentPlayer.input.rate = rate;
                }
                console.log(`Velocidade alterada para: ${rate}x`);
            } catch (error) {
                console.error('Erro ao alterar velocidade:', error);
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
        
        this.stopCurrentPlayer();
    }
}