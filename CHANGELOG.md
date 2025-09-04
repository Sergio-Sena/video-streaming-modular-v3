# Changelog - Drive Online

## [4.0.1] - 2025-01-09

### 🎯 Melhorias
- **Modal Player**: Centralização automática na tela
- **Limpeza**: Script para limpar todas as mídias dos buckets S3

### 🔧 Correções
- Modal agora sempre abre no centro independente da posição do clique
- Removido posicionamento dinâmico baseado no botão

### 📁 Arquivos Modificados
- `src/modules/media-player/components/MediaPlayer.tsx`
- `cleanup_all_media.py` (novo)

### 🚀 Deploy
- Build e deploy realizados
- Cache CloudFront invalidado
- Sistema 100% operacional