import json
import bcrypt
import jwt
import pyotp
import qrcode
import io
import base64
import boto3
from datetime import datetime, timedelta
from utils import get_cors_headers, success_response, error_response, get_credentials

def handler(event, context):
    """Handler principal para autenticação"""
    
    origin = event.get('headers', {}).get('origin') or event.get('headers', {}).get('Origin')
    
    # Resposta para OPTIONS (CORS)
    if event['httpMethod'] == 'OPTIONS':
        return {'statusCode': 200, 'headers': get_cors_headers(origin), 'body': ''}
    
    try:
        body = json.loads(event['body'])
        action = body.get('action', 'login')
        
        if action == 'setup-mfa':
            return setup_mfa()
        elif action == 'verify-mfa':
            return verify_mfa(body.get('mfaToken'))
        else:
            return login(body)
            
    except Exception as e:
        print(f"Auth error: {e}")
        return error_response('Erro interno', 500)

def setup_mfa():
    """Configura MFA e gera QR Code"""
    try:
        # Gera secret para MFA
        secret = pyotp.random_base32()
        
        # Cria URL para QR Code
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name='sergiosenaadmin@sstech',
            issuer_name='Video Streaming SStech'
        )
        
        # Gera QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Salva secret no Secrets Manager
        credentials = get_credentials()
        credentials['mfaSecret'] = secret
        
        import boto3
        secrets_client = boto3.client('secretsmanager')
        secrets_client.update_secret(
            SecretId='video-streaming-user',
            SecretString=json.dumps(credentials)
        )
        
        return success_response({
            'qrCode': f'data:image/png;base64,{qr_code_base64}',
            'manualKey': secret
        }, origin)
        
    except Exception as e:
        print(f"MFA setup error: {e}")
        return error_response('Erro ao configurar MFA', origin)

def verify_mfa(mfa_token):
    """Verifica código MFA"""
    try:
        credentials = get_credentials()
        totp = pyotp.TOTP(credentials['mfaSecret'])
        
        if totp.verify(mfa_token):
            return success_response({'message': 'MFA configurado!'}, origin)
        else:
            return error_response('Código inválido', origin)
            
    except Exception as e:
        print(f"MFA verify error: {e}")
        return error_response('Erro ao verificar MFA', origin)

def login(body):
    """Processa login com email, senha e MFA"""
    try:
        email = body.get('email')
        password = body.get('password')
        mfa_token = body.get('mfaToken')
        
        credentials = get_credentials()
        
        # Verifica email
        if email != credentials['email']:
            return error_response('Email inválido', 401)
        
        # Verifica senha
        if not bcrypt.checkpw(password.encode('utf-8'), credentials['password'].encode('utf-8')):
            return error_response('Senha inválida', 401)
        
        # Verifica MFA
        totp = pyotp.TOTP(credentials['mfaSecret'])
        if not totp.verify(mfa_token):
            return error_response('Código MFA inválido', 401)
        
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
        
        return success_response({
            'token': token,
            'user': {'email': credentials['email']}
        }, origin)
        
    except Exception as e:
        print(f"Login error: {e}")
        return error_response('Erro no login', origin)