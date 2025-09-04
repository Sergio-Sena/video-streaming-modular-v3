from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse, RedirectResponse, Response
from pydantic import BaseModel
from mangum import Mangum
import boto3
import bcrypt
import jwt
from datetime import datetime, timedelta
import os
import json

app = FastAPI(title="Drive Online Auth Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# AWS Clients
secrets_client = boto3.client('secretsmanager')
dynamodb = boto3.resource('dynamodb')

# Models
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    refreshToken: str
    user: dict

class User(BaseModel):
    id: str
    email: str
    name: str
    created_at: str

# Constants
JWT_SECRET = os.getenv('JWT_SECRET', 'dev-secret-key')
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Helper Functions
def get_secret(secret_name: str) -> str:
    """Get secret from AWS Secrets Manager"""
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except Exception as e:
        print(f"Error getting secret {secret_name}: {e}")
        # Development fallbacks
        if secret_name == 'drive-online-jwt-secret':
            return 'dev-jwt-secret-key-2025'
        elif secret_name == 'drive-online-user-password':
            return hash_password('sergiosena')  # Initial dev password
        elif secret_name == 'drive-online-reset-tokens':
            return '{}'
        return ''

def update_secret(secret_name: str, secret_value: str) -> bool:
    """Update secret in AWS Secrets Manager"""
    try:
        secrets_client.update_secret(
            SecretId=secret_name,
            SecretString=secret_value
        )
        return True
    except Exception as e:
        print(f"Error updating secret {secret_name}: {e}")
        return False

def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    secret = get_secret('drive-online-jwt-secret')
    return jwt.encode(to_encode, secret, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token"""
    try:
        secret = get_secret('drive-online-jwt-secret')
        payload = jwt.decode(credentials.credentials, secret, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_user_by_email(email: str) -> dict:
    """Get user data (only supports configured user)"""
    if email != 'senanetworker@gmail.com':
        return None
    
    # Get password hash from Secrets Manager
    password_hash = get_secret('drive-online-user-password')
    
    return {
        'id': 'user-sergio-sena',
        'email': 'senanetworker@gmail.com',
        'name': 'Sergio Sena',
        'password_hash': password_hash,
        'created_at': '2025-01-01T00:00:00Z',
        'is_active': True
    }

# Routes
@app.get("/")
async def root():
    return {"message": "Drive Online Auth Service", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and return JWT token"""
    
    # Get user
    user = get_user_by_email(request.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(request.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create tokens
    token_data = {
        "sub": user['email'],
        "user_id": user['id'],
        "name": user['name']
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_access_token({**token_data, "type": "refresh"})
    
    return LoginResponse(
        token=access_token,
        refreshToken=refresh_token,
        user={
            "id": user['id'],
            "email": user['email'],
            "name": user['name']
        }
    )

@app.post("/auth/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh access token"""
    try:
        secret = get_secret('drive-online-jwt-secret')
        payload = jwt.decode(credentials.credentials, secret, algorithms=[JWT_ALGORITHM])
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Create new access token
        new_token_data = {
            "sub": payload["sub"],
            "user_id": payload["user_id"],
            "name": payload["name"]
        }
        
        new_token = create_access_token(new_token_data)
        
        return {"token": new_token}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@app.post("/auth/logout")
async def logout(current_user: dict = Depends(verify_token)):
    """Logout user (invalidate token)"""
    # In a production environment, you would add the token to a blacklist
    return {"message": "Logged out successfully"}

@app.get("/auth/me")
async def get_current_user(current_user: dict = Depends(verify_token)):
    """Get current user info"""
    user = get_user_by_email(current_user["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user['id'],
        "email": user['email'],
        "name": user['name'],
        "created_at": user.get('created_at')
    }

@app.post("/auth/forgot-password")
async def forgot_password(request: dict):
    """Send password reset email"""
    email = request.get('email')
    user = get_user_by_email(email)
    
    if not user:
        # Don't reveal if email exists
        return {"message": "If email exists, reset instructions were sent"}
    
    # Generate reset token
    reset_token = create_reset_token(email)
    
    # Save token to DynamoDB (expires in 1 hour)
    save_reset_token(email, reset_token)
    
    # Send email via SNS
    send_reset_email(email, reset_token)
    
    return {"message": "Password reset instructions sent"}

@app.get("/auth/validate-reset-token")
async def validate_reset_token(token: str):
    """Validate reset token"""
    if not is_valid_reset_token(token):
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    return {"message": "Token is valid"}

@app.post("/auth/reset-password")
async def reset_password(request: dict):
    """Reset password with token"""
    token = request.get('token')
    new_password = request.get('newPassword')
    
    if not token or not new_password:
        raise HTTPException(status_code=400, detail="Token and new password required")
    
    # Validate token and get email
    email = validate_and_get_email_from_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Update password
    update_user_password(email, new_password)
    
    # Invalidate token
    invalidate_reset_token(token)
    
    return {"message": "Password reset successfully"}

# Helper functions for password reset
def create_reset_token(email: str) -> str:
    """Create password reset token"""
    import uuid
    from datetime import datetime, timedelta
    
    token_data = {
        "email": email,
        "token_type": "password_reset",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    
    secret = get_secret('drive-online-jwt-secret')
    return jwt.encode(token_data, secret, algorithm=JWT_ALGORITHM)

def save_reset_token(email: str, token: str):
    """Save reset token to Secrets Manager"""
    try:
        # Get existing tokens
        existing_tokens = get_secret('drive-online-reset-tokens')
        
        try:
            tokens_data = json.loads(existing_tokens) if existing_tokens else {}
        except json.JSONDecodeError:
            tokens_data = {}
        
        # Add new token with expiration
        tokens_data[token] = {
            'email': email,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'used': False
        }
        
        # Clean expired tokens
        now = datetime.utcnow()
        tokens_data = {
            k: v for k, v in tokens_data.items()
            if datetime.fromisoformat(v['expires_at']) > now
        }
        
        # Update secret
        update_secret('drive-online-reset-tokens', json.dumps(tokens_data))
        print(f"Reset token saved for {email}")
        
    except Exception as e:
        print(f"Error saving reset token: {e}")

def send_reset_email(email: str, token: str):
    """Send reset email via SNS"""
    try:
        sns = boto3.client('sns')
        frontend_url = os.getenv('FRONTEND_URL', 'https://videos.sstechnologies-cloud.com')
        reset_link = f"{frontend_url}/reset-password?token={token}"
        
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
        
        # Use configured SNS topic
        topic_arn = "arn:aws:sns:us-east-1:969430605054:drive-online-password-reset"
        
        sns.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject='Drive Online - Redefinição de Senha'
        )
        
        print(f"Reset email sent to {email} via SNS: {reset_link}")
            
    except Exception as e:
        print(f"Error sending reset email: {e}")
        # Fallback - print link for development
        frontend_url = os.getenv('FRONTEND_URL', 'https://videos.sstechnologies-cloud.com')
        print(f"Reset link for {email}: {frontend_url}/reset-password?token={token}")

def is_valid_reset_token(token: str) -> bool:
    """Check if reset token is valid"""
    try:
        # Validate JWT first
        secret = get_secret('drive-online-jwt-secret')
        payload = jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
        
        if payload.get('token_type') != 'password_reset':
            return False
        
        # Check in Secrets Manager
        tokens_json = get_secret('drive-online-reset-tokens')
        
        try:
            tokens_data = json.loads(tokens_json) if tokens_json else {}
        except json.JSONDecodeError:
            return False
        
        if token not in tokens_data:
            return False
        
        token_info = tokens_data[token]
        
        # Check if expired
        expires_at = datetime.fromisoformat(token_info['expires_at'])
        if datetime.utcnow() > expires_at:
            return False
        
        # Check if used
        return not token_info.get('used', False)
        
    except (jwt.ExpiredSignatureError, jwt.JWTError, Exception):
        return False

def validate_and_get_email_from_token(token: str) -> str:
    """Validate token and return email"""
    try:
        secret = get_secret('drive-online-jwt-secret')
        payload = jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
        
        if payload.get('token_type') != 'password_reset':
            return None
            
        return payload.get('email')
        
    except (jwt.ExpiredSignatureError, jwt.JWTError):
        return None

def update_user_password(email: str, new_password: str):
    """Update user password in Secrets Manager"""
    try:
        if email != 'senanetworker@gmail.com':
            raise ValueError("User not found")
        
        # Hash new password
        hashed_password = hash_password(new_password)
        
        # Update password in Secrets Manager
        success = update_secret('drive-online-user-password', hashed_password)
        
        if success:
            print(f"Password updated successfully for {email}")
        else:
            raise Exception("Failed to update password in Secrets Manager")
            
    except Exception as e:
        print(f"Error updating password: {e}")
        raise

def invalidate_reset_token(token: str):
    """Mark reset token as used in Secrets Manager"""
    try:
        # Get existing tokens
        tokens_json = get_secret('drive-online-reset-tokens')
        
        try:
            tokens_data = json.loads(tokens_json) if tokens_json else {}
        except json.JSONDecodeError:
            tokens_data = {}
        
        if token in tokens_data:
            tokens_data[token]['used'] = True
            
            # Update secret
            update_secret('drive-online-reset-tokens', json.dumps(tokens_data))
            print(f"Reset token invalidated")
        
    except Exception as e:
        print(f"Error invalidating token: {e}")

# S3 and File Management
s3_client = boto3.client('s3')
sts_client = boto3.client('sts')
STORAGE_BUCKET = 'drive-online-storage'
PUBLIC_VIDEO_BUCKET = 'automacao-video'

def is_video_file(filename: str) -> bool:
    """Check if file is a video"""
    video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.ts', '.m4v']
    return any(filename.lower().endswith(ext) for ext in video_extensions)

def copy_to_public_bucket(file_key: str, user_id: str):
    """Copy video to public bucket for streaming"""
    try:
        filename = file_key.split('/')[-1]
        public_key = f"videos/{user_id}/{filename}"
        
        s3_client.copy_object(
            CopySource={'Bucket': STORAGE_BUCKET, 'Key': file_key},
            Bucket=PUBLIC_VIDEO_BUCKET,
            Key=public_key,
            ContentType='video/mp4'
        )
        
        print(f"Video copied to public bucket: {public_key}")
        return public_key
        
    except Exception as e:
        print(f"Error copying to public bucket: {e}")
        raise

@app.get("/files")
async def get_files(current_user: dict = Depends(verify_token)):
    """Get user files from S3"""
    try:
        user_id = current_user.get('user_id', 'user-sergio-sena')
        prefix = f"users/{user_id}/"
        
        response = s3_client.list_objects_v2(
            Bucket=STORAGE_BUCKET,
            Prefix=prefix
        )
        
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                # Skip folder markers
                if obj['Key'].endswith('/'):
                    continue
                    
                file_name = obj['Key'].replace(prefix, '')
                if not file_name:  # Skip empty names
                    continue
                    
                # Generate presigned URL for file access
                file_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': STORAGE_BUCKET, 'Key': obj['Key']},
                    ExpiresIn=3600  # 1 hour
                )
                
                # Determine file type
                file_type = 'application/octet-stream'
                if file_name.lower().endswith(('.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.ts')):
                    file_type = 'video/mp4'
                elif file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                    file_type = 'image/jpeg'
                elif file_name.lower().endswith('.pdf'):
                    file_type = 'application/pdf'
                
                files.append({
                    'id': obj['Key'],
                    'name': file_name,
                    'size': obj['Size'],
                    'type': file_type,
                    'url': file_url,
                    'createdAt': obj['LastModified'].isoformat(),
                    'lastModified': obj['LastModified'].isoformat()
                })
        
        # Ordenar por data de modificação (mais recente primeiro)
        files.sort(key=lambda x: x['lastModified'], reverse=True)
        
        return {'files': files}
        
    except Exception as e:
        print(f"Error getting files: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving files")

@app.get("/user/storage")
async def get_storage_info(current_user: dict = Depends(verify_token)):
    """Get user storage information"""
    try:
        user_id = current_user.get('user_id', 'user-sergio-sena')
        prefix = f"users/{user_id}/"
        
        response = s3_client.list_objects_v2(
            Bucket=STORAGE_BUCKET,
            Prefix=prefix
        )
        
        total_size = 0
        file_count = 0
        
        if 'Contents' in response:
            for obj in response['Contents']:
                if not obj['Key'].endswith('/'):
                    total_size += obj['Size']
                    file_count += 1
        
        # 5TB limit
        total_limit = 5 * 1024 * 1024 * 1024 * 1024  # 5TB in bytes
        percentage = (total_size / total_limit) * 100 if total_limit > 0 else 0
        
        return {
            'used': total_size,
            'total': total_limit,
            'percentage': percentage,
            'files': file_count,
            'project_total': total_size
        }
        
    except Exception as e:
        print(f"Error getting storage info: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving storage information")

@app.options("/files/{file_key:path}/download")
async def download_file_options(file_key: str):
    """Handle CORS preflight for download endpoint"""
    return Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
            "Access-Control-Allow-Headers": "Range, Content-Range, Content-Type, Authorization",
            "Access-Control-Max-Age": "3600"
        }
    )

@app.get("/public/video/{file_key:path}")
async def public_video_stream(file_key: str):
    """Stream video publicly - no auth required for HTML5 video element"""
    try:
        # Decode URL-encoded characters
        from urllib.parse import unquote
        decoded_key = unquote(file_key)
        
        print(f"Public video request: {decoded_key}")
        
        # Basic security - only allow user files
        if not decoded_key.startswith("users/"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if file exists
        try:
            head_response = s3_client.head_object(Bucket=STORAGE_BUCKET, Key=decoded_key)
            content_length = head_response.get('ContentLength', 0)
        except s3_client.exceptions.NoSuchKey:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Stream video from S3
        def generate_stream():
            try:
                response = s3_client.get_object(Bucket=STORAGE_BUCKET, Key=decoded_key)
                for chunk in response['Body'].iter_chunks(chunk_size=8192):
                    yield chunk
            except Exception as e:
                print(f"Error streaming: {e}")
                raise
        
        return StreamingResponse(
            generate_stream(),
            media_type="video/mp4",
            headers={
                "Content-Length": str(content_length),
                "Accept-Ranges": "bytes",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                "Cache-Control": "public, max-age=3600"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in public video stream: {e}")
        raise HTTPException(status_code=500, detail="Error streaming video")

@app.get("/files/{file_key:path}/download")
async def download_file(file_key: str):
    """Stream user file from S3 with proper CORS and Content-Type headers"""
    try:
        # Para simplicidade, permitir acesso a arquivos do usuário padrão
        user_id = 'user-sergio-sena'
        
        # Decode URL-encoded characters
        from urllib.parse import unquote
        decoded_key = unquote(file_key)
        
        print(f"Download request - Original: {file_key}")
        print(f"Download request - Decoded: {decoded_key}")
        
        # Ensure user can only access their own files
        if not decoded_key.startswith(f"users/{user_id}/"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if file exists and get metadata
        try:
            head_response = s3_client.head_object(Bucket=STORAGE_BUCKET, Key=decoded_key)
            s3_content_type = head_response.get('ContentType', 'application/octet-stream')
            content_length = head_response.get('ContentLength', 0)
        except s3_client.exceptions.NoSuchKey:
            print(f"File not found: {decoded_key}")
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine correct Content-Type based on file extension
        file_name = decoded_key.split('/')[-1].lower()
        if file_name.endswith(('.mp4', '.m4v')):
            content_type = 'video/mp4'
        elif file_name.endswith('.avi'):
            content_type = 'video/x-msvideo'
        elif file_name.endswith('.mov'):
            content_type = 'video/quicktime'
        elif file_name.endswith('.wmv'):
            content_type = 'video/x-ms-wmv'
        elif file_name.endswith('.webm'):
            content_type = 'video/webm'
        elif file_name.endswith('.mkv'):
            content_type = 'video/x-matroska'
        elif file_name.endswith('.ts'):
            content_type = 'video/mp2t'
        else:
            content_type = s3_content_type
        
        print(f"Content-Type: S3={s3_content_type}, Determined={content_type}")
        
        # Stream file from S3
        from fastapi.responses import StreamingResponse
        
        def generate_stream():
            try:
                response = s3_client.get_object(Bucket=STORAGE_BUCKET, Key=decoded_key)
                for chunk in response['Body'].iter_chunks(chunk_size=8192):
                    yield chunk
            except Exception as e:
                print(f"Error streaming file: {e}")
                raise
        
        # Headers CORS completos para vídeo
        headers = {
            "Content-Length": str(content_length),
            "Accept-Ranges": "bytes",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
            "Access-Control-Allow-Headers": "Range, Content-Range, Content-Type",
            "Access-Control-Expose-Headers": "Content-Range, Content-Length, Accept-Ranges",
            "Cache-Control": "public, max-age=3600"
        }
        
        return StreamingResponse(
            generate_stream(),
            media_type=content_type,
            headers=headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail="Error downloading file")

@app.get("/files/{file_key:path}/download-url")
async def get_download_url(file_key: str, current_user: dict = Depends(verify_token)):
    """Get presigned download URL for file with enhanced credentials"""
    try:
        user_id = current_user.get('user_id', 'user-sergio-sena')
        
        # Ensure user can only access their own files
        if not file_key.startswith(f"users/{user_id}/"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Try to get S3 credentials from Secrets Manager
        try:
            s3_creds_secret = get_secret('drive-online-s3-credentials')
            if s3_creds_secret:
                import json
                creds = json.loads(s3_creds_secret)
                enhanced_s3_client = boto3.client(
                    's3',
                    aws_access_key_id=creds['access_key'],
                    aws_secret_access_key=creds['secret_key'],
                    region_name=creds.get('region', 'us-east-1')
                )
            else:
                enhanced_s3_client = s3_client
        except:
            enhanced_s3_client = s3_client
        
        # Generate presigned URL with short expiration for security
        download_url = enhanced_s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': STORAGE_BUCKET, 'Key': file_key},
            ExpiresIn=300  # 5 minutes
        )
        
        return {'downloadUrl': download_url}
        
    except Exception as e:
        print(f"Error getting download URL: {e}")
        raise HTTPException(status_code=500, detail="Error getting download URL")

@app.post("/files/upload-complete")
async def upload_complete(request: dict, current_user: dict = Depends(verify_token)):
    """Notify that upload is complete and copy video if needed"""
    try:
        file_id = request.get('fileId')
        user_id = current_user.get('user_id', 'user-sergio-sena')
        
        if not file_id or not file_id.startswith(f"users/{user_id}/"):
            raise HTTPException(status_code=400, detail="Invalid file ID")
        
        # If it's a video, auto-copy to public bucket
        if is_video_file(file_id):
            try:
                public_key = copy_to_public_bucket(file_id, user_id)
                public_url = f"https://{PUBLIC_VIDEO_BUCKET}.s3.amazonaws.com/{public_key}"
                
                return {
                    'message': 'Upload complete and video made public',
                    'publicUrl': public_url,
                    'isVideo': True
                }
            except Exception as e:
                print(f"Failed to copy video to public bucket: {e}")
                return {
                    'message': 'Upload complete but failed to make video public',
                    'isVideo': True,
                    'error': str(e)
                }
        else:
            return {
                'message': 'Upload complete',
                'isVideo': False
            }
        
    except Exception as e:
        print(f"Error in upload complete: {e}")
        raise HTTPException(status_code=500, detail="Error processing upload completion")


@app.post("/files/upload-complete")
async def upload_complete_endpoint(request: dict, current_user: dict = Depends(verify_token)):
    """Notify upload completion"""
    try:
        file_id = request.get('fileId')
        user_id = current_user.get('user_id', 'user-sergio-sena')
        
        if not file_id:
            raise HTTPException(status_code=400, detail="File ID required")
        
        if is_video_file(file_id):
            try:
                public_key = copy_to_public_bucket(file_id, user_id)
                return {'message': 'Upload complete', 'isVideo': True, 'publicKey': public_key}
            except Exception as e:
                return {'message': 'Upload complete', 'isVideo': True, 'error': str(e)}
        
        return {'message': 'Upload complete', 'isVideo': False}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/files/upload-url")
async def get_upload_url(request: dict, current_user: dict = Depends(verify_token)):
    """Get presigned URL for file upload with duplicate check"""
    try:
        user_id = current_user.get('user_id', 'user-sergio-sena')
        file_name = request.get('fileName')
        file_size = request.get('fileSize')
        content_type = request.get('contentType')
        
        if not file_name:
            raise HTTPException(status_code=400, detail="File name is required")
        
        # Check for duplicate files
        prefix = f"users/{user_id}/"
        response = s3_client.list_objects_v2(
            Bucket=STORAGE_BUCKET,
            Prefix=prefix
        )
        
        if 'Contents' in response:
            for obj in response['Contents']:
                existing_name = obj['Key'].replace(prefix, '')
                # Remove timestamp prefix from existing files
                if '-' in existing_name:
                    existing_name_clean = '-'.join(existing_name.split('-')[1:])
                else:
                    existing_name_clean = existing_name
                
                if existing_name_clean == file_name:
                    raise HTTPException(status_code=409, detail=f"Arquivo '{file_name}' já existe")
        
        # Generate unique file key
        import time
        timestamp = int(time.time())
        file_key = f"users/{user_id}/{timestamp}-{file_name}"
        
        # Generate presigned URL for upload
        upload_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': STORAGE_BUCKET,
                'Key': file_key,
                'ContentType': content_type
            },
            ExpiresIn=7200  # 2 hours
        )
        
        # Auto-copy videos to public bucket after upload URL generation
        is_video = is_video_file(file_name)
        
        return {
            'uploadUrl': upload_url,
            'fileId': file_key,
            'isVideo': is_video
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating upload URL: {e}")
        raise HTTPException(status_code=500, detail="Error generating upload URL")

@app.get("/auth/temp-credentials")
async def get_temp_credentials(current_user: dict = Depends(verify_token)):
    """Get temporary AWS credentials for direct S3 access"""
    try:
        user_id = current_user.get('user_id', 'user-sergio-sena')
        
        # Política para acesso apenas aos arquivos do usuário
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{STORAGE_BUCKET}/users/{user_id}/*"
                }
            ]
        }
        
        # Gerar credenciais temporárias
        response = sts_client.assume_role(
            RoleArn='arn:aws:iam::969430605054:role/video-streaming-lambda-role',
            RoleSessionName=f'video-session-{user_id}',
            Policy=json.dumps(policy),
            DurationSeconds=3600  # 1 hora
        )
        
        credentials = response['Credentials']
        
        return {
            'AccessKeyId': credentials['AccessKeyId'],
            'SecretAccessKey': credentials['SecretAccessKey'],
            'SessionToken': credentials['SessionToken'],
            'Expiration': credentials['Expiration'].isoformat(),
            'Region': 'us-east-1',
            'Bucket': STORAGE_BUCKET
        }
        
    except Exception as e:
        print(f"Error getting temp credentials: {e}")
        raise HTTPException(status_code=500, detail="Error getting credentials")

@app.post("/files/make-public")
async def make_video_public(request: dict, current_user: dict = Depends(verify_token)):
    """Copy video to public bucket manually"""
    try:
        file_id = request.get('fileId')
        user_id = current_user.get('user_id', 'user-sergio-sena')
        
        if not file_id.startswith(f"users/{user_id}/"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not is_video_file(file_id):
            raise HTTPException(status_code=400, detail="File is not a video")
        
        # Copy to public bucket
        public_key = copy_to_public_bucket(file_id, user_id)
        public_url = f"https://{PUBLIC_VIDEO_BUCKET}.s3.amazonaws.com/{public_key}"
        
        return {'publicUrl': public_url, 'publicKey': public_key}
        
    except Exception as e:
        print(f"Error making video public: {e}")
        raise HTTPException(status_code=500, detail="Error making video public")

@app.post("/files/upload-complete")
async def upload_complete(request: dict, current_user: dict = Depends(verify_token)):
    """Notify that upload is complete and copy video if needed"""
    try:
        file_id = request.get('fileId')
        user_id = current_user.get('user_id', 'user-sergio-sena')
        
        if not file_id or not file_id.startswith(f"users/{user_id}/"):
            raise HTTPException(status_code=400, detail="Invalid file ID")
        
        # If it's a video, auto-copy to public bucket
        if is_video_file(file_id):
            try:
                public_key = copy_to_public_bucket(file_id, user_id)
                public_url = f"https://{PUBLIC_VIDEO_BUCKET}.s3.amazonaws.com/{public_key}"
                
                return {
                    'message': 'Upload complete and video made public',
                    'publicUrl': public_url,
                    'isVideo': True
                }
            except Exception as e:
                print(f"Failed to copy video to public bucket: {e}")
                return {
                    'message': 'Upload complete but failed to make video public',
                    'isVideo': True,
                    'error': str(e)
                }
        else:
            return {
                'message': 'Upload complete',
                'isVideo': False
            }
        
    except Exception as e:
        print(f"Error in upload complete: {e}")
        raise HTTPException(status_code=500, detail="Error processing upload completion")

@app.delete("/files/{file_key:path}")
async def delete_file(file_key: str, current_user: dict = Depends(verify_token)):
    """Delete user file from S3 (private and public if video)"""
    
    # Log inicial SEMPRE
    print(f"\n=== DELETE FUNCTION CALLED ===")
    print(f"Raw file_key: '{file_key}'")
    print(f"Current user: {current_user}")
    
    try:
        user_id = current_user.get('user_id', 'user-sergio-sena')
        print(f"User ID: {user_id}")
        
        # Decode URL encoding
        from urllib.parse import unquote
        decoded_file_key = unquote(file_key)
        print(f"Decoded file_key: '{decoded_file_key}'")
        
        # Verificar se é apenas um teste
        if decoded_file_key == 'test':
            print("Test delete request - returning success")
            return {'message': 'Test delete successful'}
        
        # Se não contém o path completo, buscar o arquivo
        if not decoded_file_key.startswith(f"users/{user_id}/"):
            print(f"Searching for file in S3: {decoded_file_key}")
            
            try:
                # Buscar arquivo na listagem
                response = s3_client.list_objects_v2(
                    Bucket=STORAGE_BUCKET,
                    Prefix=f"users/{user_id}/"
                )
                
                print(f"S3 list response: {response.get('KeyCount', 0)} objects")
                
                full_file_key = None
                if 'Contents' in response:
                    for obj in response['Contents']:
                        obj_filename = obj['Key'].split('/')[-1]
                        print(f"Checking S3 object: {obj['Key']} -> filename: {obj_filename}")
                        if obj_filename == decoded_file_key:
                            full_file_key = obj['Key']
                            print(f"MATCH FOUND: {full_file_key}")
                            break
                
                if not full_file_key:
                    print(f"ERROR: File not found in S3: {decoded_file_key}")
                    raise HTTPException(status_code=404, detail="File not found")
                
                file_key_to_delete = full_file_key
                
            except Exception as e:
                print(f"ERROR searching S3: {e}")
                raise HTTPException(status_code=500, detail=f"Error searching file: {str(e)}")
        else:
            file_key_to_delete = decoded_file_key
        
        print(f"Final file key to delete: {file_key_to_delete}")
        
        # Verificar se arquivo existe antes de deletar
        try:
            print(f"Checking if file exists: {file_key_to_delete}")
            head_response = s3_client.head_object(Bucket=STORAGE_BUCKET, Key=file_key_to_delete)
            print(f"File exists, size: {head_response.get('ContentLength', 0)} bytes")
        except s3_client.exceptions.NoSuchKey:
            print(f"ERROR: File does not exist: {file_key_to_delete}")
            raise HTTPException(status_code=404, detail="File not found in storage")
        except Exception as e:
            print(f"ERROR checking file existence: {e}")
            raise HTTPException(status_code=500, detail=f"Error checking file: {str(e)}")
        
        # Executar delete
        try:
            print(f"Executing delete: {file_key_to_delete}")
            delete_response = s3_client.delete_object(Bucket=STORAGE_BUCKET, Key=file_key_to_delete)
            print(f"Delete response: {delete_response}")
        except Exception as e:
            print(f"ERROR during delete: {e}")
            raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")
        
        # Se for vídeo, deletar também do bucket público
        if is_video_file(file_key_to_delete):
            filename = file_key_to_delete.split('/')[-1]
            public_key = f"videos/{user_id}/{filename}"
            print(f"Video file detected, checking public bucket: {public_key}")
            
            try:
                s3_client.head_object(Bucket=PUBLIC_VIDEO_BUCKET, Key=public_key)
                s3_client.delete_object(Bucket=PUBLIC_VIDEO_BUCKET, Key=public_key)
                print(f"DELETED from public bucket: {public_key}")
            except s3_client.exceptions.NoSuchKey:
                print(f"File not in public bucket (OK): {public_key}")
            except Exception as e:
                print(f"ERROR deleting from public bucket: {e}")
        
        # Verificar se foi realmente deletado
        try:
            print(f"Verifying deletion: {file_key_to_delete}")
            s3_client.head_object(Bucket=STORAGE_BUCKET, Key=file_key_to_delete)
            print(f"ERROR: File still exists after delete attempt!")
            raise HTTPException(status_code=500, detail="File deletion verification failed")
        except s3_client.exceptions.NoSuchKey:
            print(f"SUCCESS: File confirmed deleted from S3")
        except Exception as e:
            print(f"ERROR during verification: {e}")
        
        print(f"=== DELETE COMPLETED SUCCESSFULLY ===")
        return {'message': 'File deleted successfully'}
        
    except HTTPException as he:
        print(f"HTTP Exception: {he.detail}")
        raise
    except Exception as e:
        print(f"UNEXPECTED ERROR in delete_file: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Lambda handler
handler = Mangum(app)