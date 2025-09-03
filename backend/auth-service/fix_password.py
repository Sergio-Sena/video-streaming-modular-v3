#!/usr/bin/env python3
"""
Fix password hash for development
"""
import bcrypt

def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def main():
    password = "sergiosena"
    hashed = hash_password(password)
    print(f"Password: {password}")
    print(f"Hash: {hashed}")
    
    # Test verification
    is_valid = bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    print(f"Verification: {is_valid}")

if __name__ == "__main__":
    main()