import boto3
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import settings

class AuthService:
    def __init__(self):
        self.secrets_client = boto3.client('secretsmanager', region_name=settings.AWS_REGION)
        self.dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        self.users_table = self.dynamodb.Table(settings.DYNAMODB_TABLE_USERS)
        self._jwt_secret = None
    
    def get_jwt_secret(self) -> str:
        """Get JWT secret from AWS Secrets Manager with caching"""
        if self._jwt_secret:
            return self._jwt_secret
            
        try:
            response = self.secrets_client.get_secret_value(SecretId=settings.JWT_SECRET_NAME)
            self._jwt_secret = response['SecretString']
            return self._jwt_secret
        except Exception as e:
            if settings.DEVELOPMENT_MODE:
                self._jwt_secret = "dev-secret-key-drive-online-2025"
                return self._jwt_secret
            raise e
    
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        return bcrypt.hashpw(
            password.encode('utf-8'), 
            bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
        ).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_access_token(self, data: Dict[str, Any], token_type: str = "access") -> str:
        """Create JWT token"""
        to_encode = data.copy()
        
        if token_type == "access":
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        else:  # refresh
            expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": token_type
        })
        
        secret = self.get_jwt_secret()
        return jwt.encode(to_encode, secret, algorithm=settings.JWT_ALGORITHM)
    
    def verify_token(self, token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            secret = self.get_jwt_secret()
            payload = jwt.decode(token, secret, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.JWTError:
            raise ValueError("Invalid token")
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user from DynamoDB"""
        try:
            response = self.users_table.get_item(Key={'email': email})
            return response.get('Item')
        except Exception as e:
            # Development fallback
            if settings.DEVELOPMENT_MODE and email == settings.DEV_USER_EMAIL:
                return {
                    'id': 'dev-user-1',
                    'email': settings.DEV_USER_EMAIL,
                    'name': settings.DEV_USER_NAME,
                    'password_hash': self.hash_password(settings.DEV_USER_PASSWORD),
                    'created_at': '2025-01-01T00:00:00Z',
                    'is_active': True
                }
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        user = self.get_user_by_email(email)
        if not user or not user.get('is_active', True):
            return None
        
        if not self.verify_password(password, user['password_hash']):
            return None
        
        return user
    
    def create_user_tokens(self, user: Dict[str, Any]) -> Dict[str, str]:
        """Create access and refresh tokens for user"""
        token_data = {
            "sub": user['email'],
            "user_id": user['id'],
            "name": user['name']
        }
        
        access_token = self.create_access_token(token_data, "access")
        refresh_token = self.create_access_token(token_data, "refresh")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

# Singleton instance
auth_service = AuthService()