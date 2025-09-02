import os
from typing import Optional

class Settings:
    # JWT Configuration
    JWT_SECRET_NAME: str = "drive-online-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # AWS Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    DYNAMODB_TABLE_USERS: str = os.getenv("DYNAMODB_TABLE_USERS", "drive-online-users")
    DYNAMODB_TABLE_TOKENS: str = os.getenv("DYNAMODB_TABLE_TOKENS", "drive-online-tokens")
    
    # SNS Configuration
    SNS_TOPIC_ARN: Optional[str] = os.getenv("SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:969430605054:drive-online-password-reset")
    
    # Frontend URL Configuration
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://videos.sstechnologies-cloud.com")
    
    # CORS Configuration
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "https://drive-online.com",
        "https://*.drive-online.com",
        "https://*.cloudfront.net"
    ]
    
    # User Configuration (no hardcoded passwords)
    USER_EMAIL: str = "senanetworker@gmail.com"
    USER_NAME: str = "Sergio Sena"
    USER_ID: str = "user-sergio-sena"
    
    # Secrets Manager Keys
    SECRET_USER_PASSWORD: str = "drive-online-user-password"
    SECRET_RESET_TOKENS: str = "drive-online-reset-tokens"
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    # Rate Limiting
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_ATTEMPT_WINDOW_MINUTES: int = 15

settings = Settings()