import json
import boto3

def handler(event, context):
    """Handler completo com upload"""
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Requested-With',
        'Access-Control-Allow-Methods': 'POST,GET,OPTIONS,DELETE,PUT',
        'Content-Type': 'application/json'
    }
    
    # OPTIONS request
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        # GET request - listar vídeos ou ações
        if event['httpMethod'] == 'GET':
            query_params = event.get('queryStringParameters') or {}
            action = query_params.get('action')
            
            # Ações especiais via GET
            if action == 'get-upload-url':
                return get_upload_url_from_params(query_params, headers)
            elif action == 'get-part-url':
                return get_part_url_from_params(query_params, headers)
            elif action == 'complete-multipart':
                return complete_multipart_from_params(query_params, headers)
            
            # Listagem normal
            show_hierarchy = query_params.get('hierarchy') == 'true'
            current_path = query_params.get('path', '')
            
            if show_hierarchy:
                return get_hierarchy_view(current_path, headers)
            else:
                return get_simple_view(headers)
        
        # POST request - upload e outras ações
        elif event['httpMethod'] == 'POST':
            return handle_post_request(event, headers)
        
        # DELETE request - deletar vídeos
        elif event['httpMethod'] == 'DELETE':
            return handle_delete_request(event, headers)
        
        # Outros métodos
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': 'Método não suportado'})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': str(e)})
        }

def handle_post_request(event, headers):
    """Processa requisições POST"""
    try:
        body = json.loads(event.get('body', '{}'))
        action = body.get('action')
        
        if action == 'get-upload-url':
            return get_upload_url(body, headers)
        elif action == 'get-part-url':
            return get_part_url(body, headers)
        elif action == 'complete-multipart':
            return complete_multipart(body, headers)
        else:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'success': False, 'message': 'Ação não reconhecida'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': str(e)})
        }

def get_upload_url(body, headers):
    """Gera URL de upload para S3"""
    try:
        s3_client = boto3.client('s3')
        
        filename = body.get('filename')
        content_type = body.get('contentType', 'video/mp4')
        file_size = body.get('fileSize', 0)
        folder_path = body.get('folderPath', '')
        
        # Sanitizar nome do arquivo
        safe_filename = filename.replace(' ', '_').replace('[', '').replace(']', '')
        
        # Definir chave do objeto
        if folder_path:
            object_key = f'videos/{folder_path}/{safe_filename}'
        else:
            object_key = f'videos/{safe_filename}'
        
        # Verificar se precisa de multipart (>50MB)
        if file_size > 50 * 1024 * 1024:
            # Iniciar multipart upload
            response = s3_client.create_multipart_upload(
                Bucket='video-streaming-sstech-eaddf6a1',
                Key=object_key,
                ContentType=content_type
            )
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'multipart': True,
                    'uploadId': response['UploadId'],
                    'key': object_key
                })
            }
        else:
            # Upload simples
            upload_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': 'video-streaming-sstech-eaddf6a1',
                    'Key': object_key,
                    'ContentType': content_type
                },
                ExpiresIn=3600
            )
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'uploadUrl': upload_url,
                    'key': object_key
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': str(e)})
        }

def get_part_url(body, headers):
    """Gera URL para parte do multipart upload"""
    try:
        s3_client = boto3.client('s3')
        
        upload_id = body.get('uploadId')
        part_number = body.get('partNumber')
        key = body.get('key')
        
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
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'uploadUrl': upload_url
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': str(e)})
        }

def complete_multipart(body, headers):
    """Completa multipart upload"""
    try:
        s3_client = boto3.client('s3')
        
        upload_id = body.get('uploadId')
        key = body.get('key')
        parts = body.get('parts', [])
        
        response = s3_client.complete_multipart_upload(
            Bucket='video-streaming-sstech-eaddf6a1',
            Key=key,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'location': response.get('Location')
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': str(e)})
        }

def get_hierarchy_view(current_path, headers):
    """Retorna visualização hierárquica navegável"""
    try:
        s3_client = boto3.client('s3')
        
        if current_path:
            prefix = f'videos/{current_path}/'
        else:
            prefix = 'videos/'
        
        response = s3_client.list_objects_v2(
            Bucket='video-streaming-sstech-eaddf6a1',
            Prefix=prefix,
            Delimiter='/'
        )
        
        folders = []
        files = []
        
        if 'CommonPrefixes' in response:
            for folder_info in response['CommonPrefixes']:
                folder_path = folder_info['Prefix']
                folder_name = folder_path.replace(prefix, '').rstrip('/')
                if folder_name:
                    folders.append({
                        'name': folder_name,
                        'path': folder_path.replace('videos/', '').rstrip('/'),
                        'type': 'folder'
                    })
        
        if 'Contents' in response:
            for obj in response['Contents']:
                if not obj['Key'].endswith('/') and obj['Key'] != prefix:
                    file_name = obj['Key'].replace(prefix, '')
                    if '/' not in file_name:
                        files.append({
                            'key': obj['Key'],
                            'name': file_name,
                            'size': obj['Size'],
                            'lastModified': obj['LastModified'].isoformat(),
                            'url': f'https://d2we88koy23cl4.cloudfront.net/{obj["Key"]}',
                            'type': 'file'
                        })
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True, 
                'hierarchy': True,
                'currentPath': current_path,
                'folders': folders,
                'files': files
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': str(e)})
        }

def get_simple_view(headers):
    """Retorna visualização simples"""
    try:
        s3_client = boto3.client('s3')
        
        response = s3_client.list_objects_v2(
            Bucket='video-streaming-sstech-eaddf6a1',
            Prefix='videos/'
        )
        
        items = []
        if 'Contents' in response:
            for obj in response['Contents']:
                if not obj['Key'].endswith('/'):
                    items.append({
                        'key': obj['Key'],
                        'name': obj['Key'].split('/')[-1],
                        'size': obj['Size'],
                        'lastModified': obj['LastModified'].isoformat(),
                        'url': f'https://d2we88koy23cl4.cloudfront.net/{obj["Key"]}',
                        'type': 'file'
                    })
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'success': True, 'items': items})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': str(e)})
        }

def get_upload_url_from_params(params, headers):
    """Processa get-upload-url via GET params"""
    try:
        body = {
            'filename': params.get('filename'),
            'contentType': params.get('contentType', 'video/mp4'),
            'fileSize': int(params.get('fileSize', 0)),
            'folderPath': params.get('folderPath', '')
        }
        return get_upload_url(body, headers)
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': str(e)})
        }

def get_part_url_from_params(params, headers):
    """Processa get-part-url via GET params"""
    try:
        body = {
            'uploadId': params.get('uploadId'),
            'partNumber': int(params.get('partNumber')),
            'key': params.get('key')
        }
        return get_part_url(body, headers)
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': str(e)})
        }

def complete_multipart_from_params(params, headers):
    """Processa complete-multipart via GET params"""
    try:
        body = {
            'uploadId': params.get('uploadId'),
            'key': params.get('key'),
            'parts': json.loads(params.get('parts', '[]'))
        }
        return complete_multipart(body, headers)
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': str(e)})
        }

def handle_delete_request(event, headers):
    """Processa requisições DELETE"""
    try:
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'success': True, 'message': 'Delete não implementado'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': str(e)})
        }