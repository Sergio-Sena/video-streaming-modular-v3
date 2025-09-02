import json
import boto3
import hashlib
import hmac
import base64
from datetime import datetime, timedelta

# AWS Clients
secrets_client = boto3.client('secretsmanager')

def get_secret(secret_name: str) -> str:
    """Get secret from AWS Secrets Manager"""
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except Exception as e:
        print(f"Error getting secret {secret_name}: {e}")
        if secret_name == 'drive-online-user-password':
            return hash_password('sergiosena')
        elif secret_name == 'drive-online-jwt-secret':
            return 'super-secret-jwt-key-2025'
        return ''

def hash_password(password: str) -> str:
    """Hash password with SHA256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

def create_jwt_token(payload: dict, secret: str) -> str:
    """Create JWT token using native Python"""
    # Header
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }
    
    # Add expiration
    payload['exp'] = int((datetime.utcnow() + timedelta(hours=24)).timestamp())
    payload['iat'] = int(datetime.utcnow().timestamp())
    
    # Encode header and payload
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    
    # Create signature
    message = f"{header_b64}.{payload_b64}"
    signature = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def verify_jwt_token(token: str, secret: str) -> dict:
    """Verify JWT token using native Python"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        header_b64, payload_b64, signature_b64 = parts
        
        # Verify signature
        message = f"{header_b64}.{payload_b64}"
        expected_signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        expected_signature_b64 = base64.urlsafe_b64encode(expected_signature).decode().rstrip('=')
        
        if signature_b64 != expected_signature_b64:
            return None
        
        # Decode payload
        payload_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_padded).decode())
        
        # Check expiration
        if payload.get('exp', 0) < int(datetime.utcnow().timestamp()):
            return None
        
        return payload
        
    except Exception as e:
        print(f"JWT verification error: {e}")
        return None

def create_reset_token(email: str) -> str:
    """Create password reset token"""
    secret = get_secret('drive-online-jwt-secret')
    payload = {
        "email": email,
        "type": "password_reset",
        "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp())
    }
    return create_jwt_token(payload, secret)

def verify_reset_token(token: str) -> str:
    """Verify reset token and return email"""
    secret = get_secret('drive-online-jwt-secret')
    payload = verify_jwt_token(token, secret)
    
    if not payload or payload.get('type') != 'password_reset':
        return None
    
    return payload.get('email')

def get_user_by_email(email: str) -> dict:
    """Get user data"""
    if email != 'senanetworker@gmail.com':
        return None
    
    password_hash = get_secret('drive-online-user-password')
    
    return {
        'id': 'user-sergio-sena',
        'email': 'senanetworker@gmail.com',
        'name': 'Sergio Sena',
        'password_hash': password_hash,
        'created_at': '2025-01-01T00:00:00Z',
        'is_active': True
    }

def update_user_password(email: str, new_password: str):
    """Update user password in Secrets Manager"""
    if email != 'senanetworker@gmail.com':
        raise ValueError("User not found")
    
    hashed_password = hash_password(new_password)
    
    try:
        secrets_client.update_secret(
            SecretId='drive-online-user-password',
            SecretString=hashed_password
        )
        print(f"Password updated for {email}")
    except Exception as e:
        print(f"Error updating password: {e}")
        raise

def handle_login(body):
    """Handle login request"""
    try:
        data = json.loads(body) if isinstance(body, str) else body
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Email and password required'})
            }
        
        user = get_user_by_email(email)
        if not user or not verify_password(password, user['password_hash']):
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Invalid credentials'})
            }
        
        # Create JWT token
        secret = get_secret('drive-online-jwt-secret')
        payload = {
            "sub": user['email'],
            "user_id": user['id'],
            "name": user['name']
        }
        
        token = create_jwt_token(payload, secret)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'token': token,
                'refreshToken': token,
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['name']
                }
            })
        }
        
    except Exception as e:
        print(f"Login error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

def handle_forgot_password(body):
    """Handle forgot password request"""
    try:
        data = json.loads(body) if isinstance(body, str) else body
        email = data.get('email')
        
        if not email:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Email required'})
            }
        
        user = get_user_by_email(email)
        if not user:
            # Don't reveal if email exists
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'If email exists, reset instructions were sent'})
            }
        
        # Create reset token
        reset_token = create_reset_token(email)
        
        # Send via SNS (simplified for now)
        try:
            sns = boto3.client('sns')
            reset_link = f"https://videos.sstechnologies-cloud.com/reset-password?token={reset_token}"
            
            message = f"""
Olá!

Você solicitou a redefinição de sua senha no Drive Online.

Clique no link abaixo para redefinir sua senha:
{reset_link}

Este link expira em 1 hora.

Se você não solicitou esta redefinição, ignore este email.

Atenciosamente,
Equipe Drive Online
"""
            
            sns.publish(
                TopicArn="arn:aws:sns:us-east-1:969430605054:video-streaming-password-reset",
                Message=message,
                Subject='Drive Online - Redefinição de Senha'
            )
            
            print(f"Reset email sent to {email}: {reset_link}")
            
        except Exception as e:
            print(f"Error sending reset email: {e}")
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Password reset instructions sent'})
        }
        
    except Exception as e:
        print(f"Forgot password error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

def handle_reset_password(body):
    """Handle reset password request"""
    try:
        data = json.loads(body) if isinstance(body, str) else body
        token = data.get('token')
        new_password = data.get('newPassword')
        
        if not token or not new_password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Token and new password required'})
            }
        
        # Verify reset token
        email = verify_reset_token(token)
        if not email:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Invalid or expired token'})
            }
        
        # Update password
        update_user_password(email, new_password)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Password reset successfully'})
        }
        
    except Exception as e:
        print(f"Reset password error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

def handle_validate_reset_token(query_params):
    """Handle validate reset token request"""
    try:
        token = query_params.get('token') if query_params else None
        
        if not token:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Token required'})
            }
        
        email = verify_reset_token(token)
        if not email:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Invalid or expired token'})
            }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Token is valid', 'email': email})
        }
        
    except Exception as e:
        print(f"Validate token error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

def handle_health():
    """Handle health check"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'Drive Online Auth (Secure)',
            'features': ['JWT', 'Password Reset', 'Secrets Manager']
        })
    }

def lambda_handler(event, context):
    """Main Lambda handler"""
    try:
        print(f"Event: {json.dumps(event)}")
        
        # Handle different event sources
        if 'httpMethod' in event:
            # API Gateway event
            method = event['httpMethod']
            path = event.get('path', '/')
            body = event.get('body')
            query_params = event.get('queryStringParameters')
            
            # CORS preflight
            if method == 'OPTIONS':
                return {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                    }
                }
            
            # Route requests
            if path == '/health' and method == 'GET':
                return handle_health()
            elif path == '/auth/login' and method == 'POST':
                return handle_login(body)
            elif path == '/auth/forgot-password' and method == 'POST':
                return handle_forgot_password(body)
            elif path == '/auth/reset-password' and method == 'POST':
                return handle_reset_password(body)
            elif path == '/auth/validate-reset-token' and method == 'GET':
                return handle_validate_reset_token(query_params)
            else:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'detail': f'Not found: {method} {path}'})
                }
        else:
            # Direct invocation - return health
            return handle_health()
            
    except Exception as e:
        print(f"Handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'detail': 'Internal server error'})
        }

# Alias for compatibility
handler = lambda_handler