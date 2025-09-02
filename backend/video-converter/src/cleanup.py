import json
import boto3
from urllib.parse import unquote_plus

# AWS Clients
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """Lambda para limpeza apos conversao bem-sucedida"""
    
    try:
        # Parse MediaConvert event
        detail = event['detail']
        status = detail['status']
        
        if status != 'COMPLETE':
            print(f"Job nao completou: {status}")
            return {'statusCode': 200}
        
        # Obter metadados do job
        user_metadata = detail.get('userMetadata', {})
        original_key = user_metadata.get('OriginalKey')
        bucket = user_metadata.get('Bucket')
        
        if not original_key or not bucket:
            print("Metadados nao encontrados")
            return {'statusCode': 400}
        
        print(f"Limpando arquivo original: {original_key}")
        
        # Verificar se arquivo convertido existe
        converted_key = generate_converted_key(original_key)
        
        try:
            s3_client.head_object(Bucket=bucket, Key=converted_key)
            print(f"Arquivo convertido existe: {converted_key}")
            
            # Deletar arquivo original
            s3_client.delete_object(Bucket=bucket, Key=original_key)
            print(f"Arquivo original deletado: {original_key}")
            
        except s3_client.exceptions.NoSuchKey:
            print(f"Arquivo convertido nao encontrado: {converted_key}")
            return {'statusCode': 404}
        
        return {
            'statusCode': 200,
            'body': json.dumps('Limpeza concluida')
        }
        
    except Exception as e:
        print(f"Erro na limpeza: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Erro: {str(e)}')
        }

def generate_converted_key(original_key):
    """Gerar chave do arquivo convertido"""
    base_key = original_key.rsplit('.', 1)[0]
    return f"{base_key}_converted.mp4"

# Alias para compatibilidade
handler = lambda_handler