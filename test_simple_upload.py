#!/usr/bin/env python3
"""
Teste simples de upload de um arquivo pequeno
"""
import requests
from pathlib import Path

def test_simple_upload():
    base_url = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
    
    # Login
    response = requests.post(f"{base_url}/auth/login", json={
        "email": "senanetworker@gmail.com",
        "password": "sergiosena"
    })
    
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Arquivo pequeno para teste
    test_file = Path("teste/d7df65f0-759e-11f0-8eb5-1d4f47706731.pdf")
    
    print(f"Testando upload: {test_file.name}")
    print(f"Tamanho: {test_file.stat().st_size} bytes")
    
    # Obter URL de upload
    upload_request = {
        "fileName": test_file.name,
        "fileSize": test_file.stat().st_size,
        "contentType": "application/pdf"
    }
    
    response = requests.post(f"{base_url}/files/upload-url", 
        headers=headers, json=upload_request)
    
    print(f"Upload URL request: {response.status_code}")
    if response.status_code != 200:
        print(f"Erro: {response.text}")
        return
    
    upload_data = response.json()
    print(f"Upload URL obtida: {upload_data.get('fileId', 'N/A')}")
    
    # Fazer upload
    upload_url = upload_data["uploadUrl"]
    
    with open(test_file, 'rb') as f:
        upload_response = requests.put(upload_url, 
            data=f, 
            headers={"Content-Type": "application/pdf"})
    
    print(f"Upload status: {upload_response.status_code}")
    
    if upload_response.status_code in [200, 204]:
        print("Upload realizado com sucesso!")
        
        # Listar arquivos para verificar
        files_response = requests.get(f"{base_url}/files", headers={"Authorization": f"Bearer {token}"})
        if files_response.status_code == 200:
            files = files_response.json().get("files", [])
            print(f"Total de arquivos agora: {len(files)}")
            
            # Procurar o arquivo enviado
            uploaded_file = None
            for f in files:
                if test_file.name in f.get('name', ''):
                    uploaded_file = f
                    break
            
            if uploaded_file:
                print(f"Arquivo encontrado: {uploaded_file['name']}")
                print(f"Tamanho: {uploaded_file['size']} bytes")
                print(f"Tipo: {uploaded_file.get('type', 'N/A')}")
            else:
                print("Arquivo nao encontrado na listagem")
    else:
        print(f"Upload falhou: {upload_response.status_code}")
        print(f"Resposta: {upload_response.text}")

if __name__ == "__main__":
    test_simple_upload()