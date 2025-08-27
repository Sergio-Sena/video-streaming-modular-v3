import json
import boto3
from datetime import datetime
from utils import CORS_HEADERS, success_response, error_response, get_credentials, verify_jwt_token

def handler(event, context):
    """Handler principal para vídeos"""
    
    # Resposta para OPTIONS (CORS)
    if event['httpMethod'] == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS}
    
    try:
        # Verifica autenticação
        auth_header = event['headers'].get('Authorization') or event['headers'].get('authorization')
        if not auth_header:
            return error_response('Token não fornecido', 401)
        
        token = auth_header.replace('Bearer ', '')
        credentials = get_credentials()
        
        if not verify_jwt_token(token, credentials['jwtSecret']):
            return error_response('Token inválido', 401)
        
        # Roteamento por método HTTP
        if event['httpMethod'] == 'POST':
            return generate_upload_url(event)
        elif event['httpMethod'] == 'GET':
            return list_videos()
            
    except Exception as e:
        print(f"Videos error: {e}")
        return error_response('Erro interno', 500)

def generate_upload_url(event):
    """Gera URL pré-assinada para upload"""
    try:
        body = json.loads(event['body'])
        file_name = body.get('fileName')
        file_type = body.get('fileType')
        file_size = body.get('fileSize')
        
        # Gera chave única para o arquivo
        timestamp = int(datetime.now().timestamp())
        key = f'videos/{timestamp}-{file_name}'
        
        # Cliente S3
        s3_client = boto3.client('s3')
        
        # Gera URL pré-assinada
        upload_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': 'video-streaming-sstech-eaddf6a1',
                'Key': key,
                'ContentType': file_type,
                'ACL': 'private'
            },
            ExpiresIn=3600  # 1 hora
        )
        
        return success_response({
            'uploadUrl': upload_url,
            'key': key,
            'message': 'URL de upload gerada'
        })
        
    except Exception as e:
        print(f"Upload URL error: {e}")
        return error_response('Erro ao gerar URL de upload')

def list_videos():
    """Lista todos os vídeos do bucket"""
    try:
        s3_client = boto3.client('s3')
        
        # Lista objetos do bucket
        response = s3_client.list_objects_v2(
            Bucket='video-streaming-sstech-eaddf6a1',
            Prefix='videos/'
        )
        
        videos = []
        if 'Contents' in response:
            for obj in response['Contents']:
                videos.append({
                    'key': obj['Key'],
                    'name': obj['Key'].split('/')[-1],
                    'size': obj['Size'],
                    'lastModified': obj['LastModified'].isoformat(),
                    'url': f'https://videos.sstechnologies-cloud.com/{obj["Key"]}'
                })
        
        return success_response({'videos': videos})
        
    except Exception as e:
        print(f"List videos error: {e}")
        return error_response('Erro ao listar vídeos')