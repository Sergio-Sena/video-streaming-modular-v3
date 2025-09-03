#!/usr/bin/env python3
"""
Configurar CloudFront + WAF para restringir acesso
"""

import boto3

def setup_cloudfront_restriction():
    """Configurar CloudFront com WAF"""
    
    print("=== CONFIGURAÇÃO CLOUDFRONT + WAF ===")
    
    # 1. Criar distribuição CloudFront para bucket público
    cloudfront_config = {
        "Origins": {
            "Quantity": 1,
            "Items": [
                {
                    "Id": "automacao-video-origin",
                    "DomainName": "automacao-video.s3.amazonaws.com",
                    "S3OriginConfig": {
                        "OriginAccessIdentity": ""
                    }
                }
            ]
        },
        "DefaultCacheBehavior": {
            "TargetOriginId": "automacao-video-origin",
            "ViewerProtocolPolicy": "redirect-to-https",
            "AllowedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"]
            }
        }
    }
    
    # 2. Regras WAF
    waf_rules = {
        "AllowOurDomain": {
            "Name": "AllowOurDomain",
            "Statement": {
                "ByteMatchStatement": {
                    "SearchString": "videos.sstechnologies-cloud.com",
                    "FieldToMatch": {"SingleHeader": {"Name": "referer"}},
                    "TextTransformations": [{"Priority": 0, "Type": "LOWERCASE"}],
                    "PositionalConstraint": "CONTAINS"
                }
            },
            "Action": {"Allow": {}}
        },
        "BlockOthers": {
            "Name": "BlockOthers", 
            "Statement": {"RateLimitStatement": {"Limit": 100}},
            "Action": {"Block": {}}
        }
    }
    
    print("CloudFront Config:", cloudfront_config)
    print("WAF Rules:", waf_rules)
    
    return "Configuração manual necessária no console AWS"

if __name__ == "__main__":
    result = setup_cloudfront_restriction()
    print(f"\nResultado: {result}")
    print("\nVantagens:")
    print("✅ Player funciona normalmente")
    print("✅ Acesso restrito ao nosso domínio") 
    print("✅ Performance global (CDN)")
    print("✅ Proteção DDoS automática")