import boto3

def invalidate_cloudfront_cache():
    """Invalidar cache do CloudFront"""
    
    cloudfront = boto3.client('cloudfront')
    
    # ID da distribuição (pegar do console AWS)
    distribution_id = 'E1234567890123'  # Substituir pelo ID real
    
    try:
        response = cloudfront.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': ['/prod/*']  # Invalidar toda a API
                },
                'CallerReference': f'delete-fix-{int(__import__("time").time())}'
            }
        )
        
        print(f"Invalidação criada: {response['Invalidation']['Id']}")
        
    except Exception as e:
        print(f"Erro: {e}")
        print("Tente invalidar manualmente no console AWS")

if __name__ == "__main__":
    invalidate_cloudfront_cache()