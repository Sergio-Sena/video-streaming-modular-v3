import json
import bcrypt
import jwt
import pyotp
import qrcode
import io
import base64
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

def get_credentials():
    secrets_client = boto3.client('secretsmanager')
    secret = secrets_client.get_secret_value(SecretId='video-streaming-user')
    return json.loads(secret['SecretString'])

def handler(event, context):
    """Handler principal para autenticação com logs de debug"""
    
    print(f"DEBUG: Event received: {json.dumps(event, default=str)}")
    
    origin = event.get('headers', {}).get('origin') or event.get('headers', {}).get('Origin')
    print(f"DEBUG: Origin: {origin}")
    
    # Resposta para OPTIONS (CORS)
    if event['httpMethod'] == 'OPTIONS':
        print("DEBUG: OPTIONS request - returning CORS headers")
        return {'statusCode': 200, 'headers': get_cors_headers(origin), 'body': ''}
    
    try:
        body = json.loads(event['body'])
        print(f"DEBUG: Body parsed: {body}")
        
        action = body.get('action', 'login')
        print(f"DEBUG: Action: {action}")
        
        if action == 'setup-mfa':
            return setup_mfa(origin)
        elif action == 'verify-mfa':
            return verify_mfa(body.get('mfaToken'), origin)
        else:
            return login(body, origin)
            
    except Exception as e:
        print(f"DEBUG: Exception in handler: {e}")
        print(f"DEBUG: Exception type: {type(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return error_response('Erro interno', origin, 500)

def login(body, origin):
    """Processa login com MFA fixo para teste"""
    try:
        email = body.get('email')
        password = body.get('password')
        mfa_token = body.get('mfaToken')
        
        print(f"DEBUG: Login attempt - Email: {email}, MFA: {mfa_token}")
        
        credentials = get_credentials()
        print(f"DEBUG: Credentials loaded - Email: {credentials['email']}")
        
        # Verifica email
        if email != credentials['email']:
            print(f"DEBUG: Email mismatch - Expected: {credentials['email']}, Got: {email}")
            return error_response('Email inválido', origin, 401)
        
        # Verifica senha
        if not bcrypt.checkpw(password.encode('utf-8'), credentials['password'].encode('utf-8')):
            print("DEBUG: Password mismatch")
            return error_response('Senha inválida', origin, 401)
        
        # MFA FIXO PARA TESTE
        if mfa_token != '123456':
            print(f"DEBUG: MFA mismatch - Expected: 123456, Got: {mfa_token}")
            return error_response('Código MFA inválido', origin, 401)
        
        print("DEBUG: All validations passed - generating JWT")
        
        # Gera JWT
        token = jwt.encode(
            {
                'email': credentials['email'],
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(hours=24)
            },
            credentials['jwtSecret'],
            algorithm='HS256'
        )
        
        print(f"DEBUG: JWT generated successfully")
        
        return success_response({
            'token': token,
            'user': {'email': credentials['email']}
        }, origin)
        
    except Exception as e:
        print(f"DEBUG: Exception in login: {e}")
        import traceback
        print(f"DEBUG: Login traceback: {traceback.format_exc()}")
        return error_response('Erro no login', origin)

def setup_mfa(origin):
    """Configura MFA"""
    try:
        print("DEBUG: Setup MFA called")
        secret = pyotp.random_base32()
        
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name='sergiosenaadmin@sstech',
            issuer_name='Video Streaming SStech'
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return success_response({
            'qrCode': f'data:image/png;base64,{qr_code_base64}',
            'manualKey': secret
        }, origin)
        
    except Exception as e:
        print(f"DEBUG: Exception in setup_mfa: {e}")
        return error_response('Erro ao configurar MFA', origin)

def verify_mfa(mfa_token, origin):
    """Verifica código MFA"""
    try:
        print(f"DEBUG: Verify MFA called with token: {mfa_token}")
        
        # Para teste, aceita 123456
        if mfa_token == '123456':
            return success_response({'message': 'MFA configurado!'}, origin)
        else:
            return error_response('Código inválido', origin)
            
    except Exception as e:
        print(f"DEBUG: Exception in verify_mfa: {e}")
        return error_response('Erro ao verificar MFA', origin)