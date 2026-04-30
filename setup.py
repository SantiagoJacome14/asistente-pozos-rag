"""
Script de instalación y setup para Windows
Ejecutar como: python setup.py
"""

import os
import sys
import subprocess
import platform

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_step(step_num, text):
    print(f"\n[{step_num}] {text}")

def run_command(command, description):
    """Ejecuta un comando y reporta el resultado."""
    print(f"   Ejecutando: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✓ {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Error: {e.stderr}")
        return False

def setup_project():
    """Realiza la instalación completa del proyecto."""
    
    print_header("ASISTENTE TÉCNICO DE POZOS - INSTALACIÓN")
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    
    # Paso 1: Verificar Python
    print_step(1, "Verificando Requisitos")
    
    if sys.version_info < (3, 8):
        print("   ✗ Se requiere Python 3.8+")
        return False
    print(f"   ✓ Python {sys.version.split()[0]} OK")
    
    # Paso 2: Crear entorno virtual
    print_step(2, "Configurando Entorno Virtual")
    
    if platform.system() == "Windows":
        venv_activate = "venv\\Scripts\\activate.bat"
        activate_cmd = "venv\\Scripts\\activate.bat && "
    else:
        venv_activate = "venv/bin/activate"
        activate_cmd = "source venv/bin/activate && "
    
    if not os.path.exists("venv"):
        run_command(f"{sys.executable} -m venv venv", "Entorno virtual creado")
    else:
        print("   ✓ Entorno virtual ya existe")
    
    # Paso 3: Instalar dependencias
    print_step(3, "Instalando Dependencias")
    
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip install -r requirements.txt"
    else:
        pip_cmd = ". venv/bin/activate && pip install -r requirements.txt"
    
    run_command(pip_cmd, "Dependencias instaladas")
    
    # Paso 4: Crear directorios necesarios
    print_step(4, "Creando Directorios")
    
    dirs = ["data/informes", "vector_db", "logs"]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"   ✓ {dir_path}")
    
    # Paso 5: Instrucciones finales
    print_step(5, "Configuración Completada")
    
    print("\n✓ Instalación completada exitosamente!")
    print("\nPróximos pasos:")
    print("\n1. Obtén tu API Key de OpenAI:")
    print("   → Ve a https://platform.openai.com/api-keys")
    print("   → Crea una nueva key")
    print("\n2. Ejecuta la aplicación:")
    
    if platform.system() == "Windows":
        print("   → venv\\Scripts\\activate.bat")
    else:
        print("   → source venv/bin/activate")
    
    print("   → streamlit run app.py")
    
    print("\n3. Abre en tu navegador:")
    print("   → http://localhost:8501")
    
    print("\nPara más información, lee README.md")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    try:
        setup_project()
    except Exception as e:
        print(f"\n✗ Error durante la instalación: {e}")
        sys.exit(1)
