#!/usr/bin/env python3
import requests
import json

# Credenciais da documentação
FRONTEND_URL = "https://videos.sstechnologies-cloud.com"
API_URL = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
EMAIL = "senanetworker@gmail.com"
PASSWORD = "sergiosena"

def test_login_manual():
    """Teste manual do login"""
    print("TESTE MANUAL DE LOGIN")
    print("=" * 30)
    
    print(f"Frontend: {FRONTEND_URL}")
    print(f"API: {API_URL}")
    print(f"Email: {EMAIL}")
    print(f"Password: {PASSWORD}")
    
    # Teste 1: Health check da API
    print("\n1. Testando health da API...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   OK - API respondendo")
        else:
            print("   ERRO - API com problema")
    except Exception as e:
        print(f"   ERRO: {e}")
    
    # Teste 2: Login
    print("\n2. Testando login...")
    try:
        payload = {"email": EMAIL, "password": PASSWORD}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(f"{API_URL}/auth/login", 
                               json=payload, 
                               headers=headers, 
                               timeout=30)
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            print("   SUCESSO!")
            print(f"   Token: {data.get('token', 'N/A')[:30]}...")
            print(f"   User: {data.get('user', {})}")
        else:
            print("   FALHOU!")
            
    except Exception as e:
        print(f"   ERRO: {e}")
    
    # Teste 3: Frontend
    print("\n3. Testando frontend...")
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   OK - Frontend carregando")
        else:
            print("   ERRO - Frontend com problema")
    except Exception as e:
        print(f"   ERRO: {e}")
    
    print("\n" + "=" * 30)
    print("INSTRUCOES PARA TESTE MANUAL:")
    print(f"1. Acesse: {FRONTEND_URL}")
    print(f"2. Use email: {EMAIL}")
    print(f"3. Use senha: {PASSWORD}")
    print("4. Verifique se o player aparece na aba Videos")

if __name__ == "__main__":
    test_login_manual()