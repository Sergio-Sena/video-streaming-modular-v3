# 🔐 Auth Service - Drive Online

Backend Lambda para autenticação do Drive Online.

## 🏗️ **Arquitetura**

```
FastAPI + Mangum + AWS Lambda
├── JWT Authentication
├── Bcrypt Password Hashing  
├── AWS Secrets Manager
├── DynamoDB Users Table
└── Development Fallback
```

## 🚀 **Endpoints**

### **Públicos**
- `GET /` - Info do serviço
- `GET /health` - Health check
- `POST /auth/login` - Login com email/senha
- `POST /auth/forgot-password` - Recuperação de senha

### **Protegidos** (Bearer Token)
- `POST /auth/refresh` - Renovar token
- `POST /auth/logout` - Logout
- `GET /auth/me` - Info do usuário atual

## 🔧 **Desenvolvimento Local**

### **Instalar dependências**
```bash
pip install -r requirements.txt
pip install fastapi[all] uvicorn  # Para desenvolvimento
```

### **Executar localmente**
```bash
uvicorn src.main:app --reload --port 8000
```

### **Testar endpoints**
```bash
python test_local.py
```

## 📦 **Deploy AWS**

### **Automático**
```bash
python deploy.py
```

### **Manual**
```bash
# Criar zip
zip -r auth-service.zip src/ requirements.txt

# Upload via AWS CLI
aws lambda update-function-code \
  --function-name drive-online-auth-service \
  --zip-file fileb://auth-service.zip
```

## 🔒 **Segurança**

### **JWT Tokens**
- **Access Token**: 24h de validade
- **Refresh Token**: 30 dias de validade
- **Secret**: AWS Secrets Manager

### **Passwords**
- **Bcrypt**: 12 rounds de hash
- **Validação**: Pydantic models

### **Development Mode**
- **User**: senanetworker@gmail.com
- **Password**: sergiosena
- **Fallback**: Quando DynamoDB não disponível

## 🗄️ **DynamoDB Schema**

### **Tabela: drive-online-users**
```json
{
  "email": "senanetworker@gmail.com",
  "id": "user-uuid",
  "name": "Sergio Sena",
  "password_hash": "bcrypt-hash",
  "created_at": "2025-01-01T00:00:00Z",
  "is_active": true
}
```

## 🔧 **Configuração**

### **Variáveis de Ambiente**
```bash
AWS_REGION=us-east-1
DEVELOPMENT_MODE=false
DYNAMODB_TABLE_USERS=drive-online-users
SNS_TOPIC_ARN=arn:aws:sns:region:account:topic
```

### **AWS Secrets Manager**
```json
{
  "SecretId": "drive-online-jwt-secret",
  "SecretString": "your-super-secret-jwt-key"
}
```

## 📊 **Status**

- ✅ **FastAPI**: Configurado
- ✅ **JWT**: Implementado  
- ✅ **Bcrypt**: Implementado
- ✅ **Development Mode**: Funcionando
- ✅ **CORS**: Configurado
- ✅ **Error Handling**: Implementado
- 🔄 **DynamoDB**: A configurar
- 🔄 **Secrets Manager**: A configurar
- 🔄 **Deploy**: A fazer

## 🧪 **Testes**

```bash
# Teste completo
python test_local.py

# Teste individual
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"senanetworker@gmail.com","password":"sergiosena"}'
```