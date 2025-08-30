# Video Streaming SStech v3.0

Sistema de streaming serverless com arquitetura desacoplada.

## 🏗️ Arquitetura

- **Backend**: Python 3.12 + AWS Lambda (5 serviços)
- **Frontend**: React 18 + TypeScript
- **AWS**: S3 + CloudFront + API Gateway + EventBridge + Secrets Manager

## 🚀 Status

### ✅ Implementado
- **auth-service-v3**: Autenticação + MFA + JWT
- **API Gateway**: Endpoints configurados (vyo27kghrh)
- **Secrets Manager**: Credenciais configuradas
- **Sanitização**: Caracteres especiais + emojis

### 🔄 Em Desenvolvimento
- Correção encoding Lambda auth-service
- upload-service-v3
- video-service-v3
- conversion-service-v3
- file-manager-service-v3
- Frontend React

## 📋 Credenciais

- **Email**: sergiosenaadmin@sstech
- **Senha**: sergiosena
- **MFA**: Google Authenticator (SI6JVTANE4GTFKADTDLK6GZN5F6NQ4EK)

## 🔧 Deploy

```bash
# Auth Service
cd backend/auth-service
aws lambda update-function-code --function-name auth-service-v3 --zip-file fileb://auth-service-v3.zip
```

## 📊 Recursos AWS

- **Lambda**: auth-service-v3 (arn:aws:lambda:us-east-1:969430605054:function:auth-service-v3)
- **API Gateway**: vyo27kghrh (auth-service-v3-api)
- **Secrets**: video-streaming-v3-user

## 🎯 Próximos Passos

1. Corrigir encoding do auth-service Lambda
2. Implementar upload-service-v3
3. Setup frontend React
4. Testes de integração

## 🌐 API Endpoints

- **Base URL**: https://vyo27kghrh.execute-api.us-east-1.amazonaws.com/prod
- **POST /auth/register**: Registro de usuário
- **POST /auth/login**: Login com MFA
- **POST /auth/verify**: Verificação de token
- **POST /auth/refresh**: Renovação de token