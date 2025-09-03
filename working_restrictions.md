# 🔒 Restrições que Funcionam com HTML5 Video

## ✅ OPÇÃO 1: CloudFront com WAF
```
Player → CloudFront → WAF Rules → S3
```
- WAF bloqueia acessos diretos
- CloudFront permite nossa aplicação
- Player funciona normalmente

## ✅ OPÇÃO 2: Signed URLs Curtas
```
Player → Lambda → Signed URL (5min) → S3
```
- URLs expiram rapidamente
- Geradas sob demanda
- Player recebe URL válida

## ✅ OPÇÃO 3: Bucket Semi-Público
```
Player → S3 (público) → Logs/Monitoring
```
- Bucket público mas monitorado
- Alertas para acessos suspeitos
- Rotação de arquivos

## ❌ O QUE NÃO FUNCIONA
- Referer (player não envia)
- Tokens customizados (S3 não valida)
- Headers customizados (CORS volta)
- IPs específicos (usuários têm IPs diferentes)