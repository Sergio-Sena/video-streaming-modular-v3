#!/usr/bin/env python3
"""
Configurar CloudFront com OAC para acesso total
"""

import boto3
import json

def setup_cloudfront_oac():
    """Configurar CloudFront com Origin Access Control"""
    cloudfront_client = boto3.client('cloudfront')
    s3_client = boto3.client('s3')
    
    distribution_id = 'E1TK4C5GORRWUM'
    bucket_name = 'drive-online-storage'
    
    # 1. Criar OAC se não existir
    try:
        oac_response = cloudfront_client.create_origin_access_control(
            OriginAccessControlConfig={
                'Name': 'drive-online-oac',
                'Description': 'OAC for Drive Online videos',
                'OriginAccessControlOriginType': 's3',
                'SigningBehavior': 'always',
                'SigningProtocol': 'sigv4'
            }
        )
        oac_id = oac_response['OriginAccessControl']['Id']
        print(f"1. OAC criado: {oac_id}")
    except Exception as e:
        print(f"1. OAC já existe ou erro: {e}")
        # Listar OACs existentes
        oacs = cloudfront_client.list_origin_access_controls()
        for oac in oacs['OriginAccessControlList']['Items']:
            if 'drive-online' in oac['Name']:
                oac_id = oac['Id']
                print(f"1. Usando OAC existente: {oac_id}")
                break
    
    # 2. Política S3 para CloudFront
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowCloudFrontServicePrincipal",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudfront.amazonaws.com"
                },
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
                "Condition": {
                    "StringEquals": {
                        "AWS:SourceArn": f"arn:aws:cloudfront::969430605054:distribution/{distribution_id}"
                    }
                }
            }
        ]
    }
    
    try:
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        print("2. Política S3 para CloudFront aplicada")
    except Exception as e:
        print(f"2. Erro na política S3: {e}")
    
    print(f"3. CloudFront URL: https://d2gikqc9umroy8.cloudfront.net/")

if __name__ == "__main__":
    setup_cloudfront_oac()