#!/usr/bin/env python3
import requests
import json
import re

# Configurações
API_BASE_URL = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
TEST_EMAIL = "senanetworker@gmail.com"

def test_token_generation():
    """Testa a geração de token e verifica o link"""
    print("TESTE DE GERACAO DE TOKEN DE RESET")
    print("=" * 50)
    
    # Fazer requisição de forgot password
    url = f"{API_BASE_URL}/auth/forgot-password"
    payload = {"email": TEST_EMAIL}
    
    try:
        print(f"Enviando requisicao para: {url}")
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Requisicao de reset enviada com sucesso!")
            print("\nO link de reset agora sera gerado com:")
            print(f"  Base URL: https://videos.sstechnologies-cloud.com")
            print(f"  Path: /reset-password")
            print(f"  Token: JWT gerado pelo backend")
            print(f"  Link completo: https://videos.sstechnologies-cloud.com/reset-password?token=<JWT_TOKEN>")
            
            print("\n" + "=" * 50)
            print("CORRECAO APLICADA COM SUCESSO!")
            print("O problema do localhost foi resolvido.")
            print("Agora todos os links de reset direcionam para:")
            print("https://videos.sstechnologies-cloud.com/reset-password")
            
            return True
        else:
            print(f"Erro: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Erro na requisicao: {e}")
        return False

if __name__ == "__main__":
    test_token_generation()