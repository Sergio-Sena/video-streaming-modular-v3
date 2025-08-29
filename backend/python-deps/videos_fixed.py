import json
import boto3
import os
from datetime import datetime

def handler(event, context):
    """Handler principal para vídeos com CORS corrigido"""
    
    print(f"Event received: {json.dumps(event)}")
    
    # CORS headers para todas as respostas
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Requested-With',
        'Access-Control-Allow-Methods': 'POST,GET,OPTIONS,DELETE,PUT',
        'Access-Control-Max-Age': '86400',
        'Content-Type': 'application/json'
    }
    
    # Resposta para OPTIONS (CORS preflight)
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': ''
        }
    
    try:
        # Verificação de token simplificada para teste
        auth_header = event.get('headers', {}).get('Authorization') or event.get('headers', {}).get('authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {
                'statusCode': 401,
                'headers': cors_headers,
                'body': json.dumps({'success': False, 'message': 'Token não fornecido'})
            }
        
        token = auth_header.replace('Bearer ', '')
        print(f"Token recebido: {token[:20]}...")
        
        # Aceita tokens de teste/fallback
        if not (token.startswith('test-token-') or token.startswith('cognito-fallback-token-')):
            # Para tokens reais, aceita por enquanto (desenvolvimento)
            print("Token real Cognito - aceitando para desenvolvimento")
        
        # Roteamento por método HTTP
        if event['httpMethod'] == 'POST':
            return handle_post_request(event, cors_headers)
        elif event['httpMethod'] == 'GET':
            return list_videos(event, cors_headers)
        elif event['httpMethod'] == 'DELETE':
            return delete_item(event, cors_headers)
        else:
            return {
                'statusCode': 405,
                'headers': cors_headers,
                'body': json.dumps({'success': False, 'message': 'Método não permitido'})
            }
            
    except Exception as e:
        print(f"Erro geral: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'success': False, 'message': 'Erro interno do servidor'})
        }

def handle_post_request(event, cors_headers):
    """Trata requisições POST"""
    try:
        body = json.loads(event.get('body', '{}'))
        action = body.get('action')
        
        if action == 'check-existing':
            return check_existing_files(body, cors_headers)
        elif action == 'get-part-url':
            return get_multipart_url(body, cors_headers)
        elif action == 'complete-multipart':
            return complete_multipart_upload(body, cors_headers)
        else:
            return generate_upload_url(body, cors_headers)
            
    except Exception as e:
        print(f"Erro POST: {str(e)}")
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({'success': False, 'message': 'Erro na requisição POST'})
        }

def generate_upload_url(body, cors_headers):
    """Gera URL pré-assinada para upload"""
    try:
        file_name = body.get('fileName')
        file_type = body.get('fileType', 'video/mp4')
        file_size = body.get('fileSize', 0)
        folder_path = body.get('folderPath', '')
        
        if not file_name:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'success': False, 'message': 'Nome do arquivo é obrigatório'})
            }
        
        # Gera chave única
        timestamp = int(datetime.now().timestamp())
        if folder_path and folder_path.strip():
            clean_path = folder_path.replace('\\', '/').strip('/')
            key = f'videos/{clean_path}/{timestamp}-{file_name}'
        else:
            key = f'videos/{timestamp}-{file_name}'
        
        s3_client = boto3.client('s3')
        bucket = 'video-streaming-sstech-eaddf6a1'
        
        # Verifica se precisa multipart (>20MB)
        if file_size > 20 * 1024 * 1024:
            # Multipart upload
            response = s3_client.create_multipart_upload(
                Bucket=bucket,
                Key=key,
                ContentType=file_type
            )
            
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'success': True,
                    'multipart': True,
                    'uploadId': response['UploadId'],
                    'key': key,
                    'message': 'Multipart upload iniciado'
                })
            }
        else:
            # Upload simples
            upload_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': bucket,
                    'Key': key,
                    'ContentType': file_type
                },
                ExpiresIn=3600
            )
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'success': True,
                'uploadUrl': upload_url,
                'key': key,
                'message': 'URL de upload gerada'
            })
        }
        
    except Exception as e:
        print(f"Erro upload URL: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'success': False, 'message': 'Erro ao gerar URL de upload'})
        }

def list_videos(event, cors_headers):
    """Lista vídeos do S3 - apenas MP4 convertidos"""
    try:
        s3_client = boto3.client('s3')
        bucket = 'video-streaming-sstech-eaddf6a1'
        
        # Lista arquivos originais
        response_videos = s3_client.list_objects_v2(
            Bucket=bucket,
            Prefix='videos/'
        )
        
        # Lista arquivos convertidos
        response_converted = s3_client.list_objects_v2(
            Bucket=bucket,
            Prefix='converted/'
        )
        
        items = []
        converted_files = set()
        
        # Mapeia arquivos convertidos
        if 'Contents' in response_converted:
            for obj in response_converted['Contents']:
                if obj['Key'].endswith('.mp4'):
                    # Extrai nome original sem timestamp
                    converted_name = obj['Key'].replace('converted/', '')
                    converted_files.add(converted_name)
                    
                    items.append({
                        'key': obj['Key'],
                        'name': converted_name,
                        'size': obj['Size'],
                        'lastModified': obj['LastModified'].isoformat(),
                        'url': f"https://d2we88koy23cl4.cloudfront.net/{obj['Key']}",
                        'type': 'file',
                        'converted': True
                    })
        
        # Mostra originais até conversão ficar pronta
        if 'Contents' in response_videos:
            for obj in response_videos['Contents']:
                if obj['Key'].endswith('/'):
                    continue
                
                file_name = obj['Key'].split('/')[-1]
                file_ext = file_name.lower().split('.')[-1]
                
                # Para arquivos que precisam conversão (.ts, .avi, etc)
                if file_ext in ['ts', 'avi', 'mov', 'mkv', 'wmv', 'flv']:
                    # Remove timestamp para comparar com convertido
                    clean_name = '-'.join(file_name.split('-')[1:]) if '-' in file_name else file_name
                    converted_name = clean_name.replace(f'.{file_ext}', '.mp4')
                    
                    # Só mostra original se conversão ainda não existe
                    if converted_name not in converted_files:
                        items.append({
                            'key': obj['Key'],
                            'name': file_name,
                            'size': obj['Size'],
                            'lastModified': obj['LastModified'].isoformat(),
                            'url': f"https://d2we88koy23cl4.cloudfront.net/{obj['Key']}",
                            'type': 'file',
                            'converting': True,
                            'status': 'Convertendo para MP4...'
                        })
                
                # Para MP4 originais, sempre mostra
                elif file_ext == 'mp4':
                    items.append({
                        'key': obj['Key'],
                        'name': file_name,
                        'size': obj['Size'],
                        'lastModified': obj['LastModified'].isoformat(),
                        'url': f"https://d2we88koy23cl4.cloudfront.net/{obj['Key']}",
                        'type': 'file',
                        'converted': False
                    })
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'success': True,
                'items': items
            })
        }
        
    except Exception as e:
        print(f"Erro list videos: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'success': False, 'message': 'Erro ao listar vídeos'})
        }

def delete_item(event, cors_headers):
    """Deleta item do S3"""
    try:
        body = json.loads(event.get('body', '{}'))
        key = body.get('key')
        
        if not key:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'success': False, 'message': 'Chave do item é obrigatória'})
            }
        
        s3_client = boto3.client('s3')
        s3_client.delete_object(
            Bucket='video-streaming-sstech-eaddf6a1',
            Key=key
        )
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'success': True,
                'message': 'Item deletado com sucesso'
            })
        }
        
    except Exception as e:
        print(f"Erro delete: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'success': False, 'message': 'Erro ao deletar item'})
        }

def get_multipart_url(body, cors_headers):
    """Gera URL para parte do multipart upload"""
    try:
        upload_id = body.get('uploadId')
        part_number = body.get('partNumber')
        key = body.get('key')
        
        if not all([upload_id, part_number, key]):
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'success': False, 'message': 'Parâmetros multipart obrigatórios'})
            }
        
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
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'success': True,
                'uploadUrl': upload_url
            })
        }
        
    except Exception as e:
        print(f"Erro multipart URL: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'success': False, 'message': 'Erro ao gerar URL multipart'})
        }

def complete_multipart_upload(body, cors_headers):
    """Completa multipart upload"""
    try:
        upload_id = body.get('uploadId')
        parts = body.get('parts')
        key = body.get('key')
        
        if not all([upload_id, parts, key]):
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'success': False, 'message': 'Parâmetros de finalização obrigatórios'})
            }
        
        s3_client = boto3.client('s3')
        
        response = s3_client.complete_multipart_upload(
            Bucket='video-streaming-sstech-eaddf6a1',
            Key=key,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'success': True,
                'location': response['Location'],
                'message': 'Upload concluído'
            })
        }
        
    except Exception as e:
        print(f"Erro complete multipart: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'success': False, 'message': 'Erro ao completar upload'})
        }

def check_existing_files(body, cors_headers):
    """Verifica arquivos existentes (simplificado)"""
    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({
            'success': True,
            'existingFiles': []  # Por enquanto, não verifica duplicatas
        })
    }