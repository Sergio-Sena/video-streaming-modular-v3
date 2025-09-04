import boto3

def fix_upload_settings():
    s3_client = boto3.client('s3')
    
    # Configurar bucket para uploads grandes
    bucket_config = {
        'Rules': [
            {
                'ID': 'LargeFileUploads',
                'Status': 'Enabled',
                'Filter': {'Prefix': 'users/'},
                'AbortIncompleteMultipartUpload': {
                    'DaysAfterInitiation': 1
                }
            }
        ]
    }
    
    try:
        s3_client.put_bucket_lifecycle_configuration(
            Bucket='drive-online-storage',
            LifecycleConfiguration=bucket_config
        )
        print("Configuracao de lifecycle aplicada")
        
        # Verificar configuracao atual
        response = s3_client.get_bucket_cors(Bucket='drive-online-storage')
        print("CORS atual:", response['CORSRules'])
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    fix_upload_settings()