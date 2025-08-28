import json
import boto3
import urllib.parse

def lambda_handler(event, context):
    """Converte vídeos automaticamente via MediaConvert"""
    
    try:
        # Parse S3 event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
        
        print(f"Processando: {bucket}/{key}")
        
        # Se já é MP4, move direto
        if key.lower().endswith('.mp4'):
            copy_to_final_bucket(bucket, key)
            return {'statusCode': 200, 'body': 'MP4 moved directly'}
        
        # Inicia conversão MediaConvert
        job_id = start_conversion(bucket, key)
        
        return {
            'statusCode': 200,
            'body': json.dumps(f'Conversion started: {job_id}')
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {'statusCode': 500, 'body': str(e)}

def copy_to_final_bucket(source_bucket, source_key):
    """Move MP4 direto para bucket final"""
    s3 = boto3.client('s3')
    
    # Copy to final bucket
    copy_source = {'Bucket': source_bucket, 'Key': source_key}
    final_key = source_key.replace('temp/', 'videos/')
    
    s3.copy_object(
        CopySource=copy_source,
        Bucket='video-streaming-sstech-eaddf6a1',
        Key=final_key
    )
    
    # Delete from temp bucket
    s3.delete_object(Bucket=source_bucket, Key=source_key)
    print(f"MP4 moved: {final_key}")

def start_conversion(source_bucket, source_key):
    """Inicia job MediaConvert"""
    mediaconvert = boto3.client('mediaconvert', region_name='us-east-1')
    
    # Get MediaConvert endpoint
    endpoints = mediaconvert.describe_endpoints()
    endpoint_url = endpoints['Endpoints'][0]['Url']
    mediaconvert = boto3.client('mediaconvert', endpoint_url=endpoint_url)
    
    # Generate output filename
    base_name = source_key.split('/')[-1].rsplit('.', 1)[0]
    output_key = f"videos/{base_name}.mp4"
    
    job_settings = {
        'Role': 'arn:aws:iam::969430605054:role/MediaConvertRole',
        'Settings': {
            'Inputs': [{
                'FileInput': f's3://{source_bucket}/{source_key}',
                'AudioSelectors': {
                    'Audio Selector 1': {
                        'DefaultSelection': 'DEFAULT'
                    }
                },
                'VideoSelector': {}
            }],
            'OutputGroups': [{
                'Name': 'File Group',
                'OutputGroupSettings': {
                    'Type': 'FILE_GROUP_SETTINGS',
                    'FileGroupSettings': {
                        'Destination': f's3://video-streaming-sstech-eaddf6a1/{output_key}'
                    }
                },
                'Outputs': [{
                    'VideoDescription': {
                        'CodecSettings': {
                            'Codec': 'H_264',
                            'H264Settings': {
                                'Bitrate': 8000000,  # 8 Mbps
                                'RateControlMode': 'CBR',
                                'QualityTuningLevel': 'SINGLE_PASS_HQ'
                            }
                        }
                    },
                    'AudioDescriptions': [{
                        'CodecSettings': {
                            'Codec': 'AAC',
                            'AacSettings': {
                                'Bitrate': 128000,
                                'CodingMode': 'CODING_MODE_2_0'
                            }
                        }
                    }],
                    'ContainerSettings': {
                        'Container': 'MP4'
                    }
                }]
            }]
        }
    }
    
    # Create job
    response = mediaconvert.create_job(**job_settings)
    job_id = response['Job']['Id']
    
    print(f"MediaConvert job created: {job_id}")
    return job_id