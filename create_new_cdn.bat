@echo off
echo 🚀 Criando novo bucket e CloudFront...

REM Criar novo bucket S3
set BUCKET_NAME=video-streaming-cognito-%RANDOM%
echo Criando bucket: %BUCKET_NAME%

aws s3 mb s3://%BUCKET_NAME% --region us-east-1

REM Configurar bucket para hosting
aws s3 website s3://%BUCKET_NAME% --index-document index.html --error-document index.html --region us-east-1

REM Upload dos arquivos
echo Fazendo upload dos arquivos...
cd frontend
aws s3 sync . s3://%BUCKET_NAME% --region us-east-1

REM Criar distribuição CloudFront
echo Criando CloudFront...
aws cloudfront create-distribution --distribution-config file://../cloudfront-new-config.json --region us-east-1

echo ✅ Novo CDN criado!
echo 📝 Bucket: %BUCKET_NAME%
pause