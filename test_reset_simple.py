#!/usr/bin/env python3
import requests
import json

# Configurações
API_BASE_URL = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
TEST_EMAIL = "senanetworker@gmail.com"

def test_forgot_password():
    print("Testando fluxo de reset de senha...")
    print(f"Email de teste: {TEST_EMAIL}")
    print(f"API Base URL: {API_BASE_URL}")
    print("-" * 50)
    
    url = f"{API_BASE_URL}/auth/forgot-password"
    payload = {"email": TEST_EMAIL}
    
    try:
        print(f"Enviando requisicao para: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Sucesso! Response: {json.dumps(response_data, indent=2)}")
            print("\nO link de reset deve ter sido enviado via SNS para:")
            print(f"Topic ARN: arn:aws:sns:us-east-1:969430605054:video-streaming-password-reset")
            print(f"Link gerado: https://videos.sstechnologies-cloud.com/reset-password?token=<TOKEN>")
            return True
        else:
            print(f"Erro: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Erro na requisicao: {e}")
        return False

def check_frontend_url():
    print("\nVerificando URL do frontend...")
    
    frontend_url = "https://videos.sstechnologies-cloud.com"
    reset_page_url = f"{frontend_url}/reset-password"
    
    try:
        print(f"Testando acesso a: {reset_page_url}")
        response = requests.get(reset_page_url, timeout=10, allow_redirects=True)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Pagina de reset acessivel!")
            print(f"URL final: {response.url}")
            return True
        else:
            print(f"Status: {response.status_code}")
            print(f"URL final: {response.url}")
            return False
            
    except Exception as e:
        print(f"Erro ao acessar frontend: {e}")
        return False

if __name__ == "__main__":
    print("TESTE DO FLUXO DE RESET DE SENHA")
    print("=" * 50)
    
    success1 = test_forgot_password()
    success2 = check_frontend_url()
    
    print("\n" + "=" * 50)
    print("RESUMO DOS TESTES:")
    print(f"Forgot Password: {'OK' if success1 else 'FALHOU'}")
    print(f"Frontend URL: {'OK' if success2 else 'FALHOU'}")
    
    if success1:
        print("\nDIRECIONAMENTO CONFIGURADO:")
        print("Emails sao enviados via SNS")
        print("Links direcionam para: https://videos.sstechnologies-cloud.com/reset-password")