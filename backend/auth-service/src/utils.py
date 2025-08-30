import json
import boto3
import sys
import os
from typing import Dict, Any

# Import local utils
from utils.sanitizer import safe_log, TextSanitizer

class ResponseHelper:
    """Helper para padronizar respostas da API"""
    
    @staticmethod
    def cors_headers() -> Dict[str, str]:
        return {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Content-Type': 'application/json'
        }
    
    @staticmethod
    def success_response(data: Any, status_code: int = 200) -> Dict[str, Any]:
        return {
            'statusCode': status_code,
            'headers': ResponseHelper.cors_headers(),
            'body': json.dumps({
                'success': True,
                'data': data
            })
        }
    
    @staticmethod
    def error_response(message: str, status_code: int = 400) -> Dict[str, Any]:
        # Sanitizar mensagem de erro
        safe_message = TextSanitizer.sanitize_json_string(message)
        
        return {
            'statusCode': status_code,
            'headers': ResponseHelper.cors_headers(),
            'body': json.dumps({
                'success': False,
                'error': safe_message
            })
        }

class SecretsManager:
    """Gerenciador de secrets AWS"""
    
    def __init__(self):
        self.client = boto3.client('secretsmanager')
    
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return json.loads(response['SecretString'])
        except Exception as e:
            # Log seguro do erro
            safe_error = safe_log(f"Erro ao buscar secret {secret_name}: {str(e)}")
            print(safe_error)  # CloudWatch logs
            raise Exception(f"Erro ao buscar secret {secret_name}: {str(e)}")