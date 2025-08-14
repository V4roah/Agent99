"""
Agent 99 - Configuración de Base de Datos
=========================================

Configuración de base de datos con SQLModel y creación automática de tablas
Siguiendo el patrón de milla99-backend
"""

from sqlmodel import Session, create_engine, SQLModel
from .config import settings
import os
from typing import Optional

# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================================================


def get_database_url() -> str:
    """Obtiene la URL de base de datos desde variables de entorno"""
    url = os.getenv(
        "DATABASE_URL", "postgresql://postgres:root@localhost:5432/agent99")
    print(f"🔍 DEBUG db.py: get_database_url() = {url}")
    return url


def validate_database_environment():
    """Valida que la configuración de base de datos sea segura"""
    database_url = get_database_url()

    # Validaciones básicas
    if not database_url:
        raise ValueError("❌ ERROR: DATABASE_URL no está configurada")

    if "localhost" in database_url or "127.0.0.1" in database_url:
        print("⚠️ ADVERTENCIA: Usando base de datos local")

    print(f"✅ Conectando a base de datos: {database_url}")


# ============================================================================
# ENGINE DE BASE DE DATOS
# ============================================================================

def create_optimized_engine():
    """Crea un engine optimizado con connection pooling"""
    database_url = get_database_url()

    # Configuración de connection pooling optimizada
    pool_config = {
        "pool_size": 10,  # Número de conexiones en el pool
        "max_overflow": 20,  # Conexiones adicionales si el pool está lleno
        "pool_pre_ping": True,  # Verificar conexiones antes de usar
        "pool_recycle": 3600,  # Reciclar conexiones cada hora
        "pool_timeout": 30,  # Timeout para obtener conexión del pool
        "echo": False,  # No mostrar SQL en logs
    }

    # Crear engine con pooling
    engine = create_engine(
        database_url,
        **pool_config
    )

    print(f"🔧 Engine creado con connection pooling:")
    print(f"   - Pool size: {pool_config['pool_size']}")
    print(f"   - Max overflow: {pool_config['max_overflow']}")
    print(f"   - Pool timeout: {pool_config['pool_timeout']}s")

    return engine


# Crear el engine optimizado
engine = create_optimized_engine()


def create_all_tables():
    """Crea todas las tablas en la base de datos automáticamente"""
    try:
        validate_database_environment()

        # Importar todos los modelos para que SQLModel los registre
        from models import (
            CustomerProfile, ProductInventory, Conversation,
            ConversationIntent, AgentLearning, AgentMetrics, WorkflowExecution
        )

        # Crear todas las tablas
        SQLModel.metadata.create_all(engine)
        print(f"✅ Todas las tablas creadas exitosamente")

    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        raise


def get_session():
    """Obtiene una sesión de base de datos"""
    validate_database_environment()
    return Session(engine)


def test_connection():
    """Prueba la conexión a la base de datos"""
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Conexión a base de datos exitosa")
            return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False


def close_connection():
    """Cierra la conexión a la base de datos"""
    try:
        engine.dispose()
        print("✅ Conexión a base de datos cerrada")
    except Exception as e:
        print(f"❌ Error cerrando conexión: {e}")


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_table_count(table_name: str) -> Optional[int]:
    """Obtiene el número de registros en una tabla"""
    try:
        with engine.connect() as conn:
            result = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = result.scalar()
            return count
    except Exception as e:
        print(f"❌ Error contando registros en {table_name}: {e}")
        return None


def get_database_info():
    """Obtiene información general de la base de datos"""
    try:
        with engine.connect() as conn:
            # Obtener lista de tablas
            result = conn.execute("""
                SELECT table_name, table_type
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = result.fetchall()

            info = {
                "database_url": get_database_url(),
                "tables_count": len(tables),
                "tables": [table[0] for table in tables],
                "connection_status": "active"
            }

            return info

    except Exception as e:
        return {
            "database_url": get_database_url(),
            "tables_count": 0,
            "tables": [],
            "connection_status": f"error: {e}"
        }
