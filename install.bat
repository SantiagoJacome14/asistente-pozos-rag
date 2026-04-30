@echo off
REM Script de instalación para Windows
REM Uso: install.bat

cls
echo ===============================================
echo   ASISTENTE TECNICO DE POZOS - INSTALACION
echo ===============================================
echo.

REM Verificar Python
echo [1] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python no esta instalado
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo. Python %PYTHON_VERSION% encontrado

REM Crear entorno virtual
echo.
echo [2] Creando entorno virtual...
if not exist "venv" (
    python -m venv venv
    echo. Entorno virtual creado
) else (
    echo. Entorno virtual ya existe
)

REM Activar entorno
echo.
echo [3] Activando entorno...
call venv\Scripts\activate.bat
echo. Entorno activado

REM Instalar dependencias
echo.
echo [4] Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo. Dependencias instaladas

REM Crear directorios
echo.
echo [5] Creando directorios...
if not exist "data\informes" mkdir data\informes
if not exist "vector_db" mkdir vector_db
if not exist "logs" mkdir logs
echo. Directorios creados

REM Listo
echo.
echo. Instalacion completada!
echo.
echo Proximos pasos:
echo 1. Obtén tu API Key en: https://platform.openai.com/api-keys
echo 2. Ejecuta: venv\Scripts\activate.bat
echo 3. Ejecuta: streamlit run app.py
echo 4. Abre: http://localhost:8501
echo.
pause
