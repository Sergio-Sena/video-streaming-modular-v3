import re
import unicodedata
from typing import str

class FileSanitizer:
    """Sanitizador de nomes de arquivos e caracteres especiais"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitiza nome de arquivo removendo caracteres especiais e emojis
        
        Args:
            filename: Nome original do arquivo
            
        Returns:
            Nome sanitizado seguro para S3/filesystem
        """
        if not filename:
            return "unnamed_file"
        
        # Remover emojis e caracteres especiais Unicode
        filename = FileSanitizer._remove_emojis(filename)
        
        # Normalizar Unicode (NFD = decomposição)
        filename = unicodedata.normalize('NFD', filename)
        
        # Remover acentos mantendo caracteres base
        filename = ''.join(c for c in filename if unicodedata.category(c) != 'Mn')
        
        # Substituir caracteres não permitidos por underscore
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remover caracteres de controle
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        
        # Substituir múltiplos espaços/underscores por um único
        filename = re.sub(r'[_\s]+', '_', filename)
        
        # Remover underscores do início/fim
        filename = filename.strip('_')
        
        # Garantir que não está vazio
        if not filename:
            filename = "unnamed_file"
        
        # Limitar tamanho (S3 limit = 1024, deixamos 255 para segurança)
        if len(filename) > 255:
            name, ext = FileSanitizer._split_extension(filename)
            max_name_len = 255 - len(ext) - 1
            filename = name[:max_name_len] + ext
        
        return filename
    
    @staticmethod
    def sanitize_folder_path(folder_path: str) -> str:
        """
        Sanitiza caminho de pasta
        
        Args:
            folder_path: Caminho original da pasta
            
        Returns:
            Caminho sanitizado
        """
        if not folder_path:
            return ""
        
        # Dividir por separadores de pasta
        parts = re.split(r'[/\\]', folder_path)
        
        # Sanitizar cada parte
        sanitized_parts = []
        for part in parts:
            if part and part not in ['.', '..']:
                sanitized_part = FileSanitizer.sanitize_filename(part)
                if sanitized_part:
                    sanitized_parts.append(sanitized_part)
        
        # Juntar com separador padrão
        return '/'.join(sanitized_parts)
    
    @staticmethod
    def _remove_emojis(text: str) -> str:
        """Remove emojis do texto"""
        # Padrão para emojis Unicode
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # símbolos & pictogramas
            "\U0001F680-\U0001F6FF"  # transporte & símbolos de mapa
            "\U0001F1E0-\U0001F1FF"  # bandeiras (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", 
            flags=re.UNICODE
        )
        return emoji_pattern.sub(r'', text)
    
    @staticmethod
    def _split_extension(filename: str) -> tuple:
        """Divide nome do arquivo e extensão"""
        if '.' in filename:
            parts = filename.rsplit('.', 1)
            return parts[0], '.' + parts[1]
        return filename, ''

class TextSanitizer:
    """Sanitizador para textos gerais (logs, mensagens, etc.)"""
    
    @staticmethod
    def sanitize_log_message(message: str) -> str:
        """Sanitiza mensagem para logs"""
        if not message:
            return ""
        
        # Remover emojis
        message = FileSanitizer._remove_emojis(message)
        
        # Normalizar Unicode
        message = unicodedata.normalize('NFKC', message)
        
        # Remover caracteres de controle exceto \n, \r, \t
        message = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', message)
        
        # Limitar tamanho
        if len(message) > 1000:
            message = message[:997] + "..."
        
        return message.strip()
    
    @staticmethod
    def sanitize_json_string(text: str) -> str:
        """Sanitiza string para JSON seguro"""
        if not text:
            return ""
        
        # Remover emojis
        text = FileSanitizer._remove_emojis(text)
        
        # Escapar caracteres especiais JSON
        text = text.replace('\\', '\\\\')
        text = text.replace('"', '\\"')
        text = text.replace('\n', '\\n')
        text = text.replace('\r', '\\r')
        text = text.replace('\t', '\\t')
        
        # Remover caracteres de controle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text

# Funções de conveniência
def sanitize_upload_filename(filename: str) -> str:
    """Função de conveniência para sanitizar nomes de upload"""
    return FileSanitizer.sanitize_filename(filename)

def sanitize_folder_name(folder_name: str) -> str:
    """Função de conveniência para sanitizar nomes de pasta"""
    return FileSanitizer.sanitize_folder_path(folder_name)

def safe_log(message: str) -> str:
    """Função de conveniência para logs seguros"""
    return TextSanitizer.sanitize_log_message(message)