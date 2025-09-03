#!/usr/bin/env python3
"""
Teste direto de login para verificar qual versão está rodando
"""
import requests
import hashlib

def test_login_versions():
    base_url = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
    
    # Testa health primeiro
    print("Testando health endpoint...")
    response = requests.get(f"{base_url}/health")
    print(f"Health: {response.status_code} - {response.text}")
    
    # Testa diferentes versões de hash
    password = "sergiosena"
    
    # SHA256 (ultra_simple_main.py)
    sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    print(f"SHA256 hash: {sha256_hash}")
    
    # Testa login
    login_data = {
        "email": "senanetworker@gmail.com", 
        "password": password
    }
    
    print("\nTestando login...")
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    print(f"Login: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("token")
        print(f"Token obtido: {token[:50]}...")
        
        # Testa endpoint protegido
        headers = {"Authorization": f"Bearer {token}"}
        files_response = requests.get(f"{base_url}/files", headers=headers)
        print(f"Files endpoint: {files_response.status_code}")
        if files_response.status_code == 200:
            files = files_response.json().get("files", [])
            print(f"Arquivos encontrados: {len(files)}")
        else:
            print(f"Erro files: {files_response.text}")

if __name__ == "__main__":
    test_login_versions()