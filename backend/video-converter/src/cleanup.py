import json
import boto3
from urllib.parse import unquote_plus

# AWS Clients
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """Lambda para limpeza após conversão bem-sucedida"""
    
    try:
        print(f"CLEANUP EVENT: {json.dumps(event)}")
        
        # Parse MediaConvert event
        detail = event['detail']
        status = detail['status']
        
        print(f"CLEANUP STATUS: {status}")
        
        if status != 'COMPLETE':
            print(f"Job não completou: {status}")
            return {'statusCode': 200}
        
        # Obter metadados do job
        user_metadata = detail.get('userMetadata', {})
        original_key = user_metadata.get('OriginalKey')
        bucket = user_metadata.get('Bucket')
        
        print(f"CLEANUP METADATA: original_key={original_key}, bucket={bucket}")
        
        if not original_key or not bucket:
            print("Metadados não encontrados")
            return {'statusCode': 400}
        
        print(f"CLEANUP: Iniciando limpeza do arquivo original: {original_key}")
        
        # Verificar se arquivo convertido existe no bucket público
        filename = original_key.split('/')[-1]
        base_name = filename.rsplit('.', 1)[0]
        converted_filename = f"{base_name}_converted.mp4"
        
        # O arquivo convertido vai para o bucket público
        public_converted_key = f"videos/user-sergio-sena/{converted_filename}"
        
        try:
            # Verificar se conversão foi bem-sucedida
            s3_client.head_object(Bucket='automacao-video', Key=public_converted_key)
            print(f"CLEANUP: Arquivo convertido confirmado: {public_converted_key}")
            
            # Deletar arquivo original do bucket privado
            print(f"CLEANUP: Deletando arquivo original: {original_key}")
            s3_client.delete_object(Bucket=bucket, Key=original_key)
            
            # Verificar se foi deletado
            try:
                s3_client.head_object(Bucket=bucket, Key=original_key)
                print(f"CLEANUP ERROR: Arquivo original ainda existe após delete!")
                return {'statusCode': 500}
            except s3_client.exceptions.NoSuchKey:
                print(f"CLEANUP SUCCESS: Arquivo original deletado: {original_key}")
            
        except s3_client.exceptions.NoSuchKey:
            print(f"CLEANUP ERROR: Arquivo convertido não encontrado: {public_converted_key}")
            return {'statusCode': 404}
        
        return {
            'statusCode': 200,
            'body': json.dumps('Limpeza concluída com sucesso')
        }
        
    except Exception as e:
        print(f"CLEANUP ERROR: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Erro na limpeza: {str(e)}')
        }

def generate_converted_key(original_key):
    """Gerar chave do arquivo convertido"""
    base_key = original_key.rsplit('.', 1)[0]
    return f"{base_key}_converted.mp4"

# Alias para compatibilidade
handler = lambda_handler