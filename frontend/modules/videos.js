/**
 * Módulo de Vídeos
 * Gerencia upload, listagem e exibição de vídeos
 */
class VideosModule {
    constructor() {
        this.initEventListeners();
    }

    initEventListeners() {
        // Upload files
        document.getElementById('fileInput').addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files);
        });

        // Upload folder
        document.getElementById('folderInput').addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files);
        });

        document.getElementById('browseBtn').addEventListener('click', () => {
            const activeTab = document.querySelector('.upload-tab.active').dataset.type;
            if (activeTab === 'folder') {
                document.getElementById('folderInput').click();
            } else {
                document.getElementById('fileInput').click();
            }
        });

        // Upload tabs
        document.querySelectorAll('.upload-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                document.querySelectorAll('.upload-tab').forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');
                
                const type = e.target.dataset.type;
                const icon = document.getElementById('uploadIcon');
                const title = document.getElementById('uploadTitle');
                const info = document.getElementById('uploadInfo');
                
                if (type === 'folder') {
                    icon.textContent = '📁';
                    title.textContent = 'Arraste pasta aqui';
                    info.innerHTML = '<small>Selecione uma pasta com vídeos (máx. 5GB cada)</small>';
                } else {
                    icon.textContent = '📄';
                    title.textContent = 'Arraste vídeos aqui';
                    info.innerHTML = '<small>Formatos suportados: MP4, WebM, AVI, MOV (máx. 5GB cada)</small>';
                }
            });
        });

        // Upload toggle
        document.getElementById('uploadToggle').addEventListener('click', () => {
            const uploadSection = document.getElementById('uploadSection');
            uploadSection.style.display = uploadSection.style.display === 'none' ? 'block' : 'none';
        });

        // Search functionality
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.filterVideos(e.target.value);
        });

        // View controls
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                
                const view = e.target.dataset.view;
                const videoGrid = document.getElementById('videoGrid');
                videoGrid.className = view === 'list' ? 'video-list' : 'video-grid';
            });
        });
    }

    async loadVideos() {
        const loadingContainer = document.getElementById('loadingContainer');
        const videoGrid = document.getElementById('videoGrid');
        
        loadingContainer.style.display = 'flex';
        
        try {
            const response = await window.api.getVideos();
            
            if (response.success) {
                this.displayVideos(response.videos);
            }
        } catch (error) {
            console.error('Erro ao carregar vídeos:', error);
            videoGrid.innerHTML = '<p>Erro ao carregar vídeos</p>';
        } finally {
            loadingContainer.style.display = 'none';
        }
    }

    displayVideos(videos) {
        const videoGrid = document.getElementById('videoGrid');
        
        if (!videos || videos.length === 0) {
            videoGrid.innerHTML = '<p>Nenhum vídeo encontrado</p>';
            return;
        }

        videoGrid.innerHTML = videos.map(video => `
            <div class="video-card" onclick="window.playerModule.play('${video.url}', '${video.name}')">
                <div class="video-thumbnail">
                    <video preload="metadata">
                        <source src="${video.url}" type="video/mp4">
                    </video>
                    <div class="play-button">▶</div>
                </div>
                <div class="video-info">
                    <h3>${video.name}</h3>
                    <p>${this.formatFileSize(video.size)}</p>
                    <small>${new Date(video.lastModified).toLocaleDateString()}</small>
                </div>
            </div>
        `).join('');
    }

    async handleFileUpload(files) {
        const uploadProgress = document.getElementById('uploadProgress');
        
        for (const file of files) {
            if (!file.type.startsWith('video/')) {
                alert(`${file.name} não é um arquivo de vídeo válido`);
                continue;
            }

            try {
                const response = await window.api.getUploadUrl(file.name, file.type, file.size);
                
                if (response.success) {
                    const progressDiv = document.createElement('div');
                    progressDiv.className = 'upload-item';
                    progressDiv.innerHTML = `
                        <div class="upload-info">
                            <span>${file.name}</span>
                            <span class="upload-status">Enviando...</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 0%"></div>
                        </div>
                    `;
                    uploadProgress.appendChild(progressDiv);

                    await window.api.uploadToS3(response.uploadUrl, file, (progress) => {
                        const progressFill = progressDiv.querySelector('.progress-fill');
                        progressFill.style.width = `${progress}%`;
                    });

                    progressDiv.querySelector('.upload-status').textContent = 'Concluído';
                    progressDiv.querySelector('.progress-fill').style.backgroundColor = '#4CAF50';
                    
                    setTimeout(() => {
                        this.loadVideos();
                        progressDiv.remove();
                    }, 2000);
                }
            } catch (error) {
                alert(`Erro no upload de ${file.name}: ${error.message}`);
            }
        }
    }

    filterVideos(searchTerm) {
        const videoCards = document.querySelectorAll('.video-card');
        
        videoCards.forEach(card => {
            const videoName = card.querySelector('h3').textContent.toLowerCase();
            const isVisible = videoName.includes(searchTerm.toLowerCase());
            card.style.display = isVisible ? 'block' : 'none';
        });
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}