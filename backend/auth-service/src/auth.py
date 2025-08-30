import jwt
import hashlib
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from utils import SecretsManager

class AuthService:
    """Serviço de autenticação com MFA"""
    
    def __init__(self):
        self.secrets_manager = SecretsManager()
        self.secret_name = "video-streaming-v3-user"
    
    def get_user_credentials(self) -> Dict[str, Any]:
        """Busca credenciais do usuário no Secrets Manager"""
        return self.secrets_manager.get_secret(self.secret_name)
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifica senha com hash simples"""
        # Para simplicidade, usar hash SHA256
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return password_hash == hashed_password or password == hashed_password
    
    def generate_jwt(self, user_email: str) -> str:
        """Gera token JWT com expiração de 24h"""
        credentials = self.get_user_credentials()
        jwt_secret = credentials.get('jwtSecret')
        
        payload = {
            'email': user_email,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, jwt_secret, algorithm='HS256')
    
    def verify_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica e decodifica token JWT"""
        try:
            credentials = self.get_user_credentials()
            jwt_secret = credentials.get('jwtSecret')
            
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Token expirado")
        except jwt.InvalidTokenError:
            raise Exception("Token inválido")
    
    def verify_mfa_code(self, code: str, secret: str) -> bool:
        """Verifica código MFA do Google Authenticator"""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)
    
    def generate_mfa_qr(self, email: str, secret: str) -> str:
        """Gera QR code para configuração MFA"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name="Video Streaming SStech v3.0"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Converter para base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def login(self, email: str, password: str, mfa_code: str) -> Dict[str, Any]:
        """Processo completo de login com MFA"""
        try:
            # Buscar credenciais
            credentials = self.get_user_credentials()
            
            # Verificar email
            if email != credentials.get('email'):
                raise Exception("Credenciais inválidas")
            
            # Verificar senha
            if not self.verify_password(password, credentials.get('password')):
                raise Exception("Credenciais inválidas")
            
            # Verificar MFA se fornecido
            if mfa_code:
                mfa_secret = credentials.get('mfaSecret')
                if not self.verify_mfa_code(mfa_code, mfa_secret):
                    raise Exception("Código MFA inválido")
            
            # Gerar JWT
            token = self.generate_jwt(email)
            
            return {
                'token': token,
                'user': {
                    'email': email
                },
                'expiresIn': 86400  # 24 horas em segundos
            }
            
        except Exception as e:
            raise Exception(f"Erro no login: {str(e)}")
    
    def setup_mfa(self, email: str) -> Dict[str, Any]:
        """Setup inicial do MFA - gera QR code"""
        try:
            credentials = self.get_user_credentials()
            
            if email != credentials.get('email'):
                raise Exception("Email não autorizado")
            
            mfa_secret = credentials.get('mfaSecret')
            qr_code = self.generate_mfa_qr(email, mfa_secret)
            
            return {
                'qrCode': qr_code,
                'secret': mfa_secret,
                'instructions': "Escaneie o QR code com Google Authenticator"
            }
            
        except Exception as e:
            raise Exception(f"Erro no setup MFA: {str(e)}")
    
    def register(self, email: str, password: str) -> Dict[str, Any]:
        """Registro de novo usuário (simulado - retorna MFA setup)"""
        try:
            credentials = self.get_user_credentials()
            
            # Verificar se é o email autorizado
            if email != credentials.get('email'):
                raise Exception("Email não autorizado para registro")
            
            # Gerar QR code para MFA
            mfa_secret = credentials.get('mfaSecret')
            qr_code = self.generate_mfa_qr(email, mfa_secret)
            
            return {
                'message': 'Usuário registrado com sucesso',
                'mfa_setup': {
                    'qr_code': qr_code,
                    'secret': mfa_secret,
                    'instructions': 'Escaneie o QR code com Google Authenticator'
                }
            }
            
        except Exception as e:
            raise Exception(f"Erro no registro: {str(e)}")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verifica se o token JWT é válido"""
        try:
            payload = self.verify_jwt(token)
            
            return {
                'valid': True,
                'user': {
                    'email': payload['email']
                },
                'expires_at': payload['exp']
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Renova token JWT usando refresh token"""
        try:
            # Por simplicidade, usar o mesmo token como refresh
            payload = self.verify_jwt(refresh_token)
            new_token = self.generate_jwt(payload['email'])
            
            return {
                'token': new_token,
                'refresh_token': new_token,  # Simplificado
                'expires_in': 86400
            }
            
        except Exception as e:
            raise Exception(f"Erro ao renovar token: {str(e)}")