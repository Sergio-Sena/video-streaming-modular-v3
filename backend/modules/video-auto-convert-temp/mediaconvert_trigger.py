import json
import boto3
import os
import urllib.parse
import re
import unicodedata

def sanitize_filename(filename):
    """Sanitiza nome do arquivo removendo caracteres problemáticos"""
    # Separar nome e extensão
    name, ext = os.path.splitext(filename)
    
    # Normalizar e remover acentos: ção → cao, ã → a
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
    
    # Remover caracteres especiais: espaços, emojis, símbolos
    name = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
    
    # Limpar múltiplos underscores: _____ → _
    name = re.sub(r'_+', '_', name)
    
    # Remover underscores no início/fim
    name = name.strip('_')
    
    # Garantir que não fique vazio
    if not name:
        name = 'video_convertido'
    
    return name + ext

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
            
        # Sanitizar nome do arquivo SEMPRE
        original_key = key
        sanitized_key = sanitize_filename(key)
        
        print(f"Arquivo original: {original_key}")
        print(f"Arquivo sanitizado: {sanitized_key}")
        
        # Se nome mudou, renomear arquivo no S3
        if original_key != sanitized_key:
            print(f"Renomeando: {original_key} → {sanitized_key}")
            try:
                s3 = boto3.client('s3')
                # Copiar com nome sanitizado
                s3.copy_object(
                    Bucket=bucket,
                    CopySource={'Bucket': bucket, 'Key': original_key},
                    Key=sanitized_key
                )
                # Deletar original
                s3.delete_object(Bucket=bucket, Key=original_key)
                print(f"Renomeação concluída: {sanitized_key}")
            except Exception as e:
                print(f"Erro na renomeação: {e}")
                sanitized_key = original_key  # Usar original se falhar
        
        # Usar nome sanitizado para conversão
        input_key = sanitized_key
        output_key = sanitized_key.replace('videos/', 'converted/').rsplit('.', 1)[0] + '.mp4'
        file_input_url = f"s3://{bucket}/{input_key}"
        
        print(f"Tentando arquivo original: {file_input_url}")
        
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
                            "CodecSettings": {
                                "Codec": "H_264",
                                "H264Settings": {
                                    "Bitrate": 4000000,
                                    "RateControlMode": "VBR",
                                    "QualityTuningLevel": "SINGLE_PASS_HQ"
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
                            "Container": "MP4"
                        }
                    }]
                }]
            },
            "UserMetadata": {
                "OriginalBucket": bucket,
                "OriginalKey": input_key,
                "SanitizedKey": sanitized_key
            }
        }
        
        try:
            response = mediaconvert.create_job(**job_settings)
            print(f"Job criado: {response['Job']['Id']} para {input_key}")
            
        except Exception as e:
            print(f"Erro ao criar job: {e}")
    
    return {'statusCode': 200}