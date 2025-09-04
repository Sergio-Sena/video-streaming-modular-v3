import requests
import time

API_BASE = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
EMAIL = "senanetworker@gmail.com"
PASSWORD = "sergiosena"

# Login
login_response = requests.post(f"{API_BASE}/auth/login", json={
    "email": EMAIL,
    "password": PASSWORD
})

token = login_response.json()["token"]
headers = {"Authorization": f"Bearer {token}"}

# Listar arquivos
files_response = requests.get(f"{API_BASE}/files", headers=headers)
files = files_response.json().get("files", [])

if files:
    target_file = files[0]
    file_name = target_file['name']
    
    print(f"Testando delete do arquivo: {file_name}")
    
    # Adicionar timestamp para evitar cache
    timestamp = int(time.time())
    delete_url = f"{API_BASE}/files/{file_name}?t={timestamp}"
    
    delete_response = requests.delete(delete_url, headers=headers)
    print(f"Status: {delete_response.status_code}")
    print(f"Response: {delete_response.text}")
else:
    print("Nenhum arquivo para testar")