"""
🛡️ MIDDLEWARE DE SEGURANÇA
Validação, sanitização e proteção contra vulnerabilidades
"""
import re
import html
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """Middleware de segurança para todas as requisições"""
    
    def __init__(self):
        self.max_request_size = 100 * 1024 * 1024  # 100MB
        self.rate_limit_requests = 100  # requests por minuto
        self.blocked_patterns = [
            r'<script[^>]*>.*?</script>',  # Scripts
            r'javascript:',                # JavaScript URLs
            r'on\w+\s*=',                 # Event handlers
            r'eval\s*\(',                 # eval()
            r'document\.',                # DOM access
            r'window\.',                  # Window object
        ]
    
    def validate_request(self, event: Dict) -> Dict:
        """Valida requisição completa"""
        try:
            # Validação de tamanho
            size_check = self._check_request_size(event)
            if not size_check['valid']:
                return size_check
            
            # Validação de headers
            headers_check = self._validate_headers(event.get('headers', {}))
            if not headers_check['valid']:
                return headers_check
            
            # Validação de body
            if event.get('body'):
                body_check = self._validate_body(event['body'])
                if not body_check['valid']:
                    return body_check
            
            # Validação de query parameters
            if event.get('queryStringParameters'):
                query_check = self._validate_query_params(event['queryStringParameters'])
                if not query_check['valid']:
                    return query_check
            
            return {'valid': True, 'message': 'Requisição válida'}
            
        except Exception as e:
            logger.error(f"Erro na validação de segurança: {str(e)}")
            return {'valid': False, 'message': 'Erro na validação de segurança'}
    
    def sanitize_input(self, data: Any) -> Any:
        """Sanitiza entrada de dados"""
        if isinstance(data, str):
            return self._sanitize_string(data)
        elif isinstance(data, dict):
            return {key: self.sanitize_input(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        else:
            return data
    
    def sanitize_for_logging(self, data: Any) -> Any:
        """Sanitiza dados para logging seguro"""
        if isinstance(data, str):
            # Remove dados sensíveis
            sanitized = re.sub(r'password["\']?\s*:\s*["\'][^"\']*["\']', 'password":"***"', data, flags=re.IGNORECASE)
            sanitized = re.sub(r'token["\']?\s*:\s*["\'][^"\']*["\']', 'token":"***"', sanitized, flags=re.IGNORECASE)
            sanitized = re.sub(r'secret["\']?\s*:\s*["\'][^"\']*["\']', 'secret":"***"', sanitized, flags=re.IGNORECASE)
            return sanitized
        elif isinstance(data, dict):
            return {key: self.sanitize_for_logging(value) for key, value in data.items()}
        else:
            return str(data)[:100]  # Limita tamanho
    
    def check_xss_patterns(self, text: str) -> bool:
        """Verifica padrões de XSS"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        for pattern in self.blocked_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        return False
    
    def validate_file_upload(self, filename: str, file_size: int, content_type: str) -> Dict:
        """Valida upload de arquivo"""
        try:
            # Validação de nome
            if not filename or len(filename) > 255:
                return {'valid': False, 'message': 'Nome do arquivo inválido'}
            
            # Validação de extensão
            allowed_extensions = {'.mp4', '.ts', '.webm', '.avi', '.mov', '.mkv', '.wmv', '.flv'}
            file_ext = '.' + filename.lower().split('.')[-1] if '.' in filename else ''
            
            if file_ext not in allowed_extensions:
                return {'valid': False, 'message': 'Tipo de arquivo não permitido'}
            
            # Validação de tamanho (5GB máximo)
            max_size = 5 * 1024 * 1024 * 1024
            if file_size > max_size:
                return {'valid': False, 'message': 'Arquivo muito grande'}
            
            # Validação de content-type
            allowed_types = {
                'video/mp4', 'video/mp2t', 'video/webm', 'video/x-msvideo',
                'video/quicktime', 'video/x-matroska', 'video/x-ms-wmv', 'video/x-flv'
            }
            
            if content_type and content_type not in allowed_types:
                logger.warning(f"Content-type suspeito: {content_type}")
            
            return {'valid': True, 'message': 'Arquivo válido'}
            
        except Exception as e:
            logger.error(f"Erro na validação de arquivo: {str(e)}")
            return {'valid': False, 'message': 'Erro na validação'}
    
    def _check_request_size(self, event: Dict) -> Dict:
        """Verifica tamanho da requisição"""
        try:
            body = event.get('body', '')
            if isinstance(body, str):
                size = len(body.encode('utf-8'))
            else:
                size = len(str(body))
            
            if size > self.max_request_size:
                return {'valid': False, 'message': 'Requisição muito grande'}
            
            return {'valid': True}
            
        except Exception:
            return {'valid': False, 'message': 'Erro ao verificar tamanho'}
    
    def _validate_headers(self, headers: Dict) -> Dict:
        """Valida headers da requisição"""
        try:
            # Verifica headers obrigatórios
            content_type = headers.get('Content-Type') or headers.get('content-type')
            
            if content_type and 'application/json' in content_type:
                # Headers JSON válidos
                pass
            elif content_type and content_type.startswith('multipart/'):
                # Upload de arquivo
                pass
            
            # Verifica headers suspeitos
            for key, value in headers.items():
                if self.check_xss_patterns(str(value)):
                    logger.warning(f"Header suspeito: {key}")
                    return {'valid': False, 'message': 'Header inválido'}
            
            return {'valid': True}
            
        except Exception as e:
            logger.error(f"Erro na validação de headers: {str(e)}")
            return {'valid': False, 'message': 'Erro na validação de headers'}
    
    def _validate_body(self, body: str) -> Dict:
        """Valida body da requisição"""
        try:
            # Verifica se é JSON válido
            if body.strip().startswith('{'):
                try:
                    json_data = json.loads(body)
                    
                    # Verifica XSS em valores
                    for key, value in json_data.items():
                        if isinstance(value, str) and self.check_xss_patterns(value):
                            logger.warning(f"Possível XSS no campo: {key}")
                            return {'valid': False, 'message': 'Conteúdo inválido'}
                    
                except json.JSONDecodeError:
                    return {'valid': False, 'message': 'JSON inválido'}
            
            return {'valid': True}
            
        except Exception as e:
            logger.error(f"Erro na validação de body: {str(e)}")
            return {'valid': False, 'message': 'Erro na validação de body'}
    
    def _validate_query_params(self, params: Dict) -> Dict:
        """Valida query parameters"""
        try:
            for key, value in params.items():
                if isinstance(value, str) and self.check_xss_patterns(value):
                    logger.warning(f"Query param suspeito: {key}")
                    return {'valid': False, 'message': 'Parâmetro inválido'}
            
            return {'valid': True}
            
        except Exception as e:
            logger.error(f"Erro na validação de query params: {str(e)}")
            return {'valid': False, 'message': 'Erro na validação'}
    
    def _sanitize_string(self, text: str) -> str:
        """Sanitiza string individual"""
        if not text:
            return ''
        
        # HTML escape
        sanitized = html.escape(text)
        
        # Remove caracteres de controle
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
        
        # Limita tamanho
        return sanitized[:1000]

# Instância global
security_middleware = SecurityMiddleware()

def validate_request(event: Dict) -> Dict:
    """Função helper para validação"""
    return security_middleware.validate_request(event)

def sanitize_input(data: Any) -> Any:
    """Função helper para sanitização"""
    return security_middleware.sanitize_input(data)

def sanitize_for_logging(data: Any) -> Any:
    """Função helper para logging seguro"""
    return security_middleware.sanitize_for_logging(data)