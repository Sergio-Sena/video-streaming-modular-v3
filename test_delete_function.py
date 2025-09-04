import requests
import json

# Configurações
API_BASE = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
EMAIL = "user@example.com"
PASSWORD = "defaultpassword"

def test_delete_function():
    """Testar função de delete"""
    
    # 1. Fazer login
    print("1. Fazendo login...")
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    
    if login_response.status_code != 200:
        print(f"ERRO Login falhou: {login_response.status_code}")
        return
    
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("OK Login realizado com sucesso")
    
    # 2. Listar arquivos
    print("\n2. Listando arquivos...")
    files_response = requests.get(f"{API_BASE}/files", headers=headers)
    
    if files_response.status_code != 200:
        print(f"ERRO ao listar arquivos: {files_response.status_code}")
        return
    
    files = files_response.json().get("files", [])
    print(f"OK Encontrados {len(files)} arquivos")
    
    if not files:
        print("INFO Nenhum arquivo para testar delete")
        return
    
    # 3. Mostrar arquivos disponíveis
    print("\n3. Arquivos disponíveis:")
    for i, file in enumerate(files):
        print(f"   {i+1}. {file['name']} (ID: {file['id']})")
    
    # 4. Testar delete no primeiro arquivo
    test_file = files[0]
    file_id = test_file["id"]
    file_name = test_file["name"]
    
    print(f"\n4. Testando delete do arquivo: {file_name}")
    print(f"   File ID completo: {file_id}")
    
    # Extrair apenas o nome do arquivo (como o frontend faz)
    file_name_only = file_id.split('/')[-1] if '/' in file_id else file_id
    print(f"   Nome extraído: {file_name_only}")
    
    # 5. Fazer delete
    delete_response = requests.delete(f"{API_BASE}/files/{file_name_only}", headers=headers)
    
    print(f"\n5. Resultado do delete:")
    print(f"   Status: {delete_response.status_code}")
    print(f"   Response: {delete_response.text}")
    
    if delete_response.status_code == 200:
        print("OK Delete funcionou!")
        
        # 6. Verificar se arquivo foi removido
        print("\n6. Verificando se arquivo foi removido...")
        files_after = requests.get(f"{API_BASE}/files", headers=headers).json().get("files", [])
        
        file_still_exists = any(f["id"] == file_id for f in files_after)
        
        if file_still_exists:
            print("ERRO Arquivo ainda existe na listagem")
        else:
            print("OK Arquivo removido da listagem")
            
    else:
        print(f"ERRO Delete falhou: {delete_response.status_code}")
        print(f"   Erro: {delete_response.text}")

if __name__ == "__main__":
    test_delete_function()