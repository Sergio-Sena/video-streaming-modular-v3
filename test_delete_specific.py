import requests
import json

# Configurações
API_BASE = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
EMAIL = "senanetworker@gmail.com"
PASSWORD = "sergiosena"

def test_delete_specific():
    """Testar delete específico com logs detalhados"""
    
    # 1. Login
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Listar arquivos ANTES do delete
    print("=== ANTES DO DELETE ===")
    files_response = requests.get(f"{API_BASE}/files", headers=headers)
    files_before = files_response.json().get("files", [])
    print(f"Arquivos antes: {len(files_before)}")
    
    target_file = None
    for file in files_before:
        if "Video automacao.mp4" in file['name'] and file['name'].startswith('1756853751'):
            target_file = file
            break
    
    if not target_file:
        print("Arquivo alvo nao encontrado!")
        return
    
    print(f"Arquivo alvo: {target_file['name']}")
    print(f"ID completo: {target_file['id']}")
    
    # 3. Fazer DELETE
    file_name = target_file['name']
    print(f"\\n=== FAZENDO DELETE ===")
    print(f"Deletando: {file_name}")
    
    delete_response = requests.delete(f"{API_BASE}/files/{file_name}", headers=headers)
    print(f"Status: {delete_response.status_code}")
    print(f"Response: {delete_response.text}")
    
    # 4. Aguardar um pouco
    import time
    print("\\nAguardando 3 segundos...")
    time.sleep(3)
    
    # 5. Listar arquivos DEPOIS do delete
    print("\\n=== DEPOIS DO DELETE ===")
    files_response_after = requests.get(f"{API_BASE}/files", headers=headers)
    files_after = files_response_after.json().get("files", [])
    print(f"Arquivos depois: {len(files_after)}")
    
    # Verificar se o arquivo ainda existe
    still_exists = False
    for file in files_after:
        if file['id'] == target_file['id']:
            still_exists = True
            print(f"PROBLEMA: Arquivo ainda existe: {file['name']}")
            break
    
    if not still_exists:
        print("SUCESSO: Arquivo foi removido!")
    
    # 6. Comparar listas
    print(f"\\n=== COMPARACAO ===")
    print(f"Antes: {len(files_before)} arquivos")
    print(f"Depois: {len(files_after)} arquivos")
    print(f"Diferenca: {len(files_before) - len(files_after)} arquivos removidos")

if __name__ == "__main__":
    test_delete_specific()