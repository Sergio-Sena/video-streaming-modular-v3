#!/usr/bin/env python3
"""
Corrigir CloudFront com OAC para vídeos
"""

import boto3
import json

def fix_cloudfront_distribution():
    """Corrigir distribuição CloudFront"""
    
    cloudfront_client = boto3.client('cloudfront')
    distribution_id = 'E1TK4C5GORRWUM'
    
    print("Correções necessárias no CloudFront:")
    print("1. Adicionar behavior para /users/*")
    print("2. Configurar CORS headers")
    print("3. Permitir métodos GET, HEAD, OPTIONS")
    
    # Configuração de behavior
    behavior_config = {
        "PathPattern": "/users/*",
        "TargetOriginId": "drive-online-storage.s3.amazonaws.com",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
            "Quantity": 3,
            "Items": ["GET", "HEAD", "OPTIONS"]
        },
        "ResponseHeadersPolicyId": "CORS_POLICY_ID"  # Criar política CORS
    }
    
    print("Behavior config:", json.dumps(behavior_config, indent=2))
    
    return "CloudFront precisa ser configurado manualmente"

if __name__ == "__main__":
    result = fix_cloudfront_distribution()
    print(f"\nResultado: {result}")
    print("Vantagens:")
    print("✅ Seguro (OAC)")
    print("✅ Performance global")
    print("❌ Configuração complexa")
    print("❌ Pode ter cache issues")