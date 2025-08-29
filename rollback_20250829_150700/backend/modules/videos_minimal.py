import json
import boto3

def handler(event, context):
    """Handler mínimo para testar"""
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Requested-With',
        'Access-Control-Allow-Methods': 'POST,GET,OPTIONS,DELETE,PUT',
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
        # GET request - listar vídeos
        if event['httpMethod'] == 'GET':
            s3_client = boto3.client('s3')
            
            response = s3_client.list_objects_v2(
                Bucket='video-streaming-sstech-eaddf6a1',
                Prefix='videos/'
            )
            
            items = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    if not obj['Key'].endswith('/'):
                        items.append({
                            'key': obj['Key'],
                            'name': obj['Key'].split('/')[-1],
                            'size': obj['Size'],
                            'lastModified': obj['LastModified'].isoformat(),
                            'url': f'https://d2we88koy23cl4.cloudfront.net/{obj["Key"]}',
                            'type': 'file'
                        })
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'success': True, 'items': items})
            }
        
        # Outros métodos
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': 'Método não suportado'})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': str(e)})
        }