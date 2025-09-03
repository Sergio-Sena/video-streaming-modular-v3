#!/usr/bin/env python3
"""
Tornar bucket S3 público para vídeos
"""

import boto3
import json

def make_s3_public():
    """Tornar bucket público para leitura"""
    s3_client = boto3.client('s3')
    bucket_name = 'drive-online-storage'
    
    # 1. Remover bloqueio de acesso público
    try:
        s3_client.delete_public_access_block(Bucket=bucket_name)
        print("1. Public access block removido")
    except Exception as e:
        print(f"1. Erro: {e}")
    
    # 2. Aplicar política pública
    policy = {
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
            Policy=json.dumps(policy)
        )
        print("2. Política pública aplicada")
    except Exception as e:
        print(f"2. Erro: {e}")
    
    # 3. Testar acesso
    test_url = f"https://{bucket_name}.s3.amazonaws.com/users/user-sergio-sena/1756853751-Video automacao.mp4"
    print(f"3. Teste esta URL: {test_url}")

if __name__ == "__main__":
    make_s3_public()