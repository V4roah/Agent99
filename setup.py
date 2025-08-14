#!/usr/bin/env python3
"""
Script de configuración para Agent99
Configura el entorno y descarga modelos necesarios
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def check_python_version():
    """Verifica la versión de Python"""
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")

def check_ollama():
    """Verifica si Ollama está instalado y ejecutándose"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama está ejecutándose")
            return True
        else:
            print("❌ Ollama no responde correctamente")
            return False
    except requests.exceptions.RequestException:
        print("❌ Ollama no está ejecutándose en http://localhost:11434")
        print("   Instala Ollama desde: https://ollama.ai")
        return False

def install_playwright_browsers():
    """Instala los navegadores necesarios para Playwright"""
    try:
        print("🔧 Instalando navegadores de Playwright...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                      check=True, capture_output=True)
        print("✅ Navegadores de Playwright instalados")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando navegadores: {e}")
        return False
    return True

def download_embedding_model():
    """Descarga el modelo de embeddings si no existe"""
    try:
        from sentence_transformers import SentenceTransformer
        
        model_name = "all-MiniLM-L6-v2"
        print(f"🔧 Descargando modelo de embeddings: {model_name}")
        
        # Esto descargará automáticamente el modelo
        model = SentenceTransformer(model_name)
        print("✅ Modelo de embeddings descargado")
        return True
    except Exception as e:
        print(f"❌ Error descargando modelo de embeddings: {e}")
        return False

def create_directories():
    """Crea los directorios necesarios"""
    directories = ["models", "data", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Directorio {directory} creado/verificado")

def create_env_file():
    """Crea archivo .env con configuración básica"""
    env_content = """# Configuración de Agent99
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Configuración de Ollama
OLLAMA_HOST=http://localhost:11434
DEFAULT_MODEL=gemma3:1b

# Configuración de embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Configuración de scraping
SCRAPING_TIMEOUT=8000
SCRAPING_HEADLESS=true

# Configuración de agentes
AGENT_LEARNING_ENABLED=true
AGENT_CROSS_LEARNING=true

# Configuración de WhatsApp
WHATSAPP_CONVERSATION_TIMEOUT=24
"""
    
    if not Path(".env").exists():
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print("✅ Archivo .env creado")
    else:
        print("ℹ️  Archivo .env ya existe")

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    required_packages = [
        "fastapi", "uvicorn", "pydantic",
        "playwright", "beautifulsoup4", "lxml",
        "scikit-learn", "joblib", "pandas",
        "sentence-transformers", "faiss-cpu",
        "ollama", "httpx", "numpy"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Paquetes faltantes: {', '.join(missing_packages)}")
        print("   Ejecuta: pip install -r requirements.txt")
        return False
    else:
        print("✅ Todas las dependencias están instaladas")
        return True

def main():
    """Función principal de configuración"""
    print("🚀 Configurando Agent99...")
    print("=" * 50)
    
    # Verificaciones básicas
    check_python_version()
    
    if not check_dependencies():
        sys.exit(1)
    
    # Crear directorios
    create_directories()
    
    # Crear archivo .env
    create_env_file()
    
    # Verificar Ollama
    ollama_ok = check_ollama()
    
    # Instalar navegadores de Playwright
    playwright_ok = install_playwright_browsers()
    
    # Descargar modelo de embeddings
    embedding_ok = download_embedding_model()
    
    print("\n" + "=" * 50)
    print("📋 Resumen de configuración:")
    print(f"   Ollama: {'✅' if ollama_ok else '❌'}")
    print(f"   Playwright: {'✅' if playwright_ok else '❌'}")
    print(f"   Embeddings: {'✅' if embedding_ok else '❌'}")
    
    if ollama_ok and playwright_ok and embedding_ok:
        print("\n🎉 ¡Configuración completada exitosamente!")
        print("\nPara ejecutar el servidor:")
        print("   python main.py")
        print("\nPara ver la documentación de la API:")
        print("   http://localhost:8000/docs")
    else:
        print("\n⚠️  Algunos componentes no se configuraron correctamente")
        print("   Revisa los errores arriba y ejecuta setup.py nuevamente")
        
        if not ollama_ok:
            print("\n💡 Para Ollama:")
            print("   1. Instala desde https://ollama.ai")
            print("   2. Ejecuta: ollama pull gemma3:1b")
        
        if not playwright_ok:
            print("\n💡 Para Playwright:")
            print("   Ejecuta: playwright install")
        
        if not embedding_ok:
            print("\n💡 Para embeddings:")
            print("   Verifica tu conexión a internet y ejecuta setup.py nuevamente")

if __name__ == "__main__":
    main()
