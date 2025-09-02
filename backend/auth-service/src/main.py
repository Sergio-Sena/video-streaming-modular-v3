from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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

# Lambda handler
handler = Mangum(app)