#!/usr/bin/env python3
"""
Script para configurar Secrets Manager para Video Streaming SStech v3.0
"""

import boto3
import json
import bcrypt
import pyotp
from datetime import datetime

def create_secrets():
    """Cria secrets no AWS Secrets Manager"""
    
    # Cliente AWS
    secrets_client = boto3.client('secretsmanager')
    
    # Dados do usuário
    email = "sergiosenaadmin@sstech"
    password = "sergiosena"
    
    # Hash da senha com bcrypt
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Gerar secret MFA
    mfa_secret = pyotp.random_base32()
    
    # JWT secret
    jwt_secret = "video-streaming-v3-jwt-super-secret-key-2025"
    
    # Estrutura do secret
    secret_data = {
        "email": email,
        "password": password_hash,
        "mfaSecret": mfa_secret,
        "jwtSecret": jwt_secret,
        "createdAt": datetime.utcnow().isoformat(),
        "version": "3.0"
    }
    
    secret_name = "video-streaming-v3-user"
    
    try:
        # Tentar criar o secret
        response = secrets_client.create_secret(
            Name=secret_name,
            Description="Credenciais do usuário para Video Streaming SStech v3.0",
            SecretString=json.dumps(secret_data),
            Tags=[
                {
                    'Key': 'Project',
                    'Value': 'VideoStreamingSStech'
                },
                {
                    'Key': 'Version',
                    'Value': '3.0'
                },
                {
                    'Key': 'Environment',
                    'Value': 'production'
                }
            ]
        )
        
        print(f"Secret criado com sucesso!")
        print(f"Nome: {secret_name}")
        print(f"ARN: {response['ARN']}")
        print(f"Email: {email}")
        print(f"MFA Secret: {mfa_secret}")
        print(f"Configure no Google Authenticator com o secret acima")
        
    except secrets_client.exceptions.ResourceExistsException:
        # Secret já existe, vamos atualizar
        print(f"Secret {secret_name} ja existe. Atualizando...")
        
        response = secrets_client.update_secret(
            SecretId=secret_name,
            SecretString=json.dumps(secret_data)
        )
        
        print(f"Secret atualizado com sucesso!")
        print(f"Nome: {secret_name}")
        print(f"ARN: {response['ARN']}")
        print(f"Email: {email}")
        print(f"MFA Secret: {mfa_secret}")
        print(f"Configure no Google Authenticator com o secret acima")
        
    except Exception as e:
        print(f"Erro ao criar/atualizar secret: {str(e)}")
        return False
    
    return True

def verify_secrets():
    """Verifica se o secret foi criado corretamente"""
    
    secrets_client = boto3.client('secretsmanager')
    secret_name = "video-streaming-v3-user"
    
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret_data = json.loads(response['SecretString'])
        
        print(f"\nVERIFICACAO DO SECRET:")
        print(f"Email: {secret_data.get('email')}")
        print(f"Password Hash: {secret_data.get('password')[:20]}...")
        print(f"MFA Secret: {secret_data.get('mfaSecret')}")
        print(f"JWT Secret: {secret_data.get('jwtSecret')[:20]}...")
        print(f"Criado em: {secret_data.get('createdAt')}")
        print(f"Versao: {secret_data.get('version')}")
        
        return True
        
    except Exception as e:
        print(f"Erro ao verificar secret: {str(e)}")
        return False

def generate_mfa_qr():
    """Gera QR code para configuração MFA"""
    
    secrets_client = boto3.client('secretsmanager')
    secret_name = "video-streaming-v3-user"
    
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret_data = json.loads(response['SecretString'])
        
        email = secret_data.get('email')
        mfa_secret = secret_data.get('mfaSecret')
        
        # Gerar URI para Google Authenticator
        totp_uri = pyotp.totp.TOTP(mfa_secret).provisioning_uri(
            name=email,
            issuer_name="Video Streaming SStech v3.0"
        )
        
        print(f"\nCONFIGURACAO MFA:")
        print(f"Email: {email}")
        print(f"Secret: {mfa_secret}")
        print(f"URI: {totp_uri}")
        print(f"\nINSTRUCOES:")
        print(f"1. Abra o Google Authenticator")
        print(f"2. Toque em '+' para adicionar conta")
        print(f"3. Escolha 'Inserir chave de configuração'")
        print(f"4. Nome da conta: Video Streaming SStech v3.0")
        print(f"5. Chave: {mfa_secret}")
        print(f"6. Tipo: Baseado em tempo")
        
        return True
        
    except Exception as e:
        print(f"Erro ao gerar MFA: {str(e)}")
        return False

if __name__ == "__main__":
    print("Configurando Secrets Manager para Video Streaming SStech v3.0")
    print("=" * 60)
    
    # Criar secrets
    if create_secrets():
        print("\n" + "=" * 60)
        
        # Verificar
        if verify_secrets():
            print("\n" + "=" * 60)
            
            # Gerar MFA
            generate_mfa_qr()
            
            print("\nCONFIGURACAO COMPLETA!")
            print("Proximo passo: Deploy do auth-service-v3")
        else:
            print("Falha na verificacao")
    else:
        print("Falha na criacao do secret")