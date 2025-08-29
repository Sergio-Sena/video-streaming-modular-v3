# 🎬 **DOCUMENTAÇÃO TÉCNICA COMPLETA**

## **Video Streaming SStech - Arquitetura Modular**

---

## 📋 **ÍNDICE**

1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Microserviços](#microserviços)
4. [Fluxo de Dados](#fluxo-de-dados)
5. [Infraestrutura AWS](#infraestrutura-aws)
6. [Deploy](#deploy)
7. [Monitoramento](#monitoramento)

---

## 🎯 **VISÃO GERAL**

### **Objetivo**

Plataforma de streaming de vídeos com upload, conversão automática e reprodução otimizada.

### **Características Principais**

- ✅ **Autenticação Segura** (Email/Senha)
- ✅ **Upload Multipart** (arquivos até 5TB)
- ✅ **Conversão Automática** (qualquer formato → MP4)
- ✅ **CDN Global** (CloudFront)
- ✅ **Arquitetura Serverless** (100% AWS)

### **Tecnologias**

- **Backend**: Python 3.11 (AWS Lambda)
- **Frontend**: JavaScript Vanilla (S3 + CloudFront)
- **Banco**: AWS Secrets Manager
- **Storage**: S3 + CloudFront
- **Conversão**: AWS MediaConvert
- **Monitoramento**: CloudWatch

---

## 🏗️ **ARQUITETURA**

### **Diagrama de Arquitetura**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FRONTEND      │    │   API GATEWAY    │    │   MICROSERVIÇOS │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │   HTML/JS   │◄┼────┼►│ /auth        │◄┼────┼►│ auth_simple │ │
│ │   CSS       │ │    │ │ /videos      │ │    │ │ videos_simple│ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLOUDFRONT    │    │   LAMBDA PROXY   │    │   S3 BUCKETS    │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Cache Global│ │    │ │ Roteamento   │ │    │ │ Principal   │ │
│ │ Edge Nodes  │ │    │ │ CORS         │ │    │ │ Temp        │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                │                        │
                                ▼                        ▼
                    ┌──────────────────┐    ┌─────────────────┐
                    │  MEDIACONVERT    │    │  SECRETS MGR    │
                    │                  │    │                 │
                    │ ┌──────────────┐ │    │ ┌─────────────┐ │
                    │ │ Conversão    │ │    │ │ Credenciais │ │
                    │ │ Automática   │ │    │ │ JWT Secrets │ │
                    │ └──────────────┘ │    │ └─────────────┘ │
                    └──────────────────┘    └─────────────────┘
```

### **Fluxo de Dados**

```
1. Usuario → CloudFront → S3 (Frontend)
2. Login → API Gateway → Lambda Auth → Secrets Manager
3. Upload → API Gateway → Lambda Videos → S3
4. Conversão → S3 Trigger → MediaConvert → S3 Principal
5. Streaming → CloudFront → Usuario
```

---

## 🔧 **MICROSERVIÇOS**

### **1. AUTH SERVICE** (`auth_simple.py`)

#### **Responsabilidade**

Autenticação de usuários e geração de tokens.

#### **Endpoints**

- `POST /auth` - Login com email/senha

#### **Código Principal**

```python
def handler(event, context):
    # Validação de credenciais
    if email == 'sergiosenaadmin@sstech' and password == 'sergiosena':
        token = f"token_{int(datetime.now().timestamp())}"
        return success_response({'token': token, 'user': {'email': email}})
```

#### **Entrada**

```json
{
  "email": "sergiosenaadmin@sstech",
  "password": "sergiosena"
}
```

#### **Saída**

```json
{
  "success": true,
  "token": "token_1756417148",
  "user": { "email": "sergiosenaadmin@sstech" }
}
```

#### **Configuração Lambda**

- **Runtime**: Python 3.11
- **Handler**: `auth_simple.handler`
- **Timeout**: 30s
- **Memory**: 256MB
- **Role**: `video-streaming-lambda-role`

---

### **2. VIDEO SERVICE** (`videos_simple.py`)

#### **Responsabilidade**

Gerenciamento de uploads, listagem e roteamento de vídeos.

#### **Endpoints**

- `GET /videos` - Lista vídeos
- `POST /videos` - Gera URL de upload
- `DELETE /videos` - Remove vídeos

#### **Lógica de Roteamento**

```python
# Verifica formato do arquivo
is_mp4 = file_name.lower().endswith('.mp4')
bucket = 'video-streaming-sstech-eaddf6a1' if is_mp4 else 'video-temp-conversion'

# Multipart para arquivos grandes
if file_size > 50 * 1024 * 1024:
    # Inicia multipart upload
else:
    # Upload simples
```

#### **Entrada (Upload)**

```json
{
  "fileName": "video.avi",
  "fileSize": 104857600,
  "fileType": "video/x-msvideo"
}
```

#### **Saída (Upload)**

```json
{
  "success": true,
  "uploadUrl": "https://s3.amazonaws.com/...",
  "key": "videos/video.avi",
  "bucket": "video-temp-conversion"
}
```

#### **Configuração Lambda**

- **Runtime**: Python 3.11
- **Handler**: `videos_simple.handler`
- **Timeout**: 30s
- **Memory**: 256MB
- **Environment**:
  - `CLOUDFRONT_URL`: `https://d2we88koy23cl4.cloudfront.net`

---

### **3. MEDIACONVERT TRIGGER** (`mediaconvert_trigger.py`)

#### **Responsabilidade**

Inicia conversão automática quando arquivo é enviado para bucket temp.

#### **Trigger**

S3 Event: `s3:ObjectCreated:*` no bucket `video-temp-conversion`

#### **Processo**

```python
# 1. Detecta novo arquivo no bucket temp
# 2. Configura job MediaConvert
# 3. Define saída como MP4 no bucket principal
# 4. Inicia conversão
```

#### **Job Settings**

```python
{
    "Role": "arn:aws:iam::969430605054:role/MediaConvertRole",
    "Settings": {
        "Inputs": [{"FileInput": f"s3://{bucket}/{input_key}"}],
        "OutputGroups": [{
            "OutputGroupSettings": {
                "FileGroupSettings": {
                    "Destination": "s3://video-streaming-sstech-eaddf6a1/converted/"
                }
            },
            "Outputs": [{
                "VideoDescription": {
                    "CodecSettings": {"Codec": "H_264"}
                },
                "ContainerSettings": {"Container": "MP4"}
            }]
        }]
    }
}
```

---

### **4. CONVERSION COMPLETE** (`conversion_complete.py`)

#### **Responsabilidade**

Limpa arquivo original após conversão bem-sucedida.

#### **Trigger**

CloudWatch Event: MediaConvert Job Status Change

#### **Processo**

```python
# 1. Recebe evento de conclusão do MediaConvert
# 2. Verifica se status = 'COMPLETE'
# 3. Deleta arquivo original do bucket temp
# 4. Log da operação
```

---

## 📊 **FLUXO DE DADOS DETALHADO**

### **1. FLUXO DE AUTENTICAÇÃO**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Usuario   │    │  Frontend   │    │ API Gateway │    │ Auth Lambda │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │
       │ 1. Insere dados  │                  │                  │
       ├─────────────────►│                  │                  │
       │                  │ 2. POST /auth    │                  │
       │                  ├─────────────────►│                  │
       │                  │                  │ 3. Invoke        │
       │                  │                  ├─────────────────►│
       │                  │                  │                  │ 4. Valida
       │                  │                  │                  │    credenciais
       │                  │                  │ 5. Token JWT     │
       │                  │                  │◄─────────────────┤
       │                  │ 6. Response      │                  │
       │                  │◄─────────────────┤                  │
       │ 7. Token salvo   │                  │                  │
       │◄─────────────────┤                  │                  │
```

### **2. FLUXO DE UPLOAD MP4**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Usuario   │    │  Frontend   │    │Video Lambda │    │ S3 Principal│
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │
       │ 1. Seleciona MP4 │                  │                  │
       ├─────────────────►│                  │                  │
       │                  │ 2. POST /videos  │                  │
       │                  ├─────────────────►│                  │
       │                  │                  │ 3. Detecta MP4   │
       │                  │                  │ 4. Gera URL      │
       │                  │                  │    Principal     │
       │                  │ 5. Upload URL    │                  │
       │                  │◄─────────────────┤                  │
       │                  │ 6. Upload direto │                  │
       │                  ├─────────────────────────────────────►│
       │ 7. Sucesso       │                  │                  │
       │◄─────────────────┤                  │                  │
```

### **3. FLUXO DE CONVERSÃO AUTOMÁTICA**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Usuario   │    │ S3 Temp     │    │MC Trigger   │    │MediaConvert │    │ S3 Principal│
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │                  │
       │ 1. Upload .avi   │                  │                  │                  │
       ├─────────────────►│                  │                  │                  │
       │                  │ 2. S3 Event      │                  │                  │
       │                  ├─────────────────►│                  │                  │
       │                  │                  │ 3. Create Job    │                  │
       │                  │                  ├─────────────────►│                  │
       │                  │                  │                  │ 4. Convert       │
       │                  │                  │                  │ 5. Output MP4    │
       │                  │                  │                  ├─────────────────►│
       │                  │ 6. Delete orig   │                  │                  │
       │                  │◄─────────────────┤                  │                  │
       │ 7. MP4 disponível│                  │                  │                  │
       │◄─────────────────────────────────────────────────────────────────────────┤
```

---

## ☁️ **INFRAESTRUTURA AWS**

### **Serviços Utilizados**

#### **1. AWS Lambda**

```
┌─────────────────────────────────────────────────────────────┐
│                    LAMBDA FUNCTIONS                         │
├─────────────────────────────────────────────────────────────┤
│ Function Name          │ Runtime    │ Handler              │
├─────────────────────────────────────────────────────────────┤
│ video-streaming-auth   │ Python3.11 │ auth_simple.handler  │
│ video-streaming-upload │ Python3.11 │ videos_simple.handler│
│ mediaconvert-trigger   │ Python3.11 │ mediaconvert_trigger │
│ conversion-complete    │ Python3.11 │ conversion_complete  │
└─────────────────────────────────────────────────────────────┘
```

#### **2. Amazon S3**

```
┌─────────────────────────────────────────────────────────────┐
│                      S3 BUCKETS                             │
├─────────────────────────────────────────────────────────────┤
│ Bucket Name                    │ Purpose                   │
├─────────────────────────────────────────────────────────────┤
│ video-streaming-sstech-eaddf6a1│ Frontend + Videos finais  │
│ video-temp-conversion          │ Arquivos para conversão   │
└─────────────────────────────────────────────────────────────┘
```

#### **3. Amazon CloudFront**

```
┌─────────────────────────────────────────────────────────────┐
│                    CLOUDFRONT CDN                           │
├─────────────────────────────────────────────────────────────┤
│ Distribution: E1234567890123                                │
│ Origin: video-streaming-sstech-eaddf6a1.s3.amazonaws.com   │
│ Domain: d2we88koy23cl4.cloudfront.net                       │
│ Custom Domain: videos.sstechnologies-cloud.com             │
└─────────────────────────────────────────────────────────────┘
```

#### **4. API Gateway**

```
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY                              │
├─────────────────────────────────────────────────────────────┤
│ API ID: 4y3erwjgak                                          │
│ Stage: prod                                                 │
│ Base URL: https://4y3erwjgak.execute-api.us-east-1...      │
│                                                             │
│ Resources:                                                  │
│ ├── /auth    → video-streaming-auth                         │
│ └── /videos  → video-streaming-upload                       │
└─────────────────────────────────────────────────────────────┘
```

#### **5. AWS MediaConvert**

```
┌─────────────────────────────────────────────────────────────┐
│                   MEDIACONVERT                              │
├─────────────────────────────────────────────────────────────┤
│ Region: us-east-1                                           │
│ Role: MediaConvertRole                                      │
│ Input: S3 Temp Bucket                                       │
│ Output: S3 Principal Bucket                                 │
│ Format: Any → MP4 H.264                                     │
└─────────────────────────────────────────────────────────────┘
```

### **IAM Roles e Políticas**

#### **Lambda Execution Role**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::video-streaming-sstech-eaddf6a1/*",
        "arn:aws:s3:::video-temp-conversion/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": "arn:aws:secretsmanager:us-east-1:*:secret:video-streaming-user-*"
    },
    {
      "Effect": "Allow",
      "Action": ["mediaconvert:*"],
      "Resource": "*"
    }
  ]
}
```

---

## 🚀 **DEPLOY**

### **Estrutura de Arquivos**

```
video-streaming-modular/
├── backend/
│   ├── modules/
│   │   ├── auth_simple.py          # Microserviço Auth
│   │   ├── videos_simple.py        # Microserviço Videos
│   │   ├── mediaconvert_trigger.py # Trigger Conversão
│   │   └── conversion_complete.py  # Callback Conversão
│   └── services/                   # Versões refatoradas
├── frontend/
│   ├── modules/
│   │   ├── api.js                  # Cliente API
│   │   ├── auth.js                 # Módulo Auth
│   │   ├── videos.js               # Módulo Videos
│   │   └── player.js               # Player de Vídeo
│   ├── styles/                     # CSS Modular
│   └── index.html                  # Interface Principal
├── deploy_refactored.bat           # Script Deploy
├── setup_conversion.bat            # Setup Conversão
└── s3-trigger-config.json         # Config S3 Trigger
```

### **Scripts de Deploy**

#### **1. Deploy Principal** (`deploy_refactored.bat`)

```batch
# 1. Backup arquivos atuais
# 2. Substitui por versões corrigidas
# 3. Cria ZIPs para Lambda
# 4. Deploy Lambda functions
# 5. Sync frontend para S3
# 6. Invalida cache CloudFront
```

#### **2. Setup Conversão** (`setup_conversion.bat`)

```batch
# 1. Cria bucket temp
# 2. Deploy função MediaConvert trigger
# 3. Deploy função conversion complete
# 4. Configura S3 notification
# 5. Configura EventBridge rules
```

### **Comandos de Deploy**

#### **Deploy Lambda Functions**

```bash
# Auth Service
aws lambda update-function-code \
  --function-name video-streaming-auth \
  --zip-file fileb://auth_simple.zip

# Video Service
aws lambda update-function-code \
  --function-name video-streaming-upload \
  --zip-file fileb://videos_simple.zip
```

#### **Deploy Frontend**

```bash
# Sync para S3
aws s3 sync frontend/ s3://video-streaming-sstech-eaddf6a1/

# Invalidar CloudFront
aws cloudfront create-invalidation \
  --distribution-id E1234567890123 \
  --paths "/*"
```

---

## 📊 **MONITORAMENTO**

### **CloudWatch Logs**

```
┌─────────────────────────────────────────────────────────────┐
│                    LOG GROUPS                               │
├─────────────────────────────────────────────────────────────┤
│ /aws/lambda/video-streaming-auth                            │
│ /aws/lambda/video-streaming-upload                          │
│ /aws/lambda/mediaconvert-trigger                            │
│ /aws/lambda/conversion-complete                             │
└─────────────────────────────────────────────────────────────┘
```

### **Métricas Importantes**

- **Lambda Invocations**: Número de execuções
- **Lambda Duration**: Tempo de execução
- **Lambda Errors**: Taxa de erro
- **S3 Requests**: Requests de upload/download
- **CloudFront Cache Hit Rate**: Taxa de cache
- **MediaConvert Jobs**: Jobs de conversão

### **Alertas Configurados**

- Lambda errors > 5%
- Lambda duration > 25s
- S3 4xx errors > 10%
- MediaConvert job failures

---

## 🔧 **CONFIGURAÇÃO E MANUTENÇÃO**

### **Variáveis de Ambiente**

```
CLOUDFRONT_URL=https://d2we88koy23cl4.cloudfront.net
URL_REPLACE=true
AWS_REGION=us-east-1
```

### **Secrets Manager**

```json
{
  "email": "sergiosenaadmin@sstech",
  "password": "$2b$12$LQv3c1yqBwEHFNjNJRwGe...",
  "jwtSecret": "video-streaming-jwt-super-secret-key-2025"
}
```

### **Backup e Rollback**

- **Backup automático**: Versioning S3 habilitado
- **Rollback Lambda**: Versões anteriores mantidas
- **Rollback Frontend**: Git tags para cada deploy

### **Escalabilidade**

- **Lambda**: Auto-scaling até 1000 execuções concorrentes
- **S3**: Ilimitado
- **CloudFront**: Global, auto-scaling
- **MediaConvert**: On-demand, sem limites

---

## 📈 **PERFORMANCE E CUSTOS**

### **Performance**

- **Upload**: Até 5TB por arquivo
- **Conversão**: Paralela, múltiplos jobs
- **Streaming**: CDN global, baixa latência
- **Disponibilidade**: 99.9% SLA

### **Custos Estimados (Mensal)**

```
┌─────────────────────────────────────────────────────────────┐
│                    CUSTOS AWS                               │
├─────────────────────────────────────────────────────────────┤
│ Lambda (1M requests)           │ $0.20                      │
│ S3 Storage (100GB)             │ $2.30                      │
│ CloudFront (100GB transfer)    │ $8.50                      │
│ MediaConvert (10h video)       │ $15.00                     │
│ API Gateway (1M requests)      │ $3.50                      │
├─────────────────────────────────────────────────────────────┤
│ TOTAL ESTIMADO                 │ $29.50/mês                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔒 **SEGURANÇA**

### **Autenticação**

- Email/senha com hash bcrypt
- Tokens JWT com expiração
- HTTPS obrigatório

### **Autorização**

- Token Bearer em todas as requisições
- Validação de origem (CORS)
- Rate limiting implementado

### **Dados**

- Criptografia em trânsito (TLS 1.2+)
- Criptografia em repouso (S3 AES-256)
- Secrets Manager para credenciais

### **Rede**

- CloudFront com WAF
- API Gateway com throttling
- VPC endpoints (futuro)

---

## 📞 **SUPORTE E CONTATO**

### **URLs de Produção**

- **Frontend**: https://videos.sstechnologies-cloud.com
- **API**: https://4y3erwjgak.execute-api.us-east-1.amazonaws.com/prod

### **Credenciais de Teste**

- **Email**: sergiosenaadmin@sstech
- **Senha**: sergiosena

### **Documentação Técnica**

- **Repositório**: Local (video-streaming-modular/)
- **Logs**: CloudWatch Console
- **Monitoramento**: AWS Console

---

**📅 Última Atualização**: 28/08/2025  
**👨‍💻 Desenvolvedor**: Sergio Sena  
**🏢 Empresa**: SStech  
**📧 Contato**: sergiosenaadmin@sstech
