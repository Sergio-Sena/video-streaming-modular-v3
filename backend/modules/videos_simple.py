import json
import boto3

def handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'POST,GET,DELETE,OPTIONS',
        'Content-Type': 'application/json'
    }
    
    if event['httpMethod'] == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    try:
        # Verifica token simples
        auth_header = event['headers'].get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({'success': False, 'message': 'Token inválido'})
            }
        
        s3_client = boto3.client('s3')
        
        if event['httpMethod'] == 'GET':
            # Lista vídeos
            response = s3_client.list_objects_v2(
                Bucket='video-streaming-sstech-eaddf6a1',
                Prefix='videos/'
            )
            
            items = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    items.append({
                        'key': obj['Key'],
                        'name': obj['Key'].split('/')[-1],
                        'size': obj['Size'],
                        'url': f'https://d2we88koy23cl4.cloudfront.net/{obj["Key"]}'
                    })
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'success': True, 'items': items})
            }
        
        elif event['httpMethod'] == 'POST':
            # Gera URL de upload
            body = json.loads(event['body'])
            file_name = body.get('fileName', '')
            file_size = body.get('fileSize', 0)
            
            key = f'videos/{file_name}'
            
            # Verifica se é MP4
            is_mp4 = file_name.lower().endswith('.mp4')
            bucket = 'video-streaming-sstech-eaddf6a1' if is_mp4 else 'video-temp-conversion'
            
            if file_size > 50 * 1024 * 1024:  # >50MB = multipart
                response = s3_client.create_multipart_upload(
                    Bucket=bucket,
                    Key=key,
                    ContentType='video/mp4'
                )
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'multipart': True,
                        'uploadId': response['UploadId'],
                        'key': key,
                        'bucket': bucket
                    })
                }
            else:
                # Upload simples
                upload_url = s3_client.generate_presigned_url(
                    'put_object',
                    Params={'Bucket': bucket, 'Key': key, 'ContentType': 'video/mp4'},
                    ExpiresIn=3600
                )
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'uploadUrl': upload_url,
                        'key': key,
                        'bucket': bucket
                    })
                }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': str(e)})
        }