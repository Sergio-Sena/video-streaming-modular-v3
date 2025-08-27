@echo off
echo ========================================
echo   DEPLOY VIDEO STREAMING MODULAR
echo ========================================

echo.
echo [1/4] Preparando backend Python...
cd backend
if exist auth.zip del auth.zip
if exist videos.zip del videos.zip

echo Criando pacote auth.zip...
powershell -Command "Compress-Archive -Path 'modules\auth.py','modules\utils.py','requirements.txt' -DestinationPath 'auth.zip' -Force"

echo Criando pacote videos.zip...
powershell -Command "Compress-Archive -Path 'modules\videos.py','modules\utils.py','requirements.txt' -DestinationPath 'videos.zip' -Force"

echo.
echo [2/4] Atualizando Lambda Auth...
aws lambda update-function-code --function-name video-streaming-auth --zip-file fileb://auth.zip

echo.
echo [3/4] Atualizando Lambda Videos...
aws lambda update-function-code --function-name video-streaming-upload --zip-file fileb://videos.zip

cd ..\frontend

echo.
echo [4/4] Atualizando Frontend...
aws s3 sync . s3://video-streaming-sstech-eaddf6a1/ --exclude "*.md" --exclude "*.bat"

echo.
echo Invalidando cache CloudFront...
aws cloudfront create-invalidation --distribution-id E153IH8TKR1LCM --paths "/*"

echo.
echo ========================================
echo   DEPLOY CONCLUIDO COM SUCESSO!
echo ========================================
echo.
echo URL: https://videos.sstechnologies-cloud.com
echo.
pause