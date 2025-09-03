#!/usr/bin/env python3
"""
Teste dos endpoints disponíveis
"""
import requests

def test_endpoints():
    base_url = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
    
    # Login
    response = requests.post(f"{base_url}/auth/login", json={
        "email": "senanetworker@gmail.com",
        "password": "sergiosena"
    })
    
    if response.status_code != 200:
        print("Login falhou")
        return
    
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Testar endpoints
    endpoints = [
        ("GET", "/files"),
        ("GET", "/user/storage"),
        ("POST", "/files/upload-url"),
        ("POST", "/files/upload")
    ]
    
    for method, endpoint in endpoints:
        try:
            if method == "GET":
                resp = requests.get(f"{base_url}{endpoint}", headers=headers)
            else:
                resp = requests.post(f"{base_url}{endpoint}", headers=headers, json={})
            
            print(f"{method} {endpoint}: {resp.status_code}")
            if resp.status_code == 404:
                print(f"  Endpoint nao existe")
            elif resp.status_code == 400:
                print(f"  Endpoint existe mas parametros invalidos")
            elif resp.status_code == 200:
                print(f"  Endpoint funcionando")
                
        except Exception as e:
            print(f"{method} {endpoint}: ERRO - {e}")

if __name__ == "__main__":
    test_endpoints()