import json
import boto3
from datetime import datetime
from utils import get_cors_headers, success_response, error_response, get_credentials, verify_jwt_token

def handler(event, context):
    """Handler principal para vídeos"""
    
    origin = event.get('headers', {}).get('origin') or event.get('headers', {}).get('Origin')
    
    # Resposta para OPTIONS (CORS)
    if event['httpMethod'] == 'OPTIONS':
        return {'statusCode': 200, 'headers': get_cors_headers(origin), 'body': ''}
    
    try:
        # Verifica autenticação
        auth_header = event['headers'].get('Authorization') or event['headers'].get('authorization')
        if not auth_header:
            return error_response('Token não fornecido', origin, 401)
        
        token = auth_header.replace('Bearer ', '')
        credentials = get_credentials()
        
        if not verify_jwt_token(token, credentials['jwtSecret']):
            return error_response('Token inválido', origin, 401)
        
        # Roteamento por método HTTP
        if event['httpMethod'] == 'POST':
            body = json.loads(event['body'])
            action = body.get('action', 'upload')
            
            if action == 'get-part-url':
                return get_multipart_url(event, origin)
            elif action == 'complete-multipart':
                return complete_multipart_upload(event, origin)
            else:
                return generate_upload_url(event, origin)
        elif event['httpMethod'] == 'GET':
            show_hierarchy = event.get('queryStringParameters', {}) or {}
            if show_hierarchy.get('hierarchy') == 'true':
                return list_videos_hierarchy(origin)
            else:
                return list_videos(origin)
        elif event['httpMethod'] == 'DELETE':
            body = json.loads(event['body'])
            if body.get('type') == 'folder':
                return delete_folder(event, origin)
            else:
                return delete_video(event, origin)
            
    except Exception as e:
        print(f"Videos error: {e}")
        return error_response('Erro interno', origin, 500)

def generate_upload_url(event, origin):
    """Gera URL pré-assinada para upload simples ou multipart"""
    try:
        body = json.loads(event['body'])
        file_name = body.get('fileName')
        file_type = body.get('fileType')
        file_size = body.get('fileSize', 0)
        
        # Preserva estrutura de pasta se fornecida
        folder_path = body.get('folderPath', '')
        timestamp = int(datetime.now().timestamp())
        
        # Sanitiza nome do arquivo
        import urllib.parse
        safe_file_name = urllib.parse.quote(file_name, safe='')
        
        if folder_path:
            # Remove barras iniciais e finais, substitui \\ por /
            folder_path = folder_path.strip('/\\').replace('\\', '/')
            safe_folder_path = urllib.parse.quote(folder_path, safe='/')
            key = f'videos/{safe_folder_path}/{timestamp}-{safe_file_name}'
        else:
            key = f'videos/{timestamp}-{safe_file_name}'
        
        # Cliente S3
        s3_client = boto3.client('s3')
        
        # Se arquivo > 50MB, usa multipart
        if file_size > 50 * 1024 * 1024:  # 50MB
            # Inicia multipart upload
            response = s3_client.create_multipart_upload(
                Bucket='video-streaming-sstech-eaddf6a1',
                Key=key,
                ContentType=file_type
            )
            
            return success_response({
                'uploadId': response['UploadId'],
                'key': key,
                'multipart': True,
                'message': 'Multipart upload iniciado'
            }, origin)
        else:
            # Upload simples para arquivos pequenos
            upload_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': 'video-streaming-sstech-eaddf6a1',
                    'Key': key,
                    'ContentType': file_type
                },
                ExpiresIn=3600  # 1 hora
            )
            
            return success_response({
                'uploadUrl': upload_url,
                'key': key,
                'multipart': False,
                'message': 'URL de upload gerada'
            }, origin)
        
    except Exception as e:
        print(f"Upload URL error: {e}")
        return error_response('Erro ao gerar URL de upload', origin)

def list_videos(origin):
    """Lista todos os vídeos e pastas do bucket"""
    try:
        s3_client = boto3.client('s3')
        
        # Lista objetos do bucket com delimiter para separar pastas
        response = s3_client.list_objects_v2(
            Bucket='video-streaming-sstech-eaddf6a1',
            Prefix='videos/',
            Delimiter='/'
        )
        
        folders = []
        files = []
        
        # Adiciona pastas (CommonPrefixes)
        if 'CommonPrefixes' in response:
            for prefix in response['CommonPrefixes']:
                folder_name = prefix['Prefix'].replace('videos/', '').rstrip('/')
                if folder_name:  # Ignora pasta raiz vazia
                    folders.append({
                        'key': prefix['Prefix'],
                        'name': folder_name,
                        'type': 'folder',
                        'size': 0,
                        'lastModified': None
                    })
        
        # Adiciona arquivos na raiz (Contents)
        if 'Contents' in response:
            for obj in response['Contents']:
                # Ignora marcadores de pasta e arquivos dentro de subpastas
                if not obj['Key'].endswith('/') and obj['Key'].count('/') == 1:
                    file_name = obj['Key'].split('/')[-1]
                    if file_name:  # Ignora arquivos vazios
                        files.append({
                            'key': obj['Key'],
                            'name': file_name,
                            'type': 'file',
                            'size': obj['Size'],
                            'lastModified': obj['LastModified'].isoformat(),
                            'url': f'https://videos.sstechnologies-cloud.com/{obj["Key"]}'
                        })
        
        # Ordena: pastas primeiro, depois arquivos
        items = sorted(folders, key=lambda x: x['name'].lower()) + sorted(files, key=lambda x: x['name'].lower())
        
        return success_response({'items': items}, origin)
        
    except Exception as e:
        print(f"List videos error: {e}")
        return error_response('Erro ao listar vídeos', origin)

def get_multipart_url(event, origin):
    """Gera URL para uma parte do multipart upload"""
    try:
        body = json.loads(event['body'])
        upload_id = body.get('uploadId')
        key = body.get('key')
        part_number = body.get('partNumber')
        
        s3_client = boto3.client('s3')
        
        # Gera URL pré-assinada para a parte
        upload_url = s3_client.generate_presigned_url(
            'upload_part',
            Params={
                'Bucket': 'video-streaming-sstech-eaddf6a1',
                'Key': key,
                'UploadId': upload_id,
                'PartNumber': part_number
            },
            ExpiresIn=3600
        )
        
        return success_response({
            'uploadUrl': upload_url,
            'partNumber': part_number
        }, origin)
        
    except Exception as e:
        print(f"Multipart URL error: {e}")
        return error_response('Erro ao gerar URL da parte', origin)

def complete_multipart_upload(event, origin):
    """Completa o multipart upload"""
    try:
        body = json.loads(event['body'])
        upload_id = body.get('uploadId')
        key = body.get('key')
        parts = body.get('parts')  # [{'ETag': 'xxx', 'PartNumber': 1}]
        
        s3_client = boto3.client('s3')
        
        # Completa o multipart upload
        response = s3_client.complete_multipart_upload(
            Bucket='video-streaming-sstech-eaddf6a1',
            Key=key,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )
        
        return success_response({
            'location': response['Location'],
            'key': key,
            'message': 'Upload concluído'
        }, origin)
        
    except Exception as e:
        print(f"Complete multipart error: {e}")
        return error_response('Erro ao completar upload', origin)

def delete_video(event, origin):
    """Deleta um vídeo do S3"""
    try:
        body = json.loads(event['body'])
        key = body.get('key')
        
        if not key:
            return error_response('Chave do vídeo não fornecida', origin, 400)
        
        s3_client = boto3.client('s3')
        
        # Deleta o objeto do S3
        s3_client.delete_object(
            Bucket='video-streaming-sstech-eaddf6a1',
            Key=key
        )
        
        return success_response({
            'message': 'Vídeo deletado com sucesso',
            'key': key
        }, origin)
        
    except Exception as e:
        print(f"Delete video error: {e}")
        return error_response('Erro ao deletar vídeo', origin)

def delete_folder(event, origin):
    """Deleta uma pasta e todo seu conteúdo"""
    try:
        body = json.loads(event['body'])
        folder_key = body.get('key')
        
        if not folder_key or not folder_key.endswith('/'):
            return error_response('Chave da pasta inválida', origin, 400)
        
        s3_client = boto3.client('s3')
        
        # Lista todos os objetos na pasta
        response = s3_client.list_objects_v2(
            Bucket='video-streaming-sstech-eaddf6a1',
            Prefix=folder_key
        )
        
        if 'Contents' not in response:
            return success_response({
                'message': 'Pasta já estava vazia ou não existe',
                'key': folder_key
            }, origin)
        
        # Prepara lista de objetos para deletar
        objects_to_delete = []
        for obj in response['Contents']:
            objects_to_delete.append({'Key': obj['Key']})
        
        # Deleta em lotes de 1000 (limite do S3)
        while objects_to_delete:
            batch = objects_to_delete[:1000]
            objects_to_delete = objects_to_delete[1000:]
            
            s3_client.delete_objects(
                Bucket='video-streaming-sstech-eaddf6a1',
                Delete={'Objects': batch}
            )
        
        return success_response({
            'message': 'Pasta deletada com sucesso',
            'key': folder_key
        }, origin)
        
    except Exception as e:
        print(f"Delete folder error: {e}")
        return error_response('Erro ao deletar pasta', origin)

def list_videos_hierarchy(origin):
    """Lista vídeos em estrutura hierárquica"""
    try:
        s3_client = boto3.client('s3')
        
        # Lista todos os objetos
        response = s3_client.list_objects_v2(
            Bucket='video-streaming-sstech-eaddf6a1',
            Prefix='videos/'
        )
        
        hierarchy = {}
        
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].endswith('/'):  # Marcador de pasta
                    continue
                    
                # Remove prefixo 'videos/'
                path = obj['Key'].replace('videos/', '')
                parts = path.split('/')
                
                if len(parts) == 1:
                    # Arquivo na raiz
                    if 'root' not in hierarchy:
                        hierarchy['root'] = {'folders': {}, 'files': []}
                    
                    hierarchy['root']['files'].append({
                        'key': obj['Key'],
                        'name': parts[0],
                        'type': 'file',
                        'size': obj['Size'],
                        'lastModified': obj['LastModified'].isoformat(),
                        'url': f'https://videos.sstechnologies-cloud.com/{obj["Key"]}'
                    })
                else:
                    # Arquivo em pasta
                    folder_name = parts[0]
                    file_name = parts[-1]
                    
                    if folder_name not in hierarchy:
                        hierarchy[folder_name] = {'folders': {}, 'files': []}
                    
                    hierarchy[folder_name]['files'].append({
                        'key': obj['Key'],
                        'name': file_name,
                        'type': 'file',
                        'size': obj['Size'],
                        'lastModified': obj['LastModified'].isoformat(),
                        'url': f'https://videos.sstechnologies-cloud.com/{obj["Key"]}'
                    })
        
        return success_response({'hierarchy': hierarchy}, origin)
        
    except Exception as e:
        print(f"List hierarchy error: {e}")
        return error_response('Erro ao listar hierarquia', origin)