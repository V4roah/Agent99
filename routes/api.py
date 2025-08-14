from fastapi import APIRouter
from . import basic, models, classification, scraping, llm, whatsapp, agents, vector, tagging, super_agent

# Crear router principal de la API
api_router = APIRouter()

# Incluir todas las rutas
api_router.include_router(basic.router)
api_router.include_router(models.router)
api_router.include_router(classification.router)
api_router.include_router(scraping.router)
api_router.include_router(llm.router)
api_router.include_router(whatsapp.router)
api_router.include_router(agents.router)
api_router.include_router(vector.router)
api_router.include_router(tagging.router)
api_router.include_router(super_agent.router)
