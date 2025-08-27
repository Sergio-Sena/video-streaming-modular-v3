import json
import boto3
import bcrypt
import jwt
from datetime import datetime, timedelta

# CORS headers para todas as respostas
CORS_HEADERS = {
    'Access-Control-Allow-Origin': 'https://videos.sstechnologies-cloud.com',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'POST,GET,OPTIONS',
    'Content-Type': 'application/json'
}

def success_response(data, status_code=200):
    """Resposta de sucesso padronizada"""
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps({'success': True, **data})
    }

def error_response(message, status_code=400):
    """Resposta de erro padronizada"""
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps({'success': False, 'message': message})
    }

def get_credentials():
    """Busca credenciais do Secrets Manager"""
    secrets_client = boto3.client('secretsmanager')
    secret = secrets_client.get_secret_value(SecretId='video-streaming-user')
    return json.loads(secret['SecretString'])

def verify_jwt_token(token, secret):
    """Verifica token JWT"""
    try:
        jwt.decode(token, secret, algorithms=['HS256'])
        return True
    except:
        return False