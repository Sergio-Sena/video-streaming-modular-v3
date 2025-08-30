#!/usr/bin/env python3
import re
import unicodedata

def sanitize_filename(filename):
    """Sanitiza nome do arquivo seguindo regras rigorosas"""
    # Separar nome e extensão
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    
    # Normalizar e remover acentos
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
    
    # Converter para minúsculas
    name = name.lower()
    
    # Remover caracteres especiais, pontuações e emojis
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

# Teste simples
test_files = [
    "Video Incrivel 1.mp4",
    "Arquivo com Acentos e Simbolos.avi", 
    "MAIUSCULAS E minusculas.MOV",
    "Espacos no inicio e fim.mkv"
]

print("Teste de Sanitizacao:")
print("=" * 50)

for original in test_files:
    sanitized = sanitize_filename(original)
    print(f"'{original}' -> '{sanitized}'")