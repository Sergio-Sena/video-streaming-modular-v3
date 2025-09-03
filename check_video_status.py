#!/usr/bin/env python3
"""
Verificar status das correções de vídeo
"""

import requests
import boto3
from botocore.exceptions import ClientError

# Configurações
API_BASE = 'https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod'
TEST_VIDEO = 'users/user-sergio-sena/1756853751-Video automacao.mp4'
BUCKET_NAME = 'drive-online-storage'

def check_lambda_status():
    """Verificar status do Lambda"""
    print("=== VERIFICANDO LAMBDA ===")
    
    try:
        # Health check
        response = requests.get(f"{API_BASE}/health", timeout=10)
        print(f"Health check: {response.status_code}")
        
        # Teste do endpoint de vídeo
        video_url = f"{API_BASE}/files/{requests.utils.quote(TEST_VIDEO, safe='')}/download"
        print(f"URL do video: {video_url}")
        
        # HEAD request
        head_response = requests.head(video_url, timeout=10)
        print(f"HEAD request: {head_response.status_code}")
        
        if head_response.status_code == 200:
            print("Headers recebidos:")
            for key, value in head_response.headers.items():
                if 'access-control' in key.lower() or 'content-type' in key.lower():
                    print(f"  {key}: {value}")
            return True
        else:
            print(f"Erro: Status {head_response.status_code}")
            return False
            
    except Exception as e:
        print(f"Erro: {e}")
        return False

def check_s3_file():
    """Verificar arquivo no S3"""
    print("\n=== VERIFICANDO S3 ===")
    
    try:
        s3_client = boto3.client('s3')
        
        # Verificar se arquivo existe
        response = s3_client.head_object(Bucket=BUCKET_NAME, Key=TEST_VIDEO)
        
        print(f"Arquivo encontrado: {TEST_VIDEO}")
        print(f"Content-Type: {response.get('ContentType', 'N/A')}")
        print(f"Tamanho: {response.get('ContentLength', 0)} bytes")
        
        return True
        
    except ClientError as e:
        print(f"Erro S3: {e}")
        return False

def deploy_lambda_fix():
    """Fazer deploy das correções do Lambda"""
    print("\n=== FAZENDO DEPLOY DO LAMBDA ===")
    
    try:
        import zipfile
        import os
        from pathlib import Path
        
        # Criar zip com as correções
        lambda_dir = Path('backend/auth-service')
        zip_path = lambda_dir / 'lambda-fix.zip'
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            src_dir = lambda_dir / 'src'
            for py_file in src_dir.glob('*.py'):
                zipf.write(py_file, py_file.name)
        
        # Deploy
        lambda_client = boto3.client('lambda')
        
        with open(zip_path, 'rb') as zip_file:
            lambda_client.update_function_code(
                FunctionName='auth-service-v3',
                ZipFile=zip_file.read()
            )
        
        print("Deploy concluido com sucesso")
        
        # Limpar arquivo temporário
        zip_path.unlink()
        
        return True
        
    except Exception as e:
        print(f"Erro no deploy: {e}")
        return False

def main():
    """Executar verificações"""
    print("VERIFICANDO STATUS DAS CORRECOES DE VIDEO")
    print("=" * 50)
    
    # Verificar S3
    s3_ok = check_s3_file()
    
    # Verificar Lambda
    lambda_ok = check_lambda_status()
    
    # Se Lambda não estiver funcionando, fazer deploy
    if not lambda_ok:
        print("\nLambda precisa de correção. Fazendo deploy...")
        if deploy_lambda_fix():
            print("Aguardando 10 segundos...")
            import time
            time.sleep(10)
            lambda_ok = check_lambda_status()
    
    # Resultado final
    print("\n" + "=" * 50)
    print("RESULTADO FINAL:")
    print(f"S3: {'OK' if s3_ok else 'ERRO'}")
    print(f"Lambda: {'OK' if lambda_ok else 'ERRO'}")
    
    if s3_ok and lambda_ok:
        print("\nTODAS AS CORRECOES APLICADAS!")
        print("Teste os videos no frontend.")
        
        # URL para teste manual
        test_url = f"{API_BASE}/files/{requests.utils.quote(TEST_VIDEO, safe='')}/download"
        print(f"\nURL para teste: {test_url}")
        
    else:
        print("\nALGUMAS CORRECOES AINDA PRECISAM SER APLICADAS")

if __name__ == "__main__":
    main()