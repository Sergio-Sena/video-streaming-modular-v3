import json
import sys
import os
from auth import AuthService
from utils import ResponseHelper

def lambda_handler(event, context):
    """
    Handler principal do auth-service-v3
    
    Endpoints:
    - POST /auth/register
    - POST /auth/login
    - POST /auth/verify
    - POST /auth/refresh
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
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")
                return ResponseHelper.error_response("JSON invalido", 400)
        else:
            body_data = {}
        
        # Instanciar servico
        auth_service = AuthService()
        
        # Roteamento
        if http_method == 'POST' and path == '/auth/register':
            return handle_register(auth_service, body_data)
            
        elif http_method == 'POST' and path == '/auth/login':
            return handle_login(auth_service, body_data)
            
        elif http_method == 'POST' and path == '/auth/verify':
            return handle_verify(auth_service, body_data)
            
        elif http_method == 'POST' and path == '/auth/refresh':
            return handle_refresh(auth_service, body_data)
            
        elif http_method == 'OPTIONS':
            # CORS preflight
            return ResponseHelper.success_response({}, 200)
            
        else:
            return ResponseHelper.error_response("Endpoint nao encontrado", 404)
    
    except Exception as e:
        print(f"Erro no lambda handler: {str(e)}")
        return ResponseHelper.error_response("Erro interno do servidor", 500)

def handle_register(auth_service, body_data):
    """Handle do endpoint de registro"""
    try:
        email = body_data.get('email')
        password = body_data.get('password')
        
        if not all([email, password]):
            return ResponseHelper.error_response("Email e senha sao obrigatorios", 400)
        
        result = auth_service.register(email, password)
        return ResponseHelper.success_response(result)
        
    except Exception as e:
        print(f"Register error: {str(e)}")
        return ResponseHelper.error_response(str(e), 400)

def handle_login(auth_service, body_data):
    """Handle do endpoint de login"""
    try:
        email = body_data.get('email')
        password = body_data.get('password')
        mfa_code = body_data.get('mfa_code')
        
        if not all([email, password]):
            return ResponseHelper.error_response("Email e senha sao obrigatorios", 400)
        
        result = auth_service.login(email, password, mfa_code)
        return ResponseHelper.success_response(result)
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return ResponseHelper.error_response(str(e), 401)

def handle_verify(auth_service, body_data):
    """Handle do endpoint de verificacao de token"""
    try:
        token = body_data.get('token')
        
        if not token:
            return ResponseHelper.error_response("Token e obrigatorio", 400)
        
        result = auth_service.verify_token(token)
        return ResponseHelper.success_response(result)
        
    except Exception as e:
        print(f"Verify error: {str(e)}")
        return ResponseHelper.error_response(str(e), 401)

def handle_refresh(auth_service, body_data):
    """Handle do endpoint de refresh token"""
    try:
        refresh_token = body_data.get('refresh_token')
        
        if not refresh_token:
            return ResponseHelper.error_response("Refresh token e obrigatorio", 400)
        
        result = auth_service.refresh_token(refresh_token)
        return ResponseHelper.success_response(result)
        
    except Exception as e:
        print(f"Refresh error: {str(e)}")
        return ResponseHelper.error_response(str(e), 401)