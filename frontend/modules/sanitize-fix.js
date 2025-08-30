// Correção temporária para sanitização de nomes de arquivos
function sanitizeFileName(filename) {
    let sanitized = filename
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/[^a-zA-Z0-9._-]/g, '_')
        .replace(/_+/g, '_')
        .replace(/^_|_$/g, '');
    
    if (!sanitized) {
        sanitized = 'video_' + Date.now();
    }
    
    return sanitized;
}

// Aplicar correção no VideosModule quando carregar
document.addEventListener('DOMContentLoaded', function() {
    if (window.videosModule) {
        window.videosModule.sanitizeFileName = sanitizeFileName;
        console.log('🧹 Sanitização aplicada ao videosModule');
    }
    
    // Também aplicar ao prototype
    if (window.VideosModule) {
        window.VideosModule.prototype.sanitizeFileName = sanitizeFileName;
        console.log('🧹 Sanitização aplicada ao prototype');
    }
});

console.log('🧹 Script de sanitização carregado');