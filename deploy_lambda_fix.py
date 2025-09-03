#!/usr/bin/env python3
"""
Script para fazer deploy das correções no Lambda
"""

import boto3
import zipfile
import os
import time
from pathlib import Path

# Configurações
LAMBDA_FUNCTION_NAME = 'auth-service-v3'
LAMBDA_SOURCE_DIR = 'backend/auth-service'

def create_deployment_package():
    """Criar pacote de deployment do Lambda"""
    print("📦 Criando pacote de deployment...")
    
    # Diretório de trabalho
    source_dir = Path(LAMBDA_SOURCE_DIR)
    zip_path = source_dir / 'lambda-deployment-fix.zip'
    
    # Remover zip anterior se existir
    if zip_path.exists():
        zip_path.unlink()
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Adicionar arquivos Python
        src_dir = source_dir / 'src'
        for py_file in src_dir.glob('*.py'):
            zipf.write(py_file, py_file.name)
            print(f"  ✅ {py_file.name}")
        
        # Adicionar requirements se existir
        req_file = source_dir / 'requirements.txt'
        if req_file.exists():
            zipf.write(req_file, 'requirements.txt')
            print(f"  ✅ requirements.txt")
    
    print(f"📦 Pacote criado: {zip_path}")
    return zip_path

def deploy_lambda(zip_path):
    """Fazer deploy do Lambda"""
    print("🚀 Fazendo deploy do Lambda...")
    
    lambda_client = boto3.client('lambda')
    
    try:
        # Ler o arquivo zip
        with open(zip_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        # Atualizar código do Lambda
        response = lambda_client.update_function_code(
            FunctionName=LAMBDA_FUNCTION_NAME,
            ZipFile=zip_content
        )
        
        print(f"✅ Deploy concluído")
        print(f"📊 Versão: {response['Version']}")
        print(f"📊 Última modificação: {response['LastModified']}")
        
        # Aguardar função ficar ativa
        print("⏳ Aguardando função ficar ativa...")
        waiter = lambda_client.get_waiter('function_active')
        waiter.wait(FunctionName=LAMBDA_FUNCTION_NAME)
        
        print("✅ Função ativa e pronta")
        return True
        
    except Exception as e:
        print(f"❌ Erro no deploy: {e}")
        return False

def test_lambda_endpoint():
    """Testar endpoint do Lambda"""
    print("🧪 Testando endpoint do Lambda...")
    
    import requests
    
    # URL de teste
    base_url = "https://g1laj6w194.execute-api.us-east-1.amazonaws.com/prod"
    
    try:
        # Teste health check
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"📊 Health check: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Status: {data.get('status')}")
            print(f"📊 Timestamp: {data.get('timestamp')}")
        
        # Teste OPTIONS no endpoint de download
        test_file = "users%2Fuser-sergio-sena%2F1756853751-Video%20automacao.mp4"
        options_response = requests.options(
            f"{base_url}/files/{test_file}/download",
            timeout=10
        )
        print(f"📊 OPTIONS request: {options_response.status_code}")
        
        if options_response.status_code in [200, 204]:
            print("✅ CORS preflight funcionando")
        else:
            print("⚠️  CORS preflight pode ter problemas")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """Executar deploy completo"""
    print("🚀 Iniciando deploy das correções do Lambda")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not Path(LAMBDA_SOURCE_DIR).exists():
        print(f"❌ Diretório {LAMBDA_SOURCE_DIR} não encontrado")
        print("Execute este script na raiz do projeto")
        return
    
    success_count = 0
    
    # Passo 1: Criar pacote
    try:
        zip_path = create_deployment_package()
        success_count += 1
    except Exception as e:
        print(f"❌ Erro ao criar pacote: {e}")
        return
    
    # Passo 2: Deploy
    if deploy_lambda(zip_path):
        success_count += 1
    
    # Passo 3: Testar
    print("\n⏳ Aguardando 10 segundos para estabilização...")
    time.sleep(10)
    
    if test_lambda_endpoint():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Resultado: {success_count}/3 passos concluídos")
    
    if success_count == 3:
        print("🎉 Deploy concluído com sucesso!")
        print("💡 Lambda atualizado com correções CORS")
    else:
        print("⚠️  Alguns passos falharam. Verifique os logs")
    
    print("\n📋 Próximos passos:")
    print("1. Execute fix_video_cors.py para aplicar correções S3/CloudFront")
    print("2. Teste os vídeos no frontend")

if __name__ == "__main__":
    main()