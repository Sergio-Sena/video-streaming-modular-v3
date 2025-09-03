#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplificado para testar correções de vídeo
"""

import boto3
import json
import requests
import time
from botocore.exceptions import ClientError

# Configurações
BUCKET_NAME = 'drive-online-storage'
CLOUDFRONT_DISTRIBUTION_ID = 'E1TK4C5GORRWUM'
API_BASE = 'https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod'
TEST_VIDEO = 'users/user-sergio-sena/1756853751-Video automacao.mp4'

def test_s3_cors():
    """Testar configuração CORS do S3"""
    print("Testando CORS do S3...")
    
    s3_client = boto3.client('s3')
    
    try:
        response = s3_client.get_bucket_cors(Bucket=BUCKET_NAME)
        cors_rules = response.get('CORSRules', [])
        
        print(f"CORS Rules encontradas: {len(cors_rules)}")
        
        for i, rule in enumerate(cors_rules):
            print(f"  Regra {i+1}:")
            print(f"    Origins: {rule.get('AllowedOrigins', [])}")
            print(f"    Methods: {rule.get('AllowedMethods', [])}")
            print(f"    Headers: {rule.get('ExposeHeaders', [])}")
        
        return len(cors_rules) > 0
        
    except ClientError as e:
        print(f"Erro ao verificar CORS: {e}")
        return False

def test_video_content_type():
    """Verificar Content-Type dos vídeos"""
    print("Verificando Content-Type dos videos...")
    
    s3_client = boto3.client('s3')
    
    try:
        # Verificar arquivo específico
        response = s3_client.head_object(
            Bucket=BUCKET_NAME, 
            Key=TEST_VIDEO
        )
        
        content_type = response.get('ContentType', 'unknown')
        size = response.get('ContentLength', 0)
        
        print(f"Arquivo: {TEST_VIDEO.split('/')[-1]}")
        print(f"Content-Type: {content_type}")
        print(f"Tamanho: {size} bytes")
        
        return content_type.startswith('video/')
        
    except ClientError as e:
        print(f"Erro ao verificar arquivo: {e}")
        return False

def test_lambda_endpoint():
    """Testar endpoint do Lambda"""
    print("Testando endpoint do Lambda...")
    
    try:
        # Teste 1: Health check
        response = requests.get(f"{API_BASE}/health", timeout=10)
        print(f"Health check: {response.status_code}")
        
        # Teste 2: OPTIONS request
        video_url = f"{API_BASE}/files/{requests.utils.quote(TEST_VIDEO, safe='')}/download"
        options_response = requests.options(video_url, timeout=10)
        print(f"OPTIONS request: {options_response.status_code}")
        
        # Teste 3: HEAD request para o vídeo
        head_response = requests.head(video_url, timeout=10)
        print(f"HEAD request: {head_response.status_code}")
        
        if head_response.status_code == 200:
            headers = dict(head_response.headers)
            print("Headers importantes:")
            print(f"  Content-Type: {headers.get('content-type', 'N/A')}")
            print(f"  CORS Origin: {headers.get('access-control-allow-origin', 'N/A')}")
            print(f"  Accept-Ranges: {headers.get('accept-ranges', 'N/A')}")
            
            return True
        
        return False
        
    except Exception as e:
        print(f"Erro no teste: {e}")
        return False

def apply_s3_cors_fix():
    """Aplicar correção CORS no S3"""
    print("Aplicando correção CORS no S3...")
    
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
        print("CORS aplicado com sucesso")
        return True
    except ClientError as e:
        print(f"Erro ao aplicar CORS: {e}")
        return False

def fix_video_content_type():
    """Corrigir Content-Type do vídeo"""
    print("Corrigindo Content-Type do video...")
    
    s3_client = boto3.client('s3')
    
    try:
        # Copiar objeto com Content-Type correto
        s3_client.copy_object(
            Bucket=BUCKET_NAME,
            CopySource={'Bucket': BUCKET_NAME, 'Key': TEST_VIDEO},
            Key=TEST_VIDEO,
            ContentType='video/mp4',
            MetadataDirective='REPLACE'
        )
        print("Content-Type corrigido para video/mp4")
        return True
    except ClientError as e:
        print(f"Erro ao corrigir Content-Type: {e}")
        return False

def main():
    """Executar testes e correções"""
    print("=== TESTE DE CORRECOES DE VIDEO ===")
    
    # Verificar estado atual
    print("\n1. VERIFICANDO ESTADO ATUAL:")
    cors_ok = test_s3_cors()
    content_type_ok = test_video_content_type()
    lambda_ok = test_lambda_endpoint()
    
    print(f"\nResultados iniciais:")
    print(f"  CORS S3: {'OK' if cors_ok else 'PRECISA CORRIGIR'}")
    print(f"  Content-Type: {'OK' if content_type_ok else 'PRECISA CORRIGIR'}")
    print(f"  Lambda: {'OK' if lambda_ok else 'PRECISA CORRIGIR'}")
    
    # Aplicar correções se necessário
    fixes_applied = 0
    
    if not cors_ok:
        print("\n2. APLICANDO CORRECAO CORS...")
        if apply_s3_cors_fix():
            fixes_applied += 1
    
    if not content_type_ok:
        print("\n3. CORRIGINDO CONTENT-TYPE...")
        if fix_video_content_type():
            fixes_applied += 1
    
    # Testar novamente após correções
    if fixes_applied > 0:
        print("\n4. TESTANDO APOS CORRECOES...")
        time.sleep(5)  # Aguardar propagação
        
        cors_ok = test_s3_cors()
        content_type_ok = test_video_content_type()
        lambda_ok = test_lambda_endpoint()
    
    # Resultado final
    print("\n=== RESULTADO FINAL ===")
    print(f"CORS S3: {'✓' if cors_ok else '✗'}")
    print(f"Content-Type: {'✓' if content_type_ok else '✗'}")
    print(f"Lambda: {'✓' if lambda_ok else '✗'}")
    
    if cors_ok and content_type_ok and lambda_ok:
        print("\n🎉 TODAS AS CORRECOES APLICADAS COM SUCESSO!")
        print("Teste os videos no frontend agora.")
    else:
        print("\n⚠️ ALGUMAS CORRECOES AINDA PRECISAM SER APLICADAS")
        
        # Instruções específicas
        if not lambda_ok:
            print("- Execute: python deploy_lambda_fix.py")
        if not cors_ok or not content_type_ok:
            print("- Verifique permissões AWS")

if __name__ == "__main__":
    main()