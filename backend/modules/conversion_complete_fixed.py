import json
import boto3
import urllib.parse

def handler(event, context):
    """Callback quando conversão MediaConvert completa"""
    
    print(f"Conversion complete event: {json.dumps(event)}")
    
    s3 = boto3.client('s3')
    bucket = 'video-streaming-sstech-eaddf6a1'
    
    # Parse do evento CloudWatch
    detail = event.get('detail', {})
    
    if detail.get('status') == 'COMPLETE':
        # Pega metadados do job
        user_metadata = detail.get('userMetadata', {})
        original_key = user_metadata.get('OriginalKey')
        
        print(f"Job completo. Original key: {original_key}")
        
        if original_key:
            try:
                # Lista arquivos na pasta converted para encontrar o MP4
                response = s3.list_objects_v2(Bucket=bucket, Prefix='converted/')
                
                if 'Contents' in response:
                    for obj in response['Contents']:
                        converted_key = obj['Key']
                        if converted_key.endswith('.mp4'):
                            print(f"Arquivo convertido encontrado: {converted_key}")
                            
                            # Gera nome final baseado no arquivo original
                            base_name = original_key.replace('videos/', '').rsplit('.', 1)[0]
                            final_key = f'videos/{base_name}.mp4'
                            
                            print(f"Movendo: {converted_key} -> {final_key}")
                            
                            # Move MP4 da pasta converted/ para videos/
                            s3.copy_object(
                                Bucket=bucket,
                                CopySource={'Bucket': bucket, 'Key': converted_key},
                                Key=final_key
                            )
                            
                            # Delete arquivo MP4 da pasta converted/
                            s3.delete_object(Bucket=bucket, Key=converted_key)
                            
                            # Delete arquivo original
                            s3.delete_object(Bucket=bucket, Key=original_key)
                            
                            print(f"Conversão completa: {original_key} -> {final_key}")
                            break
                
            except Exception as e:
                print(f"Erro no pós-processamento: {e}")
    
    return {'statusCode': 200}