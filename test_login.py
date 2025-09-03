#!/usr/bin/env python3
import requests
import json

# Configurações
FRONTEND_URL = "https://videos.sstechnologies-cloud.com"
API_URL = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
EMAIL = "senanetworker@gmail.com"
PASSWORD = "sergiosena"

def test_frontend_access():
    """Testa acesso ao frontend"""
    print("🌐 Testando acesso ao frontend...")
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Frontend acessível")
            return True
        else:
            print("❌ Frontend com problema")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_api_login():
    """Testa login na API"""
    print("\n🔐 Testando login na API...")
    try:
        payload = {
            "email": EMAIL,
            "password": PASSWORD
        }
        
        response = requests.post(f"{API_URL}/auth/login", json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login realizado com sucesso!")
            print(f"Token: {data.get('token', 'N/A')[:50]}...")
            print(f"User: {data.get('user', {}).get('name', 'N/A')}")
            return True
        else:
            print(f"❌ Erro no login: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print("🧪 TESTE DE LOGIN - DRIVE ONLINE")
    print("=" * 40)
    
    frontend_ok = test_frontend_access()
    api_ok = test_api_login()
    
    print("\n" + "=" * 40)
    print("📋 RESULTADO:")
    print(f"Frontend: {'✅ OK' if frontend_ok else '❌ FALHOU'}")
    print(f"API Login: {'✅ OK' if api_ok else '❌ FALHOU'}")
    
    if frontend_ok and api_ok:
        print("\n🎉 Sistema funcionando! Acesse:")
        print(f"🔗 {FRONTEND_URL}")
    else:
        print("\n⚠️ Problemas detectados no sistema")

if __name__ == "__main__":
    main()