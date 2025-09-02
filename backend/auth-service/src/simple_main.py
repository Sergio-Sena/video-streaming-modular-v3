import json
import boto3
import bcrypt
import jwt
from datetime import datetime, timedelta
import os

# AWS Clients
secrets_client = boto3.client('secretsmanager')

# Constants
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

def get_secret(secret_name: str) -> str:
    """Get secret from AWS Secrets Manager"""
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except Exception as e:
        print(f"Error getting secret {secret_name}: {e}")
        # Development fallbacks
        if secret_name == 'drive-online-jwt-secret':
            return 'dev-jwt-secret-key-2025'
        elif secret_name == 'drive-online-user-password':
            return hash_password('sergiosena')
        elif secret_name == 'drive-online-reset-tokens':
            return '{}'
        return ''

def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    secret = get_secret('drive-online-jwt-secret')
    return jwt.encode(to_encode, secret, algorithm=JWT_ALGORITHM)

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

def handle_login(body):
    """Handle login request"""
    try:
        data = json.loads(body) if isinstance(body, str) else body
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({'detail': 'Email and password required'})
            }
        
        user = get_user_by_email(email)
        if not user or not verify_password(password, user['password_hash']):
            return {
                'statusCode': 401,
                'body': json.dumps({'detail': 'Invalid credentials'})
            }
        
        token_data = {
            "sub": user['email'],
            "user_id": user['id'],
            "name": user['name']
        }
        
        access_token = create_access_token(token_data)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({
                'token': access_token,
                'refreshToken': access_token,
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
            'timestamp': datetime.utcnow().isoformat()
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
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'detail': 'Not found'})
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