#!/usr/bin/env python3
"""
Restringir bucket público por Referer
"""

import boto3
import json

def restrict_by_referer():
    """Permitir acesso apenas do nosso domínio"""
    s3_client = boto3.client('s3')
    bucket_name = 'automacao-video'
    
    # Política restrita por Referer
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "RestrictByReferer",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
                "Condition": {
                    "StringLike": {
                        "aws:Referer": [
                            "https://videos.sstechnologies-cloud.com/*",
                            "http://localhost:3000/*"
                        ]
                    }
                }
            }
        ]
    }
    
    try:
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(policy)
        )
        print("✅ Política Referer aplicada")
        print("Apenas nossa aplicação pode acessar")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    restrict_by_referer()