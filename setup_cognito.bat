@echo off
echo 🔐 Configurando Amazon Cognito...

REM Criar User Pool
echo Criando User Pool...
aws cognito-idp create-user-pool ^
    --pool-name "video-streaming-users" ^
    --policies "PasswordPolicy={MinimumLength=8,RequireUppercase=false,RequireLowercase=false,RequireNumbers=false,RequireSymbols=false}" ^
    --mfa-configuration OFF ^
    --account-recovery-setting "RecoveryMechanisms=[{Name=verified_email,Priority=1}]" ^
    --region us-east-1 > user-pool.json

REM Extrair User Pool ID
for /f "tokens=2 delims=:" %%a in ('findstr "Id" user-pool.json') do set USER_POOL_ID=%%a
set USER_POOL_ID=%USER_POOL_ID:"=%
set USER_POOL_ID=%USER_POOL_ID:,=%
set USER_POOL_ID=%USER_POOL_ID: =%

echo User Pool ID: %USER_POOL_ID%

REM Criar App Client
echo Criando App Client...
aws cognito-idp create-user-pool-client ^
    --user-pool-id %USER_POOL_ID% ^
    --client-name "video-streaming-client" ^
    --generate-secret false ^
    --explicit-auth-flows "ADMIN_NO_SRP_AUTH" "ALLOW_USER_PASSWORD_AUTH" "ALLOW_REFRESH_TOKEN_AUTH" ^
    --region us-east-1 > app-client.json

REM Extrair Client ID
for /f "tokens=2 delims=:" %%a in ('findstr "ClientId" app-client.json') do set CLIENT_ID=%%a
set CLIENT_ID=%CLIENT_ID:"=%
set CLIENT_ID=%CLIENT_ID:,=%
set CLIENT_ID=%CLIENT_ID: =%

echo Client ID: %CLIENT_ID%

REM Criar usuário de teste
echo Criando usuário de teste...
aws cognito-idp admin-create-user ^
    --user-pool-id %USER_POOL_ID% ^
    --username "sergiosenaadmin@sstech" ^
    --user-attributes Name=email,Value=sergiosenaadmin@sstech Name=email_verified,Value=true ^
    --temporary-password "TempPass123!" ^
    --message-action SUPPRESS ^
    --region us-east-1

REM Definir senha permanente
aws cognito-idp admin-set-user-password ^
    --user-pool-id %USER_POOL_ID% ^
    --username "sergiosenaadmin@sstech" ^
    --password "sergiosena" ^
    --permanent ^
    --region us-east-1

echo ✅ Cognito configurado!
echo User Pool ID: %USER_POOL_ID%
echo Client ID: %CLIENT_ID%
echo.
echo 📝 Atualize o frontend com estes IDs
pause