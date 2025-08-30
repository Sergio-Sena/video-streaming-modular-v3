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
    
    # Limitar tamanho (S3 limite: 1024, deixar margem para pasta)
    max_name_length = 200
    if len(name) > max_name_length:
        # Manter início e fim do nome
        name = name[:max_name_length//2] + '_' + name[-max_name_length//2:]
    
    # Reconstruir com extensão em minúsculas
    return f"{name}.{ext.lower()}" if ext else name

# Teste com nomes longos
test_files = [
    "Video Incrivel 1.mp4",
    "Este e um nome de arquivo extremamente longo que pode causar problemas no sistema de arquivos e precisa ser truncado adequadamente para funcionar corretamente.avi",
    "Nome Super Mega Ultra Hiper Extremamente Longo Com Muitas Palavras Que Pode Causar Problemas De Performance E Compatibilidade Com Sistemas De Arquivos Antigos E Modernos Incluindo S3 CloudFront E Outros Servicos AWS.mov"
]

print("Teste de Sanitizacao com Nomes Longos:")
print("=" * 60)

for original in test_files:
    sanitized = sanitize_filename(original)
    print(f"Original ({len(original)} chars):")
    print(f"  {original}")
    print(f"Sanitizado ({len(sanitized)} chars):")
    print(f"  {sanitized}")
    print("-" * 60)