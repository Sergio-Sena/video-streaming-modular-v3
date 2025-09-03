#!/usr/bin/env python3
"""
Script para corrigir problema ERR_BLOCKED_BY_ORB em vídeos
Aplica configurações CORS corretas no S3 e CloudFront
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

# Configurações
BUCKET_NAME = 'drive-online-storage'
CLOUDFRONT_DISTRIBUTION_ID = 'E1TK4C5GORRWUM'

def apply_s3_cors():
    """Aplicar configuração CORS no S3"""
    print("🔧 Aplicando configuração CORS no S3...")
    
    s3_client = boto3.client('s3')
    
    cors_config = {
        'CORSRules': [
            {
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'HEAD', 'OPTIONS'],
                'AllowedOrigins': [
                    'https://videos.sstechnologies-cloud.com',
                    'http://localhost:3000'
                ],
                'ExposeHeaders': [
                    'Content-Range',
                    'Content-Length', 
                    'Content-Type',
                    'Accept-Ranges',
                    'ETag',
                    'Last-Modified'
                ],
                'MaxAgeSeconds': 3600
            }
        ]
    }
    
    try:
        s3_client.put_bucket_cors(
            Bucket=BUCKET_NAME,
            CORSConfiguration=cors_config
        )
        print("✅ Configuração CORS aplicada no S3")
        return True
    except ClientError as e:
        print(f"❌ Erro ao aplicar CORS no S3: {e}")
        return False

def check_s3_content_types():
    """Verificar Content-Type dos vídeos no S3"""
    print("🔍 Verificando Content-Type dos vídeos...")
    
    s3_client = boto3.client('s3')
    
    try:
        # Listar objetos na pasta do usuário
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix='users/user-sergio-sena/'
        )
        
        if 'Contents' not in response:
            print("📁 Nenhum arquivo encontrado")
            return True
            
        videos_fixed = 0
        for obj in response['Contents']:
            key = obj['Key']
            if key.endswith('/'):  # Skip folders
                continue
                
            # Verificar se é vídeo
            if not any(key.lower().endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.wmv', '.webm', '.mkv', '.ts']):
                continue
                
            # Verificar Content-Type atual
            head_response = s3_client.head_object(Bucket=BUCKET_NAME, Key=key)
            current_type = head_response.get('ContentType', 'unknown')
            
            print(f"📹 {key.split('/')[-1]}: {current_type}")
            
            # Corrigir se necessário
            if current_type == 'application/octet-stream' or not current_type.startswith('video/'):
                correct_type = 'video/mp4'  # Default para MP4
                if key.lower().endswith('.avi'):
                    correct_type = 'video/x-msvideo'
                elif key.lower().endswith('.mov'):
                    correct_type = 'video/quicktime'
                elif key.lower().endswith('.wmv'):
                    correct_type = 'video/x-ms-wmv'
                elif key.lower().endswith('.webm'):
                    correct_type = 'video/webm'
                elif key.lower().endswith('.mkv'):
                    correct_type = 'video/x-matroska'
                elif key.lower().endswith('.ts'):
                    correct_type = 'video/mp2t'
                
                print(f"🔄 Corrigindo Content-Type para: {correct_type}")
                
                # Copiar objeto com Content-Type correto
                s3_client.copy_object(
                    Bucket=BUCKET_NAME,
                    CopySource={'Bucket': BUCKET_NAME, 'Key': key},
                    Key=key,
                    ContentType=correct_type,
                    MetadataDirective='REPLACE'
                )
                videos_fixed += 1
                
        print(f"✅ {videos_fixed} vídeos corrigidos")
        return True
        
    except ClientError as e:
        print(f"❌ Erro ao verificar Content-Type: {e}")
        return False

def invalidate_cloudfront():
    """Invalidar cache do CloudFront"""
    print("🔄 Invalidando cache do CloudFront...")
    
    cloudfront_client = boto3.client('cloudfront')
    
    try:
        response = cloudfront_client.create_invalidation(
            DistributionId=CLOUDFRONT_DISTRIBUTION_ID,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': ['/*']
                },
                'CallerReference': f'video-fix-{int(time.time())}'
            }
        )
        
        invalidation_id = response['Invalidation']['Id']
        print(f"✅ Invalidação criada: {invalidation_id}")
        print("⏳ Aguarde 5-15 minutos para propagação completa")
        return True
        
    except ClientError as e:
        print(f"❌ Erro ao invalidar CloudFront: {e}")
        return False

def test_video_access():
    """Testar acesso aos vídeos"""
    print("🧪 Testando acesso aos vídeos...")
    
    import requests
    
    # URL de teste
    test_url = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod/files/users%2Fuser-sergio-sena%2F1756853751-Video%20automacao.mp4/download"
    
    try:
        # Teste HEAD request
        response = requests.head(test_url, timeout=10)
        print(f"📊 Status: {response.status_code}")
        print(f"📊 Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"📊 CORS Origin: {response.headers.get('access-control-allow-origin', 'N/A')}")
        print(f"📊 Accept-Ranges: {response.headers.get('accept-ranges', 'N/A')}")
        
        if response.status_code == 200:
            print("✅ Vídeo acessível")
            return True
        else:
            print(f"❌ Erro de acesso: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """Executar todas as correções"""
    print("🚀 Iniciando correção do ERR_BLOCKED_BY_ORB")
    print("=" * 50)
    
    success_count = 0
    
    # Passo 1: Aplicar CORS no S3
    if apply_s3_cors():
        success_count += 1
    
    # Passo 2: Corrigir Content-Type dos vídeos
    if check_s3_content_types():
        success_count += 1
    
    # Passo 3: Invalidar CloudFront
    if invalidate_cloudfront():
        success_count += 1
    
    # Passo 4: Testar acesso
    print("\n⏳ Aguardando 30 segundos para propagação...")
    time.sleep(30)
    
    if test_video_access():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Resultado: {success_count}/4 passos concluídos com sucesso")
    
    if success_count == 4:
        print("🎉 Correção aplicada com sucesso!")
        print("💡 Teste os vídeos no frontend em alguns minutos")
    else:
        print("⚠️  Algumas correções falharam. Verifique os logs acima")
        
    print("\n📋 Próximos passos:")
    print("1. Aguarde 5-15 minutos para propagação do CloudFront")
    print("2. Teste os vídeos no frontend")
    print("3. Use debug_video_requests.html para diagnóstico detalhado")

if __name__ == "__main__":
    main()