import boto3
import requests

# Testar URL presigned diretamente
s3_client = boto3.client('s3')
STORAGE_BUCKET = 'drive-online-storage'

# Pegar um arquivo que sabemos que existe
file_key = "users/user-sergio-sena/1756847941-Cindel Toda Safada Esfregando a Bucetinha. Voce Quer Chupar Essa Bucetinha. Cindel_xo Cindelxoxo - Pornhub.com_converted.mp4"

print(f"Testando arquivo: {file_key}")

# Verificar se arquivo existe
try:
    response = s3_client.head_object(Bucket=STORAGE_BUCKET, Key=file_key)
    print("Arquivo existe no S3")
    print(f"Tamanho: {response['ContentLength']} bytes")
    print(f"Tipo: {response.get('ContentType', 'N/A')}")
except Exception as e:
    print(f"Arquivo nao encontrado: {e}")
    exit()

# Gerar URL presigned
try:
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': STORAGE_BUCKET, 'Key': file_key},
        ExpiresIn=3600
    )
    print("URL presigned gerada")
    print(f"URL: {presigned_url[:100]}...")
except Exception as e:
    print(f"Erro ao gerar URL: {e}")
    exit()

# Testar URL
try:
    response = requests.head(presigned_url, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    print(f"Content-Length: {response.headers.get('Content-Length', 'N/A')}")
    
    if response.status_code == 200:
        print("URL presigned funciona!")
    else:
        print("URL presigned nao funciona")
        
except Exception as e:
    print(f"Erro ao testar URL: {e}")