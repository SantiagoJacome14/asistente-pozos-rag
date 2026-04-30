#!/bin/bash
# Script de instalación para macOS/Linux
# Uso: bash install.sh

set -e

echo "==============================================="
echo "  ASISTENTE TÉCNICO DE POZOS - INSTALACIÓN"
echo "==============================================="
echo ""

# Verificar Python
echo "[1] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 no está instalado"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION encontrado"

# Crear entorno virtual
echo ""
echo "[2] Creando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Entorno virtual creado"
else
    echo "✓ Entorno virtual ya existe"
fi

# Activar entorno
echo ""
echo "[3] Activando entorno..."
source venv/bin/activate
echo "✓ Entorno activado"

# Instalar dependencias
echo ""
echo "[4] Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencias instaladas"

# Crear directorios
echo ""
echo "[5] Creando directorios..."
mkdir -p data/informes vector_db logs
echo "✓ Directorios creados"

# Listo
echo ""
echo "✓ Instalación completada!"
echo ""
echo "Próximos pasos:"
echo "1. Obtén tu API Key en: https://platform.openai.com/api-keys"
echo "2. Ejecuta: source venv/bin/activate"
echo "3. Ejecuta: streamlit run app.py"
echo "4. Abre: http://localhost:8501"
echo ""
