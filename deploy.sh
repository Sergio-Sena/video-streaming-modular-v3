#!/bin/bash

echo "🚀 Deploy Drive Online v3.0"
echo "================================"

# Build do projeto
echo "📦 Building project..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

# Deploy para S3
echo "☁️ Deploying to S3..."
aws s3 sync dist/ s3://drive-online-frontend/ --delete

if [ $? -ne 0 ]; then
    echo "❌ S3 sync failed!"
    exit 1
fi

# Invalidar CloudFront
echo "🔄 Invalidating CloudFront..."
aws cloudfront create-invalidation --distribution-id E153IH8TKR1LCM --paths "/*"

if [ $? -ne 0 ]; then
    echo "⚠️ CloudFront invalidation failed, but deploy succeeded"
fi

echo "✅ Deploy completed successfully!"
echo "🌐 URL: https://videos.sstechnologies-cloud.com"