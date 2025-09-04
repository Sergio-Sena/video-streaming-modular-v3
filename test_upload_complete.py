import requests

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

# Testar endpoint upload-complete
test_data = {"fileId": "users/user-sergio-sena/test-file.mp4"}

print("Testando POST /files/upload-complete")
response = requests.post(f"{API_BASE}/files/upload-complete", json=test_data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

# Testar outros endpoints para comparar
print("\nTestando GET /files")
files_response = requests.get(f"{API_BASE}/files", headers=headers)
print(f"Files Status: {files_response.status_code}")

print("\nTestando GET /health")
health_response = requests.get(f"{API_BASE}/health")
print(f"Health Status: {health_response.status_code}")