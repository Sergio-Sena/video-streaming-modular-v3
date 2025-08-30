#!/usr/bin/env python3
import re
import unicodedata

def sanitize_filename(filename):
    """Sanitiza nome do arquivo seguindo regras rigorosas"""
    # Separar nome e extensão
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    
    # Normalizar e remover acentos: ção → cao, ã → a
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
    
    # Converter para minúsculas
    name = name.lower()
    
    # Remover caracteres especiais, pontuações e emojis
    # Manter apenas letras, números e espaços temporariamente
    name = re.sub(r'[^a-z0-9\s]', '', name)
    
    # Substituir espaços por underscores
    name = re.sub(r'\s+', '_', name)
    
    # Limpar múltiplos underscores
    name = re.sub(r'_+', '_', name)
    
    # Remover underscores no início/fim
    name = name.strip('_')
    
    # Garantir que não fique vazio
    if not name:
        name = 'video'
    
    # Reconstruir com extensão em minúsculas
    return f"{name}.{ext.lower()}" if ext else name

# Testes
test_files = [
    "Vídeo Incrível ❤️ #1.mp4",
    "Cindel Toda Safada Esfregando a Bucetinha. Voce Quer Chupar Essa Bucetinha. Cindel_xo Cindelxoxo - Pornhub.com.ts",
    "Arquivo com Acentos & Símbolos!!! @#$%.avi",
    "MAIÚSCULAS E minúsculas.MOV",
    "   Espaços   no   início   e   fim   .mkv",
    "Emojis 🎬🎥📹 e Símbolos ★☆♥.webm"
]

print("Teste de Sanitizacao de Nomes de Arquivos")
print("=" * 80)

for original in test_files:
    sanitized = sanitize_filename(original)
    print(f"Original:   {original}")
    print(f"Sanitizado: {sanitized}")
    print("-" * 80)