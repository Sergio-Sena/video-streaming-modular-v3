#!/usr/bin/env python3
"""
Solução final para vídeos: Presigned URLs + CORS otimizado
"""

import boto3
import requests

def test_current_presigned_urls():
    """Testar presigned URLs atuais"""
    print("Testando presigned URLs atuais...")
    
    s3_client = boto3.client('s3')
    bucket_name = 'drive-online-storage'
    file_key = 'users/user-sergio-sena/1756853751-Video automacao.mp4'
    
    try:
        # Gerar presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_key},
            ExpiresIn=3600
        )
        
        print(f"Presigned URL gerada: {presigned_url[:100]}...")
        
        # Testar com HEAD request
        response = requests.head(presigned_url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Headers importantes:")
            headers = dict(response.headers)
            for key in ['content-type', 'content-length', 'accept-ranges']:
                if key in headers:
                    print(f"  {key}: {headers[key]}")
            
            # Testar CORS
            cors_response = requests.head(
                presigned_url, 
                headers={'Origin': 'https://videos.sstechnologies-cloud.com'},
                timeout=10
            )
            
            cors_headers = dict(cors_response.headers)
            cors_origin = cors_headers.get('access-control-allow-origin', 'N/A')
            print(f"  CORS Origin: {cors_origin}")
            
            return presigned_url if cors_origin != 'N/A' else None
        
        return None
        
    except Exception as e:
        print(f"Erro: {e}")
        return None

def main():
    """Testar solução atual"""
    print("=== TESTE DA SOLUCAO ATUAL ===")
    
    working_url = test_current_presigned_urls()
    
    if working_url:
        print(f"\n✅ PRESIGNED URLs FUNCIONANDO!")
        print(f"URL de teste: {working_url[:100]}...")
        print("\nSolução:")
        print("1. Use presigned URLs do S3 (já funcionando)")
        print("2. CORS já está configurado corretamente")
        print("3. Teste no frontend agora")
        
        # Criar arquivo de teste HTML
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Teste de Video</title>
</head>
<body>
    <h1>Teste de Video Drive Online</h1>
    <video controls width="800">
        <source src="{working_url}" type="video/mp4">
        Seu navegador não suporta video.
    </video>
    <p>Se o video carregar, a solução está funcionando!</p>
</body>
</html>'''
        
        with open('test_video_working.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("4. Arquivo test_video_working.html criado para teste")
        
    else:
        print(f"\n❌ PRESIGNED URLs COM PROBLEMA")
        print("Alternativas:")
        print("1. Verificar permissões do bucket S3")
        print("2. Usar CloudFront com CORS")
        print("3. Implementar proxy no backend")

if __name__ == "__main__":
    main()