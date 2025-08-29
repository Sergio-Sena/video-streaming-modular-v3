import json
import boto3
from utils import success_response, error_response

def handler(event, context):
    """
    Lambda para integração com Cognito
    Não precisa mais validar JWT - API Gateway faz isso
    """
    try:
        # Headers CORS
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        }
        
        # Preflight CORS
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'CORS OK'})
            }
        
        # Usuário já autenticado pelo API Gateway + Cognito
        # Token JWT validado automaticamente
        user_info = event.get('requestContext', {}).get('authorizer', {})
        
        return success_response({
            'message': 'Authenticated via Cognito',
            'user': user_info.get('claims', {}),
            'authenticated': True
        }, headers)
        
    except Exception as e:
        return error_response(f'Auth error: {str(e)}', headers)