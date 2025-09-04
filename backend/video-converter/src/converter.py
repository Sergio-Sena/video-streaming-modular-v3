import json
import boto3
import uuid
from urllib.parse import unquote_plus

# AWS Clients
s3_client = boto3.client('s3')
mediaconvert_client = boto3.client('mediaconvert')

import os

# Constants from environment variables
MEDIACONVERT_ROLE = os.environ.get('MEDIACONVERT_ROLE', 'arn:aws:iam::969430605054:role/MediaConvertServiceRole')
MEDIACONVERT_QUEUE = os.environ.get('MEDIACONVERT_QUEUE', 'Default')

def lambda_handler(event, context):
    """Lambda para conversao automatica de videos com MediaConvert"""
    
    try:
        # Parse S3 event
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = unquote_plus(record['s3']['object']['key'])
            size = record['s3']['object']['size']
            
            print(f"Arquivo detectado: {key} ({size} bytes)")
            
            # Verificar se precisa conversao
            if not needs_conversion(key, size):
                print(f"Nao precisa conversao: {key}")
                continue
            
            # Iniciar conversao
            start_conversion(bucket, key)
            
        return {
            'statusCode': 200,
            'body': json.dumps('Conversao iniciada')
        }
        
    except Exception as e:
        print(f"Erro: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Erro: {str(e)}')
        }

def needs_conversion(key, size_bytes):
    """Verificar se arquivo precisa conversao"""
    
    # Extensoes que sempre convertem
    always_convert = ['.ts', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
    
    # Verificar extensao
    key_lower = key.lower()
    for ext in always_convert:
        if key_lower.endswith(ext):
            print(f"Formato {ext} precisa conversao")
            return True
    
    # MP4 grande (>500MB) tambem converte para economizar
    if key_lower.endswith('.mp4'):
        size_mb = size_bytes / (1024 * 1024)
        if size_mb > 500:
            print(f"MP4 grande ({size_mb:.1f}MB) precisa conversao")
            return True
        else:
            print(f"MP4 pequeno ({size_mb:.1f}MB) nao precisa conversao")
            return False
    
    return False

def start_conversion(bucket, key):
    """Iniciar job de conversao no MediaConvert"""
    
    try:
        # Gerar nome do arquivo de saida
        output_key = generate_output_key(key)
        
        # Input e Output S3 URLs
        input_url = f"s3://{bucket}/{key}"
        # Output vai para bucket temporário de processamento
        output_url = f"s3://automacao-video/videos/user-sergio-sena/"
        
        print(f"Convertendo: {input_url} -> {output_url}")
        
        # Job configuration
        job_settings = {
            "Role": MEDIACONVERT_ROLE,
            "Queue": MEDIACONVERT_QUEUE,
            "Settings": {
                "Inputs": [{
                    "FileInput": input_url,
                    "VideoSelector": {},
                    "AudioSelectors": {
                        "Audio Selector 1": {
                            "DefaultSelection": "DEFAULT"
                        }
                    }
                }],
                "OutputGroups": [{
                    "Name": "File Group",
                    "OutputGroupSettings": {
                        "Type": "FILE_GROUP_SETTINGS",
                        "FileGroupSettings": {
                            "Destination": output_url
                        }
                    },
                    "Outputs": [{
                        "NameModifier": "_converted",
                        "VideoDescription": {
                            "CodecSettings": {
                                "Codec": "H_264",
                                "H264Settings": {
                                    "RateControlMode": "QVBR",
                                    "QvbrSettings": {
                                        "QvbrQualityLevel": 7
                                    },
                                    "MaxBitrate": 5000000,
                                    "SceneChangeDetect": "ENABLED"
                                }
                            }
                        },
                        "AudioDescriptions": [{
                            "CodecSettings": {
                                "Codec": "AAC",
                                "AacSettings": {
                                    "Bitrate": 128000,
                                    "SampleRate": 48000,
                                    "CodingMode": "CODING_MODE_2_0"
                                }
                            }
                        }],
                        "ContainerSettings": {
                            "Container": "MP4",
                            "Mp4Settings": {
                                "MoovPlacement": "PROGRESSIVE_DOWNLOAD"
                            }
                        }
                    }]
                }]
            },
            "UserMetadata": {
                "OriginalKey": key,
                "Bucket": bucket
            }
        }
        
        # Criar job
        response = mediaconvert_client.create_job(**job_settings)
        job_id = response['Job']['Id']
        
        print(f"Job criado: {job_id}")
        
        return job_id
        
    except Exception as e:
        print(f"Erro ao criar job: {e}")
        raise

def generate_output_key(input_key):
    """Gerar chave do arquivo de saida"""
    
    # Remover extensao e adicionar .mp4
    base_key = input_key.rsplit('.', 1)[0]
    return f"{base_key}.mp4"

# Alias para compatibilidade
handler = lambda_handler