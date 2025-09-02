import json
import boto3
import hashlib
import hmac
import base64
import uuid
from datetime import datetime, timedelta

# AWS Clients
secrets_client = boto3.client('secretsmanager')
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')

import os

# Constants from environment variables
S3_BUCKET = os.environ.get('S3_BUCKET', 'drive-online-storage')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', 'arn:aws:sns:us-east-1:969430605054:video-streaming-password-reset')
DEFAULT_USER_EMAIL = os.environ.get('DEFAULT_USER_EMAIL', 'user@example.com')
DEFAULT_USER_ID = os.environ.get('DEFAULT_USER_ID', 'user-default')
DEFAULT_USER_NAME = os.environ.get('DEFAULT_USER_NAME', 'Default User')

def get_secret(secret_name: str) -> str:
    """Get secret from AWS Secrets Manager"""
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except Exception as e:
        print(f"Error getting secret {secret_name}: {e}")
        if secret_name == 'drive-online-user-password':
            return hash_password(os.environ.get('DEFAULT_PASSWORD', 'defaultpassword'))
        elif secret_name == 'drive-online-jwt-secret':
            return 'super-secret-jwt-key-2025'
        return ''

def hash_password(password: str) -> str:
    """Hash password with SHA256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

def create_jwt_token(payload: dict, secret: str) -> str:
    """Create JWT token using native Python"""
    header = {"alg": "HS256", "typ": "JWT"}
    payload['exp'] = int((datetime.utcnow() + timedelta(hours=24)).timestamp())
    payload['iat'] = int(datetime.utcnow().timestamp())
    
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    
    message = f"{header_b64}.{payload_b64}"
    signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def verify_jwt_token(token: str, secret: str) -> dict:
    """Verify JWT token using native Python"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        header_b64, payload_b64, signature_b64 = parts
        
        message = f"{header_b64}.{payload_b64}"
        expected_signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
        expected_signature_b64 = base64.urlsafe_b64encode(expected_signature).decode().rstrip('=')
        
        if signature_b64 != expected_signature_b64:
            return None
        
        payload_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_padded).decode())
        
        if payload.get('exp', 0) < int(datetime.utcnow().timestamp()):
            return None
        
        return payload
        
    except Exception as e:
        print(f"JWT verification error: {e}")
        return None

def get_user_from_token(headers: dict) -> dict:
    """Extract and verify user from Authorization header"""
    auth_header = headers.get('Authorization') or headers.get('authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.replace('Bearer ', '')
    secret = get_secret('drive-online-jwt-secret')
    payload = verify_jwt_token(token, secret)
    
    if not payload:
        return None
    
    return {
        'id': payload.get('user_id'),
        'email': payload.get('sub'),
        'name': payload.get('name')
    }

def create_reset_token(email: str) -> str:
    """Create password reset token"""
    secret = get_secret('drive-online-jwt-secret')
    payload = {
        "email": email,
        "type": "password_reset",
        "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp())
    }
    return create_jwt_token(payload, secret)

def verify_reset_token(token: str) -> str:
    """Verify reset token and return email"""
    secret = get_secret('drive-online-jwt-secret')
    payload = verify_jwt_token(token, secret)
    
    if not payload or payload.get('type') != 'password_reset':
        return None
    
    return payload.get('email')

def get_user_by_email(email: str) -> dict:
    """Get user data"""
    if email != DEFAULT_USER_EMAIL:
        return None
    
    password_hash = get_secret('drive-online-user-password')
    
    return {
        'id': DEFAULT_USER_ID,
        'email': DEFAULT_USER_EMAIL,
        'name': DEFAULT_USER_NAME,
        'password_hash': password_hash,
        'created_at': '2025-01-01T00:00:00Z',
        'is_active': True
    }

def update_user_password(email: str, new_password: str):
    """Update user password in Secrets Manager"""
    if email != DEFAULT_USER_EMAIL:
        raise ValueError("User not found")
    
    hashed_password = hash_password(new_password)
    
    try:
        secrets_client.update_secret(
            SecretId='drive-online-user-password',
            SecretString=hashed_password
        )
        print(f"Password updated for {email}")
    except Exception as e:
        print(f"Error updating password: {e}")
        raise

# AUTH HANDLERS
def handle_login(body):
    """Handle login request"""
    try:
        data = json.loads(body) if isinstance(body, str) else body
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Email and password required'})
            }
        
        user = get_user_by_email(email)
        if not user or not verify_password(password, user['password_hash']):
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Invalid credentials'})
            }
        
        secret = get_secret('drive-online-jwt-secret')
        payload = {
            "sub": user['email'],
            "user_id": user['id'],
            "name": user['name']
        }
        
        token = create_jwt_token(payload, secret)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'token': token,
                'refreshToken': token,
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['name']
                }
            })
        }
        
    except Exception as e:
        print(f"Login error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

def handle_forgot_password(body):
    """Handle forgot password request"""
    try:
        data = json.loads(body) if isinstance(body, str) else body
        email = data.get('email')
        
        if not email:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Email required'})
            }
        
        user = get_user_by_email(email)
        if not user:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'If email exists, reset instructions were sent'})
            }
        
        reset_token = create_reset_token(email)
        
        try:
            reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
            
            message = f"""
Olá!

Você solicitou a redefinição de sua senha no Drive Online.

Clique no link abaixo para redefinir sua senha:
{reset_link}

Este link expira em 1 hora.

Se você não solicitou esta redefinição, ignore este email.

Atenciosamente,
Equipe Drive Online
"""
            
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=message,
                Subject='Drive Online - Redefinição de Senha'
            )
            
            print(f"Reset email sent to {email}: {reset_link}")
            
        except Exception as e:
            print(f"Error sending reset email: {e}")
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Password reset instructions sent'})
        }
        
    except Exception as e:
        print(f"Forgot password error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

def handle_reset_password(body):
    """Handle reset password request"""
    try:
        data = json.loads(body) if isinstance(body, str) else body
        token = data.get('token')
        new_password = data.get('newPassword')
        
        if not token or not new_password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Token and new password required'})
            }
        
        email = verify_reset_token(token)
        if not email:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Invalid or expired token'})
            }
        
        update_user_password(email, new_password)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Password reset successfully'})
        }
        
    except Exception as e:
        print(f"Reset password error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

def handle_validate_reset_token(query_params):
    """Handle validate reset token request"""
    try:
        token = query_params.get('token') if query_params else None
        
        if not token:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Token required'})
            }
        
        email = verify_reset_token(token)
        if not email:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Invalid or expired token'})
            }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Token is valid', 'email': email})
        }
        
    except Exception as e:
        print(f"Validate token error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

# FILES HANDLERS
def handle_list_files(headers):
    """Handle list files request"""
    try:
        user = get_user_from_token(headers)
        if not user:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Unauthorized'})
            }
        
        # List files from S3 for user
        try:
            response = s3_client.list_objects_v2(
                Bucket=S3_BUCKET,
                Prefix=f"users/{user['id']}/"
            )
            
            files = []
            for obj in response.get('Contents', []):
                if obj['Key'].endswith('/'):  # Skip folders
                    continue
                    
                filename = obj['Key'].split('/')[-1]
                
                # Detectar tipo MIME baseado na extensão
                ext = filename.lower().split('.')[-1] if '.' in filename else ''
                content_type = 'unknown'
                
                if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']:
                    content_type = f'image/{ext}'
                elif ext in ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv']:
                    content_type = f'video/{ext}'
                elif ext in ['pdf']:
                    content_type = 'application/pdf'
                elif ext in ['doc', 'docx']:
                    content_type = 'application/msword'
                elif ext in ['txt']:
                    content_type = 'text/plain'
                
                files.append({
                    'id': obj['Key'],
                    'name': filename,
                    'size': obj['Size'],
                    'lastModified': obj['LastModified'].isoformat(),
                    'type': content_type
                })
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'files': files})
            }
            
        except Exception as e:
            print(f"S3 list error: {e}")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'files': []})
            }
        
    except Exception as e:
        print(f"List files error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

def handle_upload_url(headers, body):
    """Handle upload URL generation request"""
    try:
        user = get_user_from_token(headers)
        if not user:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Unauthorized'})
            }
        
        data = json.loads(body) if isinstance(body, str) else body
        file_name = data.get('fileName')
        file_size = data.get('fileSize', 0)
        content_type = data.get('contentType', 'application/octet-stream')
        
        if not file_name:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'fileName is required'})
            }
        
        # Generate unique file ID and S3 key
        import time
        file_id = f"{int(time.time())}-{file_name}"
        key = f"users/{user['id']}/{file_id}"
        
        try:
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': S3_BUCKET,
                    'Key': key,
                    'ContentType': content_type
                },
                ExpiresIn=3600
            )
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'uploadUrl': presigned_url,
                    'fileId': file_id,
                    'key': key
                })
            }
            
        except Exception as e:
            print(f"S3 presigned URL error: {e}")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Failed to generate upload URL'})
            }
        
    except Exception as e:
        print(f"Upload URL error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

def handle_upload_file(headers, body):
    """Handle file upload request"""
    try:
        user = get_user_from_token(headers)
        if not user:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Unauthorized'})
            }
        
        # Generate presigned URL for upload
        file_id = str(uuid.uuid4())
        key = f"users/{user['id']}/{file_id}"
        
        try:
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={'Bucket': S3_BUCKET, 'Key': key},
                ExpiresIn=3600
            )
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'uploadUrl': presigned_url,
                    'fileId': file_id,
                    'key': key
                })
            }
            
        except Exception as e:
            print(f"S3 presigned URL error: {e}")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Failed to generate upload URL'})
            }
        
    except Exception as e:
        print(f"Upload file error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

def handle_multipart_start(headers, body):
    """Handle multipart upload start request"""
    try:
        user = get_user_from_token(headers)
        if not user:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Unauthorized'})
            }
        
        data = json.loads(body) if isinstance(body, str) else body
        file_name = data.get('fileName')
        content_type = data.get('contentType', 'application/octet-stream')
        
        if not file_name:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'fileName is required'})
            }
        
        # Generate unique file ID and S3 key
        import time
        file_id = f"{int(time.time())}-{file_name}"
        s3_key = f"users/{user['id']}/{file_id}"
        
        try:
            # Start multipart upload
            response = s3_client.create_multipart_upload(
                Bucket=S3_BUCKET,
                Key=s3_key,
                ContentType=content_type
            )
            
            upload_id = response['UploadId']
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'uploadId': upload_id,
                    'fileId': file_id,
                    'key': s3_key
                })
            }
            
        except Exception as e:
            print(f"S3 multipart start error: {e}")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Failed to start multipart upload'})
            }
        
    except Exception as e:
        print(f"Multipart start error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

def handle_multipart_complete(headers, body):
    """Handle multipart upload complete request"""
    try:
        user = get_user_from_token(headers)
        if not user:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Unauthorized'})
            }
        
        data = json.loads(body) if isinstance(body, str) else body
        upload_id = data.get('uploadId')
        s3_key = data.get('key')
        parts = data.get('parts', [])
        
        if not upload_id or not s3_key:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'uploadId and key are required'})
            }
        
        try:
            # Complete multipart upload
            s3_client.complete_multipart_upload(
                Bucket=S3_BUCKET,
                Key=s3_key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'Multipart upload completed successfully'})
            }
            
        except Exception as e:
            print(f"S3 multipart complete error: {e}")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Failed to complete multipart upload'})
            }
        
    except Exception as e:
        print(f"Multipart complete error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

def handle_multipart_chunk_url(headers, body):
    """Handle multipart chunk URL generation request"""
    try:
        user = get_user_from_token(headers)
        if not user:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Unauthorized'})
            }
        
        data = json.loads(body) if isinstance(body, str) else body
        upload_id = data.get('uploadId')
        s3_key = data.get('key')
        part_number = data.get('partNumber')
        
        if not upload_id or not s3_key or not part_number:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'uploadId, key and partNumber are required'})
            }
        
        try:
            # Generate presigned URL for chunk upload
            chunk_url = s3_client.generate_presigned_url(
                'upload_part',
                Params={
                    'Bucket': S3_BUCKET,
                    'Key': s3_key,
                    'UploadId': upload_id,
                    'PartNumber': part_number
                },
                ExpiresIn=3600
            )
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'chunkUrl': chunk_url,
                    'partNumber': part_number
                })
            }
            
        except Exception as e:
            print(f"S3 chunk URL error: {e}")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Failed to generate chunk URL'})
            }
        
    except Exception as e:
        print(f"Chunk URL error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

def handle_confirm_upload(headers, file_id):
    """Handle upload confirmation request"""
    try:
        user = get_user_from_token(headers)
        if not user:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Unauthorized'})
            }
        
        # Just return success - file should already be in S3
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Upload confirmed successfully'})
        }
        
    except Exception as e:
        print(f"Confirm upload error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

def handle_download_file(headers, file_id):
    """Handle file download request"""
    try:
        user = get_user_from_token(headers)
        if not user:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Unauthorized'})
            }
        
        key = f"users/{user['id']}/{file_id}"
        
        try:
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET, 'Key': key},
                ExpiresIn=3600
            )
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'downloadUrl': presigned_url
                })
            }
            
        except Exception as e:
            print(f"S3 download URL error: {e}")
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'File not found'})
            }
        
    except Exception as e:
        print(f"Download file error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

def handle_delete_file(headers, file_id):
    """Handle file delete request"""
    try:
        user = get_user_from_token(headers)
        if not user:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Unauthorized'})
            }
        
        key = f"users/{user['id']}/{file_id}"
        
        try:
            s3_client.delete_object(Bucket=S3_BUCKET, Key=key)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'File deleted successfully'})
            }
            
        except Exception as e:
            print(f"S3 delete error: {e}")
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'File not found'})
            }
        
    except Exception as e:
        print(f"Delete file error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

# USER HANDLERS
def handle_get_profile(headers):
    """Handle get user profile request"""
    try:
        user = get_user_from_token(headers)
        if not user:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Unauthorized'})
            }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'created_at': '2025-01-01T00:00:00Z'
            })
        }
        
    except Exception as e:
        print(f"Get profile error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

def handle_get_storage(headers):
    """Handle get storage usage request"""
    try:
        user = get_user_from_token(headers)
        if not user:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'detail': 'Unauthorized'})
            }
        
        try:
            response = s3_client.list_objects_v2(
                Bucket=S3_BUCKET,
                Prefix=f"users/{user['id']}/"
            )
            
            total_size = sum(obj['Size'] for obj in response.get('Contents', []))
            file_count = len([obj for obj in response.get('Contents', []) if not obj['Key'].endswith('/')])
            
            # Limite do projeto: 5TB
            total_limit = 5 * 1024 * 1024 * 1024 * 1024  # 5TB
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'used': total_size,
                    'total': total_limit,
                    'files': file_count,
                    'percentage': (total_size / total_limit) * 100 if total_limit > 0 else 0,
                    'project_total': total_size  # Tamanho total do projeto
                })
            }
            
        except Exception as e:
            print(f"S3 storage error: {e}")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'used': 0,
                    'total': 5 * 1024 * 1024 * 1024 * 1024,  # 5TB
                    'files': 0,
                    'percentage': 0,
                    'project_total': 0
                })
            }
        
    except Exception as e:
        print(f"Get storage error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'detail': 'Internal server error'})
        }

def handle_health():
    """Handle health check"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'Drive Online API (Complete)',
            'features': ['JWT', 'Password Reset', 'File Management', 'User Profile', 'S3 Storage']
        })
    }

def lambda_handler(event, context):
    """Main Lambda handler"""
    try:
        print(f"Event: {json.dumps(event)}")
        
        if 'httpMethod' in event:
            method = event['httpMethod']
            path = event.get('path', '/')
            body = event.get('body')
            headers = event.get('headers', {})
            query_params = event.get('queryStringParameters')
            path_params = event.get('pathParameters', {})
            
            # CORS preflight
            if method == 'OPTIONS':
                return {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                    }
                }
            
            # Route requests
            if path == '/health' and method == 'GET':
                return handle_health()
            
            # Auth routes
            elif path == '/auth/login' and method == 'POST':
                return handle_login(body)
            elif path == '/auth/forgot-password' and method == 'POST':
                return handle_forgot_password(body)
            elif path == '/auth/reset-password' and method == 'POST':
                return handle_reset_password(body)
            elif path == '/auth/validate-reset-token' and method == 'GET':
                return handle_validate_reset_token(query_params)
            
            # Files routes
            elif path == '/files' and method == 'GET':
                return handle_list_files(headers)
            elif path == '/files/upload-url' and method == 'POST':
                return handle_upload_url(headers, body)
            elif path == '/files/multipart/start' and method == 'POST':
                return handle_multipart_start(headers, body)
            elif path == '/files/multipart/complete' and method == 'POST':
                return handle_multipart_complete(headers, body)
            elif path == '/files/multipart/chunk-url' and method == 'POST':
                return handle_multipart_chunk_url(headers, body)
            elif path == '/files/upload' and method == 'POST':
                return handle_upload_file(headers, body)
            elif path.startswith('/files/') and path.endswith('/confirm') and method == 'POST':
                file_id = path.split('/')[-2]
                return handle_confirm_upload(headers, file_id)
            elif path.startswith('/files/') and path.endswith('/download') and method == 'GET':
                file_id = path.split('/')[-2]
                return handle_download_file(headers, file_id)
            elif path.startswith('/files/') and method == 'DELETE':
                file_id = path.split('/')[-1]
                return handle_delete_file(headers, file_id)
            
            # User routes
            elif path == '/user/profile' and method == 'GET':
                return handle_get_profile(headers)
            elif path == '/user/storage' and method == 'GET':
                return handle_get_storage(headers)
            
            else:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'detail': f'Not found: {method} {path}'})
                }
        else:
            return handle_health()
            
    except Exception as e:
        print(f"Handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'detail': 'Internal server error'})
        }

# Alias for compatibility
handler = lambda_handler