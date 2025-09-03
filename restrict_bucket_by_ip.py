#!/usr/bin/env python3
"""
Restringir bucket por IPs específicos
"""

import boto3
import json

def restrict_by_ip():
    """Permitir apenas IPs específicos"""
    s3_client = boto3.client('s3')
    bucket_name = 'automacao-video'
    
    # Política restrita por IP
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "RestrictByIP",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
                "Condition": {
                    "IpAddress": {
                        "aws:SourceIp": [
                            "0.0.0.0/0"  # Substituir por IPs específicos
                        ]
                    }
                }
            }
        ]
    }
    
    print("Para usar IP restriction:")
    print("1. Obter IP do CloudFront")
    print("2. Obter IP do servidor")
    print("3. Substituir 0.0.0.0/0 pelos IPs reais")
    
    return policy

if __name__ == "__main__":
    policy = restrict_by_ip()
    print("Política IP:", json.dumps(policy, indent=2))