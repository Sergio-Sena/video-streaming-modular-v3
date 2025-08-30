#!/usr/bin/env python3
"""
🧪 TESTE DE SANITIZAÇÃO - Video Streaming SStech
Testa a função de sanitização com casos reais
"""

import unicodedata
import re
import os

def sanitize_filename(filename):
    """Sanitiza nome do arquivo removendo caracteres problemáticos"""
    # Separar nome e extensão
    name, ext = os.path.splitext(filename)
    
    # Normalizar e remover acentos: ção → cao, ã → a
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
    
    # Remover caracteres especiais: espaços, emojis, símbolos
    name = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
    
    # Limpar múltiplos underscores: _____ → _
    name = re.sub(r'_+', '_', name)
    
    # Remover underscores no início/fim
    name = name.strip('_')
    
    # Garantir que não fique vazio
    if not name:
        name = 'video_convertido'
    
    return name + ext

# 🧪 CASOS DE TESTE
test_cases = [
    "videos/Tente Nao Gozar DESAFIO. Se Voce Gozar Na Minha Bucetinha , Voce Vai Perder! Nao me Deixe Gravida - Pornhub.com.ts",
    "videos/Video com acentos cao.ts",
    "videos/Video com emoji.ts", 
    "videos/Arquivo com espaços e símbolos @#$%.ts",
    "videos/normal-video.ts",
    "videos/123456.ts",
    "videos/arquivo___com____muitos_underscores.ts",
    "videos/.ts",  # Caso extremo
    "videos/so_simbolos_@#$%^&*().ts"
]

print("TESTE DE SANITIZACAO DE NOMES")
print("=" * 60)

for original in test_cases:
    sanitized = sanitize_filename(original)
    status = "[OK]" if sanitized != original else "[IGUAL]"
    
    print(f"{status}")
    print(f"  Original:   {original}")
    print(f"  Sanitizado: {sanitized}")
    print()

print("RESUMO:")
print("- Remove acentos: ção → cao, ã → a")
print("- Remove emojis: 😭 → _")
print("- Remove espaços: ' ' → _")
print("- Remove símbolos: @#$% → _")
print("- Limpa underscores múltiplos: ___ → _")
print("- Preserva: a-z, A-Z, 0-9, ., _, -")