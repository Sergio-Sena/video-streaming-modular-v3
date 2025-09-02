#!/usr/bin/env python3
"""
Local testing script for auth service
"""
import sys
import os
sys.path.append('src')

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health():
    """Test health endpoint"""
    response = client.get("/health")
    print(f"Health check: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_login():
    """Test login endpoint"""
    login_data = {
        "email": "senanetworker@gmail.com",
        "password": "sergiosena"
    }
    
    response = client.post("/auth/login", json=login_data)
    print(f"Login test: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("token")
        print(f"Token received: {token[:50]}...")
        return token
    
    return None

def test_protected_route(token):
    """Test protected route"""
    if not token:
        print("No token available for protected route test")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    print(f"Protected route test: {response.status_code}")
    print(f"Response: {response.json()}")

def test_invalid_login():
    """Test invalid login"""
    login_data = {
        "email": "invalid@email.com",
        "password": "wrongpassword"
    }
    
    response = client.post("/auth/login", json=login_data)
    print(f"Invalid login test: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 401

def main():
    """Run all tests"""
    print("=== Testing Auth Service Locally ===\n")
    
    print("1. Testing health endpoint...")
    test_health()
    print()
    
    print("2. Testing valid login...")
    token = test_login()
    print()
    
    print("3. Testing protected route...")
    test_protected_route(token)
    print()
    
    print("4. Testing invalid login...")
    test_invalid_login()
    print()
    
    print("=== All tests completed ===")

if __name__ == "__main__":
    main()