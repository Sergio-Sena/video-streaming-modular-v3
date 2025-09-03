#!/usr/bin/env python3
"""
Criar bucket de teste para vídeos
"""

import boto3
import json

def create_test_bucket():
    """Criar bucket público para teste"""
    s3_client = boto3.client('s3')
    bucket_name = 'automacao-video'
    
    try:
        # 1. Criar bucket
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"1. Bucket {bucket_name} criado")
    except Exception as e:
        print(f"1. Bucket já existe ou erro: {e}")
    
    # 2. Remover bloqueio público
    try:
        s3_client.delete_public_access_block(Bucket=bucket_name)
        print("2. Bloqueio público removido")
    except Exception as e:
        print(f"2. Erro: {e}")
    
    # 3. Política pública
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        ]
    }
    
    try:
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(policy)
        )
        print("3. Política pública aplicada")
    except Exception as e:
        print(f"3. Erro: {e}")
    
    # 4. CORS
    cors_config = {
        'CORSRules': [
            {
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'HEAD'],
                'AllowedOrigins': ['*'],
                'ExposeHeaders': ['Content-Range', 'Content-Length', 'Accept-Ranges'],
                'MaxAgeSeconds': 3600
            }
        ]
    }
    
    try:
        s3_client.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration=cors_config
        )
        print("4. CORS configurado")
    except Exception as e:
        print(f"4. Erro CORS: {e}")
    
    return bucket_name

def copy_video_to_test_bucket():
    """Copiar vídeo para bucket de teste"""
    s3_client = boto3.client('s3')
    
    source_bucket = 'drive-online-storage'
    source_key = 'users/user-sergio-sena/1756853751-Video automacao.mp4'
    
    dest_bucket = 'automacao-video'
    dest_key = 'video-teste.mp4'
    
    try:
        # Copiar arquivo
        s3_client.copy_object(
            CopySource={'Bucket': source_bucket, 'Key': source_key},
            Bucket=dest_bucket,
            Key=dest_key,
            ContentType='video/mp4'
        )
        print(f"5. Vídeo copiado para {dest_bucket}/{dest_key}")
        
        # URL pública
        public_url = f"https://{dest_bucket}.s3.amazonaws.com/{dest_key}"
        print(f"6. URL pública: {public_url}")
        
        return public_url
        
    except Exception as e:
        print(f"5. Erro ao copiar: {e}")
        return None

if __name__ == "__main__":
    bucket_name = create_test_bucket()
    video_url = copy_video_to_test_bucket()
    
    if video_url:
        print(f"\nSUCESSO! URL do vídeo: {video_url}")
    else:
        print("\nERRO na criação do teste")