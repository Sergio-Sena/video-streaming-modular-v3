@echo off
echo 🗑️ Script para limpeza dos recursos antigos

echo ⚠️ RECURSOS ANTIGOS PARA REMOVER:
echo.
echo 📦 Bucket S3: video-streaming-sstech-eaddf6a1
echo 🌐 CloudFront: E153IH8TKR1LCM (videos.sstechnologies-cloud.com)
echo.
echo 🔧 COMANDOS PARA EXECUTAR APÓS CONFIRMAR NOVO CDN:
echo.
echo REM Desabilitar distribuição antiga
echo aws cloudfront get-distribution-config --id E153IH8TKR1LCM --region us-east-1 ^> old-dist-config.json
echo REM Editar old-dist-config.json e mudar "Enabled": false
echo aws cloudfront update-distribution --id E153IH8TKR1LCM --distribution-config file://old-dist-config-disabled.json --if-match ETAG --region us-east-1
echo.
echo REM Aguardar desabilitação (pode levar 15-20 min)
echo aws cloudfront delete-distribution --id E153IH8TKR1LCM --if-match ETAG --region us-east-1
echo.
echo REM Remover bucket antigo
echo aws s3 rm s3://video-streaming-sstech-eaddf6a1 --recursive --region us-east-1
echo aws s3 rb s3://video-streaming-sstech-eaddf6a1 --region us-east-1
echo.
echo ✅ Execute estes comandos APENAS após confirmar que o novo CDN funciona!
pause