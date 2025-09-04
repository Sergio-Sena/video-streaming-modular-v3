import json
import boto3
from urllib.parse import unquote

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        # Extrair informações do evento
        path = event.get('pathParameters', {}).get('proxy', '')
        headers = event.get('headers', {})
        
        # Extrair token de autorização
        auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return {
                'statusCode': 401,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': json.dumps({'error': 'Unauthorized'})
            }
        
        # Para simplificar, usar usuário fixo por enquanto
        user_id = 'user-sergio-sena'
        
        # Extrair nome do arquivo
        if '/download' in path:
            filename = path.replace('/download', '')
        else:
            filename = path
            
        filename = unquote(filename)
        
        # Gerar URL presigned
        bucket = 'drive-online-storage'
        key = f'users/{user_id}/{filename}'
        
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=3600
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'downloadUrl': presigned_url
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }