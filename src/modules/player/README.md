# 🎥 Player Module

Módulo de reprodução de vídeos seguindo o padrão neon/cyberpunk do Drive Online v3.0.

## 📁 Estrutura

```
player/
├── components/
│   ├── VideoPlayer.tsx      # Player básico com controles customizados
│   ├── VideoList.tsx        # Lista de vídeos com grid responsivo
│   └── PlaylistPlayer.tsx   # Player avançado com playlist
├── services/
│   └── playerService.ts     # Serviços de gerenciamento de vídeos
└── index.ts                 # Exportações do módulo
```

## 🎨 Design System

### Cores Neon
- **Cyan**: `#00ffff` - Controles principais
- **Purple**: `#bf00ff` - Controles secundários
- **Pink**: `#ff0080` - Estados de hover
- **Blue**: `#0080ff` - Elementos informativos

### Componentes Visuais
- **Glass Cards**: Fundo translúcido com blur
- **Neon Borders**: Bordas com glow effect
- **Gradient Buttons**: Botões com gradiente neon
- **Animated Elements**: Pulse e glow animations

## 🚀 Componentes

### VideoPlayer
Player básico com controles customizados:
- Play/Pause com overlay
- Barra de progresso customizada
- Controle de volume
- Botão fullscreen
- Auto-hide dos controles

```tsx
<VideoPlayer
  src="video-url"
  title="Video Title"
  onClose={() => setShowPlayer(false)}
/>
```

### VideoList
Lista responsiva de vídeos:
- Grid adaptativo (1-3 colunas)
- Busca e filtros
- Ordenação por nome/data/tamanho
- Thumbnails placeholder
- Informações do arquivo

```tsx
<VideoList
  videos={videoFiles}
  onRefresh={loadVideos}
/>
```

### PlaylistPlayer
Player avançado com playlist:
- Navegação entre vídeos
- Sidebar com lista de reprodução
- Auto-play configurável
- Controles de anterior/próximo
- Indicador de vídeo atual

```tsx
<PlaylistPlayer
  videos={videoFiles}
  initialIndex={0}
  onClose={() => setShowPlayer(false)}
/>
```

## 🔧 Serviços

### PlayerService
Gerenciamento de estado e utilitários:

```typescript
// Configurar playlist
playerService.setPlaylist(videos)
playerService.setCurrentIndex(0)

// Navegação
playerService.playNext()
playerService.playPrevious()

// Utilitários
playerService.isVideoSupported(filename)
playerService.formatFileSize(bytes)
playerService.formatDuration(seconds)
```

## 📱 Responsividade

### Breakpoints
- **Mobile**: 320px - 768px (1 coluna)
- **Tablet**: 768px - 1024px (2 colunas)
- **Desktop**: 1024px+ (3 colunas)

### Touch Support
- Tap para play/pause
- Swipe para navegação (futuro)
- Touch-friendly controls (44px mínimo)

## 🎯 Funcionalidades

### Formatos Suportados
- **MP4**: Formato principal
- **WebM**: Suporte moderno
- **OGG**: Fallback
- **AVI/MOV/MKV**: Via conversão automática

### Controles
- ▶️ Play/Pause
- ⏮️ Anterior/Próximo
- 🔊 Volume
- ⏱️ Seek/Timeline
- 🔍 Fullscreen
- 📋 Playlist

### Estados
- Loading com spinner neon
- Error com fallback
- Empty state com ilustração
- Playing com controles dinâmicos

## 🔄 Integração

### Com Dashboard
```tsx
import { VideoList } from '../player'

// No Dashboard
<VideoList videos={videos} onRefresh={loadVideos} />
```

### Com API
```typescript
// Carregar vídeos da API
const loadVideos = async () => {
  const response = await fetch('/api/videos')
  const videos = await response.json()
  setVideos(videos)
}
```

### Com Upload
```typescript
// Após upload bem-sucedido
const handleUploadComplete = () => {
  loadVideos() // Recarrega lista
}
```

## 🎨 Customização

### Temas
Seguir variáveis CSS do projeto:
```css
--neon-cyan: #00ffff
--neon-purple: #bf00ff
--dark-900: #0a0a0f
--dark-800: #1a1a2e
```

### Animações
```css
.animate-pulse-neon
.animate-glow
.transition-all duration-300
```

### Glass Effect
```css
.glass-card {
  backdrop-blur-xl
  bg-dark-800/30
  border border-neon-cyan/20
}
```

## 🚀 Performance

### Otimizações
- Lazy loading de vídeos
- Thumbnail generation
- Progressive loading
- Memory cleanup

### Acessibilidade
- Keyboard navigation
- Screen reader support
- High contrast mode
- Focus indicators

## 📋 TODO

### Próximas Features
- [ ] Thumbnails automáticos
- [ ] Legendas/Subtitles
- [ ] Qualidade adaptativa
- [ ] Chromecast support
- [ ] Picture-in-picture
- [ ] Keyboard shortcuts
- [ ] Gesture controls
- [ ] Analytics de reprodução

### Melhorias
- [ ] Cache de thumbnails
- [ ] Preload de próximo vídeo
- [ ] Resumo de reprodução
- [ ] Favoritos/Bookmarks
- [ ] Compartilhamento
- [ ] Download offline

---

**Desenvolvido seguindo o padrão Drive Online v3.0**  
**Design System**: Neon/Cyberpunk  
**Framework**: React + TypeScript + Tailwind CSS