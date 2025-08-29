import json
import boto3
import os
import urllib.parse

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
        
        job_settings = {
            "Role": "arn:aws:iam::969430605054:role/MediaConvertRole",
            "Settings": {
                "Inputs": [{
                    "FileInput": f"s3://{bucket}/{urllib.parse.quote(input_key, safe='/')}",
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
                "OriginalKey": input_key
            }
        }
        
        try:
            response = mediaconvert.create_job(**job_settings)
            print(f"Job criado: {response['Job']['Id']} para {input_key}")
            
        except Exception as e:
            print(f"Erro ao criar job: {e}")
    
    return {'statusCode': 200}