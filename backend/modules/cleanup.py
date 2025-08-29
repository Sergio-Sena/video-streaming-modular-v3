import json
import boto3

def handler(event, context):
    """Lambda para deletar arquivos originais após conversão"""
    
    print(f"Cleanup event: {json.dumps(event)}")
    
    try:
        # Parse MediaConvert completion event
        for record in event['Records']:
            if record['source'] == 'aws.mediaconvert':
                detail = record['detail']
                
                if detail['status'] == 'COMPLETE':
                    # Extrai metadata do job
                    user_metadata = detail.get('userMetadata', {})
                    
                    if user_metadata.get('DeleteOriginal') == 'true':
                        original_key = user_metadata.get('OriginalKey')
                        source_bucket = user_metadata.get('SourceBucket')
                        
                        if original_key and source_bucket:
                            print(f"Deletando arquivo original: s3://{source_bucket}/{original_key}")
                            
                            s3_client = boto3.client('s3')
                            s3_client.delete_object(
                                Bucket=source_bucket,
                                Key=original_key
                            )
                            
                            print(f"Arquivo original deletado com sucesso")
                        else:
                            print("Metadata insuficiente para deletar original")
                    else:
                        print("Job não marcado para deletar original")
                else:
                    print(f"Job status: {detail['status']} - não deletando")
                    
    except Exception as e:
        print(f"Erro no cleanup: {str(e)}")
        raise e
    
    return {'statusCode': 200}