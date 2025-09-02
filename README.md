# 🚀 Drive Online

Sistema de armazenamento em nuvem modular e serverless.

## 🏗️ Arquitetura Modular

```
modules/
├── auth/      # Autenticação e autorização
├── files/     # Gestão de arquivos
├── sharing/   # Compartilhamento
└── admin/     # Administração
```

## 🛠️ Stack Tecnológico

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: Python 3.12 + FastAPI + AWS Lambda
- **Infraestrutura**: AWS CDK + Serverless

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

### ✅ AUTH (Implementado)
- [x] Tela de login
- [x] Serviço de autenticação
- [x] Gerenciamento de tokens
- [ ] Backend Lambda
- [ ] Infraestrutura AWS

### 🔄 FILES (Próximo)
- [ ] Upload de arquivos
- [ ] Listagem de arquivos
- [ ] Download de arquivos

### 🔄 SHARING (Futuro)
- [ ] Links de compartilhamento
- [ ] Permissões de acesso

### 🔄 ADMIN (Futuro)
- [ ] Painel administrativo
- [ ] Gestão de usuários

## 🌐 URLs

- **Desenvolvimento**: http://localhost:3000
- **Produção**: https://drive-online.com (a configurar)