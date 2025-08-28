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
        
        console.log('Iniciando player para:', videoName, 'URL:', videoUrl);
        
        this.modal.innerHTML = `
            <div class="modal-content">
                <button class="close-btn" onclick="window.playerModule.close()">×</button>
                <div class="video-container">
                    <video-js id="videoPlayer" 
                             class="vjs-default-skin" 
                             controls 
                             preload="auto" 
                             width="100%" 
                             height="100%" 
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
        const video = document.getElementById('videoPlayer');
        if (video && typeof video.load === 'function') {
            console.log('Configurando HTML5 video');
            video.src = videoUrl;
            video.load();
            
            // Event listeners para debug
            video.addEventListener('loadstart', () => console.log('HTML5: Carregamento iniciado'));
            video.addEventListener('error', (e) => {
                console.error('HTML5 Error:', e);
                console.error('Video error details:', video.error);
            });
        } else {
            console.error('Elemento video não encontrado ou inválido');
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