import json
import sys
import os
import boto3
import uuid
from datetime import datetime

# Add shared layer to path
sys.path.append('/opt/python/lib/python3.12/site-packages')

def lambda_handler(event, context):
    """Upload Service Lambda handler"""
    
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    try:
        # Handle preflight requests
        if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'OK'})
            }
        
        # Get path and method
        path = event.get('rawPath', '/')
        method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        
        # Health check
        if path == '/health' and method == 'GET':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'healthy',
                    'service': 'upload',
                    'version': '1.0.0'
                })
            }
        
        # Initialize S3 client
        s3_client = boto3.client('s3')
        bucket_name = 'video-streaming-v2-bdc2040d'
        
        # Initiate upload endpoint
        if path == '/upload/initiate' and method == 'POST':
            try:
                body = json.loads(event.get('body', '{}'))
                file_name = body.get('file_name', 'video.mp4')
                file_size = int(body.get('file_size', 0))
                content_type = body.get('content_type', 'video/mp4')
                
                # Generate unique file key
                file_key = f"videos/{datetime.now().strftime('%Y/%m/%d')}/{uuid.uuid4()}-{file_name}"
                
                # Check if multipart upload is needed (>50MB)
                if file_size > 50 * 1024 * 1024:  # 50MB
                    # Initiate multipart upload
                    response = s3_client.create_multipart_upload(
                        Bucket=bucket_name,
                        Key=file_key,
                        ContentType=content_type,
                        Metadata={
                            'original_name': file_name,
                            'upload_date': datetime.now().isoformat(),
                            'file_size': str(file_size)
                        }
                    )
                    
                    return {
                        'statusCode': 200,
                        'headers': headers,
                        'body': json.dumps({
                            'success': True,
                            'upload_type': 'multipart',
                            'upload_id': response['UploadId'],
                            'file_key': file_key,
                            'chunk_size': 20 * 1024 * 1024,  # 20MB chunks
                            'total_parts': (file_size + 20 * 1024 * 1024 - 1) // (20 * 1024 * 1024)
                        })
                    }
                else:
                    # Generate presigned URL for simple upload
                    presigned_url = s3_client.generate_presigned_url(
                        'put_object',
                        Params={
                            'Bucket': bucket_name,
                            'Key': file_key,
                            'ContentType': content_type,
                            'Metadata': {
                                'original_name': file_name,
                                'upload_date': datetime.now().isoformat(),
                                'file_size': str(file_size)
                            }
                        },
                        ExpiresIn=3600  # 1 hour
                    )
                    
                    return {
                        'statusCode': 200,
                        'headers': headers,
                        'body': json.dumps({
                            'success': True,
                            'upload_type': 'simple',
                            'presigned_url': presigned_url,
                            'file_key': file_key
                        })
                    }
                    
            except Exception as e:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'message': f'Failed to initiate upload: {str(e)}'
                    })
                }
        
        # Generate presigned URL for multipart chunk upload
        if path == '/upload/chunk-url' and method == 'POST':
            try:
                body = json.loads(event.get('body', '{}'))
                file_key = body.get('file_key')
                upload_id = body.get('upload_id')
                part_number = int(body.get('part_number'))
                
                if not all([file_key, upload_id, part_number]):
                    return {
                        'statusCode': 400,
                        'headers': headers,
                        'body': json.dumps({
                            'success': False,
                            'message': 'Missing required parameters'
                        })
                    }
                
                # Generate presigned URL for uploading part
                presigned_url = s3_client.generate_presigned_url(
                    'upload_part',
                    Params={
                        'Bucket': bucket_name,
                        'Key': file_key,
                        'PartNumber': part_number,
                        'UploadId': upload_id
                    },
                    ExpiresIn=3600  # 1 hour
                )
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'presigned_url': presigned_url,
                        'part_number': part_number
                    })
                }
                
            except Exception as e:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'message': f'Failed to generate chunk URL: {str(e)}'
                    })
                }
        
        # Complete multipart upload
        if path == '/upload/complete' and method == 'POST':
            try:
                body = json.loads(event.get('body', '{}'))
                file_key = body.get('file_key')
                upload_id = body.get('upload_id')
                parts = body.get('parts', [])  # [{'ETag': 'etag', 'PartNumber': 1}, ...]
                
                if not all([file_key, upload_id, parts]):
                    return {
                        'statusCode': 400,
                        'headers': headers,
                        'body': json.dumps({
                            'success': False,
                            'message': 'Missing required parameters'
                        })
                    }
                
                # Complete multipart upload
                response = s3_client.complete_multipart_upload(
                    Bucket=bucket_name,
                    Key=file_key,
                    UploadId=upload_id,
                    MultipartUpload={'Parts': parts}
                )
                
                # Save metadata to metadata folder
                metadata = {
                    'file_key': file_key,
                    'upload_date': datetime.now().isoformat(),
                    'upload_type': 'multipart',
                    'location': response['Location'],
                    'etag': response['ETag']
                }
                
                metadata_key = f"metadata/{file_key.replace('videos/', '').replace('/', '_')}.json"
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=metadata_key,
                    Body=json.dumps(metadata),
                    ContentType='application/json'
                )
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'message': 'Upload completed successfully',
                        'file_key': file_key,
                        'location': response['Location']
                    })
                }
                
            except Exception as e:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'message': f'Failed to complete upload: {str(e)}'
                    })
                }
        
        # Abort multipart upload
        if path == '/upload/abort' and method == 'POST':
            try:
                body = json.loads(event.get('body', '{}'))
                file_key = body.get('file_key')
                upload_id = body.get('upload_id')
                
                if not all([file_key, upload_id]):
                    return {
                        'statusCode': 400,
                        'headers': headers,
                        'body': json.dumps({
                            'success': False,
                            'message': 'Missing required parameters'
                        })
                    }
                
                # Abort multipart upload
                s3_client.abort_multipart_upload(
                    Bucket=bucket_name,
                    Key=file_key,
                    UploadId=upload_id
                )
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'message': 'Upload aborted successfully'
                    })
                }
                
            except Exception as e:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'message': f'Failed to abort upload: {str(e)}'
                    })
                }
        
        # List uploads (for debugging)
        if path == '/upload/list' and method == 'GET':
            try:
                # List objects in videos folder
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix='videos/',
                    MaxKeys=50
                )
                
                files = []
                for obj in response.get('Contents', []):
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'etag': obj['ETag']
                    })
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'files': files,
                        'count': len(files)
                    })
                }
                
            except Exception as e:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'message': f'Failed to list uploads: {str(e)}'
                    })
                }
        
        # Default response
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'message': 'Endpoint not found',
                'path': path,
                'method': method
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'message': f'Internal server error: {str(e)}'
            })
        }