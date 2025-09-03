#!/usr/bin/env python3
"""
Copiar vídeo para bucket público com estrutura correta
"""

import boto3

def copy_video_to_public():
    """Copiar vídeo para bucket público"""
    s3_client = boto3.client('s3')
    
    source_bucket = 'drive-online-storage'
    source_key = 'users/user-sergio-sena/1756853751-Video automacao.mp4'
    
    dest_bucket = 'automacao-video'
    dest_key = 'videos/user-sergio-sena/1756853751-Video automacao.mp4'
    
    try:
        # Copiar arquivo
        s3_client.copy_object(
            CopySource={'Bucket': source_bucket, 'Key': source_key},
            Bucket=dest_bucket,
            Key=dest_key,
            ContentType='video/mp4',
            MetadataDirective='REPLACE'
        )
        
        print(f"✅ Vídeo copiado para: {dest_bucket}/{dest_key}")
        
        # URL final
        public_url = f"https://{dest_bucket}.s3.amazonaws.com/{dest_key}"
        print(f"✅ URL pública: {public_url}")
        
        return public_url
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

if __name__ == "__main__":
    url = copy_video_to_public()
    if url:
        print(f"\n🎯 Teste esta URL: {url}")
    else:
        print("\n❌ Falha na cópia")