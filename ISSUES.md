# 🚨 Issues Identificados - 28/08/2025

## 🔴 CRÍTICO (Bloqueia uso)

### 1. Token JWT Frontend
**Problema**: Login API funciona, mas token não é aceito nas requisições subsequentes
**Erro**: `{"success": false, "message": "Token inválido"}`
**Impacto**: Usuário não consegue fazer upload após login
**Prioridade**: 🔥 URGENTE

### 2. MediaConvert Config
**Problema**: Configuração de áudio incompleta
**Erro**: `sampleRate is a required property`
**Impacto**: Conversão .ts/.avi/.mov falha
**Prioridade**: 🔥 URGENTE

## 🟡 MÉDIO (Funcionalidade limitada)

### 3. Upload MP4
**Problema**: Depende da correção do token JWT
**Status**: Bloqueado pelo issue #1
**Prioridade**: ⚠️ ALTA

### 4. Verificação Auth
**Problema**: Login/logout automático intermitente
**Status**: Parcialmente corrigido
**Prioridade**: ⚠️ MÉDIA

## 🟢 BAIXO (Melhorias)

### 5. Cache CloudFront
**Problema**: Demora para propagar mudanças (2-3 min)
**Impacto**: Desenvolvimento mais lento
**Prioridade**: 🔄 BAIXA

### 6. Debug Logs
**Problema**: Muitos logs de debug no console
**Impacto**: Poluição visual
**Prioridade**: 🔄 BAIXA

## 📋 Plano de Correção

### Fase 1 (2h)
1. Corrigir token JWT no frontend
2. Ajustar configuração MediaConvert

### Fase 2 (1h)
3. Testar fluxo completo
4. Validar conversão automática

### Fase 3 (30min)
5. Limpeza de logs
6. Otimizações finais

**Tempo total estimado**: 3.5 horas