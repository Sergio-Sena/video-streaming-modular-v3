@echo off
echo 🚀 Deploy com Amazon Cognito...

REM 1. Setup Cognito (se ainda não foi feito)
if not exist "user-pool.json" (
    echo Configurando Cognito...
    call setup_cognito.bat
)

REM 2. Deploy Lambda Auth Cognito
echo Deployando Lambda Auth Cognito...
cd backend\modules
zip -r auth_cognito.zip auth_cognito.py utils.py

aws lambda update-function-code ^
    --function-name video-streaming-auth ^
    --zip-file fileb://auth_cognito.zip ^
    --region us-east-1

REM 3. Configurar API Gateway com Cognito Authorizer
echo Configurando API Gateway...
aws apigateway create-authorizer ^
    --rest-api-id YOUR_API_ID ^
    --name "CognitoAuthorizer" ^
    --type COGNITO_USER_POOLS ^
    --provider-arns "arn:aws:cognito-idp:us-east-1:ACCOUNT:userpool/USER_POOL_ID" ^
    --identity-source "method.request.header.Authorization" ^
    --region us-east-1

REM 4. Deploy Frontend
echo Deployando Frontend...
cd ..\..\frontend
aws s3 sync . s3://video-streaming-sstech --delete --region us-east-1

REM 5. Invalidar CloudFront
aws cloudfront create-invalidation ^
    --distribution-id E1234567890123 ^
    --paths "/*" ^
    --region us-east-1

echo ✅ Deploy Cognito concluído!
echo 📝 Atualize os IDs no frontend
pause