#!/usr/bin/env python3
"""
Criar secret com credenciais S3 específicas
"""

import boto3
import json

def create_s3_credentials_secret():
    """Criar secret com credenciais S3"""
    secrets_client = boto3.client('secretsmanager')
    
    # Credenciais com permissões específicas para S3
    credentials = {
        "access_key": "AKIA6DNURDT7MO5EXHLQ",
        "secret_key": "CHAVE_SECRETA_AQUI",  # Você precisa fornecer
        "region": "us-east-1",
        "bucket": "drive-online-storage"
    }
    
    try:
        secrets_client.create_secret(
            Name='drive-online-s3-credentials',
            Description='Credenciais S3 para Drive Online',
            SecretString=json.dumps(credentials)
        )
        print("Secret criado com sucesso")
    except secrets_client.exceptions.ResourceExistsException:
        # Atualizar se já existe
        secrets_client.update_secret(
            SecretId='drive-online-s3-credentials',
            SecretString=json.dumps(credentials)
        )
        print("Secret atualizado")
    except Exception as e:
        print(f"Erro: {e}")

def test_current_permissions():
    """Testar permissões atuais"""
    s3_client = boto3.client('s3')
    
    try:
        # Testar listagem
        response = s3_client.list_objects_v2(
            Bucket='drive-online-storage',
            Prefix='users/user-sergio-sena/',
            MaxKeys=1
        )
        print("✅ Listagem funciona")
        
        # Testar acesso ao arquivo
        response = s3_client.head_object(
            Bucket='drive-online-storage',
            Key='users/user-sergio-sena/1756853751-Video automacao.mp4'
        )
        print("✅ Arquivo existe e é acessível")
        print(f"Content-Type: {response.get('ContentType')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro de permissão: {e}")
        return False

if __name__ == "__main__":
    print("Testando permissões atuais...")
    if test_current_permissions():
        print("Permissões OK - problema pode ser na geração da URL")
    else:
        print("Problema de permissões detectado")
        
    print("\nPara criar secret com credenciais:")
    print("1. Obtenha a secret key da AWS")
    print("2. Execute create_s3_credentials_secret()")