import requests
from urllib.parse import quote

# Configurações
API_BASE = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
EMAIL = "senanetworker@gmail.com"
PASSWORD = "sergiosena"

def test_delete_direct():
    """Testar delete direto com diferentes encodings"""
    
    # 1. Login
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Testar diferentes formas de chamar o delete
    file_name = "1756853751-Video automacao.mp4"
    
    print("=== TESTE 1: Nome sem encoding ===")
    url1 = f"{API_BASE}/files/{file_name}"
    print(f"URL: {url1}")
    response1 = requests.delete(url1, headers=headers)
    print(f"Status: {response1.status_code}")
    print(f"Response: {response1.text}")
    
    print("\\n=== TESTE 2: Nome com encoding manual ===")
    encoded_name = quote(file_name)
    url2 = f"{API_BASE}/files/{encoded_name}"
    print(f"URL: {url2}")
    response2 = requests.delete(url2, headers=headers)
    print(f"Status: {response2.status_code}")
    print(f"Response: {response2.text}")
    
    print("\\n=== TESTE 3: Path completo ===")
    full_path = f"users/user-sergio-sena/{file_name}"
    encoded_full_path = quote(full_path, safe='/')
    url3 = f"{API_BASE}/files/{encoded_full_path}"
    print(f"URL: {url3}")
    response3 = requests.delete(url3, headers=headers)
    print(f"Status: {response3.status_code}")
    print(f"Response: {response3.text}")

if __name__ == "__main__":
    test_delete_direct()