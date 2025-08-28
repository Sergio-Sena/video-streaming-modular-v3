import boto3
import json

# Atualizar código da Lambda via API
lambda_client = boto3.client('lambda')

# Código corrigido
code = '''
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
                            'url': f'https://d2we88koy23cl4.cloudfront.net/{obj["Key"]}'
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
                            'url': f'https://d2we88koy23cl4.cloudfront.net/{obj["Key"]}'
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
                        'url': f'https://d2we88koy23cl4.cloudfront.net/{obj["Key"]}',
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
'''

print("Código de correção criado")