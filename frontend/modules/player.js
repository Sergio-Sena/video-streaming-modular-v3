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
                    <video controls autoplay>
                        <source src="${videoUrl}" type="video/mp4">
                        Seu navegador não suporta o elemento de vídeo.
                    </video>
                </div>
                <div class="video-controls">
                    <button onclick="window.playerModule.toggleFullscreen()">🔳 Tela Cheia</button>
                    <button onclick="window.playerModule.downloadVideo('${videoUrl}', '${videoName}')">⬇️ Download</button>
                </div>
            </div>
        `;

        this.video = this.modal.querySelector('video');
        this.modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    close() {
        this.modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        
        if (this.video) {
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

    downloadVideo(url, name) {
        const a = document.createElement('a');
        a.href = url;
        a.download = name;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
}