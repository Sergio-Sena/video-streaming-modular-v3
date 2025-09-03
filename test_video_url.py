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

def get_files(token):
    """Obter lista de arquivos"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_URL}/files", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao obter arquivos: {response.status_code}")

def test_video_url(url):
    """Testar se URL do vídeo funciona"""
    try:
        response = requests.head(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"Content-Length: {response.headers.get('Content-Length', 'N/A')}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro ao testar URL: {e}")
        return False

def main():
    try:
        # 1. Login
        print("1. Fazendo login...")
        token = login()
        print("Login OK")
        
        # 2. Obter arquivos
        print("2. Obtendo arquivos...")
        files_data = get_files(token)
        files = files_data.get('files', [])
        
        print(f"Encontrados {len(files)} arquivos")
        
        # 3. Testar URLs de vídeos
        video_files = [f for f in files if f.get('type', '').startswith('video/')]
        
        print(f"\nTestando {len(video_files)} vídeos:")
        
        for i, video in enumerate(video_files[:3]):  # Testar apenas os 3 primeiros
            print(f"\n--- Vídeo {i+1}: {video['name'][:50]}... ---")
            print(f"Tipo: {video.get('type', 'N/A')}")
            print(f"Tamanho: {video.get('size', 'N/A')} bytes")
            print(f"Dados do vídeo: {json.dumps(video, indent=2)[:200]}...")
            
            # Verificar se tem URL
            if 'url' in video:
                print(f"URL: {video['url'][:100]}...")
                # Testar URL
                if test_video_url(video['url']):
                    print("URL funciona!")
                else:
                    print("URL não funciona")
            else:
                print("Campo 'url' não encontrado no arquivo")
                
                # Testar URL de download direto
                download_url = f"{API_URL}/files/{video['id']}/download"
                print(f"Testando download direto: {download_url[:100]}...")
                if test_video_url(download_url):
                    print("Download direto funciona!")
                else:
                    print("Download direto não funciona")
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()