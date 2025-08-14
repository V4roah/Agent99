from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes.api import api_router
import uvicorn

# Imports del core
from core.db import create_all_tables
from core.config import settings, get_environment_info
from core.init_data import init_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manager del ciclo de vida de la aplicación"""
    print("🚀 Iniciando Agent 99...")

    # Mostrar información del entorno
    env_info = get_environment_info()
    print(f"🌍 Entorno: {env_info['environment']}")
    print(f"📊 Base de datos: {env_info['database_url']}")
    print(f"🔒 Seguro para inicialización: {env_info['safe_for_init']}")

    # Crear tablas automáticamente
    create_all_tables()

    # Inicializar datos (con validaciones automáticas)
    init_data()

    print("✅ Agent 99 iniciado correctamente")
    yield
    print("🔚 Cerrando Agent 99...")


# Crear aplicación FastAPI con lifespan
app = FastAPI(
    lifespan=lifespan,
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Incluir todas las rutas de la API
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
