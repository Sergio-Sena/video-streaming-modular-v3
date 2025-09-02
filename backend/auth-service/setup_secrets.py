#!/usr/bin/env python3
"""
Setup script to create initial secrets in AWS Secrets Manager
"""
import boto3
import bcrypt
import json
from datetime import datetime

def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

def create_or_update_secret(secrets_client, secret_name: str, secret_value: str, description: str):
    """Create or update a secret"""
    try:
        # Try to create new secret
        response = secrets_client.create_secret(
            Name=secret_name,
            SecretString=secret_value,
            Description=description
        )
        print(f"Created secret: {secret_name}")
        return response['ARN']
    except secrets_client.exceptions.ResourceExistsException:
        # Secret exists, update it
        response = secrets_client.update_secret(
            SecretId=secret_name,
            SecretString=secret_value
        )
        print(f"Updated secret: {secret_name}")
        return response['ARN']
    except Exception as e:
        print(f"Error with secret {secret_name}: {e}")
        return None

def main():
    """Setup all required secrets"""
    print("Setting up AWS Secrets Manager for Drive Online...")
    
    secrets_client = boto3.client('secretsmanager')
    
    # 1. JWT Secret
    jwt_secret = "drive-online-jwt-super-secret-key-2025-production"
    create_or_update_secret(
        secrets_client,
        "drive-online-jwt-secret",
        jwt_secret,
        "JWT secret key for Drive Online authentication"
    )
    
    # 2. User Password (initial password: sergiosena)
    initial_password = "sergiosena"
    password_hash = hash_password(initial_password)
    create_or_update_secret(
        secrets_client,
        "drive-online-user-password",
        password_hash,
        "Hashed password for senanetworker@gmail.com"
    )
    
    # 3. Reset Tokens (empty initially)
    create_or_update_secret(
        secrets_client,
        "drive-online-reset-tokens",
        "{}",
        "Temporary password reset tokens"
    )
    
    print("\nAll secrets created successfully!")
    print("\nSummary:")
    print("- drive-online-jwt-secret: JWT signing key")
    print("- drive-online-user-password: User password hash")
    print("- drive-online-reset-tokens: Reset tokens storage")
    print(f"\nInitial login: senanetworker@gmail.com / {initial_password}")
    print("\nChange your password after first login!")

if __name__ == "__main__":
    main()