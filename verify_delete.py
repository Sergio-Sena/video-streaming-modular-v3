import requests

# Configurações
API_BASE = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
EMAIL = "senanetworker@gmail.com"
PASSWORD = "sergiosena"

def verify_delete():
    """Verificar se o delete realmente funcionou"""
    
    # 1. Fazer login
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    
    if login_response.status_code != 200:
        print("ERRO: Login falhou")
        return
    
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Listar arquivos após delete
    print("Verificando arquivos após delete...")
    files_response = requests.get(f"{API_BASE}/files", headers=headers)
    
    if files_response.status_code != 200:
        print("ERRO: Falha ao listar arquivos")
        return
    
    files = files_response.json().get("files", [])
    print(f"Arquivos restantes: {len(files)}")
    
    for file in files:
        print(f"  - {file['name']} (ID: {file['id']})")
    
    # Verificar se o arquivo "1756853751-Video automacao.mp4" ainda existe
    deleted_file_exists = any("1756853751-Video automacao.mp4" in file['name'] for file in files)
    
    if deleted_file_exists:
        print("❌ PROBLEMA: Arquivo ainda existe após delete!")
    else:
        print("✅ SUCESSO: Arquivo foi deletado corretamente!")

if __name__ == "__main__":
    verify_delete()