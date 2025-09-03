# 🗑️ Como Remover o Player (Rollback)

## 1. FRONTEND - Reverter FileList.tsx
```typescript
// Substituir por:
if (targetFile.type.startsWith('video/')) {
  videoUrl = await fileService.getDownloadUrl(targetFile.id)
}
```

## 2. BACKEND - Remover 3 funções (opcional)
- `is_video_file()`
- `copy_to_public_bucket()`  
- Endpoint `/files/upload-complete`

## 3. INFRAESTRUTURA (opcional)
- Manter bucket `automacao-video` (não afeta nada)
- Ou deletar se não usar mais

## RESULTADO
- ✅ Upload: Funciona normal
- ✅ Listagem: Funciona normal  
- ✅ Delete: Funciona normal
- ✅ Download: Funciona normal
- ❌ Player vídeo: Volta ao problema CORS

## IMPACTO: ZERO
Remover o player não quebra nada, apenas vídeos voltam a não reproduzir.