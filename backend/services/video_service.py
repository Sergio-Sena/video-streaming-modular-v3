"""
📹 MICROSERVIÇO DE VÍDEOS
Responsabilidade única: Gerenciamento de vídeos, upload e listagem
"""
import json
import boto3
import jwt
import os
import re
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoService:
    def __init__(self):
        self.jwt_secret = 'video-streaming-jwt-super-secret-key-2025'
        self.s3_client = boto3.client('s3')
        self.bucket_name = 'video-streaming-sstech-eaddf6a1'
        self.cloudfront_url = os.environ.get('CLOUDFRONT_URL', 'https://d2we88koy23cl4.cloudfront.net')
    
    def verify_authentication(self, event: Dict) -> Dict:
        """Verifica autenticação JWT"""
        try:
            auth_header = event['headers'].get('Authorization') or event['headers'].get('authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                return {'valid': False, 'message': 'Token não fornecido'}
            
            token = auth_header.replace('Bearer ', '')
            
            try:
                decoded = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
                
                if 'exp' in decoded and datetime.utcnow().timestamp() > decoded['exp']:
                    return {'valid': False, 'message': 'Token expirado'}
                
                return {
                    'valid': True,
                    'user': {
                        'email': decoded.get('email'),
                        'sub': decoded.get('sub')
                    }
                }
                
            except jwt.InvalidTokenError:
                return {'valid': False, 'message': 'Token inválido'}
                
        except Exception as e:
            logger.error(f"Erro na autenticação: {str(e)}")
            return {'valid': False, 'message': 'Erro na autenticação'}
    
    def generate_upload_url(self, file_name: str, file_type: str, file_size: int, 
                          folder_path: str = '', user: Dict = None) -> Dict:
        """Gera URL pré-assinada para upload"""
        try:
            # Validação e sanitização
            safe_filename = self._sanitize_filename(file_name)
            clean_path = self._sanitize_path(folder_path) if folder_path else ''
            
            if not safe_filename:
                return {'success': False, 'message': 'Nome do arquivo inválido'}
            
            if file_size <= 0:
                return {'success': False, 'message': 'Tamanho do arquivo inválido'}
            
            # Gera chave única
            timestamp = int(datetime.now().timestamp())
            if clean_path:
                key = f'videos/{clean_path}/{timestamp}-{safe_filename}'
            else:
                key = f'videos/{timestamp}-{safe_filename}'
            
            content_type = self._get_content_type(safe_filename, file_type)
            
            # Log da operação
            user_email = user.get('email', 'unknown') if user else 'unknown'
            logger.info(f"Upload iniciado: {key} por {user_email}")
            
            # Multipart para arquivos grandes
            if file_size > 50 * 1024 * 1024:
                response = self.s3_client.create_multipart_upload(
                    Bucket=self.bucket_name,
                    Key=key,
                    ContentType=content_type,
                    Metadata={
                        'uploaded-by': user_email,
                        'upload-timestamp': str(timestamp)
                    }
                )
                
                return {
                    'success': True,
                    'multipart': True,
                    'uploadId': response['UploadId'],
                    'key': key,
                    'message': 'Multipart upload iniciado'
                }
            else:
                # Upload simples
                upload_url = self.s3_client.generate_presigned_url(
                    'put_object',
                    Params={
                        'Bucket': self.bucket_name,
                        'Key': key,
                        'ContentType': content_type,
                        'Metadata': {
                            'uploaded-by': user_email,
                            'upload-timestamp': str(timestamp)
                        }
                    },
                    ExpiresIn=3600
                )
                
                return {
                    'success': True,
                    'uploadUrl': upload_url,
                    'key': key,
                    'message': 'URL de upload gerada'
                }
        
        except Exception as e:
            logger.error(f"Erro ao gerar URL: {str(e)}")
            return {'success': False, 'message': 'Erro ao gerar URL de upload'}
    
    def list_videos(self, show_hierarchy: bool = False) -> Dict:
        """Lista vídeos com suporte a hierarquia"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='videos/'
            )
            
            if show_hierarchy:
                hierarchy = self._build_hierarchy(response)
                return {'success': True, 'hierarchy': hierarchy}
            else:
                items = self._build_flat_list(response)
                return {'success': True, 'items': items}
        
        except Exception as e:
            logger.error(f"Erro ao listar vídeos: {str(e)}")
            return {'success': False, 'message': 'Erro ao listar vídeos'}
    
    def delete_item(self, key: str, item_type: str = 'file', user: Dict = None) -> Dict:
        """Deleta vídeo ou pasta"""
        try:
            # Validação de segurança
            if not key.startswith('videos/'):
                return {'success': False, 'message': 'Operação não permitida'}
            
            user_email = user.get('email', 'unknown') if user else 'unknown'
            logger.info(f"Deletando {item_type}: {key} por {user_email}")
            
            if item_type == 'folder':
                # Deleta pasta recursivamente
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=key
                )
                
                if 'Contents' in response:
                    objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
                    
                    if objects_to_delete:
                        self.s3_client.delete_objects(
                            Bucket=self.bucket_name,
                            Delete={'Objects': objects_to_delete}
                        )
            else:
                # Deleta arquivo único
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=key
                )
            
            return {'success': True, 'message': 'Item deletado com sucesso'}
        
        except Exception as e:
            logger.error(f"Erro ao deletar: {str(e)}")
            return {'success': False, 'message': 'Erro ao deletar item'}
    
    def get_multipart_url(self, upload_id: str, part_number: int, key: str) -> Dict:
        """Gera URL para parte do multipart upload"""
        try:
            upload_url = self.s3_client.generate_presigned_url(
                'upload_part',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key,
                    'PartNumber': part_number,
                    'UploadId': upload_id
                },
                ExpiresIn=3600
            )
            
            return {'success': True, 'uploadUrl': upload_url}
        
        except Exception as e:
            logger.error(f"Erro multipart URL: {str(e)}")
            return {'success': False, 'message': 'Erro ao gerar URL multipart'}
    
    def complete_multipart_upload(self, upload_id: str, parts: List[Dict], key: str, user: Dict = None) -> Dict:
        """Completa multipart upload"""
        try:
            response = self.s3_client.complete_multipart_upload(
                Bucket=self.bucket_name,
                Key=key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
            
            user_email = user.get('email', 'unknown') if user else 'unknown'
            logger.info(f"Upload concluído: {key} por {user_email}")
            
            return {
                'success': True,
                'location': response['Location'],
                'message': 'Upload concluído'
            }
        
        except Exception as e:
            logger.error(f"Erro ao completar upload: {str(e)}")
            return {'success': False, 'message': 'Erro ao completar upload'}
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitiza nome do arquivo"""
        if not filename:
            return ''
        
        # Remove caracteres perigosos
        safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        safe_name = re.sub(r'_+', '_', safe_name)
        return safe_name.strip('_')[:100]  # Limita tamanho
    
    def _sanitize_path(self, path: str) -> str:
        """Sanitiza caminho de pasta"""
        if not path:
            return ''
        
        # Remove path traversal e caracteres perigosos
        clean_path = path.replace('..', '').replace('\\', '/').strip('/')
        clean_path = re.sub(r'[^a-zA-Z0-9/_-]', '_', clean_path)
        return clean_path[:200]  # Limita tamanho
    
    def _get_content_type(self, filename: str, file_type: str) -> str:
        """Determina Content-Type"""
        if file_type and file_type != 'application/octet-stream':
            return file_type
        
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        content_types = {
            'mp4': 'video/mp4',
            'ts': 'video/mp2t',
            'webm': 'video/webm',
            'avi': 'video/x-msvideo',
            'mov': 'video/quicktime',
            'mkv': 'video/x-matroska'
        }
        return content_types.get(ext, 'video/mp4')
    
    def _build_hierarchy(self, response: Dict) -> Dict:
        """Constrói estrutura hierárquica"""
        hierarchy = {'root': {'files': []}}
        
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].endswith('/'):
                    continue
                
                path_parts = obj['Key'].replace('videos/', '').split('/')
                
                if len(path_parts) == 1:
                    hierarchy['root']['files'].append(self._build_file_info(obj, path_parts[0]))
                else:
                    folder_name = path_parts[0]
                    if folder_name not in hierarchy:
                        hierarchy[folder_name] = {'files': []}
                    
                    hierarchy[folder_name]['files'].append(
                        self._build_file_info(obj, '/'.join(path_parts[1:]))
                    )
        
        return hierarchy
    
    def _build_flat_list(self, response: Dict) -> List[Dict]:
        """Constrói lista plana"""
        items = []
        folders = set()
        
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].endswith('/'):
                    continue
                
                path_parts = obj['Key'].replace('videos/', '').split('/')
                
                if len(path_parts) > 1:
                    folders.add(path_parts[0])
                
                items.append({
                    'key': obj['Key'],
                    'name': obj['Key'].split('/')[-1],
                    'size': obj['Size'],
                    'lastModified': obj['LastModified'].isoformat(),
                    'url': f'{self.cloudfront_url}/{obj["Key"]}',
                    'type': 'file'
                })
        
        # Adiciona pastas
        for folder in folders:
            items.insert(0, {
                'key': f'videos/{folder}/',
                'name': folder,
                'type': 'folder'
            })
        
        return items
    
    def _build_file_info(self, obj: Dict, name: str) -> Dict:
        """Constrói informações do arquivo"""
        return {
            'key': obj['Key'],
            'name': name,
            'size': obj['Size'],
            'lastModified': obj['LastModified'].isoformat(),
            'url': f'{self.cloudfront_url}/{obj["Key"]}'
        }

# Instância global
video_service = VideoService()

def lambda_handler(event, context):
    """Handler Lambda para vídeos"""
    
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Requested-With',
        'Access-Control-Allow-Methods': 'POST,GET,DELETE,OPTIONS',
        'Content-Type': 'application/json'
    }
    
    if event['httpMethod'] == 'OPTIONS':
        return {'statusCode': 200, 'headers': cors_headers, 'body': ''}
    
    try:
        # Verificação de autenticação
        auth_result = video_service.verify_authentication(event)
        if not auth_result['valid']:
            return {
                'statusCode': 401,
                'headers': cors_headers,
                'body': json.dumps({'success': False, 'message': auth_result['message']})
            }
        
        user = auth_result['user']
        
        # Roteamento
        if event['httpMethod'] == 'POST':
            body = json.loads(event['body'])
            action = body.get('action')
            
            if action == 'get-part-url':
                result = video_service.get_multipart_url(
                    body.get('uploadId', ''),
                    body.get('partNumber', 0),
                    body.get('key', '')
                )
            elif action == 'complete-multipart':
                result = video_service.complete_multipart_upload(
                    body.get('uploadId', ''),
                    body.get('parts', []),
                    body.get('key', ''),
                    user
                )
            else:
                result = video_service.generate_upload_url(
                    body.get('fileName', ''),
                    body.get('fileType', ''),
                    body.get('fileSize', 0),
                    body.get('folderPath', ''),
                    user
                )
        
        elif event['httpMethod'] == 'GET':
            show_hierarchy = event.get('queryStringParameters', {}).get('hierarchy') == 'true' if event.get('queryStringParameters') else False
            result = video_service.list_videos(show_hierarchy)
        
        elif event['httpMethod'] == 'DELETE':
            body = json.loads(event['body'])
            result = video_service.delete_item(
                body.get('key', ''),
                body.get('type', 'file'),
                user
            )
        
        else:
            result = {'success': False, 'message': 'Método não permitido'}
        
        status_code = 200 if result.get('success') else 400
        
        return {
            'statusCode': status_code,
            'headers': cors_headers,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Erro no handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'success': False, 'message': 'Erro interno'})
        }