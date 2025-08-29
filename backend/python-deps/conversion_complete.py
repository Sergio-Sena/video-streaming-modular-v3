import json
import boto3
import urllib.parse

def handler(event, context):
    """Callback quando conversão MediaConvert completa"""
    
    s3 = boto3.client('s3')
    bucket = 'video-streaming-sstech-eaddf6a1'
    
    # Parse do evento CloudWatch
    detail = event.get('detail', {})
    
    if detail.get('status') == 'COMPLETE':
        # Pega metadados do job
        user_metadata = detail.get('userMetadata', {})
        original_key = user_metadata.get('OriginalKey')
        
        if original_key:
            try:
                # Gera nome do arquivo MP4 convertido
                base_name = original_key.replace('videos/', '').rsplit('.', 1)[0]
                converted_key = f'converted/{base_name}_converted.mp4'
                final_key = f'videos/{base_name}.mp4'
                
                print(f"Movendo: {converted_key} → {final_key}")
                
                # Move MP4 da pasta converted/ para videos/
                s3.copy_object(
                    Bucket=bucket,
                    CopySource={'Bucket': bucket, 'Key': converted_key},
                    Key=final_key
                )
                
                # Delete arquivo MP4 da pasta converted/
                s3.delete_object(Bucket=bucket, Key=converted_key)
                
                # Delete arquivo original .ts
                s3.delete_object(Bucket=bucket, Key=original_key)
                
                print(f"Conversão completa: {original_key} → {final_key}")
                
            except Exception as e:
                print(f"Erro no pós-processamento: {e}")
    
    return {'statusCode': 200}