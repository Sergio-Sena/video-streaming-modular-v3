#!/usr/bin/env python3
"""
Aplicar solução simples: CORS no S3 + URLs diretas
"""

import boto3
import json

def apply_s3_cors():
    """Aplicar CORS no S3 bucket"""
    print("Aplicando CORS no S3...")
    
    s3_client = boto3.client('s3')
    bucket_name = 'drive-online-storage'
    
    cors_config = {
        'CORSRules': [
            {
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'HEAD', 'OPTIONS'],
                'AllowedOrigins': ['*'],  # Permitir todos os origins
                'ExposeHeaders': [
                    'Content-Range',
                    'Content-Length', 
                    'Content-Type',
                    'Accept-Ranges',
                    'ETag'
                ],
                'MaxAgeSeconds': 3600
            }
        ]
    }
    
    try:
        s3_client.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration=cors_config
        )
        print("✓ CORS aplicado no S3")
        return True
    except Exception as e:
        print(f"✗ Erro ao aplicar CORS: {e}")
        return False

def make_bucket_public_read():
    """Tornar bucket público para leitura"""
    print("Configurando bucket para leitura pública...")
    
    s3_client = boto3.client('s3')
    bucket_name = 'drive-online-storage'
    
    # Política para permitir leitura pública
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/users/*"
            }
        ]
    }
    
    try:
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        print("✓ Bucket configurado para leitura pública")
        return True
    except Exception as e:
        print(f"✗ Erro ao configurar política: {e}")
        return False

def test_direct_s3_access():
    """Testar acesso direto ao S3"""
    print("Testando acesso direto ao S3...")
    
    import requests
    
    # URL direta do S3
    bucket_name = 'drive-online-storage'
    file_key = 'users/user-sergio-sena/1756853751-Video automacao.mp4'
    s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_key}"
    
    try:
        response = requests.head(s3_url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Acesso direto ao S3 funcionando")
            print(f"URL: {s3_url}")
            return s3_url
        else:
            print(f"✗ Acesso negado: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ Erro no teste: {e}")
        return None

def main():
    """Aplicar solução simples"""
    print("=== APLICANDO SOLUÇÃO SIMPLES ===")
    
    success_count = 0
    
    # Passo 1: CORS no S3
    if apply_s3_cors():
        success_count += 1
    
    # Passo 2: Tornar bucket público para leitura
    if make_bucket_public_read():
        success_count += 1
    
    # Passo 3: Testar acesso direto
    working_url = test_direct_s3_access()
    if working_url:
        success_count += 1
    
    print(f"\nResultado: {success_count}/3 passos concluídos")
    
    if working_url:
        print(f"\n🎉 SOLUÇÃO FUNCIONANDO!")
        print(f"Use URLs diretas do S3: {working_url}")
        print("\nPróximos passos:")
        print("1. Atualizar frontend para usar URLs diretas do S3")
        print("2. Testar reprodução de vídeo")
    else:
        print("\n⚠️ Solução não funcionou completamente")

if __name__ == "__main__":
    main()