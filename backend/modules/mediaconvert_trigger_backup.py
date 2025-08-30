import json
import boto3
import os
import urllib.parse
import re
import unicodedata

def sanitize_filename(filename):
    """Sanitiza nome do arquivo removendo caracteres problemáticos"""
    # Normalizar e remover acentos
    filename = unicodedata.normalize('NFD', filename)
    filename = ''.join(c for c in filename if unicodedata.category(c) != 'Mn')
    
    # Manter apenas caracteres seguros: letras, números, ponto, hífen, underscore
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Limpar múltiplos underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Remover underscores no início/fim
    filename = filename.strip('_')
    
    return filename

def handler(event, context):
    """Trigger MediaConvert quando arquivo é enviado para bucket temp"""
    
    mediaconvert = boto3.client('mediaconvert', region_name='us-east-1')
    
    # Pega endpoint do MediaConvert
    endpoints = mediaconvert.describe_endpoints()
    endpoint_url = endpoints['Endpoints'][0]['Url']
    mediaconvert = boto3.client('mediaconvert', endpoint_url=endpoint_url)
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        print(f"Arquivo detectado: s3://{bucket}/{key}")
        
        # Só processa arquivos .ts, .avi, .mov no bucket principal
        if bucket != 'video-streaming-sstech-eaddf6a1':
            continue
            
        # Só converte formatos específicos
        if not key.lower().endswith(('.ts', '.avi', '.mov', '.mkv')):
            continue
            
        print(f"Iniciando conversão para: {key}")
            
        # Gera nome do arquivo de saída
        input_key = key
        output_key = key.replace('videos/', 'converted/').rsplit('.', 1)[0] + '.mp4'
        
        # Sempre usar nome sanitizado para evitar problemas
        sanitized_key = sanitize_filename(input_key)
        file_input_url = f"s3://{bucket}/{sanitized_key}"
        print(f"Usando arquivo sanitizado: {file_input_url}")
        
        # Verificar se arquivo existe no S3
        s3 = boto3.client('s3')
        try:
            s3.head_object(Bucket=bucket, Key=sanitized_key)
            print(f"Arquivo encontrado: {sanitized_key}")
        except:
            # Se não existe, tentar nome original
            try:
                s3.head_object(Bucket=bucket, Key=input_key)
                file_input_url = f"s3://{bucket}/{input_key}"
                print(f"Usando arquivo original: {input_key}")
            except:
                print(f"Arquivo não encontrado: {input_key}")
                continue
        
        job_settings = {
            "Role": "arn:aws:iam::969430605054:role/MediaConvertRole",
            "Settings": {
                "Inputs": [{
                    "FileInput": file_input_url,
                    "VideoSelector": {
                        "Rotate": "AUTO"
                    },
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
                            "Destination": f"s3://video-streaming-sstech-eaddf6a1/{output_key.rsplit('/', 1)[0]}/"
                        }
                    },
                    "Outputs": [{
                        "NameModifier": "_converted",
                        "VideoDescription": {
                            "Width": 1920,
                            "Height": 1080,
                            "ScalingBehavior": "DEFAULT",
                            "CodecSettings": {
                                "Codec": "H_264",
                                "H264Settings": {
                                    "Bitrate": 4000000,
                                    "RateControlMode": "VBR",
                                    "QualityTuningLevel": "SINGLE_PASS_HQ",
                                    "FramerateControl": "INITIALIZE_FROM_SOURCE",
                                    "GopSizeUnits": "FRAMES",
                                    "GopSize": 90,
                                    "NumberBFramesBetweenReferenceFrames": 2,
                                    "GopClosedCadence": 1
                                }
                            }
                        },
                        "AudioDescriptions": [{
                            "AudioSourceName": "Audio Selector 1",
                            "CodecSettings": {
                                "Codec": "AAC",
                                "AacSettings": {
                                    "Bitrate": 128000,
                                    "SampleRate": 48000,
                                    "CodingMode": "CODING_MODE_2_0",
                                    "RateControlMode": "CBR"
                                }
                            }
                        }],
                        "ContainerSettings": {
                            "Container": "MP4"
                        }
                    }]
                }]
            },
            "UserMetadata": {
                "OriginalBucket": bucket,
                "OriginalKey": input_key
            }
        }
        
        try:
            response = mediaconvert.create_job(**job_settings)
            print(f"Job criado: {response['Job']['Id']} para {input_key}")
            
        except Exception as e:
            print(f"Erro ao criar job: {e}")
    
    return {'statusCode': 200}