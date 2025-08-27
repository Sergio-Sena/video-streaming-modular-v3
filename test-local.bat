@echo off
echo ========================================
echo   TESTE LOCAL - VIDEO STREAMING MODULAR
echo ========================================

cd frontend

echo.
echo Iniciando servidor local na porta 8080...
echo.
echo URLs de teste:
echo - Frontend: http://localhost:8080
echo - API Real:  https://4y3erwjgak.execute-api.us-east-1.amazonaws.com/prod
echo.
echo Pressione Ctrl+C para parar o servidor
echo ========================================

python -m http.server 8080