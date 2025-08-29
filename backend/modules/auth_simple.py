import json
import hashlib
from datetime import datetime, timedelta

def handler(event, context):
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'POST,OPTIONS',
        'Content-Type': 'application/json'
    }
    
    if event['httpMethod'] == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    try:
        body = json.loads(event['body'])
        email = body.get('email', '')
        password = body.get('password', '')
        
        # Credenciais fixas
        if email == 'sergiosenaadmin@sstech' and password == 'sergiosena':
            # Token simples
            token = f"token_{int(datetime.now().timestamp())}"
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'token': token,
                    'user': {'email': email}
                })
            }
        else:
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'message': 'Credenciais inválidas'
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'message': 'Erro interno'
            })
        }