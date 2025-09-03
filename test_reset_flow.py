#!/usr/bin/env python3
"""
Script para testar o fluxo de reset de senha
"""
import requests
import json
import sys
import os

# Configurações
API_BASE_URL = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
TEST_EMAIL = "senanetworker@gmail.com"

def test_forgot_password():
    """Testa o endpoint de esqueci a senha"""
    print("Testando fluxo de reset de senha...")
    print(f"Email de teste: {TEST_EMAIL}")
    print(f"API Base URL: {API_BASE_URL}")
    print("-" * 50)
    
    # Endpoint de forgot password
    url = f"{API_BASE_URL}/auth/forgot-password"
    payload = {"email": TEST_EMAIL}
    
    try:
        print(f"📤 Enviando requisição para: {url}")
        print(f"📋 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ Sucesso! Response: {json.dumps(response_data, indent=2)}")
            print("\n🔗 O link de reset deve ter sido enviado via SNS para:")
            print(f"   📧 Topic ARN: arn:aws:sns:us-east-1:969430605054:video-streaming-password-reset")
            print(f"   🌐 Link gerado: https://videos.sstechnologies-cloud.com/reset-password?token=<TOKEN>")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_validate_token():
    """Testa validação de token (com token de exemplo)"""
    print("\n🔄 Testando validação de token...")
    
    # Token de exemplo para teste
    test_token = "valid-token"
    url = f"{API_BASE_URL}/auth/validate-reset-token"
    
    try:
        print(f"📤 Testando validação com token: {test_token}")
        response = requests.get(f"{url}?token={test_token}", timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Token válido!")
            return True
        else:
            print(f"❌ Token inválido: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def check_frontend_url():
    """Verifica se a URL do frontend está acessível"""
    print("\n🔄 Verificando URL do frontend...")
    
    frontend_url = "https://videos.sstechnologies-cloud.com"
    reset_page_url = f"{frontend_url}/reset-password"
    
    try:
        print(f"🌐 Testando acesso a: {reset_page_url}")
        response = requests.get(reset_page_url, timeout=10, allow_redirects=True)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Página de reset acessível!")
            print(f"🔗 URL final: {response.url}")
            return True
        else:
            print(f"⚠️  Status: {response.status_code}")
            print(f"🔗 URL final: {response.url}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao acessar frontend: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("TESTE DO FLUXO DE RESET DE SENHA")
    print("=" * 50)
    
    # Teste 1: Forgot Password
    success1 = test_forgot_password()
    
    # Teste 2: Validate Token
    success2 = test_validate_token()
    
    # Teste 3: Frontend URL
    success3 = check_frontend_url()
    
    # Resumo
    print("\n" + "=" * 50)
    print("📋 RESUMO DOS TESTES:")
    print(f"   📧 Forgot Password: {'✅ OK' if success1 else '❌ FALHOU'}")
    print(f"   🔑 Validate Token: {'✅ OK' if success2 else '❌ FALHOU'}")
    print(f"   🌐 Frontend URL: {'✅ OK' if success3 else '❌ FALHOU'}")
    
    if success1:
        print("\n🎯 DIRECIONAMENTO CONFIGURADO:")
        print("   📧 Emails são enviados via SNS")
        print("   🔗 Links direcionam para: https://videos.sstechnologies-cloud.com/reset-password")
        print("   📱 Usuários receberão o link no email cadastrado no SNS Topic")

if __name__ == "__main__":
    main()