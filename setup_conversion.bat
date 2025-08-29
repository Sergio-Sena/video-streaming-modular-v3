@echo off
echo 🔄 CONFIGURANDO CONVERSÃO AUTOMÁTICA...

echo Criando bucket temp...
aws s3 mb s3://video-temp-conversion --region us-east-1

echo Criando função MediaConvert trigger...
cd backend\modules
powershell -command "Compress-Archive -Path 'mediaconvert_trigger.py' -DestinationPath 'mediaconvert_trigger.zip' -Force"

aws lambda create-function ^
  --function-name mediaconvert-trigger ^
  --runtime python3.11 ^
  --role arn:aws:iam::969430605054:role/video-streaming-lambda-role ^
  --handler mediaconvert_trigger.handler ^
  --zip-file fileb://mediaconvert_trigger.zip ^
  --timeout 60

echo Criando função conversion complete...
powershell -command "Compress-Archive -Path 'conversion_complete.py' -DestinationPath 'conversion_complete.zip' -Force"

aws lambda create-function ^
  --function-name conversion-complete ^
  --runtime python3.11 ^
  --role arn:aws:iam::969430605054:role/video-streaming-lambda-role ^
  --handler conversion_complete.handler ^
  --zip-file fileb://conversion_complete.zip ^
  --timeout 30

echo Configurando trigger S3...
aws s3api put-bucket-notification-configuration ^
  --bucket video-temp-conversion ^
  --notification-configuration file://../../s3-trigger-config.json

echo ✅ Conversão automática configurada!
cd ..\..
pause