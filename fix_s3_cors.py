import boto3
import json

def fix_s3_cors():
    s3_client = boto3.client('s3')
    
    cors_config = {
        'CORSRules': [
            {
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
                'AllowedOrigins': [
                    'https://videos.sstechnologies-cloud.com',
                    'http://localhost:5173',
                    'http://localhost:3000'
                ],
                'ExposeHeaders': ['ETag'],
                'MaxAgeSeconds': 3600
            }
        ]
    }
    
    try:
        s3_client.put_bucket_cors(
            Bucket='drive-online-storage',
            CORSConfiguration=cors_config
        )
        print("CORS configurado para drive-online-storage")
        
        # Tambem para bucket publico
        s3_client.put_bucket_cors(
            Bucket='automacao-video',
            CORSConfiguration=cors_config
        )
        print("CORS configurado para automacao-video")
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    fix_s3_cors()