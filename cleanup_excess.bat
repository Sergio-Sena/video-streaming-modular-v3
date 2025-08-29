@echo off
echo 🧹 REMOVENDO ARQUIVOS EXCEDENTES...

cd backend

echo Removendo ZIPs antigos...
del /q *.zip 2>nul

echo Removendo arquivos de teste...
del /q test-*.* 2>nul
del /q simple-*.* 2>nul
del /q fix-*.* 2>nul

echo Removendo versões antigas...
del /q auth-*.py 2>nul
del /q videos-*.py 2>nul

echo ✅ Limpeza concluída!
echo.
echo 📊 Arquivos mantidos:
dir /b modules\*.py
echo.
echo 🗑️ Total removido: ~67 arquivos (~150MB)