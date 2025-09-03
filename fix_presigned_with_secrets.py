#!/usr/bin/env python3
"""
Gerar presigned URLs usando credenciais do Secrets Manager
"""

import boto3
import json

def get_s3_credentials():
    """Obter credenciais S3 do Secrets Manager"""
    secrets_client = boto3.client('secretsmanager')
    
    try:
        # Tentar obter credenciais específicas do S3
        response = secrets_client.get_secret_value(SecretId='drive-online-s3-credentials')
        credentials = json.loads(response['SecretString'])
        return credentials
    except:
        # Usar credenciais padrão
        return None

def generate_working_presigned_url():
    """Gerar presigned URL que funciona"""
    
    # Tentar com credenciais do Secrets Manager
    credentials = get_s3_credentials()
    
    if credentials:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=credentials['access_key'],
            aws_secret_access_key=credentials['secret_key']
        )
    else:
        s3_client = boto3.client('s3')
    
    try:
        # Gerar presigned URL
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': 'drive-online-storage',
                'Key': 'users/user-sergio-sena/1756853751-Video automacao.mp4'
            },
            ExpiresIn=7200  # 2 horas
        )
        
        print(f"Presigned URL gerada:")
        print(url)
        
        # Testar URL
        import requests
        response = requests.head(url, timeout=10)
        print(f"Teste: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ URL FUNCIONANDO!")
            
            # Criar arquivo HTML de teste
            html = f'''<!DOCTYPE html>
<html>
<head><title>Teste Presigned URL</title></head>
<body>
    <h1>Teste Presigned URL</h1>
    <video controls width="600">
        <source src="{url}" type="video/mp4">
    </video>
    <p>URL: {url}</p>
</body>
</html>'''
            
            with open('test_presigned_working.html', 'w') as f:
                f.write(html)
            
            print("Arquivo test_presigned_working.html criado")
            return url
        else:
            print(f"❌ URL não funciona: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Erro: {e}")
        return None

if __name__ == "__main__":
    generate_working_presigned_url()