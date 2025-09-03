#!/usr/bin/env python3
"""
Corrigir permissões para vídeos
"""

import boto3
import json

def make_bucket_public():
    """Tornar bucket público para leitura"""
    s3_client = boto3.client('s3')
    bucket_name = 'drive-online-storage'
    
    # Política para leitura pública
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
        print("Bucket policy aplicada")
        return True
    except Exception as e:
        print(f"Erro: {e}")
        return False

def remove_public_access_block():
    """Remover bloqueio de acesso público"""
    s3_client = boto3.client('s3')
    bucket_name = 'drive-online-storage'
    
    try:
        s3_client.delete_public_access_block(Bucket=bucket_name)
        print("Public access block removido")
        return True
    except Exception as e:
        print(f"Erro: {e}")
        return False

if __name__ == "__main__":
    print("Corrigindo permissões...")
    remove_public_access_block()
    make_bucket_public()
    print("Teste novamente em 1-2 minutos")