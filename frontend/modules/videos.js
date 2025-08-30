/**
 * Módulo de Vídeos
 * Gerencia upload, listagem e exibição de vídeos
 */
class VideosModule {
    constructor() {
        this.showHierarchy = false;
        this.currentFolderPath = '';
        this.initEventListeners();
    }

    initEventListeners() {
        // Upload files
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                console.log(`DEBUG: Arquivos selecionados: ${e.target.files.length}`);
                this.handleFileUpload(e.target.files);
                e.target.value = ''; // Reset input
            });
        }

        // Upload folder
        const folderInput = document.getElementById('folderInput');
        if (folderInput) {
            folderInput.addEventListener('change', (e) => {
                console.log(`DEBUG: Pasta selecionada com ${e.target.files.length} arquivos`);
                this.handleFileUpload(e.target.files);
                e.target.value = ''; // Reset input
            });
        }

        // Upload option buttons
        const uploadFilesBtn = document.getElementById('uploadFilesBtn');
        if (uploadFilesBtn) {
            uploadFilesBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                document.getElementById('fileInput').click();
            });
        }

        const uploadFolderBtn = document.getElementById('uploadFolderBtn');
        const folderCheckbox = document.getElementById('folderCheckbox');
        if (uploadFolderBtn) {
            uploadFolderBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                // Toggle checkbox
                folderCheckbox.checked = !folderCheckbox.checked;
                // Abrir seletor de pasta
                document.getElementById('folderInput').click();
            });
        }
        
        // Prevenir que clique no checkbox dispare o botão
        if (folderCheckbox) {
            folderCheckbox.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }

        // Upload toggle
        const uploadToggle = document.getElementById('uploadToggle');
        if (uploadToggle) {
            uploadToggle.addEventListener('click', () => {
                const uploadSection = document.getElementById('uploadSection');
                uploadSection.style.display = uploadSection.style.display === 'none' ? 'block' : 'none';
            });
        }

        // Show folders toggle
        const showFoldersBtn = document.getElementById('showFoldersBtn');
        if (showFoldersBtn) {
            showFoldersBtn.addEventListener('click', () => {
                this.toggleHierarchyView();
            });
        }

        // Search functionality
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterVideos(e.target.value);
            });
        }

        // View controls
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                
                const view = e.target.dataset.view;
                const videoGrid = document.getElementById('videoGrid');
                if (videoGrid) {
                    videoGrid.className = view === 'list' ? 'video-list' : 'video-grid';
                }
            });
        });
    }

    async loadVideos() {
        const loadingContainer = document.getElementById('loadingContainer');
        const videoGrid = document.getElementById('videoGrid');
        
        loadingContainer.style.display = 'flex';
        
        try {
            let response;
            if (this.showHierarchy) {
                response = await this.loadHierarchyView(this.currentFolderPath);
            } else {
                response = await window.apiModule.getVideos(false);
            }
            
            if (response.success) {
                if (this.showHierarchy) {
                    this.displayFolderNavigation(response);
                } else {
                    this.displayItems(response.items || response.videos || []);
                }
            }
        } catch (error) {
            console.error('Erro ao carregar vídeos:', error);
            videoGrid.innerHTML = '<p>Erro ao carregar vídeos</p>';
        } finally {
            loadingContainer.style.display = 'none';
        }
    }
    
    async loadHierarchyView(path = '') {
        const url = `/videos?hierarchy=true${path ? `&path=${encodeURIComponent(path)}` : ''}`;
        return await window.apiModule.request(url, { method: 'GET' });
    }

    displayItems(items) {
        const videoGrid = document.getElementById('videoGrid');
        
        if (!items || items.length === 0) {
            videoGrid.innerHTML = '<p>Nenhum item encontrado</p>';
            return;
        }

        videoGrid.innerHTML = items.map((item, index) => {
            return `
                <div class="video-card">
                    <div class="video-thumbnail" onclick="window.playerModule.play('${item.url}', '${item.name}')">
                        <video preload="metadata">
                            <source src="${item.url}" type="video/mp4">
                        </video>
                        <div class="play-button">▶</div>
                    </div>
                    <div class="video-info">
                        <h3>${item.name}</h3>
                        <p>${this.formatFileSize(item.size)}</p>
                        <small>${item.lastModified ? new Date(item.lastModified).toLocaleDateString() : ''}</small>
                    </div>
                    <div class="video-actions">
                        <button class="delete-btn" onclick="window.videosModule.deleteVideo('${item.key}', ${index})" title="Deletar vídeo">
                            🗑️
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    // BACKUP: Função original (para rollback se necessário)
    displayFolderNavigationOriginal(response) {
        const videoGrid = document.getElementById('videoGrid');
        const { folders = [], files = [], currentPath = '' } = response;
        
        let html = '<div class="folder-navigation">';
        
        // Breadcrumb
        html += '<div class="folder-breadcrumb">';
        html += '<span class="breadcrumb-item" onclick="window.videosModule.navigateToFolder(\'\')">📁 Raiz</span>';
        
        if (currentPath) {
            const pathParts = currentPath.split('/');
            let buildPath = '';
            pathParts.forEach((part, index) => {
                buildPath += (buildPath ? '/' : '') + part;
                const isLast = index === pathParts.length - 1;
                html += '<span class="breadcrumb-separator">/</span>';
                if (isLast) {
                    html += `<span class="breadcrumb-item current">${part}</span>`;
                } else {
                    html += `<span class="breadcrumb-item" onclick="window.videosModule.navigateToFolder('${buildPath}')">${part}</span>`;
                }
            });
        }
        html += '</div>';
        
        // Conteúdo da pasta
        html += '<div class="folder-content">';
        
        // Botão voltar
        if (currentPath) {
            const parentPath = currentPath.split('/').slice(0, -1).join('/');
            html += `
                <div class="folder-item back-button" onclick="window.videosModule.navigateToFolder('${parentPath}')">
                    <div class="folder-icon">⬅️</div>
                    <div class="folder-info">
                        <div class="folder-name">.. (Voltar)</div>
                        <div class="folder-details">Pasta anterior</div>
                    </div>
                </div>
            `;
        }
        
        // Pastas
        folders.forEach(folder => {
            html += `
                <div class="folder-item" ondblclick="window.videosModule.navigateToFolder('${folder.path}')">
                    <div class="folder-icon">📁</div>
                    <div class="folder-info">
                        <div class="folder-name">${folder.name}</div>
                        <div class="folder-details">Pasta</div>
                    </div>
                    <div class="folder-actions">
                        <button class="folder-action-btn delete-btn" onclick="event.stopPropagation(); window.videosModule.deleteFolder('videos/${folder.path}/', '${folder.name}')" title="Deletar pasta">
                            🗑️
                        </button>
                    </div>
                </div>
            `;
        });
        
        // Arquivos
        files.forEach(file => {
            html += `
                <div class="folder-item" onclick="window.playerModule.play('${file.url}', '${file.name}')">
                    <div class="folder-icon">🎥</div>
                    <div class="folder-info">
                        <div class="folder-name">${file.name}</div>
                        <div class="folder-details">${this.formatFileSize(file.size)} • ${new Date(file.lastModified).toLocaleDateString()}</div>
                    </div>
                    <div class="folder-actions">
                        <button class="folder-action-btn play-btn" onclick="event.stopPropagation(); window.playerModule.play('${file.url}', '${file.name}')" title="Reproduzir">
                            ▶️
                        </button>
                        <button class="folder-action-btn delete-btn" onclick="event.stopPropagation(); window.videosModule.deleteVideo('${file.key}')" title="Deletar">
                            🗑️
                        </button>
                    </div>
                </div>
            `;
        });
        
        // Pasta vazia
        if (folders.length === 0 && files.length === 0) {
            html += `
                <div class="empty-folder">
                    <div class="empty-folder-icon">📂</div>
                    <p>Esta pasta está vazia</p>
                </div>
            `;
        }
        
        html += '</div></div>';
        
        videoGrid.innerHTML = html;
    }

    // NOVA IMPLEMENTAÇÃO: Visualização por seções de pasta
    displayFolderNavigation(response) {
        // Flag para testar nova implementação (pode ser alterada para rollback)
        const USE_NEW_FOLDER_VIEW = true;
        
        if (!USE_NEW_FOLDER_VIEW) {
            console.log('🔄 Usando visualização original');
            return this.displayFolderNavigationOriginal(response);
        }
        
        try {
            console.log('🆕 Usando nova visualização por seções');
            this.displayFolderNavigationNew(response);
        } catch (error) {
            console.error('❌ Erro na nova visualização, usando original:', error);
            this.displayFolderNavigationOriginal(response);
        }
    }

    displayFolderNavigationNew(response) {
        const videoGrid = document.getElementById('videoGrid');
        
        console.log('🔍 Dados recebidos:', response);
        
        // Se não há dados, usar método original
        if (!response || (!response.folders && !response.files && !response.items)) {
            console.log('⚠️ Dados insuficientes, usando visualização original');
            return this.displayFolderNavigationOriginal(response);
        }
        
        let html = '<div class="folder-sections-view">';
        
        // Processar arquivos na raiz (se houver)
        if (response.files && response.files.length > 0) {
            html += this.generateFolderSection('Pasta Raiz', response.files, '📄', true);
        }
        
        // Processar pastas
        if (response.folders && response.folders.length > 0) {
            response.folders.forEach(folder => {
                html += this.generateFolderSection(folder.name, [], '📁', false, folder.path, true);
            });
        }
        
        // Se não há conteúdo, mostrar mensagem
        if ((!response.files || response.files.length === 0) && (!response.folders || response.folders.length === 0)) {
            html = '<p>Nenhum item encontrado</p>';
        } else {
            html += '</div>';
        }
        
        videoGrid.innerHTML = html;
    }

    groupVideosByFolder(videos) {
        const grouped = {};
        
        videos.forEach(video => {
            // Extrair pasta do key ou path
            let folderPath = '';
            if (video.key) {
                const keyParts = video.key.replace('videos/', '').split('/');
                if (keyParts.length > 1) {
                    keyParts.pop(); // Remove nome do arquivo
                    folderPath = keyParts.join('/');
                }
            }
            
            if (!grouped[folderPath]) {
                grouped[folderPath] = [];
            }
            grouped[folderPath].push(video);
        });
        
        return grouped;
    }

    generateFolderSection(folderName, videos, icon, isRoot = false, folderPath = '', isFolder = false) {
        const sectionId = `folder-${folderName.replace(/[^a-zA-Z0-9]/g, '_')}`;
        
        let html = `
            <div class="folder-section" id="${sectionId}">
                <div class="folder-section-header">
        `;
        
        // Se é uma pasta (não arquivos), adicionar duplo clique para navegar
        if (isFolder) {
            html += `<h3 ondblclick="window.videosModule.navigateToFolder('${folderPath}')" style="cursor: pointer;">${icon} ${folderName}</h3>`;
        } else {
            html += `<h3>${icon} ${folderName} (${videos.length} itens)</h3>`;
        }
        
        html += `
                    <div class="folder-section-actions">
        `;
        
        // Botão deletar pasta (não para raiz)
        if (!isRoot && folderPath) {
            html += `
                <button class="folder-action-btn delete-btn" onclick="event.stopPropagation(); window.videosModule.deleteFolder('videos/${folderPath}/', '${folderName}')" title="Deletar pasta">
                    🗑️
                </button>
            `;
        }
        
        html += `
                    </div>
                </div>
        `;
        
        // Se é pasta, não mostrar conteúdo (será navegado)
        if (!isFolder) {
            html += `<div class="folder-section-content">`;
            
            // Vídeos da seção
            videos.forEach(video => {
                html += `
                    <div class="video-card folder-video">
                        <div class="video-thumbnail" onclick="window.playerModule.play('${video.url}', '${video.name}')">
                            <video preload="metadata">
                                <source src="${video.url}" type="video/mp4">
                            </video>
                            <div class="play-button">▶</div>
                        </div>
                        <div class="video-info">
                            <h3>${video.name}</h3>
                            <p>${this.formatFileSize(video.size)}</p>
                            <small>${video.lastModified ? new Date(video.lastModified).toLocaleDateString() : ''}</small>
                        </div>
                        <div class="video-actions">
                            <button class="delete-btn" onclick="window.videosModule.deleteVideo('${video.key}')" title="Deletar vídeo">
                                🗑️
                            </button>
                        </div>
                    </div>
                `;
            });
            
            html += `</div>`;
        }
        
        html += `</div>`;
        
        return html;
    }
    
    async navigateToFolder(path) {
        this.currentFolderPath = path;
        await this.loadVideos();
    }

    async handleFileUpload(files) {
        const uploadProgress = document.getElementById('uploadProgress');
        
        console.log(`DEBUG: ===== INICIANDO UPLOAD =====`);
        console.log(`DEBUG: Total de arquivos recebidos: ${files.length}`);
        
        // Lista todos os arquivos recebidos
        Array.from(files).forEach((file, index) => {
            console.log(`DEBUG: Arquivo ${index + 1}: ${file.name} (${file.type}) - Path: ${file.webkitRelativePath || 'N/A'}`);
        });
        
        // Filtra apenas vídeos
        const videoFiles = Array.from(files).filter((file, index) => {
            const isVideo = file.type.startsWith('video/');
            console.log(`DEBUG: Arquivo ${index + 1} - ${file.name}: ${isVideo ? 'VÍDEO ✓' : 'NÃO-VÍDEO ✗'}`);
            return isVideo;
        });
        
        console.log(`DEBUG: Arquivos de vídeo encontrados: ${videoFiles.length}`);
        
        if (videoFiles.length === 0) {
            this.showMessage('Nenhum arquivo de vídeo encontrado', 'error');
            return;
        }
        
        // Verifica arquivos existentes
        console.log(`DEBUG: Verificando arquivos existentes...`);
        const filesToUpload = await this.checkExistingFiles(videoFiles);
        
        console.log(`DEBUG: Arquivos para upload após verificação: ${filesToUpload.length}`);
        filesToUpload.forEach((file, index) => {
            console.log(`DEBUG: Upload ${index + 1}: ${file.name}`);
        });
        
        if (filesToUpload.length === 0) {
            this.showMessage('Todos os arquivos já existem', 'info');
            return;
        }
        
        // Mostra seção de progresso
        uploadProgress.style.display = 'block';
        console.log(`DEBUG: ===== INICIANDO UPLOADS =====`);
        
        for (let i = 0; i < filesToUpload.length; i++) {
            const file = filesToUpload[i];
            console.log(`DEBUG: Processando arquivo ${i+1}/${filesToUpload.length}: ${file.name}`);

            try {
                // Extrai caminho da pasta se for upload de pasta
                let folderPath = '';
                if (file.webkitRelativePath) {
                    const pathParts = file.webkitRelativePath.split('/');
                    if (pathParts.length > 1) {
                        pathParts.pop(); // Remove nome do arquivo
                        folderPath = pathParts.join('/').replace(/[^a-zA-Z0-9\/\-_]/g, '_');
                    }
                }

                // Redireciona uploads não-MP4 para bucket de conversão
                const isMP4 = file.name.toLowerCase().endsWith('.mp4');
                const targetBucket = isMP4 ? 'video-streaming-sstech-eaddf6a1' : 'video-conversion-temp-sstech';
                console.log(`📝 Upload: ${file.name}`);
                
                const response = await window.apiModule.getUploadUrl(file.name, file.type, file.size, folderPath);
                
                if (response.success) {
                    if (response.multipart) {
                        await this.handleMultipartUpload(file, response.uploadId, response.key, folderPath, i, filesToUpload.length);
                    } else if (response.uploadUrl) {
                    const displayName = folderPath ? `${folderPath}/${file.name}` : file.name;
                    const progressDiv = document.createElement('div');
                    progressDiv.className = 'upload-item';
                    progressDiv.innerHTML = `
                        <div class="upload-info">
                            <span class="file-name">[${i+1}/${filesToUpload.length}] ${displayName}</span>
                            <span class="upload-status">Enviando...</span>
                            <span class="upload-percent">0%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 0%"></div>
                        </div>
                        <div class="upload-speed"></div>
                    `;
                    uploadProgress.appendChild(progressDiv);

                    const startTime = Date.now();
                    
                    await window.apiModule.uploadToS3(response.uploadUrl, file, (progress, loaded, total) => {
                        const progressFill = progressDiv.querySelector('.progress-fill');
                        const progressPercent = progressDiv.querySelector('.upload-percent');
                        const uploadSpeed = progressDiv.querySelector('.upload-speed');
                        
                        progressFill.style.width = `${progress}%`;
                        progressPercent.textContent = `${Math.round(progress)}%`;
                        
                        // Calcula velocidade
                        const elapsed = (Date.now() - startTime) / 1000;
                        const speed = loaded / elapsed;
                        const speedText = speed > 1024 * 1024 ? 
                            `${(speed / (1024 * 1024)).toFixed(1)} MB/s` : 
                            `${(speed / 1024).toFixed(1)} KB/s`;
                        uploadSpeed.textContent = speedText;
                    });

                    progressDiv.querySelector('.upload-status').textContent = '✓ Concluído';
                    progressDiv.querySelector('.progress-fill').style.backgroundColor = '#4CAF50';
                    progressDiv.querySelector('.upload-percent').textContent = '100%';
                    progressDiv.querySelector('.upload-speed').textContent = '';
                    
                    setTimeout(() => {
                        progressDiv.remove();
                        // Recarrega vídeos apenas no último arquivo
                        if (i === filesToUpload.length - 1) {
                            console.log('DEBUG: Último arquivo enviado, recarregando lista');
                            this.loadVideos();
                        }
                    }, 2000);
                    } else {
                        alert(`Erro: Não foi possível obter URL de upload para ${file.name}`);
                    }
                } else {
                    alert(`Erro: ${response.message || 'Falha na geração de URL'}`);
                }
            } catch (error) {
                console.error(`DEBUG: Erro no upload de ${file.name}:`, error);
                this.showMessage(`Erro no upload de ${file.name}: ${error.message}`, 'error');
            }
        }
        
        console.log(`DEBUG: ===== TODOS OS ${filesToUpload.length} UPLOADS INICIADOS =====`);
        this.showMessage(`${filesToUpload.length} arquivos em upload`, 'success');
    }

    filterVideos(searchTerm) {
        const videoCards = document.querySelectorAll('.video-card');
        
        videoCards.forEach(card => {
            const videoName = card.querySelector('h3').textContent.toLowerCase();
            const isVisible = videoName.includes(searchTerm.toLowerCase());
            card.style.display = isVisible ? 'block' : 'none';
        });
    }

    async deleteVideo(videoKey, index) {
        if (!confirm('Tem certeza que deseja deletar este vídeo?\n\nEsta ação não pode ser desfeita!')) {
            return;
        }

        try {
            const response = await window.apiModule.deleteVideo(videoKey);
            
            if (response.success) {
                this.showMessage('Vídeo deletado com sucesso!', 'success');
                this.loadVideos();
            } else {
                this.showMessage('Erro ao deletar vídeo', 'error');
            }
        } catch (error) {
            console.error('Erro ao deletar:', error);
            this.showMessage('Erro ao deletar vídeo', 'error');
        }
    }

    async checkExistingFiles(files) {
        try {
            // Agrupa arquivos por pasta
            const filesByFolder = {};
            
            files.forEach(file => {
                let folderPath = '';
                if (file.webkitRelativePath) {
                    const pathParts = file.webkitRelativePath.split('/');
                    if (pathParts.length > 1) {
                        pathParts.pop();
                        folderPath = pathParts.join('/').replace(/[^a-zA-Z0-9\/\-_]/g, '_');
                    }
                }
                
                if (!filesByFolder[folderPath]) {
                    filesByFolder[folderPath] = [];
                }
                filesByFolder[folderPath].push(file);
            });
            
            const filesToUpload = [];
            let skippedCount = 0;
            
            // Verifica cada pasta
            for (const [folderPath, folderFiles] of Object.entries(filesByFolder)) {
                const response = await window.apiModule.request('/videos', {
                    method: 'POST',
                    body: JSON.stringify({
                        action: 'check-existing',
                        files: folderFiles.map(f => ({ name: f.name })),
                        folderPath: folderPath
                    })
                });
                
                if (response.success) {
                    const existingFiles = response.existingFiles || [];
                    
                    folderFiles.forEach(file => {
                        if (existingFiles.includes(file.name)) {
                            console.log(`DEBUG: Arquivo ${file.name} já existe, pulando`);
                            skippedCount++;
                        } else {
                            filesToUpload.push(file);
                        }
                    });
                } else {
                    // Se erro na verificação, faz upload de todos
                    filesToUpload.push(...folderFiles);
                }
            }
            
            if (skippedCount > 0) {
                this.showMessage(`${skippedCount} arquivos já existem e foram ignorados`, 'info');
            }
            
            return filesToUpload;
            
        } catch (error) {
            console.error('Erro ao verificar arquivos existentes:', error);
            // Se erro, faz upload de todos
            return files;
        }
    }

    showMessage(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 5px;
            color: white;
            z-index: 10000;
            background: ${type === 'success' ? '#28a745' : type === 'info' ? '#17a2b8' : '#dc3545'};
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 3000);
    }

    async deleteFolder(folderKey, folderName) {
        if (!confirm(`Tem certeza que deseja deletar a pasta "${folderName}" e todo seu conteúdo?\n\nEsta ação não pode ser desfeita!`)) {
            return;
        }

        try {
            const response = await window.apiModule.deleteFolder(folderKey);
            
            if (response.success) {
                this.showMessage('Pasta deletada com sucesso!', 'success');
                this.loadVideos();
            } else {
                this.showMessage('Erro ao deletar pasta', 'error');
            }
        } catch (error) {
            console.error('Erro ao deletar pasta:', error);
            this.showMessage('Erro ao deletar pasta', 'error');
        }
    }



    toggleHierarchyView() {
        this.showHierarchy = !this.showHierarchy;
        this.currentFolderPath = ''; // Reset para raiz
        const btn = document.getElementById('showFoldersBtn');
        
        if (this.showHierarchy) {
            btn.classList.add('active');
            btn.title = 'Ocultar Pastas';
        } else {
            btn.classList.remove('active');
            btn.title = 'Mostrar Pastas';
        }
        
        this.loadVideos();
    }

    displayHierarchy(hierarchy) {
        const videoGrid = document.getElementById('videoGrid');
        let html = '';
        
        // Mostra arquivos na raiz primeiro
        if (hierarchy.root && hierarchy.root.files.length > 0) {
            html += '<div class="folder-section"><h3>📁 Arquivos na Raiz</h3><div class="folder-content">';
            hierarchy.root.files.forEach(file => {
                html += this.generateFileCard(file);
            });
            html += '</div></div>';
        }
        
        // Mostra pastas
        Object.keys(hierarchy).forEach(folderName => {
            if (folderName === 'root') return;
            
            const folder = hierarchy[folderName];
            html += `
                <div class="folder-section">
                    <div class="folder-header" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">
                        <h3>📁 ${folderName} (${folder.files.length} arquivos)</h3>
                        <button class="delete-folder-btn" onclick="event.stopPropagation(); window.videosModule.deleteFolderHierarchy('${folderName}')" title="Deletar pasta">
                            🗑️
                        </button>
                    </div>
                    <div class="folder-content">
            `;
            
            folder.files.forEach(file => {
                html += this.generateFileCard(file);
            });
            
            html += '</div></div>';
        });
        
        videoGrid.innerHTML = html || '<p>Nenhum arquivo encontrado</p>';
    }

    generateFileCard(file) {
        return `
            <div class="video-card file-in-folder">
                <div class="video-thumbnail" onclick="window.playerModule.play('${file.url}', '${file.name}')">
                    <video preload="metadata">
                        <source src="${file.url}" type="video/mp4">
                    </video>
                    <div class="play-button">▶</div>
                </div>
                <div class="video-info">
                    <h3>${file.name}</h3>
                    <p>${this.formatFileSize(file.size)}</p>
                    <small>${new Date(file.lastModified).toLocaleDateString()}</small>
                </div>
                <div class="video-actions">
                    <button class="delete-btn" onclick="window.videosModule.deleteVideo('${file.key}')" title="Deletar vídeo">
                        🗑️
                    </button>
                </div>
            </div>
        `;
    }

    async deleteFolderHierarchy(folderName) {
        if (!confirm(`Tem certeza que deseja deletar a pasta "${folderName}" e todo seu conteúdo?\n\nEsta ação não pode ser desfeita!`)) {
            return;
        }

        try {
            const response = await window.apiModule.deleteFolder(`videos/${folderName}/`);
            
            if (response.success) {
                this.showMessage('Pasta deletada com sucesso!', 'success');
                this.loadVideos();
            } else {
                this.showMessage('Erro ao deletar pasta', 'error');
            }
        } catch (error) {
            console.error('Erro ao deletar pasta:', error);
            this.showMessage('Erro ao deletar pasta', 'error');
        }
    }

    async handleMultipartUpload(file, uploadId, key, folderPath, fileIndex = 0, totalFiles = 1) {
        const uploadProgress = document.getElementById('uploadProgress');
        const displayName = folderPath ? `${folderPath}/${file.name}` : file.name;
        
        const progressDiv = document.createElement('div');
        progressDiv.className = 'upload-item multipart';
        progressDiv.innerHTML = `
            <div class="upload-info">
                <span class="file-name">${displayName}</span>
                <span class="upload-status">Preparando...</span>
                <span class="upload-percent">0%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 0%"></div>
            </div>
            <div class="upload-speed"></div>
        `;
        uploadProgress.appendChild(progressDiv);
        uploadProgress.style.display = 'block';

        try {
            const chunkSize = 20 * 1024 * 1024; // 20MB
            const concurrency = 4; // 4 uploads simultâneos
            const totalChunks = Math.ceil(file.size / chunkSize);
            const parts = [];
            const startTime = Date.now();
            let uploadedBytes = 0;
            let completedChunks = 0;

            progressDiv.querySelector('.upload-status').textContent = `Enviando ${totalChunks} partes (4 simultâneas)...`;

            // Função para upload de um chunk
            const uploadChunk = async (chunkIndex) => {
                const start = chunkIndex * chunkSize;
                const end = Math.min(start + chunkSize, file.size);
                const chunk = file.slice(start, end);
                const partNumber = chunkIndex + 1;

                // Obter URL para esta parte
                const partResponse = await window.apiModule.getPartUrl(uploadId, partNumber, key);
                if (!partResponse.success) {
                    throw new Error(`Erro ao obter URL da parte ${partNumber}`);
                }

                // Upload da parte
                const etag = await window.apiModule.uploadChunk(partResponse.uploadUrl, chunk);
                
                // Atualizar progresso
                uploadedBytes += chunk.size;
                completedChunks++;
                const progress = (uploadedBytes / file.size) * 100;
                const elapsed = (Date.now() - startTime) / 1000;
                const speed = uploadedBytes / elapsed;
                
                progressDiv.querySelector('.progress-fill').style.width = `${progress}%`;
                progressDiv.querySelector('.upload-percent').textContent = `${Math.round(progress)}%`;
                progressDiv.querySelector('.upload-status').textContent = `Parte ${completedChunks}/${totalChunks} (paralelo)`;
                
                const speedText = speed > 1024 * 1024 ? 
                    `${(speed / (1024 * 1024)).toFixed(1)} MB/s` : 
                    `${(speed / 1024).toFixed(1)} KB/s`;
                progressDiv.querySelector('.upload-speed').textContent = speedText;

                return { PartNumber: partNumber, ETag: etag };
            };

            // Upload em lotes paralelos
            for (let i = 0; i < totalChunks; i += concurrency) {
                const batch = [];
                for (let j = 0; j < concurrency && (i + j) < totalChunks; j++) {
                    batch.push(uploadChunk(i + j));
                }
                
                const batchResults = await Promise.all(batch);
                parts.push(...batchResults);
            }

            // Ordenar parts por PartNumber
            parts.sort((a, b) => a.PartNumber - b.PartNumber);

            // Completar multipart upload
            progressDiv.querySelector('.upload-status').textContent = 'Finalizando...';
            const completeResponse = await window.apiModule.completeMultipart(uploadId, parts, key);
            
            if (completeResponse.success) {
                progressDiv.querySelector('.upload-status').textContent = '✓ Concluído';
                progressDiv.querySelector('.progress-fill').style.backgroundColor = '#4CAF50';
                progressDiv.querySelector('.upload-percent').textContent = '100%';
                progressDiv.querySelector('.upload-speed').textContent = '';
                
                setTimeout(() => {
                    progressDiv.remove();
                    // Recarrega vídeos apenas no último arquivo
                    if (fileIndex === totalFiles - 1) {
                        console.log('DEBUG: Último arquivo multipart enviado, recarregando lista');
                        this.loadVideos();
                    }
                }, 2000);
            } else {
                throw new Error('Erro ao finalizar upload');
            }
        } catch (error) {
            console.error('Erro no multipart upload:', error);
            progressDiv.querySelector('.upload-status').textContent = '❌ Erro';
            progressDiv.querySelector('.progress-fill').style.backgroundColor = '#dc3545';
            alert(`Erro no upload multipart: ${error.message}`);
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
            'ts': 'video/mp2t',
            'm2ts': 'video/mp2t',
            'mts': 'video/mp2t',
            'vob': 'video/dvd',
            'ogv': 'video/ogg'
        };
        return mimeTypes[ext] || 'video/mp4';
    }

    async handleSingleFileUpload(file, progressCallback) {
        console.log(`📤 Upload individual: ${file.name}`);
        
        try {
            // Extrai caminho da pasta se for upload de pasta
            let folderPath = '';
            if (file.webkitRelativePath) {
                const pathParts = file.webkitRelativePath.split('/');
                if (pathParts.length > 1) {
                    pathParts.pop(); // Remove nome do arquivo
                    folderPath = pathParts.join('/').replace(/[^a-zA-Z0-9\/\-_]/g, '_');
                }
            }

            // Redireciona uploads não-MP4 para bucket de conversão
            const isMP4 = file.name.toLowerCase().endsWith('.mp4');
            const targetBucket = isMP4 ? 'video-streaming-sstech-eaddf6a1' : 'video-conversion-temp-sstech';
            console.log(`📝 Upload individual: ${file.name}`);
            
            const response = await window.apiModule.getUploadUrl(file.name, file.type, file.size, folderPath);
            
            if (response.success) {
                if (response.multipart) {
                    await this.handleMultipartUploadWithProgress(file, response.uploadId, response.key, folderPath, progressCallback);
                } else if (response.uploadUrl) {
                    const startTime = Date.now();
                    
                    await window.apiModule.uploadToS3(response.uploadUrl, file, (progress, loaded, total) => {
                        // Calcula velocidade
                        const elapsed = (Date.now() - startTime) / 1000;
                        const speed = loaded / elapsed;
                        
                        if (progressCallback) {
                            progressCallback(progress, speed);
                        }
                    });
                } else {
                    throw new Error('Não foi possível obter URL de upload');
                }
            } else {
                throw new Error(response.message || 'Falha na geração de URL');
            }
        } catch (error) {
            console.error(`❌ Erro no upload de ${file.name}:`, error);
            throw error;
        }
    }
    
    async handleMultipartUploadWithProgress(file, uploadId, key, folderPath, progressCallback) {
        const chunkSize = 20 * 1024 * 1024; // 20MB
        const concurrency = 4;
        const totalChunks = Math.ceil(file.size / chunkSize);
        const parts = [];
        const startTime = Date.now();
        let uploadedBytes = 0;
        let completedChunks = 0;

        // Função para upload de um chunk
        const uploadChunk = async (chunkIndex) => {
            const start = chunkIndex * chunkSize;
            const end = Math.min(start + chunkSize, file.size);
            const chunk = file.slice(start, end);
            const partNumber = chunkIndex + 1;

            // Obter URL para esta parte
            const partResponse = await window.apiModule.getPartUrl(uploadId, partNumber, key);
            if (!partResponse.success) {
                throw new Error(`Erro ao obter URL da parte ${partNumber}`);
            }

            // Upload da parte
            const etag = await window.apiModule.uploadChunk(partResponse.uploadUrl, chunk);
            
            // Atualizar progresso
            uploadedBytes += chunk.size;
            completedChunks++;
            const progress = (uploadedBytes / file.size) * 100;
            const elapsed = (Date.now() - startTime) / 1000;
            const speed = uploadedBytes / elapsed;
            
            if (progressCallback) {
                progressCallback(progress, speed);
            }

            return { PartNumber: partNumber, ETag: etag };
        };

        // Upload em lotes paralelos
        for (let i = 0; i < totalChunks; i += concurrency) {
            const batch = [];
            for (let j = 0; j < concurrency && (i + j) < totalChunks; j++) {
                batch.push(uploadChunk(i + j));
            }
            
            const batchResults = await Promise.all(batch);
            parts.push(...batchResults);
        }

        // Ordenar parts por PartNumber
        parts.sort((a, b) => a.PartNumber - b.PartNumber);

        // Completar multipart upload
        const completeResponse = await window.apiModule.completeMultipart(uploadId, parts, key);
        
        if (!completeResponse.success) {
            throw new Error('Erro ao finalizar upload');
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}