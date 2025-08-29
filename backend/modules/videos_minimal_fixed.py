import json
import boto3

def handler(event, context):
    """Handler mínimo para testar"""
    
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
        # GET request - listar vídeos
        if event['httpMethod'] == 'GET':
            # Verificar se é navegação hierárquica
            query_params = event.get('queryStringParameters') or {}
            show_hierarchy = query_params.get('hierarchy') == 'true'
            current_path = query_params.get('path', '')
            
            if show_hierarchy:
                return get_hierarchy_view(current_path, headers)
            else:
                return get_simple_view(headers)
        
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

def get_hierarchy_view(current_path, headers):
    """Retorna visualização hierárquica navegável"""
    try:
        s3_client = boto3.client('s3')
        
        # Definir prefixo baseado no caminho atual
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
        
        # Processar pastas (CommonPrefixes)
        if 'CommonPrefixes' in response:
            for folder_info in response['CommonPrefixes']:
                folder_path = folder_info['Prefix']
                folder_name = folder_path.replace(prefix, '').rstrip('/')
                if folder_name:  # Evitar pastas vazias
                    folders.append({
                        'name': folder_name,
                        'path': folder_path.replace('videos/', '').rstrip('/'),
                        'type': 'folder'
                    })
        
        # Processar arquivos
        if 'Contents' in response:
            for obj in response['Contents']:
                if not obj['Key'].endswith('/') and obj['Key'] != prefix:
                    file_name = obj['Key'].replace(prefix, '')
                    if '/' not in file_name:  # Apenas arquivos do nível atual
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
    """Retorna visualização simples (atual)"""
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