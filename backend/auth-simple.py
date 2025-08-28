import json
import jwt
import boto3
from datetime import datetime, timedelta

# CORS headers
def get_cors_headers(origin=None):
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Requested-With',
        'Access-Control-Allow-Methods': 'POST,GET,OPTIONS,DELETE,PUT',
        'Access-Control-Max-Age': '86400',
        'Content-Type': 'application/json'
    }

def success_response(data, origin=None, status_code=200):
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(origin),
        'body': json.dumps({'success': True, **data})
    }

def error_response(message, origin=None, status_code=400):
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(origin),
        'body': json.dumps({'success': False, 'message': message})
    }

def handler(event, context):
    """Handler simplificado para teste"""
    
    print(f"DEBUG: Event: {json.dumps(event, default=str)}")
    
    origin = event.get('headers', {}).get('origin') or event.get('headers', {}).get('Origin')
    print(f"DEBUG: Origin: {origin}")
    
    # OPTIONS
    if event['httpMethod'] == 'OPTIONS':
        return {'statusCode': 200, 'headers': get_cors_headers(origin), 'body': ''}
    
    try:
        body = json.loads(event['body'])
        print(f"DEBUG: Body: {body}")
        
        email = body.get('email')
        password = body.get('password')
        mfa_token = body.get('mfaToken')
        
        print(f"DEBUG: Credentials - Email: {email}, Password: {password}, MFA: {mfa_token}")
        
        # Validação simples para teste
        if email != 'sergiosenaadmin@sstech':
            print("DEBUG: Email inválido")
            return error_response('Email inválido', origin, 401)
        
        if password != 'sergiosena':
            print("DEBUG: Senha inválida")
            return error_response('Senha inválida', origin, 401)
        
        if mfa_token != '123456':
            print(f"DEBUG: MFA inválido - Expected: 123456, Got: {mfa_token}")
            return error_response('Código MFA inválido', origin, 401)
        
        print("DEBUG: Login válido - gerando token")
        
        # Gera JWT simples
        token = jwt.encode(
            {
                'email': email,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(hours=24)
            },
            'test-secret-key',
            algorithm='HS256'
        )
        
        print(f"DEBUG: Token gerado: {token[:20]}...")
        
        return success_response({
            'token': token,
            'user': {'email': email}
        }, origin)
        
    except Exception as e:
        print(f"DEBUG: Exception: {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return error_response('Erro interno', origin, 500)