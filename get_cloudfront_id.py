import boto3

cloudfront = boto3.client('cloudfront')

try:
    distributions = cloudfront.list_distributions()
    
    for dist in distributions['DistributionList']['Items']:
        domain = dist['DomainName']
        dist_id = dist['Id']
        
        # Procurar pela API Gateway
        if 'execute-api' in domain or 'g1laj6w194' in domain:
            print(f"API Distribution: {dist_id} -> {domain}")
            
            # Invalidar cache
            response = cloudfront.create_invalidation(
                DistributionId=dist_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': 1,
                        'Items': ['/*']
                    },
                    'CallerReference': f'delete-fix-{int(__import__("time").time())}'
                }
            )
            
            print(f"Cache invalidado: {response['Invalidation']['Id']}")
            break
    
except Exception as e:
    print(f"Erro: {e}")
    print("Aguarde alguns minutos para o deploy se propagar")