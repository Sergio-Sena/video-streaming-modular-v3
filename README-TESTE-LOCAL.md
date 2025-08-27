# 🧪 Teste Local - Video Streaming Modular

## 🚀 Como Testar Localmente

### **1. Iniciar Servidor Local**
```bash
cd video-streaming-modular
test-local.bat
```

### **2. URLs de Teste**
- **App Principal**: http://localhost:8080/index.html
- **Página de Teste**: http://localhost:8080/test.html
- **API Real**: https://4y3erwjgak.execute-api.us-east-1.amazonaws.com/prod

### **3. Testes Disponíveis**

#### **🔍 Página de Teste (test.html)**
- ✅ Status dos módulos JS
- 🔗 Conectividade com API AWS
- 🎮 Simulação de funcionalidades
- 📊 Console de debug

#### **🎬 App Principal (index.html)**
- 🔐 Login completo com MFA
- 📤 Upload de vídeos
- 🎥 Player de vídeos
- 🎨 Interface completa

### **4. Credenciais de Teste**
- **Email**: `sergiosenaadmin@sstech`
- **Senha**: `sergiosena`
- **MFA**: Código do Google Authenticator

### **5. Checklist de Validação**

#### **Frontend Modular**
- [ ] Módulos carregam sem erro
- [ ] AuthModule funciona
- [ ] VideosModule funciona  
- [ ] PlayerModule funciona
- [ ] APIModule conecta com AWS

#### **Funcionalidades**
- [ ] Login com MFA
- [ ] Listagem de vídeos
- [ ] Upload de arquivos
- [ ] Reprodução de vídeos
- [ ] Interface responsiva

#### **Integração AWS**
- [ ] API Gateway responde
- [ ] Autenticação JWT
- [ ] S3 upload funciona
- [ ] CloudFront serve vídeos

### **6. Problemas Comuns**

#### **CORS Error**
```
Solução: API já configurada para produção
Use: https://videos.sstechnologies-cloud.com
```

#### **Módulos não carregam**
```
Verificar: Console do navegador (F12)
Caminho: modules/*.js
```

#### **API não responde**
```
Testar: https://4y3erwjgak.execute-api.us-east-1.amazonaws.com/prod/auth
Método: OPTIONS
```

### **7. Debug**
- **F12**: Console do navegador
- **Network**: Requisições HTTP
- **test.html**: Debug integrado

---

**🎯 Objetivo**: Validar refatoração antes do deploy em produção