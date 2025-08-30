import json
import sys
import os
import boto3
import hmac
import hashlib
import base64

# Add shared layer to path
sys.path.append('/opt/python/lib/python3.12/site-packages')

def lambda_handler(event, context):
    """Simple Lambda handler for testing"""
    
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    try:
        # Handle preflight requests
        if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'OK'})
            }
        
        # Get path and method
        path = event.get('rawPath', '/')
        method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        
        # Health check
        if path == '/health' and method == 'GET':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'healthy',
                    'service': 'auth',
                    'version': '1.0.0'
                })
            }
        
        # Create user endpoint for testing
        if path == '/auth/create-user' and method == 'POST':
            try:
                # Parse request body
                body = json.loads(event.get('body', '{}'))
                username = body.get('username', 'test@example.com')
                password = body.get('password', 'TempPassword123!')
                
                # Initialize Cognito client
                cognito = boto3.client('cognito-idp')
                
                # Create user
                response = cognito.admin_create_user(
                    UserPoolId='us-east-1_pVAxf4uRa',
                    Username=username,
                    TemporaryPassword=password,
                    MessageAction='SUPPRESS',
                    UserAttributes=[
                        {
                            'Name': 'email',
                            'Value': username
                        },
                        {
                            'Name': 'email_verified',
                            'Value': 'true'
                        }
                    ]
                )
                
                # Set permanent password
                cognito.admin_set_user_password(
                    UserPoolId='us-east-1_pVAxf4uRa',
                    Username=username,
                    Password=password,
                    Permanent=True
                )
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'message': 'User created successfully',
                        'username': username
                    })
                }
                
            except Exception as e:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'message': f'Error creating user: {str(e)}'
                    })
                }
        
        # Login endpoint
        if path == '/auth/login' and method == 'POST':
            try:
                # Parse request body
                body = json.loads(event.get('body', '{}'))
                username = body.get('username')
                password = body.get('password')
                
                if not username or not password:
                    return {
                        'statusCode': 400,
                        'headers': headers,
                        'body': json.dumps({
                            'success': False,
                            'message': 'Username and password required'
                        })
                    }
                
                # Initialize Cognito client
                cognito = boto3.client('cognito-idp')
                
                # Calculate secret hash
                client_id = '5j9qdr81gvb10or0a1kl70g6o7'
                
                # Get client secret from Secrets Manager
                secrets_client = boto3.client('secretsmanager')
                secret_response = secrets_client.get_secret_value(
                    SecretId='video-streaming-v2-secrets-bdc2040d'
                )
                secrets = json.loads(secret_response['SecretString'])
                client_secret = secrets['cognito_client_secret']
                
                # Calculate secret hash
                message = username + client_id
                dig = hmac.new(
                    client_secret.encode('utf-8'),
                    message.encode('utf-8'),
                    hashlib.sha256
                ).digest()
                secret_hash = base64.b64encode(dig).decode()
                
                # Initiate auth
                response = cognito.initiate_auth(
                    ClientId=client_id,
                    AuthFlow='USER_PASSWORD_AUTH',
                    AuthParameters={
                        'USERNAME': username,
                        'PASSWORD': password,
                        'SECRET_HASH': secret_hash
                    }
                )
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'message': 'Login successful',
                        'data': response
                    })
                }
                
            except Exception as e:
                return {
                    'statusCode': 401,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'message': f'Login failed: {str(e)}'
                    })
                }
        
        # Default response
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'message': 'Endpoint not found',
                'path': path,
                'method': method
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'message': f'Internal server error: {str(e)}'
            })
        }