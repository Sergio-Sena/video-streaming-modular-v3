import requests

# Teste simples do delete
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

# Testar rota simples primeiro
print("=== TESTE HEALTH ===")
health_response = requests.get(f"{API_BASE}/health")
print(f"Health: {health_response.status_code} - {health_response.text}")

print("\\n=== TESTE FILES GET ===")
files_response = requests.get(f"{API_BASE}/files", headers=headers)
print(f"Files: {files_response.status_code}")

print("\\n=== TESTE DELETE SIMPLES ===")
# Tentar delete com path mais simples
delete_response = requests.delete(f"{API_BASE}/files/test", headers=headers)
print(f"Delete test: {delete_response.status_code} - {delete_response.text}")