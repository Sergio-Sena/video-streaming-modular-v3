import json
import boto3
from urllib.parse import unquote_plus

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Lambda para mover vídeo convertido de volta e deletar original
    Triggered por EventBridge quando MediaConvert completa
    """
    
    try:
        # Parse MediaConvert completion event
        job_id = event['detail']['jobId']
        status = event['detail']['status']
        
        if status != 'COMPLETE':
            print(f"Job {job_id} não completou com sucesso: {status}")
            return {'statusCode': 200, 'body': 'Job não completado'}
        
        # Obter metadados do job
        mediaconvert = boto3.client('mediaconvert')
        job_details = mediaconvert.get_job(Id=job_id)
        
        original_key = job_details['Job']['UserMetadata']['OriginalKey']
        bucket = job_details['Job']['UserMetadata']['Bucket']
        
        print(f"Processando: {original_key} do bucket {bucket}")
        
        # Gerar chave do arquivo convertido
        converted_key = generate_converted_key(original_key)
        temp_bucket = 'automacao-video'
        temp_key = f"videos/user-sergio-sena/{converted_key.split('/')[-1]}"
        
        # 1. Copiar arquivo convertido de volta para bucket principal
        copy_source = {'Bucket': temp_bucket, 'Key': temp_key}
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=bucket,
            Key=converted_key
        )
        print(f"Copiado: {temp_bucket}/{temp_key} → {bucket}/{converted_key}")
        
        # 2. Deletar arquivo original (não convertido)
        s3_client.delete_object(Bucket=bucket, Key=original_key)
        print(f"Deletado original: {bucket}/{original_key}")
        
        # 3. Deletar arquivo temporário do bucket de processamento
        s3_client.delete_object(Bucket=temp_bucket, Key=temp_key)
        print(f"Deletado temporário: {temp_bucket}/{temp_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Conversão completada',
                'original': original_key,
                'converted': converted_key,
                'deleted_original': True,
                'cleaned_temp': True
            })
        }
        
    except Exception as e:
        print(f"Erro no cleanup: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Erro: {str(e)}')
        }

def generate_converted_key(original_key):
    """Gerar chave do arquivo convertido"""
    # Remover extensão e adicionar .mp4
    base_key = original_key.rsplit('.', 1)[0]
    return f"{base_key}.mp4"

# Alias para compatibilidade
handler = lambda_handler