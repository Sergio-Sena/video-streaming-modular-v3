import requests

# Teste simples do delete
API_BASE = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"

# 1. Login
print("Testando login...")
login_response = requests.post(f"{API_BASE}/auth/login", json={
    "email": "user@example.com",
    "password": "defaultpassword"
})

print(f"Login status: {login_response.status_code}")
if login_response.status_code == 200:
    token = login_response.json()["token"]
    print("Login OK")
    
    # 2. Listar arquivos
    print("\nListando arquivos...")
    headers = {"Authorization": f"Bearer {token}"}
    files_response = requests.get(f"{API_BASE}/files", headers=headers)
    
    print(f"Files status: {files_response.status_code}")
    if files_response.status_code == 200:
        files = files_response.json().get("files", [])
        print(f"Arquivos encontrados: {len(files)}")
        
        if files:
            # Mostrar primeiro arquivo
            file = files[0]
            print(f"Primeiro arquivo: {file['name']}")
            print(f"ID completo: {file['id']}")
            
            # Extrair nome do arquivo
            file_name = file['id'].split('/')[-1]
            print(f"Nome extraido: {file_name}")
            
            # 3. Testar delete
            print(f"\nTestando delete de: {file_name}")
            delete_response = requests.delete(f"{API_BASE}/files/{file_name}", headers=headers)
            
            print(f"Delete status: {delete_response.status_code}")
            print(f"Delete response: {delete_response.text}")
            
            if delete_response.status_code == 200:
                print("DELETE FUNCIONOU!")
            else:
                print("DELETE FALHOU!")
        else:
            print("Nenhum arquivo para testar")
    else:
        print(f"Erro ao listar: {files_response.text}")
else:
    print(f"Erro no login: {login_response.text}")