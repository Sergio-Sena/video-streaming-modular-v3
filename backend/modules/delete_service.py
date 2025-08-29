import json
import boto3

def handler(event, context):
    """Lambda separada para operações de delete - Implementação gradual"""
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Requested-With',
        'Access-Control-Allow-Methods': 'DELETE,OPTIONS',
        'Content-Type': 'application/json'
    }
    
    # OPTIONS request
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        # FASE 3: Delete normal (confirmação única do frontend)
        query_params = event.get('queryStringParameters') or {}
        video_key = query_params.get('key')
        folder_key = query_params.get('folder')
        
        print(f"DEBUG: Delete request - video_key: {video_key}, folder_key: {folder_key}")
        
        s3_client = boto3.client('s3')
        bucket = 'video-streaming-sstech-eaddf6a1'
        
        if video_key:
            try:
                print(f"DEBUG: Deletando arquivo: {video_key}")
                s3_client.delete_object(Bucket=bucket, Key=video_key)
                print(f"SUCCESS: Arquivo deletado: {video_key}")
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'message': f'Arquivo deletado: {video_key.split("/")[-1]}',
                        'phase': 'FASE_3_DELETE_NORMAL'
                    })
                }
            except Exception as e:
                print(f"ERROR: Falha ao deletar arquivo: {e}")
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'message': f'Erro ao deletar: {str(e)}'
                    })
                }
        
        elif folder_key:
            try:
                print(f"DEBUG: Deletando pasta: {folder_key}")
                
                response = s3_client.list_objects_v2(Bucket=bucket, Prefix=folder_key)
                
                if 'Contents' in response:
                    objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
                    s3_client.delete_objects(
                        Bucket=bucket,
                        Delete={'Objects': objects_to_delete}
                    )
                    print(f"SUCCESS: {len(objects_to_delete)} arquivos deletados")
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'message': f'Pasta deletada: {folder_key.split("/")[-2]}',
                        'phase': 'FASE_3_DELETE_NORMAL'
                    })
                }
            except Exception as e:
                print(f"ERROR: Falha ao deletar pasta: {e}")
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'message': f'Erro ao deletar pasta: {str(e)}'
                    })
                }
        
        else:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'success': False, 
                    'message': 'Parâmetro key ou folder obrigatório'
                })
            }
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False, 
                'message': f'Erro interno: {str(e)}'
            })
        }