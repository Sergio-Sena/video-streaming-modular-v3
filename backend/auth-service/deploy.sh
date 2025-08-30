#!/bin/bash
# Deploy script para auth-service-v3

echo "Iniciando deploy do auth-service-v3..."

# Instalar dependências
echo "Instalando dependências..."
pip install -r requirements.txt -t src/

# Criar pacote ZIP
echo "Criando pacote de deploy..."
cd src
zip -r ../auth-service-v3.zip . -x "*.pyc" "*__pycache__*"
cd ..

# Deploy via SAM
echo "Fazendo deploy com SAM..."
sam build
sam deploy --guided --stack-name auth-service-v3-stack

echo "Deploy concluído!"
echo "Testando endpoints..."

# Obter URL da API
API_URL=$(aws cloudformation describe-stacks --stack-name auth-service-v3-stack --query 'Stacks[0].Outputs[?OutputKey==`AuthServiceApi`].OutputValue' --output text)

echo "API URL: $API_URL"
echo "Endpoints disponíveis:"
echo "- POST $API_URL/auth/login"
echo "- POST $API_URL/auth/refresh"
echo "- GET $API_URL/auth/mfa-setup?email=sergiosenaadmin@sstech"
echo "- POST $API_URL/auth/mfa-verify"