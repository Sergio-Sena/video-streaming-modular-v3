import requests
import json

# Configurações
API_BASE = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
EMAIL = "senanetworker@gmail.com"  # Email correto
PASSWORD = "sergiosena"  # Senha correta

def debug_delete():
    """Debug da função de delete"""
    
    print("=== DEBUG DELETE FUNCTION ===")
    
    # 1. Fazer login
    print("\n1. Fazendo login...")
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    
    print(f"Login Status: {login_response.status_code}")
    print(f"Login Response: {login_response.text}")
    
    if login_response.status_code != 200:
        print("ERRO: Login falhou")
        return
    
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Token obtido: {token[:50]}...")
    
    # 2. Listar arquivos
    print("\n2. Listando arquivos...")
    files_response = requests.get(f"{API_BASE}/files", headers=headers)
    
    print(f"Files Status: {files_response.status_code}")
    print(f"Files Response: {files_response.text[:500]}...")
    
    if files_response.status_code != 200:
        print("ERRO: Falha ao listar arquivos")
        return
    
    files = files_response.json().get("files", [])
    print(f"Arquivos encontrados: {len(files)}")
    
    if not files:
        print("INFO: Nenhum arquivo para testar delete")
        return
    
    # 3. Mostrar primeiro arquivo
    test_file = files[0]
    print(f"\n3. Arquivo de teste:")
    print(f"   ID completo: {test_file['id']}")
    print(f"   Nome: {test_file['name']}")
    print(f"   Tamanho: {test_file['size']}")
    
    # 4. Extrair nome do arquivo (como o frontend faz)
    file_id = test_file["id"]
    file_name_only = file_id.split('/')[-1] if '/' in file_id else file_id
    print(f"   Nome extraído: {file_name_only}")
    
    # 5. Testar delete
    print(f"\n4. Testando DELETE...")
    delete_url = f"{API_BASE}/files/{file_name_only}"
    print(f"   URL: {delete_url}")
    print(f"   Headers: {headers}")
    
    delete_response = requests.delete(delete_url, headers=headers)
    
    print(f"\n5. Resultado DELETE:")
    print(f"   Status: {delete_response.status_code}")
    print(f"   Headers: {dict(delete_response.headers)}")
    print(f"   Response: {delete_response.text}")
    
    # 6. Se falhou, testar com ID completo
    if delete_response.status_code != 200:
        print(f"\n6. Tentando com ID completo...")
        delete_url_full = f"{API_BASE}/files/{file_id}"
        print(f"   URL completa: {delete_url_full}")
        
        delete_response_full = requests.delete(delete_url_full, headers=headers)
        print(f"   Status: {delete_response_full.status_code}")
        print(f"   Response: {delete_response_full.text}")

if __name__ == "__main__":
    debug_delete()