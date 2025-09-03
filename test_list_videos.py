import requests
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

def list_files(token):
    """Listar arquivos"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_URL}/files", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao listar arquivos: {response.status_code}")

def main():
    try:
        # Login
        print("Fazendo login...")
        token = login()
        
        # Listar arquivos
        print("Listando arquivos...")
        files_data = list_files(token)
        files = files_data.get('files', [])
        
        print(f"\nTotal de arquivos: {len(files)}")
        print("\nPrimeiros 10 arquivos:")
        
        for i, file in enumerate(files[:10]):
            print(f"{i+1}. {file['name']}")
            print(f"   Tipo: {file.get('type', 'N/A')}")
            print(f"   Tamanho: {file.get('size', 0)} bytes")
            print(f"   ID: {file.get('id', 'N/A')}")
            print()
        
        # Procurar vídeo de exemplo
        sample_video = None
        for file in files:
            if 'exemplo' in file['name'].lower() or 'sample' in file['name'].lower():
                sample_video = file
                break
        
        if sample_video:
            print("Video de exemplo encontrado:")
            print(f"Nome: {sample_video['name']}")
            print(f"URL: {sample_video.get('url', 'N/A')}")
        else:
            print("Video de exemplo NAO encontrado na lista")
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()