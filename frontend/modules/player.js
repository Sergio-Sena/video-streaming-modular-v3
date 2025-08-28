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
        this.modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${videoName}</h3>
                    <button class="close-btn" onclick="window.playerModule.close()">×</button>
                </div>
                <div class="video-container">
                    <video-js id="videoPlayer" 
                             class="vjs-default-skin" 
                             controls 
                             preload="auto" 
                             width="100%" 
                             height="400" 
                             data-setup='{}'>
                        <source src="${videoUrl}" type="video/mp4">
                        <p class="vjs-no-js">
                            Para ver este vídeo, ative o JavaScript e considere atualizar para um
                            <a href="https://videojs.com/html5-video-support/" target="_blank">
                                navegador que suporte HTML5 video
                            </a>.
                        </p>
                    </video-js>
                </div>
                <div class="video-controls">
                    <button onclick="window.playerModule.downloadVideo('${videoUrl}', '${videoName}')">⬇️ Download</button>
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
                    html5: {
                        vhs: {
                            overrideNative: true
                        }
                    }
                });
                
                this.player.ready(() => {
                    console.log('Video.js player ready');
                    this.setupVideoSource(videoUrl, videoName);
                });
                
                this.player.on('error', () => {
                    console.error('Video.js error:', this.player.error());
                    this.tryHLSFallback(videoUrl, videoName);
                });
            } else {
                console.log('Video.js não carregado, usando HTML5 padrão');
                this.setupHTMLVideo(videoUrl, videoName);
            }
        }, 500);
        
        this.modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    close() {
        this.modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        
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
        if (typeof Hls !== 'undefined' && Hls.isSupported()) {
            console.log('HLS.js suportado, configurando para .ts');
            
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
                    console.log('Erro fatal HLS, tentando como MP4');
                    this.tryDirectPlay(videoUrl, videoName);
                }
            });
            
            this.hls = hls;
        } else {
            console.log('HLS.js não suportado, tentando reprodução direta');
            this.tryDirectPlay(videoUrl, videoName);
        }
    }
    
    tryDirectPlay(videoUrl, videoName) {
        console.log('Tentando reprodução direta como MP4');
        this.player.src({
            src: videoUrl,
            type: 'video/mp4'
        });
    }
    
    tryHLSFallback(videoUrl, videoName) {
        const ext = videoName.toLowerCase().split('.').pop();
        if (ext === 'ts' || ext === 'm2ts' || ext === 'mts') {
            console.log('Erro no Video.js, tentando HLS direto');
            this.setupHTMLVideo(videoUrl, videoName);
        }
    }
    
    setupHTMLVideo(videoUrl, videoName) {
        const video = document.getElementById('videoPlayer');
        if (video) {
            video.src = videoUrl;
            video.load();
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

    downloadVideo(url, name) {
        const a = document.createElement('a');
        a.href = url;
        a.download = name;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
}