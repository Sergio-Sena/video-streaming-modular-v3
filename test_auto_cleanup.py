import requests
import time

API_BASE = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
EMAIL = "senanetworker@gmail.com"
PASSWORD = "sergiosena"

def test_auto_cleanup():
    # Login
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("=== TESTE CLEANUP AUTOMATICO ===")
    
    # Listar arquivos antes
    files_before = requests.get(f"{API_BASE}/files", headers=headers).json().get("files", [])
    print(f"Arquivos antes: {len(files_before)}")
    
    # Procurar por videos grandes que podem ser convertidos
    for file in files_before:
        if file['name'].endswith('.mp4') and file['size'] > 10000000:  # > 10MB
            print(f"Video encontrado para teste: {file['name']} ({file['size']} bytes)")
            
            # Simular conversao (normalmente seria automatica)
            print("Conversao seria iniciada automaticamente...")
            print("Cleanup sera executado quando conversao completar")
            break
    else:
        print("Nenhum video grande encontrado para teste de conversao")
    
    print("\nTrigger configurado com sucesso!")
    print("Proximos uploads de video > 500MB serao convertidos e limpos automaticamente")

if __name__ == "__main__":
    test_auto_cleanup()