import os
from typing import Optional

class Config:
    """Configuración centralizada del proyecto"""
    
    # Configuración de la API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    
    # Configuración de Ollama
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gemma3:1b")
    
    # Configuración de embeddings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Configuración de archivos
    MODEL_DIR: str = os.getenv("MODEL_DIR", "models")
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    
    # Configuración de scraping
    SCRAPING_TIMEOUT: int = int(os.getenv("SCRAPING_TIMEOUT", "8000"))
    SCRAPING_HEADLESS: bool = os.getenv("SCRAPING_HEADLESS", "true").lower() == "true"
    
    # Configuración de clasificación
    CLASSIFICATION_CATEGORIES: list = [
        "ventas", "soporte", "reclamo", "consulta", "otro"
    ]
    
    # Configuración de agentes
    AGENT_LEARNING_ENABLED: bool = os.getenv("AGENT_LEARNING_ENABLED", "true").lower() == "true"
    AGENT_CROSS_LEARNING: bool = os.getenv("AGENT_CROSS_LEARNING", "true").lower() == "true"
    
    # Configuración de WhatsApp
    WHATSAPP_EXPORT_PATTERN: str = r'\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] (.+?): (.+)'
    WHATSAPP_CONVERSATION_TIMEOUT: int = int(os.getenv("WHATSAPP_CONVERSATION_TIMEOUT", "24"))  # horas
    
    # Configuración de vector store
    VECTOR_INDEX_PATH: str = os.getenv("VECTOR_INDEX_PATH", "models/vector_index.faiss")
    VECTOR_SEARCH_DEFAULT_K: int = int(os.getenv("VECTOR_SEARCH_DEFAULT_K", "5"))
    
    @classmethod
    def get_model_path(cls, filename: str) -> str:
        """Obtiene la ruta completa para un archivo de modelo"""
        return os.path.join(cls.MODEL_DIR, filename)
    
    @classmethod
    def get_data_path(cls, filename: str) -> str:
        """Obtiene la ruta completa para un archivo de datos"""
        return os.path.join(cls.DATA_DIR, filename)
    
    @classmethod
    def ensure_directories(cls):
        """Asegura que existan los directorios necesarios"""
        os.makedirs(cls.MODEL_DIR, exist_ok=True)
        os.makedirs(cls.DATA_DIR, exist_ok=True)

# Instancia global de configuración
config = Config()
