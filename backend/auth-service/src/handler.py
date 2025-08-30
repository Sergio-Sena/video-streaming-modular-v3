import json
import sys
import os
from .auth import AuthService
from .utils import ResponseHelper

# Import local utils
from utils.sanitizer import safe_log, TextSanitizer

def sanitize_request_data(data):
    """Sanitiza dados da requisição recursivamente"""
    if isinstance(data, dict):
        return {k: sanitize_request_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_request_data(item) for item in data]
    elif isinstance(data, str):
        return TextSanitizer.sanitize_json_string(data)
    else:
        return data

def lambda_handler(event, context):
    """
    Handler principal do auth-service-v3
    
    Endpoints:
    - POST /auth/login
    - POST /auth/refresh  
    - GET /auth/mfa-setup
    - POST /auth/mfa-verify
    """
    
    try:
        # Parse do evento
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        body = event.get('body', '{}')
        
        # Parse do body se existir
        if body:
            try:
                body_data = json.loads(body)
                # Sanitizar strings do body
                body_data = sanitize_request_data(body_data)
            except json.JSONDecodeError as e:
                safe_error = safe_log(f"JSON decode error: {str(e)}")
                print(safe_error)
                return ResponseHelper.error_response("JSON inválido", 400)
        else:
            body_data = {}
        
        # Query parameters
        query_params = event.get('queryStringParameters') or {}
        
        # Headers
        headers = event.get('headers', {})
        
        # Instanciar serviço
        auth_service = AuthService()
        
        # Roteamento
        if http_method == 'POST' and path == '/auth/login':
            return handle_login(auth_service, body_data)
            
        elif http_method == 'POST' and path == '/auth/refresh':
            return handle_refresh(auth_service, headers)
            
        elif http_method == 'GET' and path == '/auth/mfa-setup':
            return handle_mfa_setup(auth_service, query_params)
            
        elif http_method == 'POST' and path == '/auth/mfa-verify':
            return handle_mfa_verify(auth_service, body_data)
            
        elif http_method == 'OPTIONS':
            # CORS preflight
            return ResponseHelper.success_response({}, 200)
            
        else:
            return ResponseHelper.error_response("Endpoint não encontrado", 404)
    
    except Exception as e:
        # Log seguro do erro
        safe_error = safe_log(f"Erro no lambda handler: {str(e)}")
        print(safe_error)
        return ResponseHelper.error_response("Erro interno do servidor", 500)

def handle_login(auth_service: AuthService, body_data: dict):
    """Handle do endpoint de login"""
    try:
        email = body_data.get('email')
        password = body_data.get('password')
        mfa_code = body_data.get('mfaCode')
        
        if not all([email, password, mfa_code]):
            return ResponseHelper.error_response("Email, senha e código MFA são obrigatórios", 400)
        
        result = auth_service.login(email, password, mfa_code)
        return ResponseHelper.success_response(result)
        
    except Exception as e:
        safe_error = safe_log(f"Login error: {str(e)}")
        print(safe_error)
        return ResponseHelper.error_response(str(e), 401)

def handle_refresh(auth_service: AuthService, headers: dict):
    """Handle do endpoint de refresh token"""
    try:
        auth_header = headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return ResponseHelper.error_response("Token Bearer requerido", 401)
        
        token = auth_header.replace('Bearer ', '')
        result = auth_service.refresh_token(token)
        return ResponseHelper.success_response(result)
        
    except Exception as e:
        safe_error = safe_log(f"Refresh error: {str(e)}")
        print(safe_error)
        return ResponseHelper.error_response(str(e), 401)

def handle_mfa_setup(auth_service: AuthService, query_params: dict):
    """Handle do endpoint de setup MFA"""
    try:
        email = query_params.get('email')
        
        if not email:
            return ResponseHelper.error_response("Email é obrigatório", 400)
        
        result = auth_service.setup_mfa(email)
        return ResponseHelper.success_response(result)
        
    except Exception as e:
        safe_error = safe_log(f"MFA setup error: {str(e)}")
        print(safe_error)
        return ResponseHelper.error_response(str(e), 400)

def handle_mfa_verify(auth_service: AuthService, body_data: dict):
    """Handle do endpoint de verificação MFA"""
    try:
        email = body_data.get('email')
        mfa_code = body_data.get('mfaCode')
        
        if not all([email, mfa_code]):
            return ResponseHelper.error_response("Email e código MFA são obrigatórios", 400)
        
        # Buscar credenciais para verificar MFA
        credentials = auth_service.get_user_credentials()
        
        if email != credentials.get('email'):
            return ResponseHelper.error_response("Email não autorizado", 401)
        
        mfa_secret = credentials.get('mfaSecret')
        is_valid = auth_service.verify_mfa_code(mfa_code, mfa_secret)
        
        return ResponseHelper.success_response({
            'valid': is_valid,
            'message': 'Código MFA válido' if is_valid else 'Código MFA inválido'
        })
        
    except Exception as e:
        safe_error = safe_log(f"MFA verify error: {str(e)}")
        print(safe_error)
        return ResponseHelper.error_response(str(e), 400)