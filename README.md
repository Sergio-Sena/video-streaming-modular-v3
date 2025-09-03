# 🚀 Drive Online

Sistema de armazenamento em nuvem modular e serverless com reprodução de vídeos.

## 🏗️ Arquitetura Modular

```
modules/
├── auth/      # Autenticação e autorização ✅
├── files/     # Gestão de arquivos ✅
├── player/    # Reprodução de vídeos ✅
├── sharing/   # Compartilhamento (futuro)
└── admin/     # Administração (futuro)
```

## 🛠️ Stack Tecnológico

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: Python 3.12 + FastAPI + AWS Lambda
- **Infraestrutura**: AWS S3 + CloudFront + API Gateway
- **Vídeos**: Bucket público S3 para streaming direto

## 🚀 Desenvolvimento

```bash
# Instalar dependências
npm install

# Executar em desenvolvimento
npm run dev

# Build para produção
npm run build

# Deploy para AWS
npm run deploy
```

## 📦 Módulos

### ✅ AUTH (Completo)
- [x] Tela de login
- [x] Serviço de autenticação
- [x] Gerenciamento de tokens
- [x] Reset de senha
- [x] Backend Lambda
- [x] Infraestrutura AWS

### ✅ FILES (Completo)
- [x] Upload de arquivos (até 5GB)
- [x] Listagem de arquivos
- [x] Download de arquivos
- [x] Deletar arquivos
- [x] Informações de storage
- [x] Validação de tipos

### ✅ PLAYER (Completo)
- [x] Reprodução de vídeos HTML5
- [x] Cópia automática para bucket público
- [x] Streaming direto sem CORS
- [x] Suporte a múltiplos formatos
- [x] Player responsivo

### 🔄 SHARING (Futuro)
- [ ] Links de compartilhamento
- [ ] Permissões de acesso

### 🔄 ADMIN (Futuro)
- [ ] Painel administrativo
- [ ] Gestão de usuários

## 🎬 Arquitetura de Vídeos

### Fluxo de Upload → Reprodução
```
1. Upload → S3 Privado (drive-online-storage)
2. Auto-copy → S3 Público (automacao-video) se for vídeo
3. Listagem → Mostra todos os arquivos
4. Player → Reproduz do bucket público (sem CORS)
```

### Buckets S3
- **drive-online-storage** (privado): Todos os arquivos, backup, segurança
- **automacao-video** (público): Apenas vídeos para streaming

## 🌐 URLs

- **Desenvolvimento**: http://localhost:5173
- **Produção**: https://videos.sstechnologies-cloud.com
- **API**: https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod

## 🔧 Funcionalidades

### ✅ Implementadas
- Autenticação completa
- Upload de arquivos grandes
- Reprodução de vídeos
- Gestão de arquivos
- Interface responsiva
- Deploy automatizado

### 📊 Capacidades
- **Storage**: 5TB por usuário
- **Upload**: Até 5GB por arquivo
- **Vídeos**: Streaming direto
- **Formatos**: Todos os tipos de arquivo
- **Segurança**: JWT + AWS IAM

## 🎯 Como Usar

### Upload de Arquivos
1. Faça login na aplicação
2. Arraste arquivos ou clique em "Upload"
3. Vídeos são automaticamente otimizados para streaming

### Reprodução de Vídeos
1. Clique no botão "Play" em qualquer vídeo
2. Player HTML5 carrega automaticamente
3. Streaming direto sem buffering

### Gerenciamento
- **Deletar**: Remove do storage privado e público
- **Download**: Gera URL temporária segura
- **Listagem**: Ordenação por data/tipo/tamanho

## 🚀 Deploy

O projeto está configurado para deploy automático:
- **Frontend**: S3 + CloudFront
- **Backend**: AWS Lambda + API Gateway
- **Storage**: S3 com políticas de segurança

```bash
npm run deploy
```