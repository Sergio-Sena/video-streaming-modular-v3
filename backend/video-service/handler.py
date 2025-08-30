import json
import sys
import os
import boto3
from datetime import datetime
from urllib.parse import unquote

# Add shared layer to path
sys.path.append('/opt/python/lib/python3.12/site-packages')

def lambda_handler(event, context):
    """Video Service Lambda handler"""
    
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
                    'service': 'video',
                    'version': '1.0.0'
                })
            }
        
        # Initialize S3 client
        s3_client = boto3.client('s3')
        bucket_name = 'video-streaming-v2-bdc2040d'
        
        # List videos endpoint
        if path == '/videos/list' and method == 'GET':
            try:
                # Get query parameters
                query_params = event.get('queryStringParameters', {}) or {}
                folder = query_params.get('folder', '')
                limit = int(query_params.get('limit', 50))
                
                # List objects in videos folder
                prefix = f"videos/{folder}" if folder else "videos/"
                
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=prefix,
                    MaxKeys=limit
                )
                
                videos = []
                for obj in response.get('Contents', []):
                    if obj['Key'].endswith('/'):  # Skip folder markers
                        continue
                    
                    # Generate CloudFront URL (assuming CloudFront is configured)
                    video_url = f"https://d2we88koy23cl4.cloudfront.net/{obj['Key']}"
                    
                    # Try to get metadata
                    metadata_key = f"metadata/{obj['Key'].replace('videos/', '').replace('/', '_')}.json"
                    metadata = {}
                    try:
                        metadata_obj = s3_client.get_object(Bucket=bucket_name, Key=metadata_key)
                        metadata = json.loads(metadata_obj['Body'].read().decode('utf-8'))
                    except:
                        pass  # Metadata not found, use defaults
                    
                    videos.append({
                        'id': obj['Key'].split('/')[-1].split('.')[0],
                        'key': obj['Key'],
                        'name': obj['Key'].split('/')[-1],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'url': video_url,
                        'metadata': metadata
                    })
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'videos': videos,
                        'count': len(videos),
                        'folder': folder
                    })
                }
                
            except Exception as e:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'message': f'Failed to list videos: {str(e)}'
                    })
                }
        
        # Get video details endpoint
        if path.startswith('/videos/') and method == 'GET' and len(path.split('/')) == 3:
            try:
                video_id = path.split('/')[-1]
                
                # Find video by ID (search in videos folder)
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix="videos/"
                )
                
                video_obj = None
                for obj in response.get('Contents', []):
                    if video_id in obj['Key']:
                        video_obj = obj
                        break
                
                if not video_obj:
                    return {
                        'statusCode': 404,
                        'headers': headers,
                        'body': json.dumps({
                            'success': False,
                            'message': 'Video not found'
                        })
                    }
                
                # Generate CloudFront URL
                video_url = f"https://d2we88koy23cl4.cloudfront.net/{video_obj['Key']}"
                
                # Get metadata
                metadata_key = f"metadata/{video_obj['Key'].replace('videos/', '').replace('/', '_')}.json"
                metadata = {}
                try:
                    metadata_obj = s3_client.get_object(Bucket=bucket_name, Key=metadata_key)
                    metadata = json.loads(metadata_obj['Body'].read().decode('utf-8'))
                except:
                    pass
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'video': {
                            'id': video_id,
                            'key': video_obj['Key'],
                            'name': video_obj['Key'].split('/')[-1],
                            'size': video_obj['Size'],
                            'last_modified': video_obj['LastModified'].isoformat(),
                            'url': video_url,
                            'metadata': metadata
                        }
                    })
                }
                
            except Exception as e:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'message': f'Failed to get video: {str(e)}'
                    })
                }
        
        # Delete video endpoint
        if path.startswith('/videos/') and method == 'DELETE' and len(path.split('/')) == 3:
            try:
                video_id = path.split('/')[-1]
                
                # Find video by ID
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix="videos/"
                )
                
                video_obj = None
                for obj in response.get('Contents', []):
                    if video_id in obj['Key']:
                        video_obj = obj
                        break
                
                if not video_obj:
                    return {
                        'statusCode': 404,
                        'headers': headers,
                        'body': json.dumps({
                            'success': False,
                            'message': 'Video not found'
                        })
                    }
                
                # Delete video file
                s3_client.delete_object(Bucket=bucket_name, Key=video_obj['Key'])
                
                # Delete metadata if exists
                metadata_key = f"metadata/{video_obj['Key'].replace('videos/', '').replace('/', '_')}.json"
                try:
                    s3_client.delete_object(Bucket=bucket_name, Key=metadata_key)
                except:
                    pass  # Metadata might not exist
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'message': 'Video deleted successfully',
                        'video_id': video_id
                    })
                }
                
            except Exception as e:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'message': f'Failed to delete video: {str(e)}'
                    })
                }
        
        # Get video streaming URL endpoint
        if path.startswith('/videos/') and path.endswith('/url') and method == 'GET':
            try:
                video_id = path.split('/')[-2]
                
                # Find video by ID
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix="videos/"
                )
                
                video_obj = None
                for obj in response.get('Contents', []):
                    if video_id in obj['Key']:
                        video_obj = obj
                        break
                
                if not video_obj:
                    return {
                        'statusCode': 404,
                        'headers': headers,
                        'body': json.dumps({
                            'success': False,
                            'message': 'Video not found'
                        })
                    }
                
                # Generate CloudFront URL for streaming
                streaming_url = f"https://d2we88koy23cl4.cloudfront.net/{video_obj['Key']}"
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'url': streaming_url,
                        'video_id': video_id,
                        'content_type': 'video/mp4'
                    })
                }
                
            except Exception as e:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'message': f'Failed to get video URL: {str(e)}'
                    })
                }
        
        # Get folders/directories endpoint
        if path == '/videos/folders' and method == 'GET':
            try:
                # List all objects to find folder structure
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix="videos/",
                    Delimiter="/"
                )
                
                folders = []
                for prefix in response.get('CommonPrefixes', []):
                    folder_name = prefix['Prefix'].replace('videos/', '').rstrip('/')
                    if folder_name:  # Skip empty folder names
                        folders.append({
                            'name': folder_name,
                            'path': prefix['Prefix']
                        })
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'folders': folders,
                        'count': len(folders)
                    })
                }
                
            except Exception as e:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'message': f'Failed to get folders: {str(e)}'
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