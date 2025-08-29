/**
 * Upload Manager - Sistema avançado de upload com navegação
 */
class UploadManager {
    constructor() {
        this.currentPath = [];
        this.fileTree = {};
        this.selectedFiles = new Set();
        this.allFiles = [];
        this.init();
    }

    init() {
        this.createModal();
        this.bindEvents();
    }

    createModal() {
        const modal = document.createElement('div');
        modal.className = 'upload-modal';
        modal.id = 'uploadModal';
        modal.innerHTML = `
            <div class="upload-container">
                <div class="upload-header">
                    <h3>📁 Gerenciador de Upload</h3>
                    <button class="close-btn" id="closeUploadModal">&times;</button>
                </div>
                
                <div class="upload-body">
                    <div class="file-browser">
                        <div class="breadcrumb" id="breadcrumb">
                            <span class="breadcrumb-item current">Selecionar Arquivos</span>
                        </div>
                        
                        <div class="file-list" id="fileList">
                            <div style="text-align: center; padding: 40px; color: #666;">
                                <div style="font-size: 48px; margin-bottom: 20px;">📂</div>
                                <p>Clique em "Selecionar Arquivos" ou "Selecionar Pastas" para começar</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="upload-sidebar">
                        <div class="upload-actions">
                            <button class="action-btn btn-primary" id="selectFiles">
                                📄 Selecionar Arquivos
                            </button>
                            <button class="action-btn btn-primary" id="selectFolders">
                                📁 Selecionar Pastas
                            </button>
                            <button class="action-btn btn-secondary" id="clearSelection">
                                🗑️ Limpar Seleção
                            </button>
                        </div>
                        
                        <div class="selected-files">
                            <h4>Arquivos Selecionados (<span id="selectedCount">0</span>)</h4>
                            <div id="selectedList"></div>
                        </div>
                    </div>
                </div>
                
                <div class="upload-footer">
                    <div class="upload-stats">
                        <span id="totalSize">0 MB</span> • <span id="totalFiles">0 arquivos</span>
                    </div>
                    <div class="upload-buttons">
                        <button class="action-btn btn-secondary" id="cancelUpload">Cancelar</button>
                        <button class="action-btn btn-primary" id="startUpload" disabled>
                            ⬆️ Fazer Upload
                        </button>
                    </div>
                </div>
            </div>
            
            <input type="file" id="hiddenFileInput" multiple accept="video/*" style="display: none;">
            <input type="file" id="hiddenFolderInput" webkitdirectory multiple style="display: none;">
        `;
        
        document.body.appendChild(modal);
    }

    bindEvents() {
        // Abrir modal
        const uploadBtn = document.getElementById('quickUploadBtn');
        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => this.show());
        }

        // Fechar modal
        document.getElementById('closeUploadModal').addEventListener('click', () => this.hide());
        document.getElementById('cancelUpload').addEventListener('click', () => this.hide());

        // Seleção de arquivos
        document.getElementById('selectFiles').addEventListener('click', () => {
            const input = document.getElementById('hiddenFileInput');
            input.value = ''; // Reset
            input.click();
        });

        document.getElementById('selectFolders').addEventListener('click', () => {
            const input = document.getElementById('hiddenFolderInput');
            input.value = ''; // Reset
            input.click();
        });

        // Input handlers
        document.getElementById('hiddenFileInput').addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelection(e.target.files, 'files');
            }
        });

        document.getElementById('hiddenFolderInput').addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelection(e.target.files, 'folders');
            }
        });

        // Ações
        document.getElementById('clearSelection').addEventListener('click', () => {
            this.clearSelection();
        });

        document.getElementById('startUpload').addEventListener('click', () => {
            this.startUpload();
        });

        // Fechar ao clicar fora
        document.getElementById('uploadModal').addEventListener('click', (e) => {
            if (e.target.id === 'uploadModal') {
                this.hide();
            }
        });
    }

    show() {
        document.getElementById('uploadModal').classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    hide() {
        document.getElementById('uploadModal').classList.remove('active');
        document.body.style.overflow = '';
        this.clearSelection();
    }

    handleFileSelection(files, type) {
        console.log(`📁 ${type === 'files' ? 'Arquivos' : 'Pastas'} selecionados: ${files.length}`);
        
        // Adicionar aos arquivos existentes em vez de substituir
        const newFiles = Array.from(files);
        this.allFiles = [...this.allFiles, ...newFiles];
        
        this.buildFileTree();
        this.renderFileTree();
        this.updateBreadcrumb();
        
        // Auto-selecionar novos arquivos
        if (type === 'files') {
            newFiles.forEach(file => {
                const fileId = file.name;
                this.selectedFiles.add(fileId);
            });
        }
        
        this.updateSelection();
    }

    buildFileTree() {
        this.fileTree = { folders: {}, files: [] };
        
        this.allFiles.forEach(file => {
            if (file.webkitRelativePath) {
                // Arquivo de pasta
                const pathParts = file.webkitRelativePath.split('/');
                const fileName = pathParts.pop();
                
                let current = this.fileTree;
                pathParts.forEach(part => {
                    if (!current.folders[part]) {
                        current.folders[part] = { folders: {}, files: [] };
                    }
                    current = current.folders[part];
                });
                
                current.files.push({
                    name: fileName,
                    file: file,
                    size: file.size,
                    type: file.type,
                    path: file.webkitRelativePath
                });
            } else {
                // Arquivo individual
                this.fileTree.files.push({
                    name: file.name,
                    file: file,
                    size: file.size,
                    type: file.type,
                    path: file.name
                });
            }
        });
    }

    renderFileTree() {
        const fileList = document.getElementById('fileList');
        const current = this.getCurrentFolder();
        
        let html = '';
        
        // Botão voltar
        if (this.currentPath.length > 0) {
            html += `
                <div class="file-item" onclick="uploadManager.navigateUp()">
                    <div class="file-icon">⬅️</div>
                    <div class="file-info">
                        <div class="file-name">.. (Voltar)</div>
                        <div class="file-details">Pasta anterior</div>
                    </div>
                </div>
            `;
        }
        
        // Pastas
        Object.keys(current.folders).forEach(folderName => {
            const folderPath = [...this.currentPath, folderName].join('/');
            html += `
                <div class="file-item" ondblclick="uploadManager.navigateToFolder('${folderName}')">
                    <input type="checkbox" class="file-checkbox" onchange="uploadManager.toggleFolder('${folderPath}', this.checked)">
                    <div class="file-icon">📁</div>
                    <div class="file-info">
                        <div class="file-name">${folderName}</div>
                        <div class="file-details">Pasta • ${this.countFilesInFolder(current.folders[folderName])} arquivos</div>
                    </div>
                </div>
            `;
        });
        
        // Arquivos
        current.files.forEach((fileInfo, index) => {
            const fileId = this.currentPath.length > 0 ? 
                `${this.currentPath.join('/')}/${fileInfo.name}` : 
                fileInfo.name;
            const isSelected = this.selectedFiles.has(fileId) || this.selectedFiles.has(fileInfo.name);
            
            html += `
                <div class="file-item ${isSelected ? 'selected' : ''}" onclick="uploadManager.selectFileItem('${fileId}', '${fileInfo.name}')">
                    <input type="checkbox" class="file-checkbox" ${isSelected ? 'checked' : ''} 
                           onchange="uploadManager.toggleFile('${fileId}', '${fileInfo.name}', this.checked)" onclick="event.stopPropagation()">
                    <div class="file-icon">${this.getFileIcon(fileInfo.type)}</div>
                    <div class="file-info">
                        <div class="file-name">${fileInfo.name}</div>
                        <div class="file-details">${this.formatFileSize(fileInfo.size)} • ${fileInfo.type || 'Arquivo'}</div>
                    </div>
                </div>
            `;
        });
        
        if (html === '' && this.currentPath.length === 0) {
            html = `
                <div style="text-align: center; padding: 40px; color: #666;">
                    <div style="font-size: 48px; margin-bottom: 20px;">📂</div>
                    <p>Nenhum arquivo selecionado</p>
                </div>
            `;
        }
        
        fileList.innerHTML = html;
    }

    getCurrentFolder() {
        let current = this.fileTree;
        this.currentPath.forEach(part => {
            current = current.folders[part];
        });
        return current;
    }

    navigateToFolder(folderName) {
        this.currentPath.push(folderName);
        this.renderFileTree();
        this.updateBreadcrumb();
    }

    navigateUp() {
        this.currentPath.pop();
        this.renderFileTree();
        this.updateBreadcrumb();
    }

    updateBreadcrumb() {
        const breadcrumb = document.getElementById('breadcrumb');
        let html = '<span class="breadcrumb-item" onclick="uploadManager.navigateToRoot()">📁 Raiz</span>';
        
        this.currentPath.forEach((part, index) => {
            const isLast = index === this.currentPath.length - 1;
            if (isLast) {
                html += ` / <span class="breadcrumb-item current">${part}</span>`;
            } else {
                html += ` / <span class="breadcrumb-item" onclick="uploadManager.navigateToPath(${index + 1})">${part}</span>`;
            }
        });
        
        breadcrumb.innerHTML = html;
    }

    navigateToRoot() {
        this.currentPath = [];
        this.renderFileTree();
        this.updateBreadcrumb();
    }

    navigateToPath(depth) {
        this.currentPath = this.currentPath.slice(0, depth);
        this.renderFileTree();
        this.updateBreadcrumb();
    }

    toggleFile(fileId, fileName, checked) {
        if (checked) {
            this.selectedFiles.add(fileId);
            this.selectedFiles.add(fileName); // Adicionar ambos para compatibilidade
        } else {
            this.selectedFiles.delete(fileId);
            this.selectedFiles.delete(fileName);
        }
        this.updateSelection();
        this.renderFileTree(); // Re-render para atualizar visual
    }
    
    selectFileItem(fileId, fileName) {
        // Clique no item do arquivo para seleção
        const isSelected = this.selectedFiles.has(fileId) || this.selectedFiles.has(fileName);
        this.toggleFile(fileId, fileName, !isSelected);
        
        // Atualizar checkbox
        const checkbox = event.currentTarget.querySelector('.file-checkbox');
        if (checkbox) {
            checkbox.checked = !isSelected;
        }
    }

    toggleFolder(folderPath, checked) {
        // Implementar seleção de pasta completa
        const pathParts = folderPath.split('/');
        let current = this.fileTree;
        
        pathParts.forEach(part => {
            current = current.folders[part];
        });
        
        this.toggleFolderRecursive(current, folderPath, checked);
        this.updateSelection();
        this.renderFileTree();
    }

    toggleFolderRecursive(folder, basePath, checked) {
        // Selecionar todos os arquivos da pasta
        folder.files.forEach(fileInfo => {
            const fileId = `${basePath}/${fileInfo.name}`;
            if (checked) {
                this.selectedFiles.add(fileId);
            } else {
                this.selectedFiles.delete(fileId);
            }
        });
        
        // Recursivo para subpastas
        Object.keys(folder.folders).forEach(subFolderName => {
            this.toggleFolderRecursive(
                folder.folders[subFolderName], 
                `${basePath}/${subFolderName}`, 
                checked
            );
        });
    }

    updateSelection() {
        const selectedCount = this.selectedFiles.size;
        const selectedFiles = this.getSelectedFileObjects();
        const totalSize = selectedFiles.reduce((sum, file) => sum + file.size, 0);
        
        document.getElementById('selectedCount').textContent = selectedCount;
        document.getElementById('totalFiles').textContent = `${selectedCount} arquivos`;
        document.getElementById('totalSize').textContent = this.formatFileSize(totalSize);
        document.getElementById('startUpload').disabled = selectedCount === 0;
        
        // Atualizar lista de selecionados
        const selectedList = document.getElementById('selectedList');
        selectedList.innerHTML = selectedFiles.slice(0, 10).map(file => 
            `<div class="selected-item">${file.name}</div>`
        ).join('') + (selectedFiles.length > 10 ? `<div class="selected-item">... e mais ${selectedFiles.length - 10}</div>` : '');
    }

    getSelectedFileObjects() {
        const selected = [];
        this.selectedFiles.forEach(fileId => {
            const file = this.findFileById(fileId);
            if (file) selected.push(file);
        });
        return selected;
    }

    findFileById(fileId) {
        return this.allFiles.find(file => {
            const id = file.webkitRelativePath || file.name;
            const cleanFileId = fileId.replace(/^.*\//, ''); // Pegar apenas o nome do arquivo
            return id === fileId || 
                   file.name === fileId || 
                   file.name === cleanFileId ||
                   id === cleanFileId ||
                   id.endsWith(cleanFileId);
        });
    }

    clearSelection() {
        this.selectedFiles.clear();
        this.allFiles = [];
        this.fileTree = {};
        this.currentPath = [];
        this.updateSelection();
        this.renderFileTree();
        this.updateBreadcrumb();
    }

    async startUpload() {
        const selectedFiles = this.getSelectedFileObjects();
        if (selectedFiles.length === 0) return;
        
        console.log(`🚀 Iniciando upload de ${selectedFiles.length} arquivos`);
        
        this.hide();
        
        // Usar o sistema de upload existente
        if (window.videosModule && window.videosModule.handleFileUpload) {
            await window.videosModule.handleFileUpload(selectedFiles);
        }
    }

    countFilesInFolder(folder) {
        let count = folder.files.length;
        Object.values(folder.folders).forEach(subFolder => {
            count += this.countFilesInFolder(subFolder);
        });
        return count;
    }

    getFileIcon(type) {
        if (type.startsWith('video/')) return '🎥';
        if (type.startsWith('image/')) return '🖼️';
        if (type.startsWith('audio/')) return '🎵';
        return '📄';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.uploadManager = new UploadManager();
});