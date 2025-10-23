@echo off
cd /d "%~dp0"
echo Activando entorno virtual...
call .\venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error al activar el entorno virtual
    pause
    exit /b 1
)
echo Iniciando aplicacion...
python run_app.py
if errorlevel 1 (
    echo Error al ejecutar la aplicacion
    pause
)
pause