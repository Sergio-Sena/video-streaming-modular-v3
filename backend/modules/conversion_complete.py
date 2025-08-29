import json
import boto3

def handler(event, context):
    """Callback quando conversão MediaConvert completa"""
    
    s3 = boto3.client('s3')
    
    # Parse do evento CloudWatch
    detail = event.get('detail', {})
    
    if detail.get('status') == 'COMPLETE':
        # Pega metadados do job
        user_metadata = detail.get('userMetadata', {})
        original_bucket = user_metadata.get('OriginalBucket')
        original_key = user_metadata.get('OriginalKey')
        
        if original_bucket and original_key:
            try:
                # Delete arquivo original do bucket temp
                s3.delete_object(
                    Bucket=original_bucket,
                    Key=original_key
                )
                print(f"Arquivo original deletado: {original_key}")
                
            except Exception as e:
                print(f"Erro ao deletar arquivo original: {e}")
    
    return {'statusCode': 200}