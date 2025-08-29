@echo off
echo 🔄 CRIANDO PONTO DE ROLLBACK...

set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set ROLLBACK_DIR=rollback_%TIMESTAMP%

mkdir %ROLLBACK_DIR%
mkdir %ROLLBACK_DIR%\backend\modules
mkdir %ROLLBACK_DIR%\frontend\modules

echo Salvando estado atual...
copy "backend\modules\auth.py" "%ROLLBACK_DIR%\backend\modules\" >nul
copy "backend\modules\videos.py" "%ROLLBACK_DIR%\backend\modules\" >nul
copy "backend\modules\utils.py" "%ROLLBACK_DIR%\backend\modules\" >nul
copy "frontend\modules\api.js" "%ROLLBACK_DIR%\frontend\modules\" >nul
copy "frontend\modules\auth.js" "%ROLLBACK_DIR%\frontend\modules\" >nul
copy "frontend\modules\videos.js" "%ROLLBACK_DIR%\frontend\modules\" >nul

echo ✅ Rollback criado em: %ROLLBACK_DIR%
echo.