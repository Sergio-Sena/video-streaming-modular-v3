#!/usr/bin/env python3
"""
Gerar token de teste para signed URLs
"""

import jwt
import datetime

def generate_test_token():
    """Gerar token JWT válido"""
    
    # Payload do token
    payload = {
        'user_id': 'user-sergio-sena',
        'email': 'sergio@test.com',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        'iat': datetime.datetime.utcnow()
    }
    
    # Chave secreta (mesma do Lambda)
    secret_key = 'your-secret-key-here'  # Substituir pela chave real
    
    try:
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        print(f"Token gerado: {token}")
        return token
    except Exception as e:
        print(f"Erro: {e}")
        return None

if __name__ == "__main__":
    token = generate_test_token()
    if token:
        print(f"\nUse este token no teste: {token}")
    else:
        print("\nUse um token existente do localStorage")