import json
import boto3
import os
from urllib.parse import unquote

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        # Usar usuário fixo se BYPASS_AUTH estiver ativo
        if os.environ.get('BYPASS_AUTH') == 'true':
            user_id = os.environ.get('FIXED_USER', 'user-sergio-sena')
        else:
            # Lógica de autenticação original (se necessário)
            user_id = 'user-sergio-sena'  # fallback
        
        # Extrair nome do arquivo da URL
        path = event.get('pathParameters', {}).get('proxy', '')
        if '/download' in path:
            filename = path.replace('/download', '')
            filename = unquote(filename)
        else:
            filename = path
            
        # Gerar URL presigned para download
        bucket = 'drive-online-storage'
        key = f'users/{user_id}/{filename}'
        
        # Gerar URL presigned válida por 1 hora
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