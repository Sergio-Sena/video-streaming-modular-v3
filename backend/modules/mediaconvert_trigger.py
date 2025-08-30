import json
import boto3
import os
from datetime import datetime

def handler(event, context):
    """Lambda trigger para conversão automática de vídeos"""
    
    print(f"MediaConvert trigger event: {json.dumps(event)}")
    
    try:
        # Parse S3 event
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            
            print(f"Arquivo detectado: s3://{bucket}/{key}")
            
            # Verifica se é um arquivo que precisa conversão
            if should_convert(key):
                print(f"Iniciando conversão para: {key}")
                start_conversion(bucket, key)
            else:
                print(f"Arquivo não precisa conversão: {key}")
                
    except Exception as e:
        print(f"Erro no MediaConvert trigger: {str(e)}")
        raise e

def should_convert(key):
    """Verifica se arquivo precisa conversão para MP4"""
    # Ignora arquivos já convertidos
    if '/converted/' in key or key.startswith('converted/'):
        return False
    
    # Ignora se não é vídeo
    if not key.startswith('videos/'):
        return False
        
    # Extensões de vídeo suportadas (TODAS exceto MP4)
    video_extensions = ['.ts', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.m2ts', '.mts', 
                       '.webm', '.ogv', '.3gp', '.m4v', '.vob', '.asf', '.rm', '.rmvb']
    
    # Converte TUDO exceto MP4
    file_lower = key.lower()
    if file_lower.endswith('.mp4'):
        return False  # MP4 já está no formato correto
        
    # Verifica se é algum formato de vídeo
    for ext in video_extensions:
        if file_lower.endswith(ext):
            return True
            
    return False

def start_conversion(source_bucket, source_key):
    """Inicia job de conversão no MediaConvert"""
    
    mediaconvert = boto3.client('mediaconvert', region_name='us-east-1')
    
    # Obter endpoint do MediaConvert
    endpoints = mediaconvert.describe_endpoints()
    endpoint_url = endpoints['Endpoints'][0]['Url']
    
    # Cliente com endpoint específico
    mc_client = boto3.client('mediaconvert', endpoint_url=endpoint_url, region_name='us-east-1')
    
    # Gerar nome do arquivo de saída
    output_key = generate_output_key(source_key)
    
    # Configuração do job - Conversão Universal para MP4
    job_settings = {
        "Role": "arn:aws:iam::969430605054:role/MediaConvertRole",
        "Settings": {
            "TimecodeConfig": {"Source": "ZEROBASED"},
            "OutputGroups": [{
                "Name": "MP4_Universal",
                "Outputs": [{
                    "VideoDescription": {
                        "CodecSettings": {
                            "Codec": "H_264",
                            "H264Settings": {
                                "RateControlMode": "CBR",
                                "Bitrate": 5000000,  # 5 Mbps
                                "CodecProfile": "HIGH",
                                "CodecLevel": "AUTO"
                            }
                        },
                        "Width": 1920,
                        "Height": 1080
                    },
                    "AudioDescriptions": [{
                        "CodecSettings": {
                            "Codec": "AAC",
                            "AacSettings": {
                                "Bitrate": 128000,  # 128 kbps
                                "SampleRate": 48000,
                                "CodingMode": "CODING_MODE_2_0"
                            }
                        }
                    }],
                    "ContainerSettings": {
                        "Container": "MP4",
                        "Mp4Settings": {
                            "FreeSpaceBox": "EXCLUDE",
                            "MoovPlacement": "PROGRESSIVE_DOWNLOAD"
                        }
                    },
                    "NameModifier": "_mp4"
                }],
                "OutputGroupSettings": {
                    "Type": "FILE_GROUP_SETTINGS",
                    "FileGroupSettings": {
                        "Destination": f"s3://{source_bucket}/videos/"
                    }
                }
            }],
            "Inputs": [{
                "AudioSelectors": {
                    "Audio Selector 1": {
                        "DefaultSelection": "DEFAULT",
                        "SelectorType": "TRACK"
                    }
                },
                "VideoSelector": {
                    "ColorSpace": "FOLLOW"
                },
                "TimecodeSource": "ZEROBASED",
                "FileInput": f"s3://{source_bucket}/{source_key}"
            }]
        },
        "Queue": "arn:aws:mediaconvert:us-east-1:969430605054:queues/Default",
        "UserMetadata": {
            "OriginalKey": source_key,
            "SourceBucket": source_bucket,
            "ConversionType": "Universal_to_MP4"
        }
    }
    
    try:
        response = mc_client.create_job(**job_settings)
        job_id = response['Job']['Id']
        
        print(f"Job MediaConvert criado: {job_id}")
        print(f"Input: s3://{source_bucket}/{source_key}")
        print(f"Output: s3://{source_bucket}/converted/{output_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Conversão iniciada',
                'jobId': job_id,
                'inputFile': source_key,
                'outputFile': f"converted/{output_key}"
            })
        }
        
    except Exception as e:
        print(f"Erro ao criar job MediaConvert: {str(e)}")
        raise e

def generate_output_key(source_key):
    """Gera nome do arquivo de saída"""
    # Remove extensão e adiciona .mp4
    base_name = os.path.splitext(source_key)[0]
    
    # Remove prefixo 'videos/' se existir
    if base_name.startswith('videos/'):
        base_name = base_name[7:]
    
    return f"{base_name}.mp4"