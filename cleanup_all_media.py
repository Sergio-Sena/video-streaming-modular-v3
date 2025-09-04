#!/usr/bin/env python3
"""
Script para limpar todas as mídias dos buckets S3 do Drive Online
"""

import boto3
import json
from botocore.exceptions import ClientError

# Configuração dos buckets
BUCKETS = [
    'drive-online-storage',  # Bucket privado principal
    'automacao-video'        # Bucket público para vídeos
]

def cleanup_bucket(bucket_name):
    """Limpa todos os objetos de um bucket S3"""
    s3 = boto3.client('s3')
    
    try:
        # Lista todos os objetos
        response = s3.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' not in response:
            print(f"Bucket {bucket_name} ja esta vazio")
            return
        
        # Prepara lista de objetos para deletar
        objects_to_delete = []
        for obj in response['Contents']:
            objects_to_delete.append({'Key': obj['Key']})
        
        # Deleta em lotes
        if objects_to_delete:
            delete_response = s3.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': objects_to_delete}
            )
            
            deleted_count = len(delete_response.get('Deleted', []))
            print(f"Deletados {deleted_count} arquivos do bucket {bucket_name}")
            
            # Mostra erros se houver
            if 'Errors' in delete_response:
                for error in delete_response['Errors']:
                    print(f"Erro ao deletar {error['Key']}: {error['Message']}")
        
    except ClientError as e:
        print(f"Erro ao acessar bucket {bucket_name}: {e}")

def main():
    """Executa limpeza completa"""
    print("Iniciando limpeza completa das midias...")
    
    for bucket in BUCKETS:
        print(f"\nLimpando bucket: {bucket}")
        cleanup_bucket(bucket)
    
    print("\nLimpeza concluida!")

if __name__ == "__main__":
    main()