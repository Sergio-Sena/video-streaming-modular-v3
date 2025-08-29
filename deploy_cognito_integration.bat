@echo off
echo 🚀 Deploy com Cognito Integration...

REM Deploy Frontend com Cognito
echo Deployando Frontend com Cognito...
cd frontend
aws s3 sync . s3://video-streaming-sstech --delete --region us-east-1

REM Invalidar CloudFront
echo Invalidando CloudFront...
aws cloudfront create-invalidation ^
    --distribution-id E1234567890123 ^
    --paths "/*" ^
    --region us-east-1

echo ✅ Deploy Cognito Integration concluído!
echo 🌐 Teste: https://videos.sstechnologies-cloud.com
pause