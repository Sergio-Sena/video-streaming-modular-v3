import json
import boto3
import jwt
import os
from datetime import datetime

# CORS headers para todas as respostas
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



def handler(event, context):
    """Handler principal para vídeos"""
    
    origin = event.get('headers', {}).get('origin') or event.get('headers', {}).get('Origin')
    
    # Resposta para OPTIONS (CORS)
    if event['httpMethod'] == 'OPTIONS':
        return {'statusCode': 200, 'headers': get_cors_headers(origin), 'body': ''}
    
    try:
        # Autenticação simplificada - aceita qualquer token Bearer
        auth_header = event['headers'].get('Authorization') or event['headers'].get('authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return error_response('Token não fornecido', origin, 401)
        
        print(f"DEBUG: Auth OK - token presente")
        
        # Roteamento por método HTTP
        if event['httpMethod'] == 'POST':
            return handle_post_request(event, origin)
        elif event['httpMethod'] == 'GET':
            return list_videos(event, origin)
        elif event['httpMethod'] == 'DELETE':
            return delete_item(event, origin)
        else:
            return error_response('Método não suportado', origin, 405)
            
    except Exception as e:
        print(f"Videos error: {e}")
        return error_response('Erro interno', origin, 500)

def handle_post_request(event, origin):
    """Trata requisições POST (upload, multipart, etc.)"""
    try:
        body = json.loads(event['body'])
        action = body.get('action')
        
        if action == 'get-part-url':
            return get_multipart_url(body, origin)
        elif action == 'complete-multipart':
            return complete_multipart_upload(body, origin)
        elif action == 'check-existing':
            return check_existing_files(body, origin)
        else:
            return generate_upload_url(body, origin)
            
    except Exception as e:
        print(f"POST request error: {e}")
        return error_response('Erro na requisição POST', origin)

def generate_upload_url(body, origin):
    """Gera URL pré-assinada para upload"""
    try:
        file_name = body.get('fileName')
        file_type = body.get('fileType')
        file_size = body.get('fileSize')
        folder_path = body.get('folderPath', '')
        
        # Determina bucket de destino
        target_bucket = body.get('targetBucket', 'video-streaming-sstech-eaddf6a1')
        
        # Gera chave com pasta se especificada
        timestamp = int(datetime.now().timestamp())
        if folder_path and folder_path.strip():
            # Remove caracteres inválidos do path
            clean_path = folder_path.replace('\\', '/').strip('/')
            key = f'videos/{clean_path}/{timestamp}-{file_name}'
        else:
            key = f'videos/{timestamp}-{file_name}'
            
        # Determina Content-Type correto
        content_type = file_type
        if file_name.lower().endswith(('.ts', '.m2ts', '.mts')):
            content_type = 'video/mp2t'  # Tipo correto para .ts
        elif not content_type or content_type == 'application/octet-stream':
            # Fallback baseado na extensão
            ext = file_name.lower().split('.')[-1]
            content_type_map = {
                'mp4': 'video/mp4',
                'webm': 'video/webm',
                'avi': 'video/x-msvideo',
                'mov': 'video/quicktime',
                'mkv': 'video/x-matroska'
            }
            content_type = content_type_map.get(ext, 'video/mp4')
        
        s3_client = boto3.client('s3')
        
        # Verifica se precisa de multipart (>50MB)
        if file_size > 50 * 1024 * 1024:
            # Inicia multipart upload
            response = s3_client.create_multipart_upload(
                Bucket=target_bucket,
                Key=key,
                ContentType=file_type
            )
            
            return success_response({
                'multipart': True,
                'uploadId': response['UploadId'],
                'key': key,
                'message': 'Multipart upload iniciado'
            }, origin)
        else:
            # Upload simples
            upload_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': target_bucket,
                    'Key': key,
                    'ContentType': content_type
                },
                ExpiresIn=3600
            )
            
            return success_response({
                'uploadUrl': upload_url,
                'key': key,
                'message': 'URL de upload gerada'
            }, origin)
        
    except Exception as e:
        print(f"Upload URL error: {e}")
        return error_response('Erro ao gerar URL de upload', origin)

def get_multipart_url(body, origin):
    """Gera URL para parte do multipart upload"""
    try:
        upload_id = body.get('uploadId')
        part_number = body.get('partNumber')
        key = body.get('key')
        
        s3_client = boto3.client('s3')
        
        upload_url = s3_client.generate_presigned_url(
            'upload_part',
            Params={
                'Bucket': 'video-streaming-sstech-eaddf6a1',
                'Key': key,
                'PartNumber': part_number,
                'UploadId': upload_id
            },
            ExpiresIn=3600
        )
        
        return success_response({
            'uploadUrl': upload_url
        }, origin)
        
    except Exception as e:
        print(f"Multipart URL error: {e}")
        return error_response('Erro ao gerar URL multipart', origin)

def complete_multipart_upload(body, origin):
    """Completa multipart upload"""
    try:
        upload_id = body.get('uploadId')
        parts = body.get('parts')
        key = body.get('key')
        
        s3_client = boto3.client('s3')
        
        response = s3_client.complete_multipart_upload(
            Bucket='video-streaming-sstech-eaddf6a1',
            Key=key,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )
        
        return success_response({
            'location': response['Location'],
            'message': 'Upload concluído'
        }, origin)
        
    except Exception as e:
        print(f"Complete multipart error: {e}")
        return error_response('Erro ao completar upload', origin)

def list_videos(event, origin):
    """Lista vídeos com suporte a hierarquia"""
    try:
        s3_client = boto3.client('s3')
        show_hierarchy = event.get('queryStringParameters', {}).get('hierarchy') == 'true' if event.get('queryStringParameters') else False
        
        response = s3_client.list_objects_v2(
            Bucket='video-streaming-sstech-eaddf6a1',
            Prefix='videos/'
        )
        
        if show_hierarchy:
            hierarchy = {'root': {'files': []}}
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    if obj['Key'].endswith('/'):
                        continue
                        
                    path_parts = obj['Key'].replace('videos/', '').split('/')
                    
                    if len(path_parts) == 1:
                        # Arquivo na raiz
                        hierarchy['root']['files'].append({
                            'key': obj['Key'],
                            'name': path_parts[0],
                            'size': obj['Size'],
                            'lastModified': obj['LastModified'].isoformat(),
                            'url': f'{os.environ.get("CLOUDFRONT_URL", "https://d2we88koy23cl4.cloudfront.net")}/{obj["Key"]}'
                        })
                    else:
                        # Arquivo em pasta
                        folder_name = path_parts[0]
                        if folder_name not in hierarchy:
                            hierarchy[folder_name] = {'files': []}
                        
                        hierarchy[folder_name]['files'].append({
                            'key': obj['Key'],
                            'name': '/'.join(path_parts[1:]),
                            'size': obj['Size'],
                            'lastModified': obj['LastModified'].isoformat(),
                            'url': f'{os.environ.get("CLOUDFRONT_URL", "https://d2we88koy23cl4.cloudfront.net")}/{obj["Key"]}'
                        })
            
            return success_response({'hierarchy': hierarchy}, origin)
        else:
            # Lista simples
            items = []
            folders = set()
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    if obj['Key'].endswith('/'):
                        continue
                        
                    path_parts = obj['Key'].replace('videos/', '').split('/')
                    
                    if len(path_parts) > 1:
                        folder_name = path_parts[0]
                        folders.add(folder_name)
                    
                    items.append({
                        'key': obj['Key'],
                        'name': obj['Key'].split('/')[-1],
                        'size': obj['Size'],
                        'lastModified': obj['LastModified'].isoformat(),
                        'url': f'{os.environ.get("CLOUDFRONT_URL", "https://d2we88koy23cl4.cloudfront.net")}/{obj["Key"]}',
                        'type': 'file'
                    })
            
            # Adiciona pastas como items
            for folder in folders:
                items.insert(0, {
                    'key': f'videos/{folder}/',
                    'name': folder,
                    'type': 'folder'
                })
            
            return success_response({'items': items}, origin)
        
    except Exception as e:
        print(f"List videos error: {e}")
        return error_response('Erro ao listar vídeos', origin)

def delete_item(event, origin):
    """Deleta vídeo ou pasta"""
    try:
        body = json.loads(event['body'])
        key = body.get('key')
        item_type = body.get('type', 'file')
        
        s3_client = boto3.client('s3')
        
        if item_type == 'folder':
            # Deleta todos os objetos da pasta
            response = s3_client.list_objects_v2(
                Bucket='video-streaming-sstech-eaddf6a1',
                Prefix=key
            )
            
            if 'Contents' in response:
                objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
                
                s3_client.delete_objects(
                    Bucket='video-streaming-sstech-eaddf6a1',
                    Delete={'Objects': objects_to_delete}
                )
        else:
            # Deleta arquivo único
            s3_client.delete_object(
                Bucket='video-streaming-sstech-eaddf6a1',
                Key=key
            )
        
        return success_response({'message': 'Item deletado com sucesso'}, origin)
        
    except Exception as e:
        print(f"Delete error: {e}")
        return error_response('Erro ao deletar item', origin)

def check_existing_files(body, origin):
    """Verifica quais arquivos já existem no S3"""
    try:
        files_to_check = body.get('files', [])
        folder_path = body.get('folderPath', '')
        
        s3_client = boto3.client('s3')
        existing_files = []
        
        # Lista objetos na pasta
        prefix = f'videos/{folder_path}/' if folder_path else 'videos/'
        response = s3_client.list_objects_v2(
            Bucket='video-streaming-sstech-eaddf6a1',
            Prefix=prefix
        )
        
        if 'Contents' in response:
            existing_keys = [obj['Key'] for obj in response['Contents']]
            
            for file_info in files_to_check:
                file_name = file_info['name']
                # Verifica se existe arquivo com mesmo nome (ignora timestamp)
                for key in existing_keys:
                    if key.endswith(file_name):
                        existing_files.append(file_name)
                        break
        
        return success_response({
            'existingFiles': existing_files
        }, origin)
        
    except Exception as e:
        print(f"Check existing error: {e}")
        return error_response('Erro ao verificar arquivos', origin)