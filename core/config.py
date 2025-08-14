"""
Agent 99 - Configuración del Sistema
====================================

Configuración centralizada del sistema siguiendo el patrón de milla99-backend
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class Settings(BaseSettings):
    """Configuración principal del sistema"""

    # ============================================================================
    # CONFIGURACIÓN DE LA APLICACIÓN
    # ============================================================================
    APP_NAME: str = "Agent 99"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = "Agente inteligente que hace scraping, analiza WhatsApp y clasifica interacciones"

    # ============================================================================
    # CONFIGURACIÓN DE BASE DE DATOS
    # ============================================================================
    DATABASE_URL: str = Field(
        default="postgresql://postgres:root@localhost:5432/agent99",
        description="URL de conexión a PostgreSQL"
    )

    # ============================================================================
    # CONFIGURACIÓN DE LA API
    # ============================================================================
    API_HOST: str = Field(default="0.0.0.0", description="Host de la API")
    API_PORT: int = Field(default=8000, description="Puerto de la API")
    DEBUG: bool = Field(default=True, description="Modo debug")

    # ============================================================================
    # CONFIGURACIÓN DE CORS
    # ============================================================================
    CORS_ORIGINS: List[str] = Field(
        default=["*"],
        description="Orígenes permitidos para CORS"
    )
    CORS_CREDENTIALS: bool = Field(
        default=True, description="Credenciales CORS")
    CORS_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Métodos HTTP permitidos"
    )
    CORS_HEADERS: List[str] = Field(
        default=["*"],
        description="Headers permitidos para CORS"
    )

    # ============================================================================
    # CONFIGURACIÓN DE OLLAMA
    # ============================================================================
    OLLAMA_MODEL: str = Field(
        default="gemma3:1b",
        description="Modelo de Ollama a usar"
    )
    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434",
        description="URL base de Ollama"
    )

    # ============================================================================
    # CONFIGURACIÓN DE EMBEDDINGS
    # ============================================================================
    EMBEDDING_MODEL: str = Field(
        default="paraphrase-MiniLM-L3-v2",
        description="Modelo de embeddings a usar"
    )

    # ============================================================================
    # CONFIGURACIÓN DE AGENTES
    # ============================================================================
    ENABLE_LEARNING: bool = Field(
        default=True, description="Habilitar aprendizaje de agentes")
    ENABLE_CROSS_AGENT_LEARNING: bool = Field(
        default=True, description="Habilitar aprendizaje entre agentes")

    # ============================================================================
    # CONFIGURACIÓN DE DIRECTORIOS
    # ============================================================================
    MODELS_DIR: str = Field(
        default="models", description="Directorio de modelos")
    DATA_DIR: str = Field(default="data", description="Directorio de datos")
    LOGS_DIR: str = Field(default="logs", description="Directorio de logs")

    # ============================================================================
    # CONFIGURACIÓN DE LOGGING
    # ============================================================================
    LOG_LEVEL: str = Field(default="INFO", description="Nivel de logging")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Formato de logs"
    )

    # ============================================================================
    # CONFIGURACIÓN DE SEGURIDAD
    # ============================================================================
    SECRET_KEY: str = Field(
        default="agent99-secret-key-change-in-production",
        description="Clave secreta para JWT"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Tiempo de expiración del token de acceso"
    )

    # ============================================================================
    # CONFIGURACIÓN DE MONITOREO
    # ============================================================================
    ENABLE_METRICS: bool = Field(
        default=True, description="Habilitar métricas")
    METRICS_PORT: int = Field(default=8001, description="Puerto para métricas")

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_config()

    def _validate_config(self):
        """Valida la configuración del sistema"""
        if not self.DATABASE_URL:
            raise ValueError("❌ DATABASE_URL es requerida")

        if self.DEBUG and "localhost" not in self.DATABASE_URL:
            print("⚠️ ADVERTENCIA: Modo DEBUG activado con base de datos no local")

    @property
    def database_config(self):
        """Obtiene la configuración de base de datos parseada"""
        from urllib.parse import urlparse

        parsed = urlparse(self.DATABASE_URL)
        return {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path[1:],
            'user': parsed.username,
            'password': parsed.password
        }

    @property
    def is_development(self):
        """Verifica si estamos en entorno de desarrollo"""
        return self.DEBUG or "localhost" in self.DATABASE_URL

    @property
    def is_production(self):
        """Verifica si estamos en entorno de producción"""
        return not self.is_development


# Instancia global de configuración
settings = Settings()


def get_settings() -> Settings:
    """Obtiene la configuración del sistema"""
    return settings


def reload_settings():
    """Recarga la configuración desde variables de entorno"""
    global settings
    settings = Settings()
    return settings


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_environment_info():
    """Obtiene información del entorno actual"""
    return {
        "environment": "development" if settings.is_development else "production",
        "database_url": settings.DATABASE_URL,
        "safe_for_init": settings.is_development,
        "debug_mode": settings.DEBUG,
        "api_host": settings.API_HOST,
        "api_port": settings.API_PORT
    }


def print_config_summary():
    """Imprime un resumen de la configuración"""
    print("🔧 Configuración del Sistema:")
    print(f"   - Aplicación: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(
        f"   - Entorno: {'Desarrollo' if settings.is_development else 'Producción'}")
    print(f"   - Base de datos: {settings.DATABASE_URL}")
    print(f"   - API: {settings.API_HOST}:{settings.API_PORT}")
    print(f"   - Ollama: {settings.OLLAMA_MODEL}")
    print(f"   - Embeddings: {settings.EMBEDDING_MODEL}")
    print(f"   - Debug: {'Sí' if settings.DEBUG else 'No'}")


if __name__ == "__main__":
    print_config_summary()
