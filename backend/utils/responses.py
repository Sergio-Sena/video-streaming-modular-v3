"""
📤 UTILITÁRIOS DE RESPOSTA
Respostas padronizadas e seguras para todas as APIs
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime

def get_cors_headers(origin: Optional[str] = None) -> Dict[str, str]:
    """Retorna headers CORS seguros"""
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Requested-With',
        'Access-Control-Allow-Methods': 'POST,GET,OPTIONS,DELETE,PUT',
        'Access-Control-Max-Age': '86400',
        'Content-Type': 'application/json',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }

def success_response(data: Dict[str, Any], origin: Optional[str] = None, status_code: int = 200) -> Dict:
    """Resposta de sucesso padronizada"""
    response_data = {
        'success': True,
        'timestamp': datetime.utcnow().isoformat(),
        **data
    }
    
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(origin),
        'body': json.dumps(response_data, default=str)
    }

def error_response(message: str, origin: Optional[str] = None, status_code: int = 400, 
                  error_code: Optional[str] = None) -> Dict:
    """Resposta de erro padronizada"""
    response_data = {
        'success': False,
        'message': str(message)[:200],  # Limita tamanho da mensagem
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if error_code:
        response_data['errorCode'] = error_code
    
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(origin),
        'body': json.dumps(response_data)
    }

def validation_error_response(errors: Dict[str, str], origin: Optional[str] = None) -> Dict:
    """Resposta de erro de validação"""
    return error_response(
        message='Dados inválidos',
        origin=origin,
        status_code=400
    )

def unauthorized_response(message: str = 'Não autorizado', origin: Optional[str] = None) -> Dict:
    """Resposta de não autorizado"""
    return error_response(
        message=message,
        origin=origin,
        status_code=401,
        error_code='UNAUTHORIZED'
    )

def forbidden_response(message: str = 'Acesso negado', origin: Optional[str] = None) -> Dict:
    """Resposta de acesso negado"""
    return error_response(
        message=message,
        origin=origin,
        status_code=403,
        error_code='FORBIDDEN'
    )

def not_found_response(message: str = 'Recurso não encontrado', origin: Optional[str] = None) -> Dict:
    """Resposta de não encontrado"""
    return error_response(
        message=message,
        origin=origin,
        status_code=404,
        error_code='NOT_FOUND'
    )

def internal_error_response(message: str = 'Erro interno do servidor', origin: Optional[str] = None) -> Dict:
    """Resposta de erro interno"""
    return error_response(
        message=message,
        origin=origin,
        status_code=500,
        error_code='INTERNAL_ERROR'
    )

def options_response(origin: Optional[str] = None) -> Dict:
    """Resposta para requisições OPTIONS (CORS)"""
    return {
        'statusCode': 200,
        'headers': get_cors_headers(origin),
        'body': ''
    }