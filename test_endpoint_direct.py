#!/usr/bin/env python3
"""
Teste direto do endpoint de vídeo
"""

import requests
import urllib.parse

# Configurações
API_BASE = 'https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod'
TEST_VIDEO = 'users/user-sergio-sena/1756853751-Video automacao.mp4'

def test_different_encodings():
    """Testar diferentes formas de encoding da URL"""
    print("=== TESTANDO DIFERENTES ENCODINGS ===")
    
    # Diferentes formas de encoding
    encodings = [
        ('Original', TEST_VIDEO),
        ('URL Encoded', urllib.parse.quote(TEST_VIDEO, safe='')),
        ('Partial Encoded', urllib.parse.quote(TEST_VIDEO, safe='/')),
        ('Double Encoded', urllib.parse.quote(urllib.parse.quote(TEST_VIDEO, safe=''), safe='')),
    ]
    
    for name, encoded_path in encodings:
        print(f"\n--- {name} ---")
        url = f"{API_BASE}/files/{encoded_path}/download"
        print(f"URL: {url}")
        
        try:
            # Teste HEAD
            response = requests.head(url, timeout=10)
            print(f"HEAD: {response.status_code}")
            
            if response.status_code == 200:
                print("SUCCESS! Headers:")
                for key, value in response.headers.items():
                    if any(x in key.lower() for x in ['content-type', 'access-control', 'accept-ranges']):
                        print(f"  {key}: {value}")
                return url
                
        except Exception as e:
            print(f"Erro: {e}")
    
    return None

def test_manual_paths():
    """Testar paths manuais"""
    print("\n=== TESTANDO PATHS MANUAIS ===")
    
    # Paths para testar
    test_paths = [
        'users%2Fuser-sergio-sena%2F1756853751-Video%20automacao.mp4',
        'users/user-sergio-sena/1756853751-Video%20automacao.mp4',
        'users%2Fuser-sergio-sena%2F1756853751-Video+automacao.mp4',
    ]
    
    for path in test_paths:
        print(f"\n--- Testando: {path} ---")
        url = f"{API_BASE}/files/{path}/download"
        
        try:
            response = requests.head(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("SUCCESS!")
                return url
                
        except Exception as e:
            print(f"Erro: {e}")
    
    return None

def test_other_endpoints():
    """Testar outros endpoints para verificar se Lambda está funcionando"""
    print("\n=== TESTANDO OUTROS ENDPOINTS ===")
    
    endpoints = [
        ('Health', '/health'),
        ('Root', '/'),
        ('Files List', '/files'),  # Este vai dar 401 sem token, mas deve responder
    ]
    
    for name, endpoint in endpoints:
        print(f"\n--- {name}: {endpoint} ---")
        url = f"{API_BASE}{endpoint}"
        
        try:
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code in [200, 401]:  # 401 é esperado para /files
                print("Endpoint funcionando")
            else:
                print("Endpoint com problema")
                
        except Exception as e:
            print(f"Erro: {e}")

def main():
    """Executar todos os testes"""
    print("TESTE DIRETO DO ENDPOINT DE VIDEO")
    print("=" * 50)
    
    # Testar outros endpoints primeiro
    test_other_endpoints()
    
    # Testar diferentes encodings
    working_url = test_different_encodings()
    
    if not working_url:
        working_url = test_manual_paths()
    
    if working_url:
        print(f"\n🎉 URL FUNCIONANDO ENCONTRADA:")
        print(f"{working_url}")
        
        # Teste final com GET para ver se o vídeo carrega
        print(f"\n--- TESTE FINAL COM GET ---")
        try:
            response = requests.get(working_url, timeout=30, stream=True)
            print(f"GET Status: {response.status_code}")
            
            if response.status_code == 200:
                # Ler primeiros bytes para confirmar
                chunk = next(response.iter_content(chunk_size=1024), None)
                if chunk:
                    print(f"Dados recebidos: {len(chunk)} bytes")
                    print("✅ VIDEO CARREGANDO CORRETAMENTE!")
                else:
                    print("❌ Nenhum dado recebido")
            
        except Exception as e:
            print(f"Erro no GET: {e}")
    else:
        print("\n❌ NENHUMA URL FUNCIONANDO ENCONTRADA")
        print("O endpoint de download precisa ser corrigido no Lambda")

if __name__ == "__main__":
    main()