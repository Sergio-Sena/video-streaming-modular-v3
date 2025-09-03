#!/usr/bin/env python3
"""
Solução direta para reprodução de vídeos
"""

import boto3
import requests

def test_presigned_url():
    """Testar presigned URL atual"""
    s3_client = boto3.client('s3')
    
    try:
        # Gerar presigned URL
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': 'drive-online-storage',
                'Key': 'users/user-sergio-sena/1756853751-Video automacao.mp4'
            },
            ExpiresIn=3600
        )
        
        print(f"Presigned URL: {url}")
        
        # Testar acesso
        response = requests.head(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS - Presigned URL funciona!")
            return url
        else:
            print(f"FAILED - Status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"ERROR: {e}")
        return None

if __name__ == "__main__":
    test_presigned_url()