import requests
import os
import json

# Configurações
API_URL = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
EMAIL = "senanetworker@gmail.com"
PASSWORD = "sergiosena"

def login():
    """Fazer login e obter token"""
    response = requests.post(f"{API_URL}/auth/login", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        return data["token"]
    else:
        raise Exception(f"Login falhou: {response.status_code}")

def get_upload_url(token, file_name, file_size, content_type):
    """Obter URL de upload"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{API_URL}/files/upload-url", 
        json={
            "fileName": file_name,
            "fileSize": file_size,
            "contentType": content_type
        },
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao obter URL: {response.status_code} - {response.text}")

def upload_file(upload_url, file_path, content_type):
    """Fazer upload do arquivo"""
    with open(file_path, 'rb') as f:
        response = requests.put(upload_url, 
            data=f,
            headers={"Content-Type": content_type}
        )
    
    if response.status_code not in [200, 204]:
        raise Exception(f"Upload falhou: {response.status_code}")

def main():
    # Verificar qual arquivo .ts é menor
    ts_files = []
    teste_dir = "teste"
    
    for file in os.listdir(teste_dir):
        if file.endswith('.ts'):
            file_path = os.path.join(teste_dir, file)
            size = os.path.getsize(file_path)
            ts_files.append((file, file_path, size))
    
    if not ts_files:
        print("Nenhum arquivo .ts encontrado na pasta teste")
        return
    
    # Pegar o menor arquivo
    smallest_file = min(ts_files, key=lambda x: x[2])
    file_name, file_path, file_size = smallest_file
    
    print(f"Fazendo upload do menor arquivo .ts: {file_name} ({file_size} bytes)")
    
    try:
        # 1. Login
        print("1. Fazendo login...")
        token = login()
        print("Login OK")
        
        # 2. Obter URL de upload
        print("2. Obtendo URL de upload...")
        upload_data = get_upload_url(token, file_name, file_size, "video/mp2t")
        print("URL obtida")
        
        # 3. Upload
        print("3. Fazendo upload...")
        upload_file(upload_data["uploadUrl"], file_path, "video/mp2t")
        print("Upload concluido!")
        
        print(f"Arquivo enviado: {file_name}")
        print(f"ID do arquivo: {upload_data['fileId']}")
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()