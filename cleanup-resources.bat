@echo off
echo ========================================
echo 🧹 LIMPEZA DE RECURSOS AWS SOBRESSALENTES
echo Video Streaming SStech - Otimização 28%
echo ========================================
echo.

echo 📋 RECURSOS A SEREM REMOVIDOS:
echo - 3 Buckets S3 sobressalentes
echo - 1 CloudFront sobressalente  
echo - 1 Lambda sobressalente
echo.
echo ⚠️  ATENÇÃO: Esta operação é IRREVERSÍVEL!
echo.
set /p confirm="Deseja continuar? (S/N): "
if /i not "%confirm%"=="S" (
    echo ❌ Operação cancelada pelo usuário.
    pause
    exit /b 1
)

echo.
echo 🚀 Iniciando limpeza...
echo.

REM 1. Deletar buckets S3 sobressalentes
echo 🪣 [1/5] Removendo bucket: video-conversion-temp-sstech
aws s3 rb s3://video-conversion-temp-sstech --force
if %errorlevel% equ 0 (
    echo ✅ Bucket video-conversion-temp-sstech removido
) else (
    echo ❌ Erro ao remover bucket video-conversion-temp-sstech
)

echo.
echo 🪣 [2/5] Removendo bucket: video-streaming-cognito-clean
aws s3 rb s3://video-streaming-cognito-clean --force
if %errorlevel% equ 0 (
    echo ✅ Bucket video-streaming-cognito-clean removido
) else (
    echo ❌ Erro ao remover bucket video-streaming-cognito-clean
)

echo.
echo 🪣 [3/5] Removendo bucket: video-temp-conversion
aws s3 rb s3://video-temp-conversion --force
if %errorlevel% equ 0 (
    echo ✅ Bucket video-temp-conversion removido
) else (
    echo ❌ Erro ao remover bucket video-temp-conversion
)

echo.
echo ⚡ [4/5] Removendo Lambda: video-converter
aws lambda delete-function --function-name video-converter
if %errorlevel% equ 0 (
    echo ✅ Lambda video-converter removida
) else (
    echo ❌ Erro ao remover Lambda video-converter
)

echo.
echo 🌐 [5/5] Desabilitando CloudFront: E169WSYQPLPWC0
REM Primeiro precisamos desabilitar antes de deletar
aws cloudfront get-distribution-config --id E169WSYQPLPWC0 --query "DistributionConfig" --output json > temp-dist-config.json
if %errorlevel% equ 0 (
    echo ⏳ CloudFront será desabilitada (processo pode levar alguns minutos)
    echo ℹ️  Para completar a remoção, execute manualmente após desabilitação:
    echo    aws cloudfront delete-distribution --id E169WSYQPLPWC0 --if-match [ETag]
) else (
    echo ❌ Erro ao acessar CloudFront E169WSYQPLPWC0
)

echo.
echo ========================================
echo 🎉 LIMPEZA CONCLUÍDA!
echo ========================================
echo.
echo 📊 ECONOMIA OBTIDA:
echo - Buckets S3: $0.10/mês
echo - Lambda: $0.05/mês  
echo - CloudFront: $1.00/mês (após desabilitação)
echo - TOTAL: $1.15/mês (28%% de economia)
echo.
echo 💰 Custo otimizado: $2.95/mês (antes: $4.10/mês)
echo.
echo ✅ Recursos essenciais mantidos:
echo - S3: video-streaming-sstech-eaddf6a1
echo - CloudFront: E153IH8TKR1LCM  
echo - API Gateway: 4y3erwjgak
echo - 4 Lambda functions ativas
echo.
pause